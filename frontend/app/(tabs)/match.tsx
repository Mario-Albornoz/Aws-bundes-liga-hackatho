import { useCallback, useEffect } from "react";
import { StyleSheet, View } from "react-native";
import { usePositionalStream } from "../../src/api/usePositionalStream";
import { useApi } from "../../src/api/ApiContext";
import type { BetOpportunityMessage } from "../../src/api/types/bets";
import { PitchCanvas } from "../../src/components/pitch/PitchCanvas";
import { ChatOverlay } from "../../src/components/chat/ChatOverlay";
import { BetOpportunityBanner } from "../../src/components/bets/BetOpportunityBanner";
import { BetStatusDashboard } from "../../src/components/bets/BetStatusDashboard";

export default function MatchScreen() {
  const positional = usePositionalStream();
  const {
    connectBetSettlementSocket,
    disconnectBetSettlementSocket,
    latestBetOpportunity,
    clearLatestBetOpportunity,
    setLatestBetOpportunity,
  } = useApi();

  useEffect(() => {
    positional.connect();
    connectBetSettlementSocket();
    return () => {
      positional.disconnect();
      disconnectBetSettlementSocket();
    };
  }, []);

  // Chat-room path: forwards opportunities to the shared ApiContext state
  // so both delivery channels (settlement socket + chat room) use one banner.
  const handleBetOpportunity = useCallback(
    (msg: BetOpportunityMessage) => {
      setLatestBetOpportunity(msg.opportunity);
    },
    [setLatestBetOpportunity]
  );

  return (
    <View style={styles.container}>
      <PitchCanvas lastMessage={positional.lastMessage} />
      <ChatOverlay onBetOpportunity={handleBetOpportunity} />
      <BetStatusDashboard />
      {latestBetOpportunity && (
        <BetOpportunityBanner
          opportunity={latestBetOpportunity}
          onDismiss={clearLatestBetOpportunity}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
});
