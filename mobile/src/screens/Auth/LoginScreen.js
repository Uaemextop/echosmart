import React from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';

export default function LoginScreen({ navigation }) {
  return (
    <View style={styles.container}>
      <Text style={styles.logo}>🌿 EchoSmart</Text>
      <Text style={styles.subtitle}>Monitoreo Inteligente de Invernaderos</Text>

      <TextInput style={styles.input} placeholder="Correo electrónico" keyboardType="email-address" autoCapitalize="none" />
      <TextInput style={styles.input} placeholder="Contraseña" secureTextEntry />

      <TouchableOpacity style={styles.button} onPress={() => navigation.replace('Main')}>
        <Text style={styles.buttonText}>Iniciar Sesión</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', paddingHorizontal: 32, backgroundColor: '#fff' },
  logo: { fontSize: 36, fontWeight: 'bold', color: '#2E7D32', textAlign: 'center', marginBottom: 8 },
  subtitle: { fontSize: 14, color: '#666', textAlign: 'center', marginBottom: 40 },
  input: { borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 14, marginBottom: 16, fontSize: 16 },
  button: { backgroundColor: '#2E7D32', borderRadius: 8, padding: 16, alignItems: 'center' },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
});
