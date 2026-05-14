import { RefObject, useCallback, useRef } from "react";
import { Mesh, Scene } from "three";
import { PositionalFrame } from "../../../types/positional";
import { createPlayerMesh, HOME_COLOR, AWAY_COLOR } from "../mesh/PlayerMesh";
import { BALL_RADIUS } from "../constants";

const LERP = 0.3;

/**
 * Returns an `onTick` callback that reads the latest positional frame and
 * moves player and ball meshes accordingly. Designed to run inside the
 * Three.js animation loop without triggering React re-renders.
 */
export function usePositionSync(
  sceneRef: RefObject<Scene | null>,
  ballMeshRef: RefObject<Mesh | null>,
  playerMeshMap: RefObject<Map<string, Mesh>>,
  latestFrameRef: RefObject<PositionalFrame | null>,
): () => void {
  const teamColors = useRef<Map<string, number>>(new Map());

  return useCallback(() => {
    const frame = latestFrameRef.current;
    const scene = sceneRef.current;
    if (!frame || !scene) return;

    for (const person of frame.persons) {
      let mesh = playerMeshMap.current.get(person.person_id);

      if (!mesh) {
        const colors = teamColors.current;
        if (!colors.has(person.team_id)) {
          colors.set(
            person.team_id,
            colors.size === 0 ? HOME_COLOR : AWAY_COLOR,
          );
        }
        mesh = createPlayerMesh(colors.get(person.team_id)!);
        scene.add(mesh);
        playerMeshMap.current.set(person.person_id, mesh);
      }

      if (person.x == null || person.y == null) {
        mesh.visible = false;
        continue;
      }

      mesh.visible = true;
      mesh.position.x += (person.x - mesh.position.x) * LERP;
      mesh.position.z += (person.y - mesh.position.z) * LERP;
    }

    const ball = ballMeshRef.current;
    const b = frame.ball;
    if (ball && b?.x != null && b?.y != null) {
      // DFL axes: X→Three.js X, Y (pitch depth)→Three.js Z, Z (height)→Three.js Y.
      ball.position.set(b.x, (b.z ?? 0) + BALL_RADIUS, b.y);
    }
  }, []);
}
