#!/bin/sh
set -e

PASSWD_FILE="/mosquitto/config/passwd"

# Generate password file if it doesn't exist
if [ ! -f "$PASSWD_FILE" ]; then
  echo "Generating Mosquitto password file..."
  touch "$PASSWD_FILE"
  # Create users from environment variables (or use defaults for development)
  MQTT_USER="${MQTT_USER:-echosmart}"
  MQTT_PASSWORD="${MQTT_PASSWORD:-echosmart123}"
  MQTT_GATEWAY_USER="${MQTT_GATEWAY_USER:-gateway}"
  MQTT_GATEWAY_PASSWORD="${MQTT_GATEWAY_PASSWORD:-gateway123}"

  mosquitto_passwd -b "$PASSWD_FILE" "$MQTT_USER" "$MQTT_PASSWORD"
  mosquitto_passwd -b "$PASSWD_FILE" "$MQTT_GATEWAY_USER" "$MQTT_GATEWAY_PASSWORD"
  echo "Password file generated with users: $MQTT_USER, $MQTT_GATEWAY_USER"
fi

exec "$@"
