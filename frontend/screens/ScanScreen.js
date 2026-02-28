import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import axios from 'axios';
import { Ionicons } from '@expo/vector-icons';
import { Camera } from 'expo-camera';
import { BarCodeScanner } from 'expo-barcode-scanner';

const API_URL = " https://skincare-ai-backend-8klh.onrender.com";

export default function ScanScreen({ route }) {
  const [barcode, setBarcode] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  // Camera scanner states
  const [hasPermission, setHasPermission] = useState(null);
  const [scanning, setScanning] = useState(false);

  const userId = route.params?.userId || 'demo-user';

  // Request camera permissions
  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  // Scan product via backend
  const scanProduct = async () => {
    if (!barcode.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(`${API_URL}/api/products/scan`, {
        barcode: barcode.trim(),
        user_id: userId,
      });
      setResult(response.data);
    } catch (error) {
      alert('Scan failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Camera barcode scanned handler
  const handleBarCodeScanned = ({ data }) => {
    setScanning(false);
    setBarcode(data);
    scanProduct();
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🔍 Scan Product</Text>
      </View>

      <View style={styles.content}>
        {/* Camera Scanner */}
        {scanning && hasPermission ? (
          <View style={{ flex: 1 }}>
            <Camera
              style={styles.camera}
              onBarCodeScanned={handleBarCodeScanned}
              barCodeScannerSettings={{
                barCodeTypes: [BarCodeScanner.Constants.BarCodeType.ean13],
              }}
            />
            <TouchableOpacity
              style={styles.cancelButton}
              onPress={() => setScanning(false)}
            >
              <Text style={styles.cancelButtonText}>✖ Cancel</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <>
            {/* Manual input + Scan button */}
            <View style={styles.scanBox}>
              <Ionicons name="scan-outline" size={80} color="#FF6B9D" />
              <Text style={styles.scanText}>Enter barcode manually</Text>
              <Text style={styles.scanSubtext}>(or scan with camera!)</Text>
            </View>

            <TextInput
              style={styles.input}
              placeholder="Enter barcode number"
              value={barcode}
              onChangeText={setBarcode}
              keyboardType="numeric"
            />

            {hasPermission && (
              <TouchableOpacity
                style={styles.button}
                onPress={() => setScanning(true)}
              >
                <Text style={styles.buttonText}>Scan with Camera</Text>
              </TouchableOpacity>
            )}

            <TouchableOpacity
              style={[styles.button, loading && styles.buttonDisabled]}
              onPress={scanProduct}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>Analyze Product</Text>
              )}
            </TouchableOpacity>

            {/* Results */}
            {result && (
              <ScrollView style={styles.resultContainer}>
                <View style={styles.productCard}>
                  <Text style={styles.productName}>{result.product.name}</Text>
                  <Text style={styles.productBrand}>{result.product.brand}</Text>

                  <View style={styles.scoreContainer}>
                    <Text style={styles.scoreLabel}>AI Score</Text>
                    <Text style={styles.scoreValue}>
                      {result.analysis.overall_score}/100
                    </Text>
                  </View>

                  <View
                    style={[
                      styles.recommendationBadge,
                      result.analysis.recommendation === 'recommended' &&
                        styles.recommendedBadge,
                      result.analysis.recommendation === 'not_recommended' &&
                        styles.notRecommendedBadge,
                    ]}
                  >
                    <Text style={styles.recommendationText}>
                      {result.analysis.recommendation.toUpperCase()}
                    </Text>
                  </View>

                  {result.analysis.warnings.length > 0 && (
                    <View style={styles.section}>
                      <Text style={styles.sectionTitle}>⚠️ Warnings</Text>
                      {result.analysis.warnings.map((warning, idx) => (
                        <Text key={idx} style={styles.listItem}>
                          • {warning}
                        </Text>
                      ))}
                    </View>
                  )}

                  {result.analysis.benefits.length > 0 && (
                    <View style={styles.section}>
                      <Text style={styles.sectionTitle}>✅ Benefits</Text>
                      {result.analysis.benefits.map((benefit, idx) => (
                        <Text key={idx} style={styles.listItem}>
                          • {benefit}
                        </Text>
                      ))}
                    </View>
                  )}

                  {result.alternatives && result.alternatives.length > 0 && (
                    <View style={styles.section}>
                      <Text style={styles.sectionTitle}>💡 Better Alternatives</Text>
                      {result.alternatives.map((alt, idx) => (
                        <View key={idx} style={styles.alternativeCard}>
                          <Text style={styles.altName}>{alt.name}</Text>
                          <Text style={styles.altBrand}>{alt.brand}</Text>
                          <Text style={styles.altReason}>{alt.why_better}</Text>
                          <Text style={styles.altPrice}>{alt.price_range}</Text>
                        </View>
                      ))}
                    </View>
                  )}
                </View>
              </ScrollView>
            )}
          </>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F7F9FC' },
  header: { backgroundColor: '#FF6B9D', paddingTop: 50, paddingBottom: 15, paddingHorizontal: 20 },
  headerTitle: { fontSize: 24, fontWeight: 'bold', color: '#fff' },
  content: { flex: 1, padding: 20 },
  scanBox: { alignItems: 'center', paddingVertical: 40 },
  scanText: { fontSize: 18, fontWeight: '600', color: '#333', marginTop: 15 },
  scanSubtext: { fontSize: 14, color: '#999', marginTop: 5 },
  input: { backgroundColor: '#fff', borderWidth: 1, borderColor: '#E0E0E0', borderRadius: 12, padding: 15, fontSize: 16, marginBottom: 15 },
  button: { backgroundColor: '#FF6B9D', paddingVertical: 18, borderRadius: 12, alignItems: 'center', marginBottom: 10 },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  resultContainer: { marginTop: 20 },
  productCard: { backgroundColor: '#fff', borderRadius: 16, padding: 20, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 8, elevation: 4 },
  productName: { fontSize: 22, fontWeight: 'bold', color: '#333', marginBottom: 5 },
  productBrand: { fontSize: 16, color: '#999', marginBottom: 15 },
  scoreContainer: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#F7F9FC', padding: 15, borderRadius: 12, marginBottom: 15 },
  scoreLabel: { fontSize: 16, color: '#666' },
  scoreValue: { fontSize: 28, fontWeight: 'bold', color: '#FF6B9D' },
  recommendationBadge: { paddingVertical: 10, paddingHorizontal: 20, borderRadius: 20, alignItems: 'center', marginBottom: 20 },
  recommendedBadge: { backgroundColor: '#4CAF50' },
  notRecommendedBadge: { backgroundColor: '#FF5252' },
  recommendationText: { color: '#fff', fontWeight: 'bold', fontSize: 14 },
  section: { marginTop: 20 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#333', marginBottom: 10 },
  listItem: { fontSize: 15, color: '#666', marginBottom: 8, lineHeight: 22 },
  alternativeCard: { backgroundColor: '#F7F9FC', padding: 15, borderRadius: 12, marginBottom: 10 },
  altName: { fontSize: 16, fontWeight: 'bold', color: '#333' },
  altBrand: { fontSize: 14, color: '#999', marginBottom: 5 },
  altReason: { fontSize: 14, color: '#666', marginBottom: 5 },
  altPrice: { fontSize: 14, color: '#FF6B9D', fontWeight: '600' },
  camera: { flex: 1, borderRadius: 12, marginBottom: 15 },
  cancelButton: {
    position: 'absolute',
    top: 50,
    right: 20,
    backgroundColor: 'rgba(0,0,0,0.6)',
    paddingVertical: 8,
    paddingHorizontal: 15,
    borderRadius: 20,
  },
  cancelButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});