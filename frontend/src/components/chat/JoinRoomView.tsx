import { useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { joinRoom } from '@/src/api/chat';
import {
  COLOR_DANGER,
  COLOR_PRIMARY,
  COLOR_SURFACE,
  COLOR_SURFACE_SUBTLE,
  COLOR_TEXT_MUTED,
  COLOR_TEXT_SECONDARY,
  COLOR_WHITE,
  STR_BACK,
  STR_JOIN,
  STR_JOIN_CODE_LABEL,
  STR_JOIN_CODE_PLACEHOLDER,
} from './constants';

interface Props {
  userId: string;
  onJoined: (roomId: string, wsToken: string) => void;
  onBack: () => void;
}

export function JoinRoomView({ userId, onJoined, onBack }: Props) {
  const [connectionString, setConnectionString] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = connectionString.trim().length > 0;

  async function handleJoin() {
    if (!canSubmit) return;
    setLoading(true);
    setError(null);
    try {
      const res = await joinRoom(userId, connectionString.trim());
      onJoined(res.room_id, res.ws_token);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to join room');
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.label}>{STR_JOIN_CODE_LABEL}</Text>
      <TextInput
        style={styles.input}
        value={connectionString}
        onChangeText={setConnectionString}
        placeholder={STR_JOIN_CODE_PLACEHOLDER}
        placeholderTextColor={COLOR_TEXT_MUTED}
        autoCapitalize="none"
        autoCorrect={false}
      />
      {error && <Text style={styles.error}>{error}</Text>}
      <Pressable
        style={[styles.primaryBtn, !canSubmit && styles.disabledBtn]}
        onPress={handleJoin}
        disabled={loading || !canSubmit}
      >
        {loading
          ? <ActivityIndicator color={COLOR_WHITE} size="small" />
          : <Text style={styles.primaryBtnText}>{STR_JOIN}</Text>}
      </Pressable>
      <Pressable style={styles.secondaryBtn} onPress={onBack}>
        <Text style={styles.secondaryBtnText}>{STR_BACK}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 14, gap: 10 },
  label: { color: COLOR_TEXT_SECONDARY, fontSize: 12 },
  input: {
    backgroundColor: COLOR_SURFACE,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 8,
    color: COLOR_WHITE,
    fontSize: 13,
  },
  error: { color: COLOR_DANGER, fontSize: 12 },
  primaryBtn: {
    backgroundColor: COLOR_PRIMARY,
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: 'center',
  },
  primaryBtnText: { color: COLOR_WHITE, fontWeight: '600', fontSize: 14 },
  secondaryBtn: {
    backgroundColor: COLOR_SURFACE_SUBTLE,
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: 'center',
  },
  secondaryBtnText: { color: COLOR_TEXT_SECONDARY, fontSize: 14 },
  disabledBtn: { opacity: 0.4 },
});
