import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import axios from 'axios';

const API_URL = process.env.EXPO_PUBLIC_API_URL; // Change this for production

export default function ProfileSetupScreen({ navigation, setUserId }) {
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [workLocation, setWorkLocation] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const createProfile = async () => {
    if (!name || !age || !workLocation || !description) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_URL}/api/users/create-from-description`, {
        name,
        age: parseInt(age),
        work_location: workLocation,
        description,
      });

      setUserId(response.data.user_id);
      navigation.navigate("Profile", {
  userId: response.data.user_id,
});
      
      // Navigate to main app
      navigation.navigate('Main');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>🌸 Tell me about yourself</Text>
        <Text style={styles.subtitle}>
          I'll use AI to understand your skin and create a personalized profile
        </Text>

        <TextInput
          style={styles.input}
          placeholder="Your Name"
          value={name}
          onChangeText={setName}
        />

        <TextInput
          style={styles.input}
          placeholder="Age"
          value={age}
          onChangeText={setAge}
          keyboardType="numeric"
        />

        <TextInput
         style={styles.input}
         placeholder="Work Location"
         value={workLocation}
         onChangeText={setWorkLocation}
        />

        <TextInput
          style={[styles.input, styles.textArea]}
          placeholder="Describe your skin in your own words...
          
Example: My skin gets oily by afternoon, especially on my forehead and nose. I struggle with occasional breakouts around my chin. I've tried many products but they either dry out my skin or don't help with the oiliness."
          value={description}
          onChangeText={setDescription}
          multiline
          numberOfLines={8}
        />

        {error ? <Text style={styles.error}>{error}</Text> : null}

        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={createProfile}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Create My Profile ✨</Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F7F9FC',
  },
  scrollContent: {
    padding: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 30,
    lineHeight: 22,
  },
  input: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 12,
    padding: 15,
    fontSize: 16,
    marginBottom: 15,
  },
  textArea: {
    height: 150,
    textAlignVertical: 'top',
  },
  button: {
    backgroundColor: '#FF6B9D',
    paddingVertical: 18,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 20,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  error: {
    color: '#FF3B30',
    textAlign: 'center',
    marginTop: 10,
  },
});