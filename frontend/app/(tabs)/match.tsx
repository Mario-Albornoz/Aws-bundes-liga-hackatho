import { useEffect } from "react";
import { StyleSheet, View } from "react-native";
import { usePositionalStream } from "../../src/ws/usePositionalStream";
import { PitchCanvas } from "../../src/components/pitch/PitchCanvas";

export default function MatchScreen() {
  const positional = usePositionalStream();

  useEffect(() => {
    positional.connect();
    return () => positional.disconnect();
  }, []);

  return (
    <View style={styles.container}>
      <PitchCanvas lastMessage={positional.lastMessage} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
});
