/**
 * Servicio de notificaciones push.
 */
import * as Notifications from 'expo-notifications';

export async function registerForPushNotifications() {
  // TODO: Solicitar permisos y registrar token FCM
}

export async function schedulePushNotification(title, body) {
  await Notifications.scheduleNotificationAsync({
    content: { title, body },
    trigger: { seconds: 1 },
  });
}
