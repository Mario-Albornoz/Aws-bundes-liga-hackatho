import { useRef } from "react";
import { Gesture } from "react-native-gesture-handler";
import { PerspectiveCamera } from "three";
import {
  CAMERA_FOV,
  CAMERA_MAX_PHI,
  CAMERA_MIN_PHI,
  CAMERA_MIN_RADIUS,
  CAMERA_PAN_SENSITIVITY,
  PITCH_WIDTH,
} from "../constants";

const FOV_RAD = (CAMERA_FOV * Math.PI) / 180;

/**
 * Manages a spherical-coordinate orbit camera with pan and pinch gestures.
 * @returns `cameraRef` — the live camera; pass to the render loop via `renderer.render(scene, cameraRef.current!)`;
 *          `onViewportReady` — call once with GL viewport dimensions to create and position the camera;
 *          `cameraGesture` — gesture handler to wrap around GLView for camera controls;
 *          `resetCamera` — restores the camera to its initial position and angle.
 */
export function useCameraControls() {
  const cameraRef = useRef<PerspectiveCamera | null>(null);
  const radiusRef = useRef(100);
  const initialRadiusRef = useRef(100);
  const thetaRef = useRef(0);
  const phiRef = useRef(CAMERA_MIN_PHI);
  const maxRadiusRef = useRef(100);
  const pinchStartRadius = useRef(100);
  const prevTranslation = useRef({ x: 0, y: 0 });

  const applyToCamera = () => {
    const camera = cameraRef.current;
    if (!camera) return;
    camera.position.setFromSphericalCoords(
      radiusRef.current,
      phiRef.current,
      thetaRef.current,
    );
    camera.lookAt(0, 0, 0);
  };

  const onViewportReady = (width: number, height: number) => {
    const aspect = width / height;
    const camera = new PerspectiveCamera(CAMERA_FOV, aspect, 0.1, 500);

    const radius =
      (PITCH_WIDTH / 2 / Math.tan(FOV_RAD / 2) / Math.sin(CAMERA_MAX_PHI)) * 3;
    const maxRadius =
      (PITCH_WIDTH / 2 / Math.tan(FOV_RAD / 2) / Math.sin(CAMERA_MAX_PHI)) * 4;
    radiusRef.current = radius;
    initialRadiusRef.current = radius;
    maxRadiusRef.current = maxRadius;

    phiRef.current = CAMERA_MAX_PHI;
    thetaRef.current = -Math.PI / 4;

    camera.position.setFromSphericalCoords(
      radius,
      CAMERA_MAX_PHI,
      -Math.PI / 4,
    );
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;
  };

  const pan = Gesture.Pan()
    .runOnJS(true)
    .onStart(() => {
      prevTranslation.current = { x: 0, y: 0 };
    })
    .onUpdate((e) => {
      const dx = e.translationX - prevTranslation.current.x;
      const dy = e.translationY - prevTranslation.current.y;
      prevTranslation.current = { x: e.translationX, y: e.translationY };
      thetaRef.current -= dx * CAMERA_PAN_SENSITIVITY;
      phiRef.current = Math.max(
        CAMERA_MIN_PHI,
        Math.min(CAMERA_MAX_PHI, phiRef.current + dy * CAMERA_PAN_SENSITIVITY),
      );
      applyToCamera();
    });

  const pinch = Gesture.Pinch()
    .runOnJS(true)
    .onStart(() => {
      pinchStartRadius.current = radiusRef.current;
    })
    .onUpdate((e) => {
      radiusRef.current = Math.max(
        CAMERA_MIN_RADIUS,
        Math.min(maxRadiusRef.current, pinchStartRadius.current / e.scale),
      );
      applyToCamera();
    });

  const cameraGesture = Gesture.Simultaneous(pan, pinch);

  const resetCamera = () => {
    radiusRef.current = initialRadiusRef.current;
    phiRef.current = CAMERA_MAX_PHI;
    thetaRef.current = -Math.PI / 4;
    applyToCamera();
  };

  return { cameraRef, onViewportReady, cameraGesture, resetCamera };
}
