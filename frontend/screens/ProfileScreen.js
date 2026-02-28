import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  TextInput,
  Modal,
} from 'react-native';
import axios from 'axios';
import { Ionicons } from '@expo/vector-icons';

const API_URL = process.env.EXPO_PUBLIC_API_URL;

export default function ProfileScreen({ route }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editName, setEditName] = useState('');
  const [editAge, setEditAge] = useState('');
  const [editWorkLocation, setEditWorkLocation] = useState('');

  const userId = route.params?.userId;

if (!userId) {
  return <Text>No user found</Text>;
}

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/users/${userId}`);
      setProfile(response.data);
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const openEditModal = () => {
    setEditName(profile.name || '');
    setEditAge(profile.age?.toString() || '');
    setEditWorkLocation(profile.work_location || '');
    setModalVisible(true);
  };

  const saveProfile = async () => {
    try {
      const payload = {
        name: editName,
        age: parseInt(editAge),
        description: 'Updated via app',
        work_location: editWorkLocation,
      };
      const response = await axios.put(`${API_URL}/api/users/${userId}`, payload);
      setProfile(response.data.profile);
      setModalVisible(false);
    } catch (error) {
      console.error('Failed to update profile:', error);
      alert('Error updating profile');
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FF6B9D" />
      </View>
    );
  }

  if (!profile) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Failed to load profile</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadProfile}>
          <Text style={styles.retryText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>👤 My Profile</Text>
      </View>

      <ScrollView style={styles.content}>
        {/* Profile Card */}
        <View style={styles.profileCard}>
          <View style={styles.avatarContainer}>
            <Text style={styles.avatar}>
              {profile.name?.charAt(0).toUpperCase() || "U"}
            </Text>
          </View>
          <Text style={styles.name}>{profile.name}</Text>
          <Text style={styles.age}>{profile.age} years old</Text>
          {profile.work_location && (
            <Text style={styles.workLocation}>🏢 {profile.work_location}</Text>
          )}
        </View>

        {/* Skin Info */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🌸 Skin Profile</Text>
          <View style={styles.infoRow}>
            <View style={styles.infoCard}>
              <Ionicons name="water" size={24} color="#FF6B9D" />
              <Text style={styles.infoLabel}>Skin Type</Text>
              <Text style={styles.infoValue}>{profile.skin_type}</Text>
            </View>
            <View style={styles.infoCard}>
              <Ionicons name="sunny" size={24} color="#FF6B9D" />
              <Text style={styles.infoLabel}>Climate</Text>
              <Text style={styles.infoValue}>{profile.climate}</Text>
            </View>
          </View>
        </View>

        {/* Skin Concerns */}
        {profile.concerns?.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🎯 Skin Concerns</Text>
            <View style={styles.tagContainer}>
              {profile.concerns.map((concern, idx) => (
                <View key={idx} style={styles.tag}>
                  <Text style={styles.tagText}>{concern}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Allergies */}
        {profile.allergies?.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>⚠️ Allergies</Text>
            <View style={styles.tagContainer}>
              {profile.allergies.map((allergy, idx) => (
                <View key={idx} style={[styles.tag, styles.allergyTag]}>
                  <Text style={[styles.tagText, styles.allergyText]}>
                    {allergy}
                  </Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Actions */}
        <View style={styles.section}>
          <TouchableOpacity style={styles.actionButton} onPress={openEditModal}>
            <Ionicons name="settings-outline" size={20} color="#666" />
            <Text style={styles.actionText}>Edit Profile</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* Edit Modal */}
      <Modal visible={modalVisible} animationType="slide" transparent={true}>
        <View style={styles.modalBackground}>
          <View style={styles.modalContainer}>
            <Text style={styles.modalTitle}>Edit Profile</Text>

            <TextInput
              style={styles.input}
              placeholder="Name"
              value={editName}
              onChangeText={setEditName}
            />
            <TextInput
              style={styles.input}
              placeholder="Age"
              value={editAge}
              onChangeText={setEditAge}
              keyboardType="number-pad"
            />
            <TextInput
              style={styles.input}
              placeholder="Work Location"
              value={editWorkLocation}
              onChangeText={setEditWorkLocation}
            />

            <TouchableOpacity style={styles.saveButton} onPress={saveProfile}>
              <Text style={styles.saveButtonText}>Save</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.cancelButton} onPress={() => setModalVisible(false)}>
              <Text style={styles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F7F9FC' },
  header: { backgroundColor: '#FF6B9D', paddingTop: 50, paddingBottom: 15, paddingHorizontal: 20 },
  headerTitle: { fontSize: 24, fontWeight: 'bold', color: '#fff' },
  content: { flex: 1, padding: 20 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F7F9FC' },
  errorContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F7F9FC', padding: 20 },
  errorText: { fontSize: 18, color: '#666', marginBottom: 20 },
  retryButton: { backgroundColor: '#FF6B9D', paddingHorizontal: 30, paddingVertical: 12, borderRadius: 20 },
  retryText: { color: '#fff', fontWeight: 'bold' },
  profileCard: { backgroundColor: '#fff', borderRadius: 16, padding: 25, alignItems: 'center', marginBottom: 20, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 8, elevation: 4 },
  avatarContainer: { width: 80, height: 80, borderRadius: 40, backgroundColor: '#FF6B9D', justifyContent: 'center', alignItems: 'center', marginBottom: 15 },
  avatar: { fontSize: 36, fontWeight: 'bold', color: '#fff' },
  name: { fontSize: 24, fontWeight: 'bold', color: '#333', marginBottom: 5 },
  age: { fontSize: 16, color: '#999' },
  workLocation: { fontSize: 16, color: '#555', marginTop: 5, textTransform: 'capitalize' },
  section: { marginBottom: 25 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#333', marginBottom: 15 },
  infoRow: { flexDirection: 'row', justifyContent: 'space-between' },
  infoCard: { flex: 1, backgroundColor: '#fff', borderRadius: 12, padding: 15, alignItems: 'center', marginHorizontal: 5 },
  infoLabel: { fontSize: 12, color: '#999', marginTop: 8, marginBottom: 4 },
  infoValue: { fontSize: 16, fontWeight: 'bold', color: '#333', textTransform: 'capitalize' },
  tagContainer: { flexDirection: 'row', flexWrap: 'wrap' },
  tag: { backgroundColor: '#E3F2FD', paddingHorizontal: 15, paddingVertical: 8, borderRadius: 20, marginRight: 8, marginBottom: 8 },
  tagText: { color: '#1976D2', fontSize: 14, fontWeight: '600' },
  allergyTag: { backgroundColor: '#FFEBEE' },
  allergyText: { color: '#C62828' },
  actionButton: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', padding: 18, borderRadius: 12, marginBottom: 10 },
  actionText: { marginLeft: 15, fontSize: 16, color: '#333', fontWeight: '500' },
  modalBackground: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.4)' },
  modalContainer: { width: '85%', backgroundColor: '#fff', borderRadius: 16, padding: 20 },
  modalTitle: { fontSize: 20, fontWeight: 'bold', marginBottom: 15, textAlign: 'center' },
  input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 12, padding: 12, marginBottom: 15 },
  saveButton: { backgroundColor: '#FF6B9D', padding: 15, borderRadius: 12, alignItems: 'center', marginBottom: 10 },
  saveButtonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  cancelButton: { padding: 15, borderRadius: 12, alignItems: 'center', borderWidth: 1, borderColor: '#FF6B9D' },
  cancelButtonText: { color: '#FF6B9D', fontWeight: 'bold', fontSize: 16 },
});