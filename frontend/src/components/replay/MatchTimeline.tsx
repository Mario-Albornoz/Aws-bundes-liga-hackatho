import { useCallback, useRef } from "react";
import { StyleSheet, View, Text, PanResponder } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { AnimatedPressable } from "../ui/AnimatedPressable";

interface Props {
  scrubRatio: number;
  disabled: boolean;
  onScrubMove: (ratio: number) => void;
  onScrubEnd: (ratio: number) => void;
  onGoLive: () => void;
  onSkipBack: () => void;
  onSkipForward: () => void;
}

export function MatchTimeline({
  scrubRatio,
  disabled,
  onScrubMove,
  onScrubEnd,
  onGoLive,
  onSkipBack,
  onSkipForward,
}: Props) {
  const insets = useSafeAreaInsets();
  const boundsRef = useRef({ x: 0, width: 1 });
  const trackRef = useRef<View>(null);
  const disabledRef = useRef(disabled);
  const onScrubMoveRef = useRef(onScrubMove);
  const onScrubEndRef = useRef(onScrubEnd);

  disabledRef.current = disabled;
  onScrubMoveRef.current = onScrubMove;
  onScrubEndRef.current = onScrubEnd;

  const measureTrack = useCallback(() => {
    trackRef.current?.measureInWindow((x, _y, width) => {
      boundsRef.current = { x, width: Math.max(width, 1) };
    });
  }, []);

  const ratioFromPageX = useCallback((pageX: number) => {
    const { x, width } = boundsRef.current;
    return Math.max(0, Math.min(1, (pageX - x) / width));
  }, []);

  const emitScrubMove = useCallback(
    (pageX: number) => {
      if (disabledRef.current) return;
      onScrubMoveRef.current(ratioFromPageX(pageX));
    },
    [ratioFromPageX],
  );

  const emitScrubEnd = useCallback(
    (pageX: number) => {
      if (disabledRef.current) return;
      onScrubEndRef.current(ratioFromPageX(pageX));
    },
    [ratioFromPageX],
  );

  const thumbPanResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => !disabledRef.current,
      onMoveShouldSetPanResponder: () => !disabledRef.current,
      onPanResponderGrant: (evt) => {
        measureTrack();
        emitScrubMove(evt.nativeEvent.pageX);
      },
      onPanResponderMove: (evt) => {
        emitScrubMove(evt.nativeEvent.pageX);
      },
      onPanResponderRelease: (evt) => {
        emitScrubEnd(evt.nativeEvent.pageX);
      },
      onPanResponderTerminate: (evt) => {
        emitScrubEnd(evt.nativeEvent.pageX);
      },
    }),
  ).current;

  const progress = Math.max(0, Math.min(1, scrubRatio));

  return (
    <View style={[styles.container, { paddingBottom: insets.bottom + 16 }]}>
      <View style={styles.topRow}>
        <AnimatedPressable style={styles.liveBtn} onPress={onGoLive}>
          <Text style={styles.liveBtnText}>Go Live</Text>
        </AnimatedPressable>
      </View>
      <View style={styles.row}>
        <AnimatedPressable
          style={[styles.skipBtn, disabled && styles.btnDisabled]}
          onPress={onSkipBack}
          disabled={disabled}
        >
          <Ionicons name="play-back" size={22} color="#fff" />
        </AnimatedPressable>
        <View
          ref={trackRef}
          style={[styles.touchArea, disabled && styles.touchAreaDisabled]}
          onLayout={measureTrack}
        >
          <View style={styles.track} pointerEvents="none">
            <View style={[styles.fill, { width: `${progress * 100}%` }]} />
          </View>
          <View
            style={[styles.thumbHit, { left: `${progress * 100}%` }]}
            {...thumbPanResponder.panHandlers}
          >
            <View style={styles.thumb} pointerEvents="none" />
          </View>
        </View>
        <AnimatedPressable
          style={[styles.skipBtn, disabled && styles.btnDisabled]}
          onPress={onSkipForward}
          disabled={disabled}
        >
          <Ionicons name="play-forward" size={22} color="#fff" />
        </AnimatedPressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: "rgba(0,0,0,0.72)",
    paddingHorizontal: 16,
    paddingTop: 12,
    zIndex: 20,
    elevation: 20,
  },
  topRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  skipBtn: {
    padding: 6,
  },
  btnDisabled: {
    opacity: 0.35,
  },
  liveBtn: {
    borderWidth: 1,
    borderColor: "#e63c3c",
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 6,
  },
  liveBtnText: { color: "#e63c3c", fontWeight: "600", fontSize: 13 },
  touchArea: {
    flex: 1,
    height: 44,
    justifyContent: "center",
  },
  touchAreaDisabled: {
    opacity: 0.35,
  },
  track: {
    height: 4,
    backgroundColor: "rgba(255,255,255,0.2)",
    borderRadius: 2,
    justifyContent: "center",
  },
  fill: {
    height: 4,
    backgroundColor: "rgba(255,255,255,0.85)",
    borderRadius: 2,
  },
  thumbHit: {
    position: "absolute",
    top: 0,
    bottom: 0,
    width: 44,
    marginLeft: -22,
    justifyContent: "center",
    alignItems: "center",
  },
  thumb: {
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: "#fff",
  },
});
