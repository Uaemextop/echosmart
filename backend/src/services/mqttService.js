'use strict';

const mqtt = require('mqtt');
const { processAlert } = require('../controllers/alertController');

let client = null;

function connect() {
  const brokerUrl = process.env.MQTT_BROKER || 'mqtt://mosquitto:1883';
  const connectOptions = {
    clientId: `backend-${Date.now()}`,
    clean: true,
    reconnectPeriod: 5000,
  };
  if (process.env.MQTT_USERNAME) {
    connectOptions.username = process.env.MQTT_USERNAME;
    connectOptions.password = process.env.MQTT_PASSWORD;
  }
  client = mqtt.connect(brokerUrl, connectOptions);

  client.on('connect', () => {
    console.log('MQTT connected to', brokerUrl);
    client.subscribe('/sensors/+/data', { qos: 1 }, (err) => {
      if (err) console.error('MQTT subscribe error:', err);
      else console.log('Subscribed to /sensors/+/data');
    });
  });

  client.on('message', async (topic, payload) => {
    try {
      const data = JSON.parse(payload.toString());
      // Extract UUID from topic /sensors/{uuid}/data
      const parts = topic.split('/');
      const uuid = parts[2];
      if (!uuid) return;

      const { query } = require('../config/database');
      const { rows } = await query('SELECT id FROM sensors WHERE uuid = $1', [uuid]);
      if (rows.length) {
        await query('UPDATE sensors SET status = $1, last_seen = NOW() WHERE uuid = $2', ['online', uuid]);
        await processAlert(rows[0].id, data);
      }
    } catch (err) {
      console.error('MQTT message handling error:', err.message);
    }
  });

  client.on('error', (err) => console.error('MQTT error:', err.message));
  client.on('reconnect', () => console.log('MQTT reconnecting...'));
}

function publish(topic, message) {
  if (!client || !client.connected) {
    console.warn('MQTT not connected; cannot publish to', topic);
    return;
  }
  const payload = typeof message === 'string' ? message : JSON.stringify(message);
  client.publish(topic, payload, { qos: 1 });
}

module.exports = { connect, publish, getClient: () => client };
