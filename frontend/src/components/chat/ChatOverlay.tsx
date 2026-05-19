import { useRef, useState } from "react";
import {
  Animated,
  PanResponder,
  Pressable,
  StyleSheet,
  Text,
  useWindowDimensions,
  View,
} from "react-native";
import { useApi } from "@/src/api/ApiContext";
import { useChatStream } from "@/src/api/useChatStream";
import { CreateRoomView } from "./CreateRoomView";
import { JoinRoomView } from "./JoinRoomView";
import { ChatView } from "./ChatView";
import {
  COLOR_DRAG_BORDER,
  COLOR_DRAG_PILL,
  COLOR_PANEL_BG,
  COLOR_PANEL_BORDER,
  COLOR_PRIMARY,
  COLOR_SURFACE_SUBTLE,
  COLOR_TEXT_MUTED,
  COLOR_TEXT_SECONDARY,
  COLOR_TOGGLE_BG,
  COLOR_WHITE,
  PANEL_HEIGHT,
  STR_CLOSE,
  STR_CREATE_ROOM,
  STR_JOIN_ROOM,
  STR_TOGGLE_ICON,
  STR_WATCH_PARTY,
} from "./constants";

type Screen = "idle" | "creating" | "joining" | "in_room";

export function ChatOverlay() {
  const { userId } = useApi();
  const { width: windowWidth, height: windowHeight } = useWindowDimensions();
  const [isOpen, setIsOpen] = useState(false);
  const [screen, setScreen] = useState<Screen>("idle");
  const chat = useChatStream();
  const userIdStr = String(userId);

  const panelWidth = windowWidth / 2;
  const maxHeightRef = useRef(windowHeight / 2);
  maxHeightRef.current = windowHeight / 2;

  const heightAnim = useRef(new Animated.Value(PANEL_HEIGHT)).current;
  const startHeightRef = useRef(PANEL_HEIGHT);

  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onPanResponderGrant: () => {
        heightAnim.stopAnimation((value) => {
          startHeightRef.current = value;
        });
      },
      onPanResponderMove: (_, { dy }) => {
        const next = Math.max(
          PANEL_HEIGHT,
          Math.min(maxHeightRef.current, startHeightRef.current + dy),
        );
        heightAnim.setValue(next);
      },
    }),
  ).current;

  function handleCreated(roomId: string, wsToken: string) {
    chat.connect(roomId, wsToken, userIdStr);
    setScreen("in_room");
  }

  function handleJoined(roomId: string, wsToken: string) {
    chat.connect(roomId, wsToken, userIdStr);
    setScreen("in_room");
  }

  function handleLeave() {
    chat.disconnect();
    setScreen("idle");
    setIsOpen(false);
  }

  if (!isOpen) {
    return (
      <Pressable style={styles.toggleBtn} onPress={() => setIsOpen(true)}>
        <Text style={styles.toggleBtnText}>{STR_TOGGLE_ICON}</Text>
      </Pressable>
    );
  }

  return (
    <Animated.View
      style={[styles.panel, { width: panelWidth, height: heightAnim }]}
    >
      <View style={styles.content}>
        {screen === "idle" && (
          <View style={styles.section}>
            <View style={styles.panelHeader}>
              <Text style={styles.panelTitle}>{STR_WATCH_PARTY}</Text>
              <Pressable
                onPress={() => setIsOpen(false)}
                style={styles.closeBtn}
              >
                <Text style={styles.closeBtnText}>{STR_CLOSE}</Text>
              </Pressable>
            </View>
            <Pressable
              style={styles.primaryBtn}
              onPress={() => setScreen("creating")}
            >
              <Text style={styles.primaryBtnText}>{STR_CREATE_ROOM}</Text>
            </Pressable>
            <Pressable
              style={styles.secondaryBtn}
              onPress={() => setScreen("joining")}
            >
              <Text style={styles.secondaryBtnText}>{STR_JOIN_ROOM}</Text>
            </Pressable>
          </View>
        )}

        {screen === "creating" && (
          <CreateRoomView
            userId={userIdStr}
            onCreated={handleCreated}
            onBack={() => setScreen("idle")}
          />
        )}

        {screen === "joining" && (
          <JoinRoomView
            userId={userIdStr}
            onJoined={handleJoined}
            onBack={() => setScreen("idle")}
          />
        )}

        {screen === "in_room" && (
          <ChatView
            messages={chat.messages}
            userId={userIdStr}
            sendMessage={chat.sendMessage}
            onMinimize={() => setIsOpen(false)}
            onLeave={handleLeave}
          />
        )}
      </View>

      <View {...panResponder.panHandlers} style={styles.dragHandle}>
        <View style={styles.dragHandlePill} />
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  toggleBtn: {
    position: "absolute",
    top: 48,
    left: 12,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: COLOR_TOGGLE_BG,
    alignItems: "center",
    justifyContent: "center",
  },
  toggleBtnText: { fontSize: 22 },
  panel: {
    position: "absolute",
    top: 48,
    left: 12,
    backgroundColor: COLOR_PANEL_BG,
    borderRadius: 12,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: COLOR_PANEL_BORDER,
  },
  content: { flex: 1, overflow: "hidden" },
  panelHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  panelTitle: { color: COLOR_WHITE, fontWeight: "700", fontSize: 15 },
  closeBtn: { padding: 4 },
  closeBtnText: { color: COLOR_TEXT_MUTED, fontSize: 14 },
  section: { padding: 14, gap: 10 },
  primaryBtn: {
    backgroundColor: COLOR_PRIMARY,
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: "center",
  },
  primaryBtnText: { color: COLOR_WHITE, fontWeight: "600", fontSize: 14 },
  secondaryBtn: {
    backgroundColor: COLOR_SURFACE_SUBTLE,
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: "center",
  },
  secondaryBtnText: { color: COLOR_TEXT_SECONDARY, fontSize: 14 },
  dragHandle: {
    height: 20,
    alignItems: "center",
    justifyContent: "center",
    borderTopWidth: 1,
    borderTopColor: COLOR_DRAG_BORDER,
  },
  dragHandlePill: {
    width: 32,
    height: 4,
    borderRadius: 2,
    backgroundColor: COLOR_DRAG_PILL,
  },
});
