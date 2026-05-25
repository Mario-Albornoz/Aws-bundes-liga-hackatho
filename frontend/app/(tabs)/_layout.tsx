import { Tabs } from "expo-router";
import { StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

const BG = "#0f172a";
const BORDER = "#1e293b";

function MatchHeader() {
  const { top } = useSafeAreaInsets();
  return (
    <View style={[styles.header, { paddingTop: top + 4 }]}>
      <Text style={styles.title}>MATCH</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    backgroundColor: BG,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: BORDER,
    paddingBottom: 8,
    alignItems: "center",
  },
  title: {
    color: "#f1f5f9",
    fontSize: 12,
    fontWeight: "700",
    letterSpacing: 2,
  },
});

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        // Slim custom header at the top; no bottom tab bar (single-tab app)
        header: () => <MatchHeader />,
        tabBarStyle: { display: "none" },
      }}
    >
      <Tabs.Screen name="match" options={{ title: "Match" }} />
    </Tabs>
  );
}
