type SocketCallbacks = {
  onOpen?: () => void;
  onMessage?: (data: string) => void;
  onClose?: () => void;
  onError?: (event: Event) => void;
};

export class EventsSocket {
  private ws: WebSocket;

  constructor(url: string, callbacks: SocketCallbacks = {}) {
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
