/**
 * REST base URL for the FastAPI backend (no trailing slash).
 * Override with EXPO_PUBLIC_API_BASE_URL, e.g. http://192.168.1.10:8000 for a device on LAN.
 */
export function getApiBaseUrl(): string {
  const raw = process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
  return raw.replace(/\/$/, "");
}

/** WebSocket base derived from the HTTP(S) API base (ws / wss). */
export function getWebSocketBaseUrl(): string {
  return (
    process.env.EXPO_PUBLIC_WS_URL ?? getApiBaseUrl().replace(/^http/, "ws")
  );
}

export function getBetSettlementWebSocketUrl(userId: number): string {
  return `${getWebSocketBaseUrl()}/bets/stream?user_id=${encodeURIComponent(String(userId))}`;
}

export function getCreateBetUrl(): string {
  return `${getApiBaseUrl()}/bets/create`;
}

export function getCreateRoomUrl(): string {
  return `${getApiBaseUrl()}/chat-room/create`;
}

export function getJoinRoomUrl(): string {
  return `${getApiBaseUrl()}/chat-room/join`;
}

export function getChatStreamUrl(roomId: string, wsToken: string): string {
  return `${getWebSocketBaseUrl()}/chat-room/stream?room_id=${encodeURIComponent(roomId)}&ws_token=${encodeURIComponent(wsToken)}`;
}

export function getPositionalStreamUrl(speed: number, seq: number): string {
  return `${getWebSocketBaseUrl()}/positional/stream?speed=${speed}&seq=${seq}`;
}

export function getEventsStreamUrl(speed: number, seq: number): string {
  return `${getWebSocketBaseUrl()}/events/stream?speed=${speed}&seq=${seq}`;
}
