import { useCallback, useEffect, useRef, useState } from "react";
import { PositionalSocket } from "./PositionalSocket";
import { StreamStatus } from "./useEventsStream";
import { getReplayStatusUrl, getReplayStreamUrl } from "./config";

export const REPLAY_CHUNK_SIZE = Number(process.env.EXPO_PUBLIC_REPLAY_CHUNK_SIZE ?? "25");
export const REPLAY_FRAME_INTERVAL_SEC = Number(process.env.EXPO_PUBLIC_REPLAY_FRAME_INTERVAL_SEC ?? "0.04");
export const REPLAY_SKIP_SECONDS = Number(process.env.EXPO_PUBLIC_REPLAY_SKIP_SECONDS ?? "10");
export const REPLAY_SKIP_FRAMES = Math.round(REPLAY_SKIP_SECONDS / REPLAY_FRAME_INTERVAL_SEC);

export interface ReplayStatus {
  available: boolean;
  chunk_count: number;
  pending_frames: number;
  live_edge_seq: number | null;
  first_frame_n: number | null;
  frame_count: number;
}

export function frameNToChunk(
  frameN: number,
  firstFrameN: number | null,
): number {
  const first = firstFrameN ?? frameN;
  return Math.max(0, Math.floor((frameN - first) / REPLAY_CHUNK_SIZE));
}

export function bufferedChunkCount(status: ReplayStatus): number {
  return status.chunk_count + (status.pending_frames > 0 ? 1 : 0);
}

export function chunkToRatio(chunk: number, flushedChunks: number): number {
  if (flushedChunks <= 0) return 0;
  return Math.min(1, (chunk + 1) / flushedChunks);
}

export function useReplayStream() {
  const [status, setStatus] = useState<StreamStatus>("idle");
  const [lastMessage, setLastMessage] = useState<string | null>(null);
  const [replayStatus, setReplayStatus] = useState<ReplayStatus>({
    available: false,
    chunk_count: 0,
    pending_frames: 0,
    live_edge_seq: null,
    first_frame_n: null,
    frame_count: 0,
  });
  const socketRef = useRef<PositionalSocket | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const totalChunks = bufferedChunkCount(replayStatus);

  useEffect(() => {
    async function poll() {
      try {
        const res = await fetch(getReplayStatusUrl());
        const data = (await res.json()) as ReplayStatus;
        setReplayStatus(data);
      } catch {}
    }

    poll();
    pollRef.current = setInterval(poll, 2000);

    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
      socketRef.current?.close();
    };
  }, []);

  const connect = useCallback((fromChunk = 0) => {
    socketRef.current?.close();
    setLastMessage(null);
    setStatus("connecting");
    const url = getReplayStreamUrl(fromChunk);
    socketRef.current = new PositionalSocket(url, {
      onOpen: () => setStatus("connected"),
      onMessage: (data) => setLastMessage(data),
      onClose: () => setStatus("closed"),
      onError: () => setStatus("error"),
    });
  }, []);

  const disconnect = useCallback(() => {
    socketRef.current?.close();
    socketRef.current = null;
    setStatus("idle");
  }, []);

  const seek = useCallback(
    (chunk: number) => {
      disconnect();
      connect(chunk);
    },
    [connect, disconnect],
  );

  const refreshStatus = useCallback(async (): Promise<ReplayStatus> => {
    const res = await fetch(getReplayStatusUrl());
    const data = (await res.json()) as ReplayStatus;
    setReplayStatus(data);
    return data;
  }, []);

  return {
    status,
    lastMessage,
    replayStatus,
    totalChunks,
    liveEdgeSeq: replayStatus.live_edge_seq,
    firstFrameN: replayStatus.first_frame_n,
    isAvailable: replayStatus.available,
    connect,
    disconnect,
    seek,
    refreshStatus,
  };
}
