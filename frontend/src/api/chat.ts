import { getCreateRoomUrl, getJoinRoomUrl } from '@/src/api/config';
import type { ChatRoom, JoinRoomResponse } from '@/src/api/types/chat';

async function request<T>(url: string, body: object): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  if (!res.ok) throw new Error(text || res.statusText);
  return JSON.parse(text) as T;
}

export function createRoom(name: string, userId: string): Promise<ChatRoom> {
  return request<ChatRoom>(
    `${getCreateRoomUrl()}?name=${encodeURIComponent(name)}&user_id=${encodeURIComponent(userId)}`,
    {},
  );
}

export function joinRoom(
  userId: string,
  connectionString: string,
): Promise<JoinRoomResponse> {
  return request<JoinRoomResponse>(getJoinRoomUrl(), {
    user_id: userId,
    connection_string: connectionString,
  });
}
