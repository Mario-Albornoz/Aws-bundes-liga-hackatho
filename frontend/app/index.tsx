import { ActivityIndicator, StyleSheet, View } from 'react-native';

/**
 * Briefly visible while AuthProvider resolves the stored refresh token.
 * Navigation away from this screen is handled by RedirectController in _layout.tsx.
 */
export default function Index() {
  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#ffffff" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0d0d0d',
    justifyContent: 'center',
    alignItems: 'center',
  },
});
