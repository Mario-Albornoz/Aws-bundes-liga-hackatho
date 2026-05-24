import { useRef, useState } from "react";
import {
  Animated,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useApi } from "@/src/api/ApiContext";
import { getTeamName } from "@/src/api/teamNames";
import type { Bet, BetStatus } from "@/src/api/types/bets";

// ─── status config ───────────────────────────────────────────────────────────

const STATUS_CONFIG: Record<
  BetStatus,
  { label: string; bg: string; text: string; dot: string }
> = {
  PENDING: { label: "Pending",  bg: "#1f2937", text: "#9ca3af", dot: "#6b7280" },
  ACTIVE:  { label: "Live",     bg: "#1e3a5f", text: "#60a5fa", dot: "#3b82f6" },
  SUCCESS: { label: "Won",      bg: "#14532d", text: "#4ade80", dot: "#22c55e" },
  FAILED:  { label: "Lost",     bg: "#450a0a", text: "#f87171", dot: "#ef4444" },
};

// ─── single bet card ─────────────────────────────────────────────────────────

function BetCard({ bet, userId }: { bet: Bet; userId: number }) {
  const cfg = STATUS_CONFIG[bet.bet_status];
  const me = bet.participants.find((p) => p.user_id === userId);
  const amount = me?.bet_amount ?? "?";
  const isMatchResult = bet.bet_info.bet_type === "match_result";

  // ── Match Result ──────────────────────────────────────────────────────────
  // body: "Bayern wins"  subtitle: "Full Match"
  // ── Substitution ─────────────────────────────────────────────────────────
  // body: player identifier  subtitle: team name  badge: YES / NO
  const bodyText = isMatchResult
    ? `${getTeamName(bet.bet_info.bet_specs.team_id ?? "")} wins`
    : (bet.bet_info.bet_specs.player_id ?? "—");

  const subtitleText = isMatchResult
    ? "Full Match"
    : getTeamName(bet.bet_info.bet_specs.team_id ?? "");

  return (
    <View style={[styles.card, { backgroundColor: cfg.bg }]}>
      <View style={styles.cardHeader}>
        <View style={[styles.dot, { backgroundColor: cfg.dot }]} />
        <Text style={[styles.statusLabel, { color: cfg.text }]}>{cfg.label}</Text>
        {/* For substitution bets show YES/NO; for match-result the team name is self-explanatory */}
        {!isMatchResult && (
          <Text style={styles.positionBadge}>{me?.position ? "YES" : "NO"}</Text>
        )}
      </View>
      <Text style={styles.playerName} numberOfLines={1}>{bodyText}</Text>
      <Text style={styles.teamName} numberOfLines={1}>{subtitleText}</Text>
      <Text style={styles.stakeText}>{amount} coins</Text>
    </View>
  );
}

// ─── dashboard ───────────────────────────────────────────────────────────────

