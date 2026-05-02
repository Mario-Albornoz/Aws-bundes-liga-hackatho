export type StatusOfPlay = 0 | 1;
export type Possession = 1 | 2;

export interface PersonFrame {
  person_id: string;
  team_id: string;
  x: number | null;
  y: number | null;
  speed: number | null;
  distance: number | null;
  acceleration: number | null;
}

export interface BallFrame {
  x: number | null;
  y: number | null;
  z: number | null;
  speed: number | null;
  distance: number | null;
  acceleration: number | null;
  status: StatusOfPlay | null;
  possession: Possession | null;
}

export interface PositionalFrame {
  frame_n: string;
  match_id: string;
  timestamp: string;
  game_section: string;
  persons: PersonFrame[];
  ball: BallFrame | null;
}
