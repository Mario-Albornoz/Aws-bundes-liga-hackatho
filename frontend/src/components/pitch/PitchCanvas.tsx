import { RefObject, useCallback, useEffect, useRef } from "react";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { StyleSheet, Text, View } from "react-native";
import { AnimatedPressable } from "../ui/AnimatedPressable";
import { GLView } from "expo-gl";
import { GestureDetector } from "react-native-gesture-handler";
import { Mesh, Scene } from "three";
import { PositionalFrame } from "../../types/positional";
import { useThreeScene } from "./hooks/useThreeScene";
import { usePositionSync } from "./hooks/usePositionSync";
import { createPitchGeometry } from "./mesh/PitchMesh";
import { createBallMesh } from "./mesh/BallMesh";

interface Props {
  frameRef: RefObject<PositionalFrame | null>;
}

export function PitchCanvas({ frameRef }: Props) {
  const insets = useSafeAreaInsets();
  const sceneRef = useRef<Scene | null>(null);
  const ballMeshRef = useRef<Mesh | null>(null);
  const playerMeshMap = useRef<Map<string, Mesh>>(new Map());

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
    frameRef,
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
      <AnimatedPressable style={[styles.resetButton, { bottom: insets.bottom + 120 }]} onPress={resetCamera}>
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
