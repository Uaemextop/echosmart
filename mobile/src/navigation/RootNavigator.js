import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

// Auth Screens
import LoginScreen from '../screens/Auth/LoginScreen';
import RegisterScreen from '../screens/Auth/RegisterScreen';
import SearchEchoPyScreen from '../screens/Auth/SearchEchoPyScreen';
import PairEchoPyScreen from '../screens/Auth/PairEchoPyScreen';

// Main Screens
import DashboardScreen from '../screens/Dashboard/DashboardScreen';
import SensorsScreen from '../screens/Sensors/SensorsScreen';
import AlertsScreen from '../screens/Alerts/AlertsScreen';
import ReportsScreen from '../screens/Reports/ReportsScreen';
import SettingsScreen from '../screens/Settings/SettingsScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#2E7D32',
        headerStyle: { backgroundColor: '#2E7D32' },
        headerTintColor: '#fff',
      }}
    >
      <Tab.Screen name="Dashboard" component={DashboardScreen} options={{ title: 'Inicio' }} />
      <Tab.Screen name="Sensors" component={SensorsScreen} options={{ title: 'Sensores' }} />
      <Tab.Screen name="Alerts" component={AlertsScreen} options={{ title: 'Alertas' }} />
      <Tab.Screen name="Reports" component={ReportsScreen} options={{ title: 'Reportes' }} />
      <Tab.Screen name="Settings" component={SettingsScreen} options={{ title: 'Ajustes' }} />
    </Tab.Navigator>
  );
}

export default function RootNavigator() {
  // TODO: Verificar autenticación para mostrar Login o MainTabs
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {/* Auth Flow */}
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
      <Stack.Screen name="SearchEchoPy" component={SearchEchoPyScreen} />
      <Stack.Screen name="PairEchoPy" component={PairEchoPyScreen} />

      {/* Main App */}
      <Stack.Screen name="Main" component={MainTabs} />
    </Stack.Navigator>
  );
}
