import { useEffect, useRef, useState } from 'react';
import { PositionalSocket } from './PositionalSocket';
import { StreamStatus } from './useEventsStream';

export function usePositionalStream() {
  const [status, setStatus] = useState<StreamStatus>('idle');
  const [lastMessage, setLastMessage] = useState<string | null>(null);
  const socketRef = useRef<PositionalSocket | null>(null);

  useEffect(() => {
    return () => { socketRef.current?.close(); };
  }, []);

  function connect(matchId: string, speed = 1, seq = 0) {
    socketRef.current?.close();
    setStatus('connecting');
    setLastMessage(null);
    socketRef.current = new PositionalSocket(matchId, speed, seq, {
      onOpen: () => setStatus('connected'),
      onMessage: (data) => setLastMessage(data),
      onClose: () => setStatus('closed'),
      onError: () => setStatus('error'),
    });
  }

  function disconnect() {
    socketRef.current?.close();
    socketRef.current = null;
  }

  return { status, lastMessage, connect, disconnect };
}
