export type BetSettlementSocketCallbacks = {
  onOpen?: () => void;
  onMessage?: (data: string) => void;
  onClose?: () => void;
  onError?: (event: Event) => void;
};

/**
 * WebSocket client for `/bets/stream?user_id=…` (settlement notifications).
 */
export class BetSettlementSocket {
  private ws: WebSocket;

  constructor(url: string, callbacks: BetSettlementSocketCallbacks = {}) {
    this.ws = new WebSocket(url);
    this.ws.onopen = () => callbacks.onOpen?.();
    this.ws.onmessage = (e) => callbacks.onMessage?.(String(e.data));
    this.ws.onclose = () => callbacks.onClose?.();
    this.ws.onerror = (e) => {
      console.error('[BetSettlementSocket] error', e);
      callbacks.onError?.(e);
    };
  }

  sendPing(text = 'ping') {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(text);
    }
  }

  close() {
    this.ws.close();
  }
}
