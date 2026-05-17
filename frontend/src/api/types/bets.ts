export type BetStatus = 'PENDING' | 'ACTIVE' | 'SUCCESS' | 'FAILED';

/** Matches backend `BetTypes` string values. */
export type BetType = 'substitution';

export interface BetParticipant {
  user_id: number;
  bet_amount: number;
  position: boolean;
}

export interface BetSpecifications {
  player_id: string;
  trigger_event_type?: string;
  team_id?: string | null;
}

export interface BetInfo {
  bet_id: string;
  bet_type: BetType;
  duration: number;
  match_id: number;
  bet_specs: BetSpecifications;
}

export interface BetSubscription {
  participant: BetParticipant;
}

export interface BetCreateRequest {
  bet_info: BetInfo;
  bet_subscription: BetSubscription;
}

export interface Bet {
  bet_info: BetInfo;
  participants: BetParticipant[];
  bet_status: BetStatus;
  triggered: boolean;
  scored: boolean;
}

export interface BetSettledMessage {
  type: 'bet_settled';
  bet_id: string;
  status: BetStatus;
  match_id: number;
  user_id: number;
  new_balance: number;
}
