import {
  BoxGeometry,
  BufferGeometry,
  Float32BufferAttribute,
  Group,
  LineBasicMaterial,
  LineSegments,
  Mesh,
  MeshLambertMaterial,
} from "three";
import {
  CENTER_CIRCLE_RADIUS,
  COLOR_PITCH_MARKINGS,
  COLOR_PITCH_SURFACE,
  CORNER_ARC_RADIUS,
  GOAL_AREA_HALF_WIDTH,
  GOAL_AREA_INNER_X,
  GOAL_DEPTH,
  GOAL_HALF_WIDTH,
  GOAL_HEIGHT,
  PENALTY_ARC_RADIUS,
  PENALTY_ARC_TANGENT,
  PENALTY_AREA_HALF_WIDTH,
  PENALTY_AREA_INNER_X,
  PENALTY_SPOT_X,
  PITCH_HALF_LENGTH,
  PITCH_HALF_WIDTH,
  PITCH_LENGTH,
  PITCH_WIDTH,
} from "../constants";

const LINE_Y = 0.02;

function seg(v: number[], x1: number, z1: number, x2: number, z2: number) {
  v.push(x1, LINE_Y, z1, x2, LINE_Y, z2);
}

function arc(
  v: number[],
  cx: number,
  cz: number,
  r: number,
  start: number,
  end: number,
  steps: number,
) {
  const step = (end - start) / steps;
  for (let i = 0; i < steps; i++) {
    const a0 = start + i * step;
    const a1 = start + (i + 1) * step;
    v.push(
      cx + r * Math.cos(a0),
      LINE_Y,
      cz + r * Math.sin(a0),
      cx + r * Math.cos(a1),
      LINE_Y,
      cz + r * Math.sin(a1),
    );
  }
}

function addBoundary(v: number[]) {
  seg(
    v,
    -PITCH_HALF_LENGTH,
    -PITCH_HALF_WIDTH,
    PITCH_HALF_LENGTH,
    -PITCH_HALF_WIDTH,
  );
  seg(
    v,
    -PITCH_HALF_LENGTH,
    PITCH_HALF_WIDTH,
    PITCH_HALF_LENGTH,
    PITCH_HALF_WIDTH,
  );
  seg(
    v,
    -PITCH_HALF_LENGTH,
    -PITCH_HALF_WIDTH,
    -PITCH_HALF_LENGTH,
    PITCH_HALF_WIDTH,
  );
  seg(
    v,
    PITCH_HALF_LENGTH,
    -PITCH_HALF_WIDTH,
    PITCH_HALF_LENGTH,
    PITCH_HALF_WIDTH,
  );
}

function addHalfwayLine(v: number[]) {
  seg(v, 0, -PITCH_HALF_WIDTH, 0, PITCH_HALF_WIDTH);
}

function addCenterCircle(v: number[]) {
  arc(v, 0, 0, CENTER_CIRCLE_RADIUS, 0, Math.PI * 2, 64);
  arc(v, 0, 0, 0.3, 0, Math.PI * 2, 8);
}

function addPenaltyArea(v: number[], s: number) {
  const gx = s * PITCH_HALF_LENGTH;
  const ix = s * PENALTY_AREA_INNER_X;
  seg(v, gx, -PENALTY_AREA_HALF_WIDTH, ix, -PENALTY_AREA_HALF_WIDTH);
  seg(v, gx, PENALTY_AREA_HALF_WIDTH, ix, PENALTY_AREA_HALF_WIDTH);
  seg(v, ix, -PENALTY_AREA_HALF_WIDTH, ix, PENALTY_AREA_HALF_WIDTH);
}

