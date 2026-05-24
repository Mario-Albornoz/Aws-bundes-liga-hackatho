import { useEffect, useRef, useState } from "react";
import {
  Animated,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { useApi } from "@/src/api/ApiContext";
import { getTeamName } from "@/src/api/teamNames";
import type {
  BetCreateRequest,
  BetOpportunity,
  MatchResultContext,
  SubstitutionContext,
} from "@/src/api/types/bets";

interface Props {
  opportunity: BetOpportunity;
  onDismiss: () => void;
}

/** Use backend-provided name if available, otherwise fall back to shared lookup. */
function teamLabel(id: string, name?: string): string {
  return name && name.trim() ? name : getTeamName(id);
}

export function BetOpportunityBanner({ opportunity, onDismiss }: Props) {
  const { userId, createBet } = useApi();
  const slideAnim = useRef(new Animated.Value(-160)).current;
  const [secondsLeft, setSecondsLeft] = useState(0);
  const [amount, setAmount] = useState("10");
  const [joining, setJoining] = useState(false);
  const [result, setResult] = useState<"success" | "error" | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  const isMatchResult = opportunity.bet_type === "match_result";
  const subCtx = isMatchResult
    ? null
    : (opportunity.context as SubstitutionContext);
  const mrCtx = isMatchResult
    ? (opportunity.context as MatchResultContext)
    : null;

  // Compute remaining seconds from expires_at
  useEffect(() => {
    const tick = () => {
      const diff = Math.max(
        0,
        Math.floor(
          (new Date(opportunity.expires_at).getTime() - Date.now()) / 1000
        )
      );
      setSecondsLeft(diff);
      // Match-result bets span the full game — don't auto-dismiss them
      if (diff === 0 && !isMatchResult) onDismiss();
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [opportunity.expires_at, onDismiss]);

  // Slide in on mount
  useEffect(() => {
    Animated.spring(slideAnim, {
      toValue: 0,
      useNativeDriver: true,
      tension: 60,
      friction: 9,
    }).start();
  }, [slideAnim]);

  function dismiss() {
    Animated.timing(slideAnim, {
      toValue: -160,
      duration: 220,
      useNativeDriver: true,
    }).start(onDismiss);
  }

  async function handleSubstitutionJoin(position: boolean) {
    if (!subCtx) return;
    const parsedAmount = parseInt(amount, 10);
    if (isNaN(parsedAmount) || parsedAmount <= 0) return;

    setJoining(true);
    setResult(null);

    const body: BetCreateRequest = {
      bet_info: {
        bet_id: opportunity.bet_id,
        bet_type: "substitution",
        duration: opportunity.window_seconds,
        match_id: opportunity.match_id,
        bet_specs: {
          player_id: subCtx.player_on,
          team_id: subCtx.team,
          trigger_event_type: "Substitution",
        },
      },
      bet_subscription: {
        participant: { user_id: userId, bet_amount: parsedAmount, position },
      },
    };

    await submitBet(body);
  }

  async function handleMatchResultJoin(chosenTeamId: string) {
    if (!mrCtx) return;
    const parsedAmount = parseInt(amount, 10);
    if (isNaN(parsedAmount) || parsedAmount <= 0) return;

    setJoining(true);
    setResult(null);

    const body: BetCreateRequest = {
      bet_info: {
        bet_id: opportunity.bet_id,
        bet_type: "match_result",
        duration: opportunity.window_seconds,
        match_id: opportunity.match_id,
        bet_specs: {
          trigger_event_type: "KickOff",
          team_id: chosenTeamId,
          team_left: mrCtx.team_left,
          team_right: mrCtx.team_right,
        },
      },
      bet_subscription: {
        participant: {
          user_id: userId,
          bet_amount: parsedAmount,
          position: true, // position=true always means "I bet my chosen team wins"
        },
      },
    };

    await submitBet(body);
  }

  async function submitBet(body: BetCreateRequest) {
    try {
      await createBet(body);
      setResult("success");
      setTimeout(dismiss, 1800);
    } catch (e: unknown) {
      setResult("error");
      setErrorMsg(e instanceof Error ? e.message : "Failed to join bet.");
    } finally {
      setJoining(false);
    }
  }

  // Match-result bets last the whole match — show "Full Match" instead of a countdown
  const timerLabel = isMatchResult
    ? "Full Match"
    : (() => {
        const m = Math.floor(secondsLeft / 60);
        const s = secondsLeft % 60;
        return `${m}:${s.toString().padStart(2, "0")}`;
      })();
  const urgentColor = isMatchResult ? "#22c55e" : secondsLeft <= 30 ? "#ef4444" : "#22c55e";

  return (
    <Animated.View
      style={[styles.container, { transform: [{ translateY: slideAnim }] }]}
    >
      <View style={styles.header}>
        <View style={styles.badgeRow}>
          <View style={styles.liveBadge}>
            <Text style={styles.liveBadgeText}>LIVE BET</Text>
          </View>
          <Text style={[styles.timer, { color: urgentColor }]}>{timerLabel}</Text>
        </View>
        <Pressable onPress={dismiss} style={styles.closeBtn} hitSlop={8}>
          <Text style={styles.closeBtnText}>✕</Text>
        </Pressable>
      </View>

      {isMatchResult && mrCtx ? (
        // ── Match Result Bet ─────────────────────────────────────────
        <>
          <Text style={styles.title}>Match Result Bet</Text>
          <Text style={styles.body}>Which team will win the match?</Text>

          {result === "success" ? (
            <View style={styles.resultRow}>
              <Text style={styles.successText}>✓ Bet placed!</Text>
            </View>
          ) : (
            <>
              {result === "error" && (
                <Text style={styles.errorText}>{errorMsg}</Text>
              )}
              <View style={styles.amountRow}>
                <Text style={styles.amountLabel}>Stake</Text>
                <TextInput
                  style={styles.amountInput}
                  keyboardType="number-pad"
                  value={amount}
                  onChangeText={setAmount}
                  maxLength={5}
                  editable={!joining}
                />
                <Text style={styles.amountCurrency}>coins</Text>
              </View>
              <View style={styles.btnRow}>
                <Pressable
                  style={[styles.teamBtn, joining && styles.btnDisabled]}
                  onPress={() => handleMatchResultJoin(mrCtx.team_left)}
                  disabled={joining}
                >
                  <Text style={styles.teamBtnText}>
                    {teamLabel(mrCtx.team_left, mrCtx.team_left_name)}
                  </Text>
                  <Text style={styles.teamBtnSub}>wins</Text>
                </Pressable>
                <Pressable
                  style={[styles.teamBtn, joining && styles.btnDisabled]}
                  onPress={() => handleMatchResultJoin(mrCtx.team_right)}
                  disabled={joining}
                >
                  <Text style={styles.teamBtnText}>
                    {teamLabel(mrCtx.team_right, mrCtx.team_right_name)}
                  </Text>
                  <Text style={styles.teamBtnSub}>wins</Text>
                </Pressable>
              </View>
            </>
          )}
        </>
      ) : (
        // ── Substitution Bet ─────────────────────────────────────────
        <>
          <Text style={styles.title}>Substitution Incoming!</Text>
          <Text style={styles.body}>
            <Text style={styles.highlight}>{subCtx?.player_on}</Text>
            {" is coming on for "}
            <Text style={styles.highlight}>{subCtx?.team}</Text>.
            {"\n"}Will they make an impact?
          </Text>

          {result === "success" ? (
            <View style={styles.resultRow}>
              <Text style={styles.successText}>✓ Bet placed!</Text>
            </View>
          ) : (
            <>
              {result === "error" && (
                <Text style={styles.errorText}>{errorMsg}</Text>
              )}
              <View style={styles.amountRow}>
                <Text style={styles.amountLabel}>Stake</Text>
                <TextInput
                  style={styles.amountInput}
                  keyboardType="number-pad"
                  value={amount}
                  onChangeText={setAmount}
                  maxLength={5}
                  editable={!joining}
                />
                <Text style={styles.amountCurrency}>coins</Text>
              </View>
              <View style={styles.btnRow}>
                <Pressable
                  style={[styles.yesBtn, joining && styles.btnDisabled]}
                  onPress={() => handleSubstitutionJoin(true)}
                  disabled={joining}
                >
                  <Text style={styles.yesBtnText}>YES</Text>
                </Pressable>
                <Pressable
                  style={[styles.noBtn, joining && styles.btnDisabled]}
                  onPress={() => handleSubstitutionJoin(false)}
                  disabled={joining}
                >
                  <Text style={styles.noBtnText}>NO</Text>
                </Pressable>
              </View>
            </>
          )}
        </>
      )}
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    backgroundColor: "#1a1a2e",
    borderBottomWidth: 1,
    borderBottomColor: "#f59e0b",
    paddingHorizontal: 16,
    paddingTop: 52,
    paddingBottom: 14,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 8,
    elevation: 10,
    zIndex: 999,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6,
  },
  badgeRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  liveBadge: {
    backgroundColor: "#f59e0b",
    borderRadius: 4,
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  liveBadgeText: {
    color: "#000",
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 0.8,
  },
  timer: {
    fontSize: 14,
    fontWeight: "700",
    fontVariant: ["tabular-nums"],
  },
  closeBtn: {
    padding: 4,
  },
  closeBtnText: {
    color: "#9ca3af",
    fontSize: 14,
  },
  title: {
    color: "#f9fafb",
    fontWeight: "700",
    fontSize: 15,
    marginBottom: 4,
  },
  body: {
    color: "#d1d5db",
    fontSize: 13,
    lineHeight: 18,
    marginBottom: 10,
  },
  highlight: {
    color: "#f59e0b",
    fontWeight: "600",
  },
  amountRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginBottom: 10,
  },
  amountLabel: {
    color: "#9ca3af",
    fontSize: 13,
  },
  amountInput: {
    backgroundColor: "#374151",
    color: "#f9fafb",
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 4,
    fontSize: 14,
    fontWeight: "600",
    width: 64,
    textAlign: "center",
  },
  amountCurrency: {
    color: "#9ca3af",
    fontSize: 13,
  },
  btnRow: {
    flexDirection: "row",
    gap: 10,
  },
  yesBtn: {
    flex: 1,
    backgroundColor: "#16a34a",
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: "center",
  },
  yesBtnText: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 14,
    letterSpacing: 0.5,
  },
  noBtn: {
    flex: 1,
    backgroundColor: "#dc2626",
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: "center",
  },
  noBtnText: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 14,
    letterSpacing: 0.5,
  },
  teamBtn: {
    flex: 1,
    backgroundColor: "#1d4ed8",
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: "center",
  },
  teamBtnText: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 13,
    letterSpacing: 0.5,
  },
  teamBtnSub: {
    color: "#93c5fd",
    fontSize: 11,
    marginTop: 2,
  },
  btnDisabled: {
    opacity: 0.5,
  },
  resultRow: {
    alignItems: "center",
    paddingVertical: 6,
  },
  successText: {
    color: "#22c55e",
    fontSize: 15,
    fontWeight: "700",
  },
  errorText: {
    color: "#ef4444",
    fontSize: 12,
    marginBottom: 6,
  },
});
