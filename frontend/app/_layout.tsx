import { Stack } from "expo-router";
import { GestureHandlerRootView } from "react-native-gesture-handler";

import { ApiProvider } from '@/src/api/ApiContext';

export default function Layout() {
  return (
      <ApiProvider>
        <GestureHandlerRootView style={{ flex: 1 }}>
            <Stack screenOptions={{ headerShown: false }} />
        </GestureHandlerRootView>
    </ApiProvider>
  );
}
