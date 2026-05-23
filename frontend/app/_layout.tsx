import { Stack, useRouter, useSegments } from "expo-router";
import { useEffect } from "react";
import { GestureHandlerRootView } from "react-native-gesture-handler";

import { AuthProvider, useAuth } from '@/src/api/AuthContext';
import { ApiProvider } from '@/src/api/ApiContext';

/**
 * Sits inside both AuthProvider and the Stack's context so it can read auth
 * state and trigger navigation. Renders nothing — purely a side-effect hook.
 */
function RedirectController() {
  const { status } = useAuth();
  const segments = useSegments();
  const router = useRouter();

  useEffect(() => {
    if (status === 'loading') return;

    const onAuthScreen = segments[0] === 'login' || segments[0] === 'register';
    const onAppScreen = segments[0] === '(tabs)';

    if (status === 'unauthenticated' && !onAuthScreen) {
      router.replace('/login');
    } else if (status === 'authenticated' && !onAppScreen) {
      // Covers: index (spinner), login, register — redirect all to match
      router.replace('/(tabs)/match');
    }
  }, [status, segments, router]);

  return null;
}

export default function Layout() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <AuthProvider>
        <ApiProvider>
          <Stack screenOptions={{ headerShown: false }} />
          <RedirectController />
        </ApiProvider>
      </AuthProvider>
    </GestureHandlerRootView>
  );
}
