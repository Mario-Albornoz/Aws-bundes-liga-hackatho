import { getLoginUrl, getLogoutUrl, getMeUrl, getRefreshUrl, getRegisterUrl } from './config';

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user_id: number;
  username: string;
  name: string;
  last_name: string;
  balance: number;
}

export interface AccessTokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserProfile {
  user_id: number;
  username: string;
  name: string;
  last_name: string;
  balance: number;
}

const REQUEST_TIMEOUT_MS = 8000;

function fetchWithTimeout(url: string, options: RequestInit): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  return fetch(url, { ...options, signal: controller.signal }).finally(() =>
    clearTimeout(id),
  );
}

async function post<T>(url: string, body: object, accessToken?: string): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  };
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }
  const res = await fetchWithTimeout(url, { method: 'POST', headers, body: JSON.stringify(body) });
  const text = await res.text();
  if (!res.ok) {
    let detail = text;
    try {
      detail = JSON.parse(text)?.detail ?? text;
    } catch {}
    throw new Error(detail || res.statusText);
  }
  return JSON.parse(text) as T;
}

export function register(
  username: string,
  name: string,
  last_name: string,
  password: string,
): Promise<TokenResponse> {
  return post<TokenResponse>(getRegisterUrl(), { username, name, last_name, password });
}

export function login(username: string, password: string): Promise<TokenResponse> {
  return post<TokenResponse>(getLoginUrl(), { username, password });
}

export function refreshAccessToken(refreshToken: string): Promise<AccessTokenResponse> {
  return post<AccessTokenResponse>(getRefreshUrl(), { refresh_token: refreshToken });
}

export async function logout(accessToken: string, refreshToken: string): Promise<void> {
  await post<void>(getLogoutUrl(), { refresh_token: refreshToken }, accessToken);
}

export async function getMe(accessToken: string): Promise<UserProfile> {
  const res = await fetchWithTimeout(getMeUrl(), {
    method: 'GET',
    headers: { Authorization: `Bearer ${accessToken}`, Accept: 'application/json' },
  });
  const text = await res.text();
  if (!res.ok) throw new Error(text || res.statusText);
  return JSON.parse(text) as UserProfile;
}
