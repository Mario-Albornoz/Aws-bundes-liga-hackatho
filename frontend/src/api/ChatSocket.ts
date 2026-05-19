type ChatSocketCallbacks = {
  onOpen?: () => void;
  onMessage?: (data: string) => void;
  onClose?: () => void;
  onError?: (event: Event) => void;
};

export class ChatSocket {
  private ws: WebSocket;

  constructor(url: string, callbacks: ChatSocketCallbacks = {}) {
    this.ws = new WebSocket(url);
    this.ws.onopen = () => callbacks.onOpen?.();
    this.ws.onmessage = (e) => callbacks.onMessage?.(String(e.data));
    this.ws.onclose = () => callbacks.onClose?.();
    this.ws.onerror = (e) => {
      console.error('[ChatSocket] error', e);
      callbacks.onError?.(e);
    };
  }

  send(data: string) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(data);
    }
  }

  close() {
    this.ws.close();
  }
}
