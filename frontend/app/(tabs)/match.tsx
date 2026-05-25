import { useCallback, useEffect, useRef, useState } from "react";
import { StyleSheet, View } from "react-native";
import { usePositionalStream } from "../../src/api/usePositionalStream";
import {
  chunkToRatio,
  frameNToChunk,
  REPLAY_CHUNK_SIZE,
  REPLAY_SKIP_FRAMES,
  useReplayStream,
} from "../../src/api/useReplayStream";
import { useApi } from "../../src/api/ApiContext";
import type { BetOpportunityMessage } from "../../src/api/types/bets";
import { PitchCanvas } from "../../src/components/pitch/PitchCanvas";
import { ChatOverlay } from "../../src/components/chat/ChatOverlay";
import { BetOpportunityBanner } from "../../src/components/bets/BetOpportunityBanner";
import { BetStatusDashboard } from "../../src/components/bets/BetStatusDashboard";
import { MatchTimeline } from "../../src/components/replay/MatchTimeline";
import { PositionalFrame } from "../../src/types/positional";

type PlaybackMode = "live" | "dvr";

function ratioToChunk(ratio: number, flushedChunks: number): number {
  if (flushedChunks <= 0) return 0;
  return Math.min(Math.floor(ratio * flushedChunks), flushedChunks - 1);
}


export default function MatchScreen() {
  const positional = usePositionalStream();
  const {
    connectBetSettlementSocket,
    disconnectBetSettlementSocket,
    latestBetOpportunity,
    clearLatestBetOpportunity,
    setLatestBetOpportunity,
  } = useApi();
  const replay = useReplayStream();
  const [mode, setMode] = useState<PlaybackMode>("live");
  const [scrubRatio, setScrubRatio] = useState(1);
  const [isScrubbing, setIsScrubbing] = useState(false);

  const flushedChunks = replay.replayStatus.chunk_count;
  const flushedChunksRef = useRef(flushedChunks);
  flushedChunksRef.current = flushedChunks;
  const lastPlayedChunkRef = useRef(0);
  const { liveEdgeSeq, firstFrameN } = replay;
  const frameRef = useRef<PositionalFrame | null>(null);

  useEffect(() => {
    positional.connect(1, 0, frameRef);
    connectBetSettlementSocket();
    return () => {
      {
        positional.disconnect();
        disconnectBetSettlementSocket();
      }
      replay.disconnect();
    };
  }, []);

  // Chat-room path: forwards opportunities to the shared ApiContext state
  // so both delivery channels (settlement socket + chat room) use one banner.
  const handleBetOpportunity = useCallback(
    (msg: BetOpportunityMessage) => {
      setLatestBetOpportunity(msg.opportunity);
    },
    [setLatestBetOpportunity],
  );

  useEffect(() => {
    if (mode === "live" && !isScrubbing) {
      setScrubRatio(1);
    }
  }, [mode, isScrubbing, flushedChunks]);

  const seekToChunk = useCallback(
    (targetChunk: number) => {
      const chunks = flushedChunksRef.current;
      if (chunks === 0) return;

      const clamped = Math.max(0, Math.min(targetChunk, chunks - 1));
      lastPlayedChunkRef.current = Math.max(0, clamped - 1);
      setScrubRatio(chunkToRatio(clamped, chunks));
      setMode("dvr");
      setIsScrubbing(false);
      replay.connect(clamped, frameRef);
      positional.disconnect();
    },
    [positional, replay],
  );

  const getCurrentFrameN = useCallback((): number | null => {
    if (mode === "dvr") {
      if (replay.lastSeq != null) return replay.lastSeq;
    } else {
      const fromActive = positional.lastSeq ?? replay.lastSeq;
      if (fromActive != null) return fromActive;
      if (liveEdgeSeq != null) return liveEdgeSeq;
    }

    // Fallback: estimate from scrubRatio (covers the gap right after a seek
    // before any replay messages have arrived).
    const first = replay.replayStatus.first_frame_n;
    const chunks = flushedChunksRef.current;
    if (first != null && chunks > 0) {
      const chunk = ratioToChunk(scrubRatio, chunks);
      return first + chunk * REPLAY_CHUNK_SIZE;
    }
    return null;
  }, [
    mode,
    replay.lastSeq,
    positional.lastSeq,
    liveEdgeSeq,
    replay.replayStatus.first_frame_n,
    scrubRatio,
  ]);

  const handleSkip = useCallback(
    (direction: -1 | 1) => {
      const first = replay.replayStatus.first_frame_n;
      const liveEdge = replay.replayStatus.live_edge_seq;
      const chunks = flushedChunksRef.current;
      if (first == null || liveEdge == null || chunks === 0) return;

      const current = getCurrentFrameN();
      if (current == null) return;

      if (direction < 0) {
        if (current - first < REPLAY_SKIP_FRAMES) return;
      } else if (liveEdge - current < REPLAY_SKIP_FRAMES) {
        return;
      }

      const targetFrame = current + direction * REPLAY_SKIP_FRAMES;
      const targetChunk = frameNToChunk(targetFrame, first);
      seekToChunk(targetChunk);
    },
    [getCurrentFrameN, replay.replayStatus, seekToChunk],
  );

  const handleScrubMove = useCallback(
    (ratio: number) => {
      setIsScrubbing(true);
      setScrubRatio(ratio);
      if (mode === "dvr") {
        replay.disconnect();
      }
    },
    [mode, replay],
  );

  const handleScrubEnd = useCallback(
    (ratio: number) => {
      setIsScrubbing(false);
      setScrubRatio(ratio);

      const chunks = flushedChunksRef.current;
      if (chunks === 0) return;

      const targetChunk = ratioToChunk(ratio, chunks);
      seekToChunk(targetChunk);
    },
    [seekToChunk],
  );

  useEffect(() => {
    if (mode !== "dvr" || replay.lastSeq == null) return;
    lastPlayedChunkRef.current = frameNToChunk(replay.lastSeq, replay.firstFrameN);
  }, [mode, replay.lastSeq, replay.firstFrameN]);

  function handleGoLive() {
    if (mode === "live" && !isScrubbing) return;

    replay.disconnect();
    setMode("live");
    setScrubRatio(1);
    setIsScrubbing(false);
    const resumeSeq = liveEdgeSeq ?? 0;
    positional.connect(1, resumeSeq, frameRef);
  }

  return (
    <View style={styles.container}>
      <PitchCanvas frameRef={frameRef} />
      <MatchTimeline
        scrubRatio={scrubRatio}
        disabled={flushedChunks === 0}
        onScrubMove={handleScrubMove}
        onScrubEnd={handleScrubEnd}
        onGoLive={handleGoLive}
        onSkipBack={() => handleSkip(-1)}
        onSkipForward={() => handleSkip(1)}
      />
      <ChatOverlay onBetOpportunity={handleBetOpportunity} />
      <BetStatusDashboard />
      {latestBetOpportunity && (
        <BetOpportunityBanner
          opportunity={latestBetOpportunity}
          onDismiss={clearLatestBetOpportunity}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
});
