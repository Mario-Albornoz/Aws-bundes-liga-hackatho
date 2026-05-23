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
import type {
  Bet,
  BetCreateRequest,
  BetSettledMessage,
  BetSnapshotMessage,
  BetUpdatedMessage,
} from '@/src/api/types/bets';
import { useAuth } from '@/src/api/AuthContext';

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
  myBets: Bet[];
  connectBetSettlementSocket: () => void;
  disconnectBetSettlementSocket: () => void;
};

const ApiContext = createContext<ApiContextValue | null>(null);

export function ApiProvider({ children }: { children: React.ReactNode }) {
  const { user, accessToken } = useAuth();
  const [userId, setUserId] = useState(user?.user_id ?? 1);

  useEffect(() => {
    if (user?.user_id) setUserId(user.user_id);
  }, [user?.user_id]);
  const [settlementSocketStatus, setSettlementSocketStatus] =
    useState<SettlementSocketStatus>('idle');
  const [lastSettlementMessage, setLastSettlementMessage] = useState<BetSettledMessage | null>(
    null
  );
  const [myBets, setMyBets] = useState<Bet[]>([]);
  const [createBetError, setCreateBetError] = useState<string | null>(null);
  const socketRef = useRef<BetSettlementSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const intentionalCloseRef = useRef(false);

  const apiBaseUrl = useMemo(() => getApiBaseUrl(), []);

  const clearCreateBetError = useCallback(() => setCreateBetError(null), []);
  const clearLastSettlementMessage = useCallback(() => setLastSettlementMessage(null), []);

  const disconnectBetSettlementSocket = useCallback(() => {
    intentionalCloseRef.current = true;
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    socketRef.current?.close();
    socketRef.current = null;
    setSettlementSocketStatus('idle');
  }, []);

  const connectBetSettlementSocket = useCallback(() => {
    intentionalCloseRef.current = false;
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    socketRef.current?.close();
    socketRef.current = null;
    setSettlementSocketStatus('connecting');
    const url = getBetSettlementWebSocketUrl(userId);
    socketRef.current = new BetSettlementSocket(url, {
      onOpen: () => setSettlementSocketStatus('connected'),
      onMessage: (raw) => {
        try {
          const data = JSON.parse(raw) as
            | BetSettledMessage
            | BetSnapshotMessage
            | BetUpdatedMessage;
          if (!data?.type) return;

          if (data.type === 'bet_snapshot') {
            setMyBets((data as BetSnapshotMessage).bets);
          } else if (data.type === 'bet_updated') {
            const { bet_id, status } = data as BetUpdatedMessage;
            setMyBets((prev) =>
              prev.map((b) =>
                b.bet_info.bet_id === bet_id ? { ...b, bet_status: status } : b
              )
            );
          } else if (data.type === 'bet_settled') {
            const msg = data as BetSettledMessage;
            setLastSettlementMessage(msg);
            setMyBets((prev) =>
              prev.map((b) =>
                b.bet_info.bet_id === msg.bet_id ? { ...b, bet_status: msg.status } : b
              )
            );
          }
        } catch {
          /* ignore non-JSON */
        }
      },
      onClose: () => {
        setSettlementSocketStatus('closed');
        if (!intentionalCloseRef.current) {
          reconnectTimerRef.current = setTimeout(() => {
            connectBetSettlementSocket();
          }, 3000);
        }
      },
      onError: () => setSettlementSocketStatus('error'),
    });
  }, [userId]);

  useEffect(() => {
    return () => {
      intentionalCloseRef.current = true;
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      socketRef.current?.close();
      socketRef.current = null;
    };
  }, []);

  const createBet = useCallback(async (body: BetCreateRequest): Promise<Bet> => {
    setCreateBetError(null);
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    };
    if (accessToken) headers['Authorization'] = `Bearer ${accessToken}`;
    const res = await fetch(getCreateBetUrl(), {
      method: 'POST',
      headers,
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
      myBets,
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
      myBets,
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
