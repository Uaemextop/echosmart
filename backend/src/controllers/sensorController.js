'use strict';

const { v4: uuidv4 } = require('uuid');
const { query } = require('../config/database');

async function registerSensor(req, res) {
  const { uuid, sensor_type, capabilities, gateway_id, ip_address, port } = req.body;
  if (!uuid || !sensor_type || !gateway_id) {
    return res.status(400).json({ error: 'uuid, sensor_type, and gateway_id are required' });
  }

  const { rows: existing } = await query('SELECT * FROM sensors WHERE uuid = $1', [uuid]);

  let sensor;
  if (existing.length) {
    await query(
      `UPDATE sensors SET sensor_type = $1, capabilities = $2, gateway_id = $3, ip_address = $4, port = $5, updated_at = NOW()
       WHERE uuid = $6`,
      [sensor_type, JSON.stringify(capabilities || []), gateway_id, ip_address || null, port || null, uuid]
    );
    const { rows } = await query('SELECT * FROM sensors WHERE uuid = $1', [uuid]);
    sensor = rows[0];
  } else {
    let tenantId = null;
    const { rows: gatewayRows } = await query(
      'SELECT DISTINCT tenant_id FROM sensors WHERE gateway_id = $1 AND tenant_id IS NOT NULL LIMIT 1',
      [gateway_id]
    );
    if (gatewayRows.length) tenantId = gatewayRows[0].tenant_id;

    const sensorId = uuidv4();
    const measurement = `sensor_${uuid.replace(/-/g, '_')}`;
    await query(
      `INSERT INTO sensors (id, tenant_id, uuid, sensor_type, capabilities, status, gateway_id, ip_address, port, influxdb_measurement)
       VALUES ($1, $2, $3, $4, $5, 'offline', $6, $7, $8, $9)`,
      [sensorId, tenantId, uuid, sensor_type, JSON.stringify(capabilities || []), gateway_id, ip_address || null, port || null, measurement]
    );
    const { rows } = await query('SELECT * FROM sensors WHERE id = $1', [sensorId]);
    sensor = rows[0];
  }

  return res.json({
    sensor_id: sensor.id,
    tenant_id: sensor.tenant_id,
    mqtt_topic_data: `/sensors/${uuid}/data`,
    mqtt_topic_config: `/sensors/${uuid}/config`,
  });
}

async function getSensors(req, res) {
  const tenantId = req.tenantId;
  if (!tenantId) return res.status(400).json({ error: 'Tenant context required' });
  const { rows } = await query(
    'SELECT * FROM sensors WHERE tenant_id = $1 ORDER BY created_at DESC',
    [tenantId]
  );
  return res.json(rows);
}

async function getSensorById(req, res) {
  const tenantId = req.tenantId;
  const { rows } = await query(
    'SELECT * FROM sensors WHERE id = $1 AND tenant_id = $2',
    [req.params.id, tenantId]
  );
  if (!rows.length) return res.status(404).json({ error: 'Sensor not found' });
  return res.json(rows[0]);
}

async function getSensorData(req, res) {
  const { id } = req.params;
  const { start = '-24h', end = 'now', field = 'temperature' } = req.query;
  const tenantId = req.tenantId;

  const { rows } = await query('SELECT * FROM sensors WHERE id = $1 AND tenant_id = $2', [id, tenantId]);
  if (!rows.length) return res.status(404).json({ error: 'Sensor not found' });

  // Mock time-series data – replace with InfluxDB client query in production
  const now = Date.now();
  const mockData = Array.from({ length: 24 }, (_, i) => ({
    timestamp: new Date(now - (23 - i) * 3600 * 1000).toISOString(),
    [field]: parseFloat((20 + Math.random() * 10).toFixed(2)),
  }));

  return res.json({ sensor_id: id, field, data: mockData });
}

async function updateSensorConfig(req, res) {
  const { id } = req.params;
  const tenantId = req.tenantId;
  const config = req.body;

  const { rows } = await query('SELECT * FROM sensors WHERE id = $1 AND tenant_id = $2', [id, tenantId]);
  if (!rows.length) return res.status(404).json({ error: 'Sensor not found' });

  const sensor = rows[0];
  const { publish } = require('../services/mqttService');
  publish(`/sensors/${sensor.uuid}/config`, JSON.stringify(config));

  return res.json({ message: 'Config published', topic: `/sensors/${sensor.uuid}/config` });
}

module.exports = { registerSensor, getSensors, getSensorById, getSensorData, updateSensorConfig };
