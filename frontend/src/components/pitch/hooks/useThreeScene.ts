import { useCallback, useRef } from "react";
import { ExpoWebGLRenderingContext } from "expo-gl";
import { Renderer } from "expo-three";
import { AmbientLight, DirectionalLight, Scene } from "three";
import { useCameraControls } from "./useCameraControls";
import {
  COLOR_AMBIENT_LIGHT,
  COLOR_BACKGROUND,
  COLOR_DIR_LIGHT,
} from "../constants";

/**
 * Sets up the Three.js renderer, scene, and animation loop inside an Expo GL context.
 * @param onReady - called once after the scene is built; use it to populate the scene.
 * @param onTick  - called every frame before rendering; use it to update positions.
 * @returns `onContextCreate` — pass to GLView's prop to boot the renderer;
 *          `dispose` — call on unmount to cancel the animation loop;
 *          `cameraGesture` — gesture handler to wrap around GLView for camera controls;
 *          `resetCamera` — restores the camera to its initial position and angle.
 */
export function useThreeScene(
  onReady?: (scene: Scene) => void,
  onTick?: () => void,
) {
  const onReadyRef = useRef(onReady);
  onReadyRef.current = onReady;

  const onTickRef = useRef(onTick);
  onTickRef.current = onTick;

  const animFrameRef = useRef<number>(0);

  const { cameraRef, onViewportReady, cameraGesture, resetCamera } = useCameraControls();

  const onContextCreate = useCallback((gl: ExpoWebGLRenderingContext) => {
    const { drawingBufferWidth: width, drawingBufferHeight: height } = gl;

    const renderer = new Renderer({ gl });
    renderer.setSize(width, height);
    renderer.setClearColor(COLOR_BACKGROUND);

    const scene = new Scene();

    onViewportReady(width, height);

    scene.add(new AmbientLight(COLOR_AMBIENT_LIGHT, 0.6));
    const dirLight = new DirectionalLight(COLOR_DIR_LIGHT, 0.8);
    dirLight.position.set(10, 50, 10);
    scene.add(dirLight);

    onReadyRef.current?.(scene);

    const animate = () => {
      animFrameRef.current = requestAnimationFrame(animate);
      onTickRef.current?.();
      renderer.render(scene, cameraRef.current!);
      gl.endFrameEXP();
    };
    animate();
  }, []);

  const dispose = useCallback(() => {
    cancelAnimationFrame(animFrameRef.current);
  }, []);

  return { onContextCreate, dispose, cameraGesture, resetCamera };
}