export function BetStatusDashboard() {
  const { myBets, userId, settlementSocketStatus } = useApi();
  const [isOpen, setIsOpen] = useState(false);
  const slideAnim = useRef(new Animated.Value(0)).current;

  function toggle() {
    const toValue = isOpen ? 0 : 1;
    Animated.spring(slideAnim, {
      toValue,
      useNativeDriver: true,
      tension: 70,
      friction: 10,
    }).start();
    setIsOpen(!isOpen);
  }

  const panelTranslateX = slideAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [220, 0],
  });

  const activeBets = myBets.filter((b) => b.bet_status === "ACTIVE").length;
  const isConnected = settlementSocketStatus === "connected";

  return (
    <View style={styles.wrapper} pointerEvents="box-none">
      {/* Toggle button */}
      <Pressable style={styles.toggleBtn} onPress={toggle}>
        <View style={styles.toggleInner}>
          <View
            style={[
              styles.connectionDot,
              { backgroundColor: isConnected ? "#22c55e" : "#6b7280" },
            ]}
          />
          <Text style={styles.toggleIcon}>🎰</Text>
          {myBets.length > 0 && (
            <View style={[styles.badge, activeBets > 0 && styles.badgeActive]}>
              <Text style={styles.badgeText}>{myBets.length}</Text>
            </View>
          )}
        </View>
      </Pressable>

      {/* Slide-in panel */}
      <Animated.View
        style={[
          styles.panel,
          { transform: [{ translateX: panelTranslateX }] },
        ]}
        pointerEvents={isOpen ? "auto" : "none"}
      >
        <View style={styles.panelHeader}>
          <Text style={styles.panelTitle}>My Bets</Text>
          <Pressable onPress={toggle} hitSlop={8}>
            <Text style={styles.closeText}>✕</Text>
          </Pressable>
        </View>

        {myBets.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>No active bets yet.</Text>
            <Text style={styles.emptySubText}>
              Join a bet when an opportunity appears.
            </Text>
          </View>
        ) : (
          <ScrollView
            style={styles.list}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
          >
            {myBets.map((bet) => (
              <BetCard
                key={bet.bet_info.bet_id}
                bet={bet}
                userId={userId}
              />
            ))}
          </ScrollView>
        )}
      </Animated.View>
    </View>
  );
}

// ─── styles ──────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  wrapper: {
    position: "absolute",
    top: 48,
    right: 0,
    alignItems: "flex-end",
  },
  toggleBtn: {
    backgroundColor: "rgba(17,24,39,0.85)",
    borderTopLeftRadius: 10,
    borderBottomLeftRadius: 10,
    padding: 10,
    marginBottom: 4,
    borderWidth: 1,
    borderRightWidth: 0,
    borderColor: "#374151",
  },
  toggleInner: {
    alignItems: "center",
    gap: 4,
  },
  connectionDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  toggleIcon: {
    fontSize: 20,
  },
  badge: {
    backgroundColor: "#374151",
    borderRadius: 8,
    minWidth: 16,
    height: 16,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 3,
  },
  badgeActive: {
    backgroundColor: "#3b82f6",
  },
  badgeText: {
    color: "#fff",
    fontSize: 10,
    fontWeight: "700",
  },
  panel: {
    width: 200,
    backgroundColor: "#111827",
    borderTopLeftRadius: 12,
    borderBottomLeftRadius: 12,
    borderWidth: 1,
    borderRightWidth: 0,
    borderColor: "#374151",
    overflow: "hidden",
  },
  panelHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#1f2937",
  },
  panelTitle: {
    color: "#f9fafb",
    fontWeight: "700",
    fontSize: 13,
  },
  closeText: {
    color: "#6b7280",
    fontSize: 14,
  },
  list: {
    maxHeight: 300,
  },
  listContent: {
    padding: 8,
  },
  card: {
    borderRadius: 8,
    padding: 10,
    marginBottom: 6,
  },
  cardHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginBottom: 4,
  },
  dot: {
    width: 7,
    height: 7,
    borderRadius: 4,
  },
  statusLabel: {
    fontSize: 11,
    fontWeight: "700",
    flex: 1,
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  positionBadge: {
    color: "#f9fafb",
    fontSize: 10,
    fontWeight: "700",
    backgroundColor: "#374151",
    paddingHorizontal: 5,
    paddingVertical: 2,
    borderRadius: 4,
  },
  playerName: {
    color: "#e5e7eb",
    fontSize: 12,
    fontWeight: "600",
  },
  teamName: {
    color: "#9ca3af",
    fontSize: 11,
  },
  stakeText: {
    color: "#6b7280",
    fontSize: 11,
    marginTop: 2,
  },
  emptyState: {
    padding: 16,
    alignItems: "center",
    gap: 4,
  },
  emptyText: {
    color: "#6b7280",
    fontSize: 12,
    fontWeight: "600",
  },
  emptySubText: {
    color: "#4b5563",
    fontSize: 11,
    textAlign: "center",
  },
});
