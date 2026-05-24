import { useCallback, useEffect, useRef } from "react";
import { StyleSheet, Text, View } from "react-native";
import { AnimatedPressable } from "../ui/AnimatedPressable";
import { GLView } from "expo-gl";
import { GestureDetector } from "react-native-gesture-handler";
import { Mesh, Scene } from "three";
import { WSServerMessage } from "../../types/common";
import { PositionalFrame } from "../../types/positional";
import { useThreeScene } from "./hooks/useThreeScene";
import { usePositionSync } from "./hooks/usePositionSync";
import { createPitchGeometry } from "./mesh/PitchMesh";
import { createBallMesh } from "./mesh/BallMesh";

interface Props {
  lastMessage: string | null;
}

export function PitchCanvas({ lastMessage }: Props) {
  const sceneRef = useRef<Scene | null>(null);
  const ballMeshRef = useRef<Mesh | null>(null);
  const playerMeshMap = useRef<Map<string, Mesh>>(new Map());
  const latestFrameRef = useRef<PositionalFrame | null>(null);

  useEffect(() => {
    if (!lastMessage) return;
    try {
      const msg = JSON.parse(lastMessage) as WSServerMessage<PositionalFrame>;
      if (msg.type === "positional") {
        latestFrameRef.current = msg.payload;
      }
    } catch {}
  }, [lastMessage]);

  const onSceneReady = useCallback((scene: Scene) => {
    sceneRef.current = scene;
    scene.add(createPitchGeometry());

    const ball = createBallMesh();
    ball.position.set(0, 0.11, 0);
    scene.add(ball);
    ballMeshRef.current = ball;
  }, []);

  const onTick = usePositionSync(
    sceneRef,
    ballMeshRef,
    playerMeshMap,
    latestFrameRef,
  );
  const { onContextCreate, dispose, cameraGesture, resetCamera } =
    useThreeScene(onSceneReady, onTick);

  useEffect(() => {
    return dispose;
  }, []);

  return (
    <View style={styles.container}>
      <GestureDetector gesture={cameraGesture}>
        <GLView style={styles.gl} onContextCreate={onContextCreate} />
      </GestureDetector>
      <AnimatedPressable style={styles.resetButton} onPress={resetCamera}>
        <Text style={styles.resetButtonText}>Reset</Text>
      </AnimatedPressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  gl: { flex: 1 },
  resetButton: {
    position: "absolute",
    bottom: 120,
    right: 16,
    backgroundColor: "rgba(0,0,0,0.55)",
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  resetButtonText: {
    color: "#fff",
    fontSize: 14,
  },
});
