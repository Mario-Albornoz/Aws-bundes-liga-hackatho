import * as SecureStore from 'expo-secure-store';
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';

import {
  type TokenResponse,
  type UserProfile,
  login as apiLogin,
  logout as apiLogout,
  refreshAccessToken,
  register as apiRegister,
} from './auth';

const SECURE_STORE_REFRESH_KEY = 'auth_refresh_token';

// Refresh the access token 60 seconds before it expires (token lives 30 min)
const ACCESS_TOKEN_LIFETIME_MS = 30 * 60 * 1000;
const REFRESH_BUFFER_MS = 60 * 1000;
const REFRESH_INTERVAL_MS = ACCESS_TOKEN_LIFETIME_MS - REFRESH_BUFFER_MS;

export type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';

export interface AuthContextValue {
  status: AuthStatus;
  accessToken: string | null;
  user: UserProfile | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, name: string, lastName: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function sessionFromResponse(res: TokenResponse): {
  user: UserProfile;
  accessToken: string;
  refreshToken: string;
} {
  return {
    accessToken: res.access_token,
    refreshToken: res.refresh_token,
    user: {
      user_id: res.user_id,
      username: res.username,
      name: res.name,
      last_name: res.last_name,
      balance: res.balance,
    },
  };
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>('loading');
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refreshTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const refreshTokenRef = useRef<string | null>(null);

  const clearError = useCallback(() => setError(null), []);

  const scheduleRefresh = useCallback((currentRefreshToken: string) => {
    if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current);
    refreshTimerRef.current = setTimeout(async () => {
      try {
        const res = await refreshAccessToken(currentRefreshToken);
        setAccessToken(res.access_token);
        scheduleRefresh(currentRefreshToken);
      } catch {
        // Refresh failed — session expired, force logout
        setAccessToken(null);
        setUser(null);
        setStatus('unauthenticated');
        await SecureStore.deleteItemAsync(SECURE_STORE_REFRESH_KEY);
      }
    }, REFRESH_INTERVAL_MS);
  }, []);

  const applySession = useCallback(
    (session: { accessToken: string; refreshToken: string; user: UserProfile }) => {
      refreshTokenRef.current = session.refreshToken;
      setAccessToken(session.accessToken);
      setUser(session.user);
      setStatus('authenticated');
      scheduleRefresh(session.refreshToken);
    },
    [scheduleRefresh],
  );

  // On mount: try to restore session from stored refresh token
  useEffect(() => {
    (async () => {
      try {
        const stored = await SecureStore.getItemAsync(SECURE_STORE_REFRESH_KEY);
        if (!stored) {
          setStatus('unauthenticated');
          return;
        }
        const res = await refreshAccessToken(stored);
        // We don't have user profile from refresh — just set minimal info
        // A proper GET /auth/me call would enrich this
        setAccessToken(res.access_token);
        refreshTokenRef.current = stored;
        setStatus('authenticated');
        scheduleRefresh(stored);
      } catch {
        await SecureStore.deleteItemAsync(SECURE_STORE_REFRESH_KEY);
        setStatus('unauthenticated');
      }
    })();

    return () => {
      if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current);
    };
  }, [scheduleRefresh]);

  const login = useCallback(
    async (username: string, password: string) => {
      setError(null);
      try {
        const res = await apiLogin(username, password);
        const session = sessionFromResponse(res);
        await SecureStore.setItemAsync(SECURE_STORE_REFRESH_KEY, session.refreshToken);
        applySession(session);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : 'Login failed');
        throw e;
      }
    },
    [applySession],
  );

  const register = useCallback(
    async (username: string, name: string, lastName: string, password: string) => {
      setError(null);
      try {
        const res = await apiRegister(username, name, lastName, password);
        const session = sessionFromResponse(res);
        await SecureStore.setItemAsync(SECURE_STORE_REFRESH_KEY, session.refreshToken);
        applySession(session);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : 'Registration failed');
        throw e;
      }
    },
    [applySession],
  );

  const logout = useCallback(async () => {
    if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current);
    try {
      if (accessToken && refreshTokenRef.current) {
        await apiLogout(accessToken, refreshTokenRef.current);
      }
    } catch {
      // best-effort logout
    } finally {
      refreshTokenRef.current = null;
      setAccessToken(null);
      setUser(null);
      setStatus('unauthenticated');
      await SecureStore.deleteItemAsync(SECURE_STORE_REFRESH_KEY);
    }
  }, [accessToken]);

  return (
    <AuthContext.Provider
      value={{ status, accessToken, user, login, register, logout, error, clearError }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
