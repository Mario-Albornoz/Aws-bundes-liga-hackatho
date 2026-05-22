import { useCallback, useEffect, useRef, useState } from 'react';
import { ChatSocket } from './ChatSocket';
import { getChatStreamUrl } from './config';
import type { IncomingWsMessage } from './types/chat';
import type { StreamStatus } from './useEventsStream';

export function useChatStream() {
  const [status, setStatus] = useState<StreamStatus>('idle');
  const [messages, setMessages] = useState<IncomingWsMessage[]>([]);
  const socketRef = useRef<ChatSocket | null>(null);
  const userIdRef = useRef<string | null>(null);

  useEffect(() => {
    return () => {
      socketRef.current?.close();
    };
  }, []);

  function connect(roomId: string, wsToken: string, userId: string) {
    socketRef.current?.close();
    userIdRef.current = userId;
    setStatus('connecting');
    setMessages([]);
    const url = getChatStreamUrl(roomId, wsToken);
    socketRef.current = new ChatSocket(url, {
      onOpen: () => setStatus('connected'),
      onMessage: (raw) => {
        try {
          const msg = JSON.parse(raw) as IncomingWsMessage;
          setMessages((prev) => [...prev, msg]);
        } catch {
          // ignore non-JSON frames
        }
      },
      onClose: () => setStatus('closed'),
      onError: () => setStatus('error'),
    });
  }

  function disconnect() {
    socketRef.current?.close();
    socketRef.current = null;
    userIdRef.current = null;
    setMessages([]);
    setStatus('idle');
  }

  const sendMessage = useCallback((content: string) => {
    socketRef.current?.send(JSON.stringify({
      content,
      sender_id: userIdRef.current,
      timestamp: new Date().toISOString(),
    }));
  }, []);

  return { status, messages, connect, disconnect, sendMessage };
}
