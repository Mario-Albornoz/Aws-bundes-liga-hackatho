const BASE_URL = process.env.EXPO_PUBLIC_EVENTS_WS_URL!;

type SocketCallbacks = {
  onOpen?: () => void;
  onMessage?: (data: string) => void;
  onClose?: () => void;
  onError?: (event: Event) => void;
};

export class EventsSocket {
  private ws: WebSocket;

  constructor(speed = 1, seq = 0, callbacks: SocketCallbacks = {}) {
    const url = `${BASE_URL}?speed=${speed}&seq=${seq}`;
    this.ws = new WebSocket(url);
    this.ws.onopen = () => callbacks.onOpen?.();
    this.ws.onmessage = (e) => callbacks.onMessage?.(e.data);
    this.ws.onclose = () => callbacks.onClose?.();
    this.ws.onerror = (e) => {
      console.error("[EventsSocket] error", e);
      callbacks.onError?.(e);
    };
  }

  close() {
    this.ws.close();
  }
}
