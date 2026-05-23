import { useCallback, useEffect, useState } from "react";
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
  const { connectBetSettlementSocket, disconnectBetSettlementSocket } = useApi();
  const [activeBet, setActiveBet] = useState<BetOpportunityMessage | null>(null);

  useEffect(() => {
    positional.connect();
    connectBetSettlementSocket();
    return () => {
      positional.disconnect();
      disconnectBetSettlementSocket();
    };
  }, []);

  const handleBetOpportunity = useCallback((msg: BetOpportunityMessage) => {
    setActiveBet(msg);
  }, []);

  const handleDismiss = useCallback(() => {
    setActiveBet(null);
  }, []);

  return (
    <View style={styles.container}>
      <PitchCanvas lastMessage={positional.lastMessage} />
      <ChatOverlay onBetOpportunity={handleBetOpportunity} />
      <BetStatusDashboard />
      {activeBet && (
        <BetOpportunityBanner
          opportunity={activeBet.opportunity}
          onDismiss={handleDismiss}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
});
