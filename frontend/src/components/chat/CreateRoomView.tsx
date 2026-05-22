import { useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import * as Clipboard from 'expo-clipboard';
import { createRoom, joinRoom } from '@/src/api/chat';
import {
  COLOR_COPY_BTN_BG,
  COLOR_DANGER,
  COLOR_PRIMARY,
  COLOR_SURFACE,
  COLOR_SURFACE_SUBTLE,
  COLOR_TEXT_CODE,
  COLOR_TEXT_COPY_BTN,
  COLOR_TEXT_MUTED,
  COLOR_TEXT_SECONDARY,
  COLOR_WHITE,
  STR_BACK,
  STR_CANCEL,
  STR_COPIED,
  STR_COPY,
  STR_CREATE,
  STR_ENTER_ROOM,
  STR_ROOM_NAME_LABEL,
  STR_ROOM_NAME_PLACEHOLDER,
  STR_SHARE_CODE_LABEL,
} from './constants';

interface Props {
  userId: string;
  onCreated: (roomId: string, wsToken: string) => void;
  onBack: () => void;
}

export function CreateRoomView({ userId, onCreated, onBack }: Props) {
  const [name, setName] = useState('');
  const [connectionString, setConnectionString] = useState<string | null>(null);
  const [roomId, setRoomId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    if (!connectionString) return;
    await Clipboard.setStringAsync(connectionString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  async function handleCreate() {
    if (!name.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const room = await createRoom(name.trim(), userId);
      setRoomId(room.room_id);
      setConnectionString(room.connection_string);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to create room');
    } finally {
      setLoading(false);
    }
  }

  async function handleEnter() {
    if (!roomId || !connectionString) return;
    setLoading(true);
    setError(null);
    try {
      const res = await joinRoom(userId, connectionString);
      onCreated(res.room_id, res.ws_token);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to enter room');
    } finally {
      setLoading(false);
    }
  }

  if (connectionString && roomId) {
    return (
      <View style={styles.container}>
        <Text style={styles.label}>{STR_SHARE_CODE_LABEL}</Text>
        <View style={styles.codeBox}>
          <Text style={styles.code} selectable>{connectionString}</Text>
          <Pressable onPress={handleCopy} style={styles.copyBtn}>
            <Text style={styles.copyBtnText}>{copied ? STR_COPIED : STR_COPY}</Text>
          </Pressable>
        </View>
        {error && <Text style={styles.error}>{error}</Text>}
        <Pressable style={styles.primaryBtn} onPress={handleEnter} disabled={loading}>
          {loading
            ? <ActivityIndicator color={COLOR_WHITE} size="small" />
            : <Text style={styles.primaryBtnText}>{STR_ENTER_ROOM}</Text>}
        </Pressable>
        <Pressable style={styles.secondaryBtn} onPress={onBack}>
          <Text style={styles.secondaryBtnText}>{STR_CANCEL}</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.label}>{STR_ROOM_NAME_LABEL}</Text>
      <TextInput
        style={styles.input}
        value={name}
        onChangeText={setName}
        placeholder={STR_ROOM_NAME_PLACEHOLDER}
        placeholderTextColor={COLOR_TEXT_MUTED}
      />
      {error && <Text style={styles.error}>{error}</Text>}
      <Pressable
        style={[styles.primaryBtn, !name.trim() && styles.disabledBtn]}
        onPress={handleCreate}
        disabled={loading || !name.trim()}
      >
        {loading
          ? <ActivityIndicator color={COLOR_WHITE} size="small" />
          : <Text style={styles.primaryBtnText}>{STR_CREATE}</Text>}
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
  codeBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLOR_SURFACE_SUBTLE,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 8,
    gap: 8,
  },
  code: { flex: 1, color: COLOR_TEXT_CODE, fontSize: 12, fontFamily: 'monospace' },
  copyBtn: {
    backgroundColor: COLOR_COPY_BTN_BG,
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  copyBtnText: { color: COLOR_TEXT_COPY_BTN, fontSize: 12 },
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
