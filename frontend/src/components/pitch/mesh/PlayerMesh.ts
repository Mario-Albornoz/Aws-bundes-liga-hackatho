import { CylinderGeometry, Mesh, MeshLambertMaterial } from "three";
import { COLOR_PLAYER_AWAY, COLOR_PLAYER_HOME, PLAYER_HEIGHT, PLAYER_RADIUS } from "../constants";

export const HOME_COLOR = COLOR_PLAYER_HOME;
export const AWAY_COLOR = COLOR_PLAYER_AWAY;

export function createPlayerMesh(color: number): Mesh {
  const mesh = new Mesh(
    new CylinderGeometry(PLAYER_RADIUS, PLAYER_RADIUS, PLAYER_HEIGHT, 8),
    new MeshLambertMaterial({ color }),
  );
  mesh.position.y = PLAYER_HEIGHT / 2;
  return mesh;
}
