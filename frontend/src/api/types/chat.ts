export interface ChatRoom {
  room_id: string;
  name: string;
  connection_string: string;
  created_by: string;
}

export interface ChatMessage {
  room_id: string;
  sender_id: string;
  content: string;
  timestamp: string;
}

export interface JoinRoomResponse {
  room_id: string;
  user_id: string;
  ws_token: string;
}

export interface UserJoinedEvent {
  type: "user_joined";
  room_id: string;
  user_id: string;
  timestamp: string;
}

export interface UserLeftEvent {
  type: "user_left";
  room_id: string;
  user_id: string;
  timestamp: string;
}

export type IncomingWsMessage = UserJoinedEvent | UserLeftEvent | ChatMessage;
