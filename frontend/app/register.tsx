import { router } from 'expo-router';
import { useState } from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { useAuth } from '@/src/api/AuthContext';

export default function RegisterScreen() {
  const { register, error, clearError } = useAuth();
  const [username, setUsername] = useState('');
  const [name, setName] = useState('');
  const [lastName, setLastName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  async function handleRegister() {
    setLocalError(null);
    clearError();

    if (!username.trim() || !name.trim() || !lastName.trim() || !password) {
      setLocalError('All fields are required');
      return;
    }
    if (password !== confirmPassword) {
      setLocalError('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      await register(username.trim(), name.trim(), lastName.trim(), password);
      // RedirectController in _layout.tsx handles the navigation to /(tabs)/match
    } catch {
      // error displayed via context
    } finally {
      setLoading(false);
    }
  }

  const displayError = localError ?? error;

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        contentContainerStyle={styles.scroll}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.card}>
          <Text style={styles.title}>Create Account</Text>
          <Text style={styles.subtitle}>Join the Bundesliga experience</Text>

          {displayError ? <Text style={styles.errorText}>{displayError}</Text> : null}

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
            placeholder="First name"
            placeholderTextColor="#666"
            autoCapitalize="words"
            value={name}
            onChangeText={setName}
          />
          <TextInput
            style={styles.input}
            placeholder="Last name"
            placeholderTextColor="#666"
            autoCapitalize="words"
            value={lastName}
            onChangeText={setLastName}
          />
          <TextInput
            style={styles.input}
            placeholder="Password"
            placeholderTextColor="#666"
            secureTextEntry
            value={password}
            onChangeText={setPassword}
          />
          <TextInput
            style={styles.input}
            placeholder="Confirm password"
            placeholderTextColor="#666"
            secureTextEntry
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            onSubmitEditing={handleRegister}
            returnKeyType="go"
          />

          <Pressable
            style={[styles.button, loading && styles.buttonDisabled]}
            onPress={handleRegister}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Create Account</Text>
            )}
          </Pressable>

          <Pressable style={styles.linkButton} onPress={() => router.back()}>
            <Text style={styles.linkText}>
              Already have an account? <Text style={styles.linkBold}>Sign In</Text>
            </Text>
          </Pressable>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0d0d0d',
  },
  scroll: {
    flexGrow: 1,
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
