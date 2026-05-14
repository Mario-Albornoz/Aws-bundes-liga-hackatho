import { useEffect, useRef, useState } from "react";
import { EventsSocket } from "./EventsSocket";

export type StreamStatus =
  | "idle"
  | "connecting"
  | "connected"
  | "error"
  | "closed";

export function useEventsStream() {
  const [status, setStatus] = useState<StreamStatus>("idle");
  const [lastMessage, setLastMessage] = useState<string | null>(null);
  const socketRef = useRef<EventsSocket | null>(null);

  useEffect(() => {
    return () => {
      socketRef.current?.close();
    };
  }, []);

  function connect(speed = 1, seq = 0) {
    socketRef.current?.close();
    setStatus("connecting");
    setLastMessage(null);
    socketRef.current = new EventsSocket(speed, seq, {
      onOpen: () => setStatus("connected"),
      onMessage: (data) => setLastMessage(data),
      onClose: () => setStatus("closed"),
      onError: () => setStatus("error"),
    });
  }

  function disconnect() {
    socketRef.current?.close();
    socketRef.current = null;
  }

  return { status, lastMessage, connect, disconnect };
}
