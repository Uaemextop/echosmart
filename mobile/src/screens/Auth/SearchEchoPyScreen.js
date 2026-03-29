import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from 'react-native';

export default function SearchEchoPyScreen({ navigation, route }) {
  const { serialCode } = route.params || {};
  const [searching, setSearching] = useState(true);
  const [devices, setDevices] = useState([]);

  useEffect(() => {
    // Simular búsqueda BLE/WiFi de dispositivos EchoPy
    const timer = setTimeout(() => {
      setSearching(false);
      // TODO: Implementar BLE scan y mDNS discovery
      setDevices([
        { id: '1', name: 'echopy-a1b2c3', type: 'bluetooth', signal: -45 },
        { id: '2', name: 'echopy-d4e5f6', type: 'wifi', signal: -60 },
      ]);
    }, 3000);
    return () => clearTimeout(timer);
  }, []);

  const selectDevice = (device) => {
    navigation.navigate('PairEchoPy', { serialCode, device });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🔍 Buscar EchoPy</Text>

      {/* Progress indicator */}
      <View style={styles.progressContainer}>
        {[1, 2, 3, 4, 5].map((s) => (
          <View key={s} style={[styles.progressDot, s <= 3 && styles.progressDotActive]} />
        ))}
      </View>
      <Text style={styles.stepLabel}>Paso 3: Buscar tu EchoPy</Text>

      <Text style={styles.instructions}>
        Asegúrate de que tu EchoPy esté encendido y cerca de tu teléfono.
        Buscando vía Bluetooth y WiFi...
      </Text>

      {searching ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2E7D32" />
          <Text style={styles.loadingText}>Buscando dispositivos EchoPy...</Text>
        </View>
      ) : (
        <>
          {devices.length > 0 ? (
            <FlatList
              data={devices}
              keyExtractor={(item) => item.id}
              renderItem={({ item }) => (
                <TouchableOpacity style={styles.deviceCard} onPress={() => selectDevice(item)}>
                  <Text style={styles.deviceName}>{item.name}</Text>
                  <Text style={styles.deviceType}>
                    {item.type === 'bluetooth' ? '📶 Bluetooth' : '📡 WiFi'}
                  </Text>
                  <Text style={styles.deviceSignal}>Señal: {item.signal} dBm</Text>
                </TouchableOpacity>
              )}
            />
          ) : (
            <Text style={styles.noDevices}>No se encontraron dispositivos EchoPy</Text>
          )}

          <TouchableOpacity
            style={styles.retryButton}
            onPress={() => {
              setSearching(true);
              // Reintentar búsqueda
              setTimeout(() => setSearching(false), 3000);
            }}
          >
            <Text style={styles.retryText}>Buscar de nuevo</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, paddingHorizontal: 24, paddingTop: 60, backgroundColor: '#fff' },
  title: { fontSize: 28, fontWeight: 'bold', color: '#2E7D32', textAlign: 'center', marginBottom: 12 },
  progressContainer: { flexDirection: 'row', justifyContent: 'center', marginBottom: 8 },
  progressDot: { width: 12, height: 12, borderRadius: 6, backgroundColor: '#ddd', marginHorizontal: 4 },
  progressDotActive: { backgroundColor: '#2E7D32' },
  stepLabel: { fontSize: 14, color: '#666', textAlign: 'center', marginBottom: 16 },
  instructions: { fontSize: 13, color: '#888', textAlign: 'center', marginBottom: 24 },
  loadingContainer: { alignItems: 'center', marginTop: 40 },
  loadingText: { fontSize: 14, color: '#666', marginTop: 16 },
  deviceCard: {
    backgroundColor: '#f9f9f9', borderRadius: 12, padding: 16, marginBottom: 12,
    borderWidth: 1, borderColor: '#e0e0e0',
  },
  deviceName: { fontSize: 18, fontWeight: 'bold', color: '#333' },
  deviceType: { fontSize: 14, color: '#666', marginTop: 4 },
  deviceSignal: { fontSize: 12, color: '#999', marginTop: 2 },
  noDevices: { fontSize: 14, color: '#999', textAlign: 'center', marginTop: 40 },
  retryButton: {
    borderWidth: 1, borderColor: '#2E7D32', borderRadius: 8, padding: 14,
    alignItems: 'center', marginTop: 16,
  },
  retryText: { color: '#2E7D32', fontSize: 14, fontWeight: 'bold' },
});
