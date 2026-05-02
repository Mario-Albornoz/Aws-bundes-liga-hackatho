import { useState } from 'react';
import { ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';
import { useEventsStream } from '../../src/ws/useEventsStream';
import { usePositionalStream } from '../../src/ws/usePositionalStream';

const STATUS_COLOR: Record<string, string> = {
  idle: '#888',
  connecting: '#f0a500',
  connected: '#2ecc71',
  error: '#e74c3c',
  closed: '#888',
};

export default function MatchScreen() {
  const [matchId, setMatchId] = useState('');

  const events = useEventsStream();
  const positional = usePositionalStream();

  const isActive = (s: string) => s === 'connected' || s === 'connecting';

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>WebSocket Test</Text>

      <TextInput
        style={styles.input}
        placeholder="Match ID"
        value={matchId}
        onChangeText={setMatchId}
        autoCapitalize="none"
      />

      <Section
        label="Events"
        status={events.status}
        lastMessage={events.lastMessage}
        onConnect={() => events.connect(matchId)}
        onDisconnect={events.disconnect}
        isActive={isActive(events.status)}
      />

      <Section
        label="Positional"
        status={positional.status}
        lastMessage={positional.lastMessage}
        onConnect={() => positional.connect(matchId)}
        onDisconnect={positional.disconnect}
        isActive={isActive(positional.status)}
      />
    </ScrollView>
  );
}

type SectionProps = {
  label: string;
  status: string;
  lastMessage: string | null;
  onConnect: () => void;
  onDisconnect: () => void;
  isActive: boolean;
};

function Section({ label, status, lastMessage, onConnect, onDisconnect, isActive }: SectionProps) {
  return (
    <View style={styles.section}>
      <View style={styles.row}>
        <Text style={styles.sectionTitle}>{label}</Text>
        <Text style={[styles.status, { color: STATUS_COLOR[status] ?? '#888' }]}>{status}</Text>
      </View>
      <TouchableOpacity
        style={[styles.button, isActive && styles.buttonDisconnect]}
        onPress={isActive ? onDisconnect : onConnect}
      >
        <Text style={styles.buttonText}>{isActive ? 'Disconnect' : 'Connect'}</Text>
      </TouchableOpacity>
      {lastMessage && (
        <ScrollView style={styles.messageBox} nestedScrollEnabled>
          <Text style={styles.messageText}>{lastMessage}</Text>
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, gap: 16 },
  title: { fontSize: 20, fontWeight: 'bold', marginBottom: 8 },
  input: {
    borderWidth: 1, borderColor: '#ccc', borderRadius: 8,
    padding: 10, fontSize: 16,
  },
  section: { gap: 8 },
  row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  sectionTitle: { fontSize: 16, fontWeight: '600' },
  status: { fontSize: 13, fontWeight: '500' },
  button: {
    backgroundColor: '#3498db', borderRadius: 8,
    paddingVertical: 10, alignItems: 'center',
  },
  buttonDisconnect: { backgroundColor: '#e74c3c' },
  buttonText: { color: '#fff', fontWeight: '600' },
  messageBox: {
    backgroundColor: '#f4f4f4', borderRadius: 8,
    padding: 10, maxHeight: 160,
  },
  messageText: { fontFamily: 'monospace', fontSize: 12 },
});
