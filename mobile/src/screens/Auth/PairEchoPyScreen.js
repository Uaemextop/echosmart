import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from 'react-native';

export default function PairEchoPyScreen({ navigation, route }) {
  const { serialCode, device } = route.params || {};
  const [pairing, setPairing] = useState(false);
  const [paired, setPaired] = useState(false);
  const [wifiSsid, setWifiSsid] = useState('');
  const [wifiPassword, setWifiPassword] = useState('');
  const [step, setStep] = useState('pair'); // pair, wifi, done

  const handlePair = async () => {
    setPairing(true);
    // TODO: Vincular EchoPy via POST /api/v1/echopy/bind
    setTimeout(() => {
      setPairing(false);
      setPaired(true);
      setStep('wifi');
    }, 2000);
  };

  const handleConfigureWifi = async () => {
    if (!wifiSsid) {
      Alert.alert('Error', 'Ingresa el nombre de tu red WiFi');
      return;
    }
    // TODO: Enviar configuración WiFi al EchoPy via BLE/WiFi directo
    setStep('done');
  };

  const handleFinish = () => {
    navigation.reset({ index: 0, routes: [{ name: 'Main' }] });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🔗 Vincular EchoPy</Text>

      {/* Progress indicator */}
      <View style={styles.progressContainer}>
        {[1, 2, 3, 4, 5].map((s) => (
          <View
            key={s}
            style={[
              styles.progressDot,
              s <= (step === 'pair' ? 4 : step === 'wifi' ? 5 : 5) && styles.progressDotActive,
            ]}
          />
        ))}
      </View>

      {step === 'pair' && (
        <>
          <Text style={styles.stepLabel}>Paso 4: Vincular tu EchoPy</Text>
          <View style={styles.deviceInfo}>
            <Text style={styles.deviceName}>📟 {device?.name || 'EchoPy'}</Text>
            <Text style={styles.serialText}>Serial: {serialCode}</Text>
          </View>

          <Text style={styles.instructions}>
            Se vinculará permanentemente este EchoPy con tu número de serie y tu cuenta.
          </Text>

          {pairing ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#2E7D32" />
              <Text style={styles.loadingText}>Vinculando EchoPy...</Text>
            </View>
          ) : (
            <TouchableOpacity style={styles.button} onPress={handlePair}>
              <Text style={styles.buttonText}>Vincular EchoPy</Text>
            </TouchableOpacity>
          )}
        </>
      )}

      {step === 'wifi' && (
        <>
          <Text style={styles.stepLabel}>Paso 5: Configurar WiFi</Text>
          <Text style={styles.successText}>✅ EchoPy vinculado exitosamente</Text>

          <Text style={styles.instructions}>
            Configura la red WiFi para que tu EchoPy se conecte al servidor.
          </Text>

          <TextInput
            style={styles.input}
            placeholder="Nombre de red WiFi (SSID)"
            value={wifiSsid}
            onChangeText={setWifiSsid}
          />
          <TextInput
            style={styles.input}
            placeholder="Contraseña WiFi"
            value={wifiPassword}
            onChangeText={setWifiPassword}
            secureTextEntry
          />

          <TouchableOpacity style={styles.button} onPress={handleConfigureWifi}>
            <Text style={styles.buttonText}>Configurar WiFi</Text>
          </TouchableOpacity>
        </>
      )}

      {step === 'done' && (
        <>
          <View style={styles.doneContainer}>
            <Text style={styles.doneEmoji}>🎉</Text>
            <Text style={styles.doneTitle}>¡Todo listo!</Text>
            <Text style={styles.doneText}>
              Tu EchoPy está configurado y conectándose al servidor.
              Podrás ver los datos de tus sensores en unos minutos.
            </Text>
          </View>

          <TouchableOpacity style={styles.button} onPress={handleFinish}>
            <Text style={styles.buttonText}>Ir al Dashboard</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, paddingHorizontal: 32, paddingTop: 60, backgroundColor: '#fff' },
  title: { fontSize: 28, fontWeight: 'bold', color: '#2E7D32', textAlign: 'center', marginBottom: 12 },
  progressContainer: { flexDirection: 'row', justifyContent: 'center', marginBottom: 8 },
  progressDot: { width: 12, height: 12, borderRadius: 6, backgroundColor: '#ddd', marginHorizontal: 4 },
  progressDotActive: { backgroundColor: '#2E7D32' },
  stepLabel: { fontSize: 14, color: '#666', textAlign: 'center', marginBottom: 16 },
  deviceInfo: {
    backgroundColor: '#f0f7f0', borderRadius: 12, padding: 20, marginBottom: 16,
    alignItems: 'center', borderWidth: 1, borderColor: '#c8e6c9',
  },
  deviceName: { fontSize: 20, fontWeight: 'bold', color: '#2E7D32' },
  serialText: { fontSize: 14, color: '#666', marginTop: 4 },
  instructions: { fontSize: 13, color: '#888', textAlign: 'center', marginBottom: 20 },
  loadingContainer: { alignItems: 'center', marginTop: 20 },
  loadingText: { fontSize: 14, color: '#666', marginTop: 12 },
  successText: { fontSize: 16, color: '#2E7D32', textAlign: 'center', marginBottom: 16, fontWeight: 'bold' },
  input: { borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 14, marginBottom: 12, fontSize: 16 },
  button: { backgroundColor: '#2E7D32', borderRadius: 8, padding: 16, alignItems: 'center', marginTop: 8 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  doneContainer: { alignItems: 'center', marginVertical: 32 },
  doneEmoji: { fontSize: 64, marginBottom: 16 },
  doneTitle: { fontSize: 24, fontWeight: 'bold', color: '#2E7D32', marginBottom: 8 },
  doneText: { fontSize: 14, color: '#666', textAlign: 'center', paddingHorizontal: 16 },
});
