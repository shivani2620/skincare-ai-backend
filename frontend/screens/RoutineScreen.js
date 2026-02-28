import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import axios from 'axios';
import { Ionicons } from '@expo/vector-icons';

const API_URL = process.env.EXPO_PUBLIC_API_URL;

export default function RoutineScreen({ route }) {
  const [loading, setLoading] = useState(false);
  const [routine, setRoutine] = useState(null);
  const [selectedBudget, setSelectedBudget] = useState('mid-range');

  const userId = route.params?.userId || 'demo-user';

  const budgetOptions = [
    { value: 'budget', label: 'Budget', icon: 'wallet-outline' },
    { value: 'mid-range', label: 'Mid-Range', icon: 'card-outline' },
    { value: 'premium', label: 'Premium', icon: 'diamond-outline' },
  ];

  const generateRoutine = async () => {
    setLoading(true);
    setRoutine(null);

    try {
      const response = await axios.post(
        `${API_URL}/api/routine/generate?user_id=${userId}&budget=${selectedBudget}`
      );
      setRoutine(response.data);
    } catch (error) {
      alert('Failed to generate routine. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderStep = (step, index) => (
    <View key={index} style={styles.stepCard}>
      <View style={styles.stepHeader}>
        <Text style={styles.stepNumber}>{step.step}</Text>
        <View style={styles.stepInfo}>
          <Text style={styles.stepType}>{step.product_type}</Text>
          <Text style={styles.stepProduct}>{step.recommendation}</Text>
        </View>
      </View>
      <Text style={styles.stepWhy}>{step.why}</Text>
      <Text style={styles.stepPrice}>{step.price}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>📋 My Routine</Text>
      </View>

      <ScrollView style={styles.content}>
        <Text style={styles.sectionTitle}>Choose Your Budget</Text>
        
        <View style={styles.budgetContainer}>
          {budgetOptions.map((option) => (
            <TouchableOpacity
              key={option.value}
              style={[
                styles.budgetOption,
                selectedBudget === option.value && styles.budgetOptionActive,
              ]}
              onPress={() => setSelectedBudget(option.value)}
            >
              <Ionicons
                name={option.icon}
                size={24}
                color={selectedBudget === option.value ? '#FF6B9D' : '#999'}
              />
              <Text
                style={[
                  styles.budgetLabel,
                  selectedBudget === option.value && styles.budgetLabelActive,
                ]}
              >
                {option.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <TouchableOpacity
          style={[styles.generateButton, loading && styles.buttonDisabled]}
          onPress={generateRoutine}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Ionicons name="sparkles" size={20} color="#fff" />
              <Text style={styles.generateButtonText}>Generate AI Routine</Text>
            </>
          )}
        </TouchableOpacity>

        {routine && !routine.error && (
          <View style={styles.routineContainer}>
            <View style={styles.routineHeader}>
              <Text style={styles.routineTitle}>Your Personalized Routine</Text>
              {routine.total_monthly_cost && (
                <Text style={styles.monthlyCost}>
                  💰 {routine.total_monthly_cost}/month
                </Text>
              )}
            </View>

            {/* Morning Routine */}
            {routine.morning && (
              <View style={styles.timeSection}>
                <View style={styles.timeSectionHeader}>
                  <Ionicons name="sunny" size={24} color="#FFB74D" />
                  <Text style={styles.timeSectionTitle}>Morning Routine</Text>
                </View>
                {routine.morning.map((step, idx) => renderStep(step, idx))}
              </View>
            )}

            {/* Night Routine */}
            {routine.night && (
              <View style={styles.timeSection}>
                <View style={styles.timeSectionHeader}>
                  <Ionicons name="moon" size={24} color="#7E57C2" />
                  <Text style={styles.timeSectionTitle}>Night Routine</Text>
                </View>
                {routine.night.map((step, idx) => renderStep(step, idx))}
              </View>
            )}

            {/* Weekly Treatments */}
            {routine.weekly && (
              <View style={styles.timeSection}>
                <View style={styles.timeSectionHeader}>
                  <Ionicons name="calendar" size={24} color="#FF6B9D" />
                  <Text style={styles.timeSectionTitle}>Weekly Treatments</Text>
                </View>
                {routine.weekly.map((step, idx) => renderStep(step, idx))}
              </View>
            )}

            {/* Expected Results */}
            {routine.expected_results && (
              <View style={styles.resultsBox}>
                <Ionicons name="trending-up" size={20} color="#4CAF50" />
                <Text style={styles.resultsText}>{routine.expected_results}</Text>
              </View>
            )}

            {/* Tips */}
            {routine.tips && routine.tips.length > 0 && (
              <View style={styles.tipsSection}>
                <Text style={styles.tipsTitle}>💡 Pro Tips</Text>
                {routine.tips.map((tip, idx) => (
                  <Text key={idx} style={styles.tipItem}>
                    • {tip}
                  </Text>
                ))}
              </View>
            )}
          </View>
        )}

        {routine && routine.error && (
          <View style={styles.errorBox}>
            <Text style={styles.errorText}>
              Failed to generate routine. Please try again.
            </Text>
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F7F9FC',
  },
  header: {
    backgroundColor: '#FF6B9D',
    paddingTop: 50,
    paddingBottom: 15,
    paddingHorizontal: 20,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  budgetContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  budgetOption: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 12,
    alignItems: 'center',
    marginHorizontal: 5,
    borderWidth: 2,
    borderColor: '#E0E0E0',
  },
  budgetOptionActive: {
    borderColor: '#FF6B9D',
    backgroundColor: '#FFF0F5',
  },
  budgetLabel: {
    marginTop: 8,
    fontSize: 14,
    color: '#999',
    fontWeight: '600',
  },
  budgetLabelActive: {
    color: '#FF6B9D',
  },
  generateButton: {
    backgroundColor: '#FF6B9D',
    paddingVertical: 18,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  generateButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  routineContainer: {
    marginTop: 25,
  },
  routineHeader: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 16,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  routineTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  monthlyCost: {
    fontSize: 16,
    color: '#FF6B9D',
    fontWeight: '600',
  },
  timeSection: {
    marginBottom: 25,
  },
  timeSectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  timeSectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginLeft: 10,
  },
  stepCard: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 12,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  stepHeader: {
    flexDirection: 'row',
    marginBottom: 10,
  },
  stepNumber: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#FF6B9D',
    color: '#fff',
    textAlign: 'center',
    lineHeight: 30,
    fontWeight: 'bold',
    fontSize: 16,
  },
  stepInfo: {
    flex: 1,
    marginLeft: 12,
  },
  stepType: {
    fontSize: 14,
    color: '#999',
    marginBottom: 2,
  },
  stepProduct: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  stepWhy: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 8,
  },
  stepPrice: {
    fontSize: 14,
    color: '#FF6B9D',
    fontWeight: '600',
  },
  resultsBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E8F5E9',
    padding: 15,
    borderRadius: 12,
    marginTop: 10,
  },
  resultsText: {
    flex: 1,
    marginLeft: 10,
    fontSize: 15,
    color: '#2E7D32',
    fontWeight: '600',
  },
  tipsSection: {
    backgroundColor: '#FFF9E6',
    padding: 15,
    borderRadius: 12,
    marginTop: 15,
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#F57C00',
    marginBottom: 10,
  },
  tipItem: {
    fontSize: 14,
    color: '#666',
    marginBottom: 6,
    lineHeight: 20,
  },
  errorBox: {
    backgroundColor: '#FFEBEE',
    padding: 20,
    borderRadius: 12,
    marginTop: 20,
  },
  errorText: {
    color: '#C62828',
    textAlign: 'center',
    fontSize: 16,
  },
});