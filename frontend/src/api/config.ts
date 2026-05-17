/**
 * REST base URL for the FastAPI backend (no trailing slash).
 * Override with EXPO_PUBLIC_API_BASE_URL, e.g. http://192.168.1.10:8000 for a device on LAN.
 */
export function getApiBaseUrl(): string {
  const raw = process.env.EXPO_PUBLIC_API_BASE_URL ?? 'http://127.0.0.1:8000';
  return raw.replace(/\/$/, '');
}

/** WebSocket base derived from the HTTP(S) API base (ws / wss). */
export function getWebSocketBaseUrl(): string {
  const base = getApiBaseUrl();
  if (/^https:\/\//i.test(base)) {
    return 'wss://' + base.slice('https://'.length);
  }
  return 'ws://' + base.replace(/^http:\/\//i, '');
}

export function getBetSettlementWebSocketUrl(userId: number): string {
  return `${getWebSocketBaseUrl()}/bets/stream?user_id=${encodeURIComponent(String(userId))}`;
}

export function getCreateBetUrl(): string {
  return `${getApiBaseUrl()}/bets/create`;
}
