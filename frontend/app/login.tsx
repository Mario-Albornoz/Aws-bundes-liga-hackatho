import { router } from 'expo-router';
import { useState } from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { useAuth } from '@/src/api/AuthContext';

export default function LoginScreen() {
  const { login, error, clearError } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    if (!username.trim() || !password) return;
    clearError();
    setLoading(true);
    try {
      await login(username.trim(), password);
      // RedirectController in _layout.tsx handles the navigation to /(tabs)/match
    } catch {
      // error displayed via context
    } finally {
      setLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.card}>
        <Text style={styles.title}>Bundesliga Live</Text>
        <Text style={styles.subtitle}>Sign in to continue</Text>

        {error ? <Text style={styles.errorText}>{error}</Text> : null}

        <TextInput
          style={styles.input}
          placeholder="Username"
          placeholderTextColor="#666"
          autoCapitalize="none"
          autoCorrect={false}
          value={username}
          onChangeText={setUsername}
        />
        <TextInput
          style={styles.input}
          placeholder="Password"
          placeholderTextColor="#666"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
          onSubmitEditing={handleLogin}
          returnKeyType="go"
        />

        <Pressable
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={handleLogin}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Sign In</Text>
          )}
        </Pressable>

        <Pressable style={styles.linkButton} onPress={() => router.push('/register')}>
          <Text style={styles.linkText}>
            Don't have an account? <Text style={styles.linkBold}>Register</Text>
          </Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0d0d0d',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  card: {
    width: '100%',
    maxWidth: 380,
    backgroundColor: '#1a1a1a',
    borderRadius: 16,
    padding: 28,
    gap: 14,
  },
  title: {
    fontSize: 26,
    fontWeight: '700',
    color: '#e8131d',
    textAlign: 'center',
    marginBottom: 2,
  },
  subtitle: {
    fontSize: 14,
    color: '#fff',
    textAlign: 'center',
    marginBottom: 8,
  },
  errorText: {
    color: '#ff6b6b',
    fontSize: 13,
    textAlign: 'center',
    backgroundColor: '#2a1010',
    padding: 10,
    borderRadius: 8,
  },
  input: {
    backgroundColor: '#262626',
    borderRadius: 10,
    paddingHorizontal: 16,
    paddingVertical: 13,
    color: '#fff',
    fontSize: 15,
    borderWidth: 1,
    borderColor: '#333',
  },
  button: {
    backgroundColor: '#e8131d',
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 4,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  linkButton: {
    alignItems: 'center',
    paddingTop: 4,
  },
  linkText: {
    color: '#fff',
    fontSize: 14,
  },
  linkBold: {
    color: '#e8131d',
    fontWeight: '600',
  },
});
