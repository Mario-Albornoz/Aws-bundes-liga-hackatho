import { Mesh, MeshLambertMaterial, SphereGeometry } from "three";
import { BALL_RADIUS, COLOR_BALL } from "../constants";

export function createBallMesh(): Mesh {
  return new Mesh(
    new SphereGeometry(BALL_RADIUS, 16, 16),
    new MeshLambertMaterial({ color: COLOR_BALL }),
  );
}
