export type BetStatus = 'PENDING' | 'ACTIVE' | 'SUCCESS' | 'FAILED';

export interface BetOpportunityContext {
  player_on: string;
  team: string;
}

export interface BetOpportunity {
  bet_type: string;
  trigger_event_id: string;
  window_seconds: number;
  match_id: string;
  context: BetOpportunityContext;
  expires_at: string;
  bet_id: string;
}

export interface BetOpportunityMessage {
  type: 'bet_opportunity';
  opportunity: BetOpportunity;
}

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
  match_id: string;
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
  match_id: string;
  user_id: number;
  new_balance: number;
}

export interface BetSnapshotMessage {
  type: 'bet_snapshot';
  bets: Bet[];
}

export interface BetUpdatedMessage {
  type: 'bet_updated';
  bet_id: string;
  status: BetStatus;
}
