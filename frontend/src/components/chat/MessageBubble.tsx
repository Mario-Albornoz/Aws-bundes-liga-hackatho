import { StyleSheet, Text, View } from "react-native";
import type { IncomingWsMessage } from "@/src/api/types/chat";
import {
  COLOR_BUBBLE_OTHER,
  COLOR_BUBBLE_OWN,
  COLOR_MSG_TIME,
  COLOR_TEXT_MUTED,
  COLOR_TEXT_SECONDARY,
  COLOR_WHITE,
  STR_USER_JOINED,
  STR_USER_LEFT,
} from "./constants";

interface Props {
  msg: IncomingWsMessage;
  userId: string;
}

export function MessageBubble({ msg, userId }: Props) {
  if ("type" in msg) {
    const label =
      msg.type === "user_joined"
        ? STR_USER_JOINED(msg.user_id)
        : STR_USER_LEFT(msg.user_id);
    return (
      <View style={styles.systemRow}>
        <Text style={styles.systemText}>{label}</Text>
      </View>
    );
  }

  const isOwn = msg.sender_id === userId;
  return (
    <View style={[styles.row, isOwn ? styles.rowOwn : styles.rowOther]}>
      {!isOwn && <Text style={styles.sender}>{msg.sender_id}</Text>}
      <View
        style={[styles.bubble, isOwn ? styles.bubbleOwn : styles.bubbleOther]}
      >
        <Text style={styles.content}>{msg.content}</Text>
        <Text style={styles.time}>
          {new Date(msg.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  systemRow: { alignItems: "center", marginVertical: 4 },
  systemText: { color: COLOR_TEXT_MUTED, fontSize: 11 },
  row: { marginVertical: 2, paddingHorizontal: 8 },
  rowOwn: { alignItems: "flex-end" },
  rowOther: { alignItems: "flex-start" },
  sender: { color: COLOR_TEXT_SECONDARY, fontSize: 10, marginBottom: 2 },
  bubble: {
    maxWidth: "85%",
    borderRadius: 12,
    paddingHorizontal: 10,
    paddingVertical: 6,
  },
  bubbleOwn: { backgroundColor: COLOR_BUBBLE_OWN },
  bubbleOther: { backgroundColor: COLOR_BUBBLE_OTHER },
  content: { color: COLOR_WHITE, fontSize: 13 },
  time: {
    color: COLOR_MSG_TIME,
    fontSize: 10,
    marginTop: 2,
    textAlign: "right",
  },
});
