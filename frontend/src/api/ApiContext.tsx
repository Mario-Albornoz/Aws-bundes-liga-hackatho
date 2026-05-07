import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';

import { BetSettlementSocket } from '@/src/api/BetSettlementSocket';
import { getApiBaseUrl, getBetSettlementWebSocketUrl, getCreateBetUrl } from '@/src/api/config';
import type { Bet, BetCreateRequest, BetSettledMessage } from '@/src/api/types/bets';

export type SettlementSocketStatus = 'idle' | 'connecting' | 'connected' | 'error' | 'closed';

export type ApiContextValue = {
  apiBaseUrl: string;
  userId: number;
  setUserId: (id: number) => void;
  createBet: (body: BetCreateRequest) => Promise<Bet>;
  createBetError: string | null;
  clearCreateBetError: () => void;
  settlementSocketStatus: SettlementSocketStatus;
  lastSettlementMessage: BetSettledMessage | null;
  clearLastSettlementMessage: () => void;
  connectBetSettlementSocket: () => void;
  disconnectBetSettlementSocket: () => void;
};

const ApiContext = createContext<ApiContextValue | null>(null);

export function ApiProvider({ children }: { children: React.ReactNode }) {
  const [userId, setUserId] = useState(1);
  const [settlementSocketStatus, setSettlementSocketStatus] =
    useState<SettlementSocketStatus>('idle');
  const [lastSettlementMessage, setLastSettlementMessage] = useState<BetSettledMessage | null>(
    null
  );
  const [createBetError, setCreateBetError] = useState<string | null>(null);
  const socketRef = useRef<BetSettlementSocket | null>(null);

  const apiBaseUrl = useMemo(() => getApiBaseUrl(), []);

  const clearCreateBetError = useCallback(() => setCreateBetError(null), []);
  const clearLastSettlementMessage = useCallback(() => setLastSettlementMessage(null), []);

  const disconnectBetSettlementSocket = useCallback(() => {
    socketRef.current?.close();
    socketRef.current = null;
    setSettlementSocketStatus('idle');
  }, []);

  const connectBetSettlementSocket = useCallback(() => {
    socketRef.current?.close();
    socketRef.current = null;
    setSettlementSocketStatus('connecting');
    const url = getBetSettlementWebSocketUrl(userId);
    socketRef.current = new BetSettlementSocket(url, {
      onOpen: () => setSettlementSocketStatus('connected'),
      onMessage: (raw) => {
        try {
          const data = JSON.parse(raw) as BetSettledMessage;
          if (data && data.type === 'bet_settled') {
            setLastSettlementMessage(data);
          }
        } catch {
          /* ignore non-JSON */
        }
      },
      onClose: () => setSettlementSocketStatus('closed'),
      onError: () => setSettlementSocketStatus('error'),
    });
  }, [userId]);

  useEffect(() => {
    return () => {
      socketRef.current?.close();
      socketRef.current = null;
    };
  }, []);

  const createBet = useCallback(async (body: BetCreateRequest): Promise<Bet> => {
    setCreateBetError(null);
    const res = await fetch(getCreateBetUrl(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(body),
    });
    const text = await res.text();
    if (!res.ok) {
      setCreateBetError(text || res.statusText);
      throw new Error(text || res.statusText);
    }
    return JSON.parse(text) as Bet;
  }, []);

  const value = useMemo<ApiContextValue>(
    () => ({
      apiBaseUrl,
      userId,
      setUserId,
      createBet,
      createBetError,
      clearCreateBetError,
      settlementSocketStatus,
      lastSettlementMessage,
      clearLastSettlementMessage,
      connectBetSettlementSocket,
      disconnectBetSettlementSocket,
    }),
    [
      apiBaseUrl,
      userId,
      createBet,
      createBetError,
      clearCreateBetError,
      settlementSocketStatus,
      lastSettlementMessage,
      clearLastSettlementMessage,
      connectBetSettlementSocket,
      disconnectBetSettlementSocket,
    ]
  );

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
}

export function useApi(): ApiContextValue {
  const ctx = useContext(ApiContext);
  if (!ctx) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return ctx;
}
