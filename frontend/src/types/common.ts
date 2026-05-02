export type ServerMessageType =
  | 'event'
  | 'positional'
  | 'match_start'
  | 'match_end'
  | 'heartbeat'
  | 'error';


export type ClientMessageType = 'pause' | 'resume';

export interface WSServerMessage<T = unknown> {
  type: ServerMessageType;
  seq: number;
  match_id: string;
  payload: T;
}

export interface WSClientMessage {
  type: ClientMessageType;
}