function addGoalArea(v: number[], s: number) {
  const gx = s * PITCH_HALF_LENGTH;
  const ix = s * GOAL_AREA_INNER_X;
  seg(v, gx, -GOAL_AREA_HALF_WIDTH, ix, -GOAL_AREA_HALF_WIDTH);
  seg(v, gx, GOAL_AREA_HALF_WIDTH, ix, GOAL_AREA_HALF_WIDTH);
  seg(v, ix, -GOAL_AREA_HALF_WIDTH, ix, GOAL_AREA_HALF_WIDTH);
}

function addPenaltySpotAndArc(v: number[], s: number, penArcHalf: number) {
  const spotX = s * PENALTY_SPOT_X;
  arc(v, spotX, 0, 0.3, 0, Math.PI * 2, 8);
  const base = s < 0 ? 0 : Math.PI;
  arc(
    v,
    spotX,
    0,
    PENALTY_ARC_RADIUS,
    base - penArcHalf,
    base + penArcHalf,
    32,
  );
}

function addGoalFrame(v: number[], s: number) {
  const gx = s * PITCH_HALF_LENGTH;
  const back = gx - s * GOAL_DEPTH;
  const hw = GOAL_HALF_WIDTH;
  const h = GOAL_HEIGHT;

  // prettier-ignore
  v.push(
    gx,   0, -hw,   gx,   h, -hw,  // front left post
    gx,   0,  hw,   gx,   h,  hw,  // front right post
    gx,   h, -hw,   gx,   h,  hw,  // crossbar
    back, 0, -hw,   back, h, -hw,  // back left post
    back, 0,  hw,   back, h,  hw,  // back right post
    back, h, -hw,   back, h,  hw,  // back crossbar
    gx,   h, -hw,   back, h, -hw,  // top left side
    gx,   h,  hw,   back, h,  hw,  // top right side
  );
}

function addCornerArcs(v: number[]) {
  arc(
    v,
    -PITCH_HALF_LENGTH,
    -PITCH_HALF_WIDTH,
    CORNER_ARC_RADIUS,
    0,
    Math.PI / 2,
    8,
  );
  arc(
    v,
    PITCH_HALF_LENGTH,
    -PITCH_HALF_WIDTH,
    CORNER_ARC_RADIUS,
    Math.PI / 2,
    Math.PI,
    8,
  );
  arc(
    v,
    PITCH_HALF_LENGTH,
    PITCH_HALF_WIDTH,
    CORNER_ARC_RADIUS,
    Math.PI,
    Math.PI * 1.5,
    8,
  );
  arc(
    v,
    -PITCH_HALF_LENGTH,
    PITCH_HALF_WIDTH,
    CORNER_ARC_RADIUS,
    -Math.PI / 2,
    0,
    8,
  );
}

function buildMarkings(): LineSegments {
  const v: number[] = [];

  addBoundary(v);
  addHalfwayLine(v);
  addCenterCircle(v);

  const penArcHalf = Math.acos(PENALTY_ARC_TANGENT / PENALTY_ARC_RADIUS);
  for (const s of [-1, 1]) {
    addPenaltyArea(v, s);
    addGoalArea(v, s);
    addPenaltySpotAndArc(v, s, penArcHalf);
    addGoalFrame(v, s);
  }

  addCornerArcs(v);

  const geo = new BufferGeometry();
  geo.setAttribute(
    "position",
    new Float32BufferAttribute(new Float32Array(v), 3),
  );
  return new LineSegments(
    geo,
    new LineBasicMaterial({ color: COLOR_PITCH_MARKINGS }),
  );
}

/** Returns a Group containing the grass surface and all line markings. */
export function createPitchGeometry(): Group {
  const group = new Group();

  const surface = new Mesh(
    new BoxGeometry(PITCH_LENGTH, PITCH_WIDTH, 2),
    new MeshLambertMaterial({ color: COLOR_PITCH_SURFACE }),
  );
  surface.rotation.x = -Math.PI / 2;
  // Box is 2m thick; shift down 1m so its top face sits at y=0.
  surface.position.y = -1;
  group.add(surface);

  group.add(buildMarkings());

  return group;
}
