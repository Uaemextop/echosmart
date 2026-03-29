import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';

export default function RegisterScreen({ navigation }) {
  const [step, setStep] = useState(1);
  const [serialCode, setSerialCode] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');

  const validateSerial = async () => {
    if (!serialCode.match(/^ES-\d{6}-\d{4,5}$/)) {
      Alert.alert('Error', 'Formato de serial inválido. Ejemplo: ES-202603-0001 o ES-202603-10001');
      return;
    }
    // TODO: Llamar a POST /api/v1/serials/validate
    setStep(2);
  };

  const handleRegister = async () => {
    if (!email || !password || !fullName) {
      Alert.alert('Error', 'Todos los campos son obligatorios');
      return;
    }
    // TODO: Llamar a POST /api/v1/auth/register con serialCode
    setStep(3);
    navigation.navigate('SearchEchoPy', { serialCode });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>🌿 EchoSmart</Text>
      <Text style={styles.subtitle}>Registro de Kit</Text>

      {/* Progress indicator */}
      <View style={styles.progressContainer}>
        {[1, 2, 3, 4, 5].map((s) => (
          <View key={s} style={[styles.progressDot, s <= step && styles.progressDotActive]} />
        ))}
      </View>
      <Text style={styles.stepLabel}>
        {step === 1 ? 'Paso 1: Número de Serie' : 'Paso 2: Tu Información'}
      </Text>

      {step === 1 && (
        <>
          <Text style={styles.instructions}>
            Ingresa el número de serie que se encuentra en la etiqueta dentro de tu kit.
          </Text>
          <TextInput
            style={styles.input}
            placeholder="ES-202603-0001"
            value={serialCode}
            onChangeText={setSerialCode}
            autoCapitalize="characters"
          />
          <TouchableOpacity style={styles.button} onPress={validateSerial}>
            <Text style={styles.buttonText}>Verificar Serial</Text>
          </TouchableOpacity>
        </>
      )}

      {step === 2 && (
        <>
          <TextInput
            style={styles.input}
            placeholder="Nombre completo"
            value={fullName}
            onChangeText={setFullName}
          />
          <TextInput
            style={styles.input}
            placeholder="Correo electrónico"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
          />
          <TextInput
            style={styles.input}
            placeholder="Contraseña"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />
          <TextInput
            style={styles.input}
            placeholder="Teléfono (opcional)"
            value={phone}
            onChangeText={setPhone}
            keyboardType="phone-pad"
          />
          <TouchableOpacity style={styles.button} onPress={handleRegister}>
            <Text style={styles.buttonText}>Crear Cuenta</Text>
          </TouchableOpacity>
        </>
      )}

      <TouchableOpacity onPress={() => navigation.navigate('Login')}>
        <Text style={styles.link}>¿Ya tienes cuenta? Inicia sesión</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', paddingHorizontal: 32, backgroundColor: '#fff' },
  logo: { fontSize: 36, fontWeight: 'bold', color: '#2E7D32', textAlign: 'center', marginBottom: 4 },
  subtitle: { fontSize: 18, color: '#333', textAlign: 'center', marginBottom: 16 },
  progressContainer: { flexDirection: 'row', justifyContent: 'center', marginBottom: 8 },
  progressDot: { width: 12, height: 12, borderRadius: 6, backgroundColor: '#ddd', marginHorizontal: 4 },
  progressDotActive: { backgroundColor: '#2E7D32' },
  stepLabel: { fontSize: 14, color: '#666', textAlign: 'center', marginBottom: 16 },
  instructions: { fontSize: 13, color: '#888', textAlign: 'center', marginBottom: 16, paddingHorizontal: 16 },
  input: { borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 14, marginBottom: 12, fontSize: 16 },
  button: { backgroundColor: '#2E7D32', borderRadius: 8, padding: 16, alignItems: 'center', marginTop: 8 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  link: { color: '#2E7D32', textAlign: 'center', marginTop: 16, fontSize: 14 },
});
