import { Tabs } from 'expo-router';

export default function TabLayout() {
  return (
    <Tabs>
      <Tabs.Screen name="match" options={{ title: 'Match' }} />
    </Tabs>
  );
}