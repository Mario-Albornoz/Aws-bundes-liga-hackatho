import { RefObject, useEffect, useRef, useState } from "react";
import { PositionalSocket } from "./PositionalSocket";
import { StreamStatus } from "./useEventsStream";
import { getPositionalStreamUrl } from "./config";
import { WSServerMessage } from "../types/common";
import { PositionalFrame } from "../types/positional";

export function usePositionalStream() {
  const [status, setStatus] = useState<StreamStatus>("idle");
  const [lastSeq, setLastSeq] = useState<number | null>(null);
  const socketRef = useRef<PositionalSocket | null>(null);
  const targetFrameRef = useRef<RefObject<PositionalFrame | null> | null>(null);

  useEffect(() => {
    return () => {
      socketRef.current?.close();
    };
  }, []);

  function connect(speed = 1, seq = 0, frameRef?: RefObject<PositionalFrame | null>) {
    if (frameRef !== undefined) {
      targetFrameRef.current = frameRef;
    }
    socketRef.current?.close();
    setStatus("connecting");
    setLastSeq(null);
    const url = getPositionalStreamUrl(speed, seq);
    socketRef.current = new PositionalSocket(url, {
      onOpen: () => setStatus("connected"),
      onMessage: (data) => {
        try {
          const msg = JSON.parse(data) as WSServerMessage<PositionalFrame>;
          if (msg.type === "positional") {
            const ref = targetFrameRef.current;
            if (ref) ref.current = msg.payload;
            setLastSeq(msg.seq);
          }
        } catch {}
      },
      onClose: () => setStatus("closed"),
      onError: () => setStatus("error"),
    });
  }

  function disconnect() {
    socketRef.current?.close();
    socketRef.current = null;
  }

  return { status, lastSeq, connect, disconnect };
}
