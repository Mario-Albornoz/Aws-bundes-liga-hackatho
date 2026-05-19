import { useRef, useState } from 'react';
import { FlatList, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import type { IncomingWsMessage } from '@/src/api/types/chat';
import { MessageBubble } from './MessageBubble';
import {
  COLOR_DANGER,
  COLOR_DANGER_BG,
  COLOR_PANEL_BORDER,
  COLOR_PRIMARY,
  COLOR_SURFACE,
  COLOR_TEXT_SECONDARY,
  COLOR_WHITE,
  STR_CHAT_TITLE,
  STR_LEAVE,
  STR_MESSAGE_PLACEHOLDER,
  STR_MINIMIZE,
  STR_SEND_ICON,
} from './constants';

interface Props {
  messages: IncomingWsMessage[];
  userId: string;
  sendMessage: (content: string) => void;
  onMinimize: () => void;
  onLeave: () => void;
}

export function ChatView({ messages, userId, sendMessage, onMinimize, onLeave }: Props) {
  const [text, setText] = useState('');
  const listRef = useRef<FlatList>(null);

  function handleSend() {
    const trimmed = text.trim();
    if (!trimmed) return;
    sendMessage(trimmed);
    setText('');
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{STR_CHAT_TITLE}</Text>
        <View style={styles.headerActions}>
          <Pressable onPress={onMinimize} style={styles.iconBtn}>
            <Text style={styles.iconBtnText}>{STR_MINIMIZE}</Text>
          </Pressable>
          <Pressable onPress={onLeave} style={styles.leaveBtn}>
            <Text style={styles.leaveBtnText}>{STR_LEAVE}</Text>
          </Pressable>
        </View>
      </View>

      <FlatList
        ref={listRef}
        data={messages}
        keyExtractor={(item, index) =>
          'id' in item ? item.id : `evt-${index}-${item.timestamp}`
        }
        renderItem={({ item }) => <MessageBubble msg={item} userId={userId} />}
        onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: true })}
        style={styles.list}
        contentContainerStyle={styles.listContent}
      />

      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          value={text}
          onChangeText={setText}
          placeholder={STR_MESSAGE_PLACEHOLDER}
          placeholderTextColor={COLOR_TEXT_SECONDARY}
          onSubmitEditing={handleSend}
          returnKeyType="send"
          blurOnSubmit={false}
        />
        <Pressable
          onPress={handleSend}
          style={[styles.sendBtn, !text.trim() && styles.sendBtnDisabled]}
          disabled={!text.trim()}
        >
          <Text style={styles.sendBtnText}>{STR_SEND_ICON}</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: COLOR_PANEL_BORDER,
  },
  title: { color: COLOR_WHITE, fontWeight: '600', fontSize: 14 },
  headerActions: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  iconBtn: { padding: 4 },
  iconBtnText: { color: COLOR_TEXT_SECONDARY, fontSize: 18, lineHeight: 20 },
  leaveBtn: {
    backgroundColor: COLOR_DANGER_BG,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
  },
  leaveBtnText: { color: COLOR_DANGER, fontSize: 12 },
  list: { flex: 1 },
  listContent: { paddingVertical: 8 },
  inputRow: {
    flexDirection: 'row',
    gap: 6,
    padding: 8,
    borderTopWidth: 1,
    borderTopColor: COLOR_PANEL_BORDER,
  },
  input: {
    flex: 1,
    backgroundColor: COLOR_SURFACE,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 6,
    color: COLOR_WHITE,
    fontSize: 13,
  },
  sendBtn: {
    backgroundColor: COLOR_PRIMARY,
    borderRadius: 8,
    width: 36,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendBtnDisabled: { opacity: 0.4 },
  sendBtnText: { color: COLOR_WHITE, fontSize: 18 },
});
