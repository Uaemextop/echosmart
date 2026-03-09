'use strict';

const Joi = require('joi');
const { v4: uuidv4 } = require('uuid');
const { query } = require('../config/database');

const conditionSchema = Joi.object({
  operator: Joi.string().valid('AND', 'OR', 'NOT').required(),
  conditions: Joi.array().items(
    Joi.alternatives().try(
      Joi.object({
        field: Joi.string().required(),
        op: Joi.string().valid('>', '<', '>=', '<=', '==', '!=').required(),
        value: Joi.number().required(),
      }),
      Joi.link('/')
    )
  ).min(1).required(),
});

const alertRuleSchema = Joi.object({
  sensor_id: Joi.string().uuid().optional().allow(null),
  name: Joi.string().min(1).max(200).required(),
  conditions: conditionSchema.required(),
  hysteresis_count: Joi.number().integer().min(1).default(1),
  time_window_start: Joi.string().pattern(/^\d{2}:\d{2}(:\d{2})?$/).optional().allow(null, ''),
  time_window_end: Joi.string().pattern(/^\d{2}:\d{2}(:\d{2})?$/).optional().allow(null, ''),
  severity: Joi.string().valid('info', 'warning', 'critical').default('warning'),
  is_active: Joi.boolean().default(true),
  notification_channels: Joi.array().items(Joi.string()).default([]),
});

function evaluateCondition(condition, sensorData) {
  if (condition.operator) {
    const { operator, conditions } = condition;
    if (operator === 'AND') return conditions.every((c) => evaluateCondition(c, sensorData));
    if (operator === 'OR') return conditions.some((c) => evaluateCondition(c, sensorData));
    if (operator === 'NOT') return !evaluateCondition(conditions[0], sensorData);
    return false;
  }
  const { field, op, value } = condition;
  const actual = sensorData[field];
  if (actual === undefined) return false;
  switch (op) {
    case '>': return actual > value;
    case '<': return actual < value;
    case '>=': return actual >= value;
    case '<=': return actual <= value;
    case '==': return actual === value;
    case '!=': return actual !== value;
    default: return false;
  }
}

function isWithinTimeWindow(start, end) {
  if (!start || !end) return true;
  const now = new Date();
  const [sh, sm] = start.split(':').map(Number);
  const [eh, em] = end.split(':').map(Number);
  const currentMinutes = now.getHours() * 60 + now.getMinutes();
  const startMinutes = sh * 60 + sm;
  const endMinutes = eh * 60 + em;
  if (startMinutes <= endMinutes) return currentMinutes >= startMinutes && currentMinutes <= endMinutes;
  return currentMinutes >= startMinutes || currentMinutes <= endMinutes;
}

// In-memory hysteresis counters (keyed by rule_id)
const hysteresisCounters = {};

async function processAlert(sensorId, sensorData) {
  const { rows: rules } = await query(
    "SELECT * FROM alert_rules WHERE (sensor_id = $1 OR sensor_id IS NULL) AND is_active = true",
    [sensorId]
  );

  for (const rule of rules) {
    const conditions = typeof rule.conditions === 'string' ? JSON.parse(rule.conditions) : rule.conditions;
    const triggered = evaluateCondition(conditions, sensorData);
    const inWindow = isWithinTimeWindow(rule.time_window_start, rule.time_window_end);

    if (!inWindow) continue;

    if (!hysteresisCounters[rule.id]) hysteresisCounters[rule.id] = 0;

    if (triggered) {
      hysteresisCounters[rule.id]++;
      if (hysteresisCounters[rule.id] >= rule.hysteresis_count) {
        const alreadyOpen = await query(
          'SELECT id FROM alert_history WHERE alert_rule_id = $1 AND resolved_at IS NULL',
          [rule.id]
        );
        if (!alreadyOpen.rows.length) {
          await query(
            `INSERT INTO alert_history (tenant_id, alert_rule_id, sensor_id, severity, message, sensor_data)
             VALUES ($1, $2, $3, $4, $5, $6)`,
            [rule.tenant_id, rule.id, sensorId, rule.severity, `Alert "${rule.name}" triggered`, JSON.stringify(sensorData)]
          );
        }
        hysteresisCounters[rule.id] = 0;
      }
    } else {
      hysteresisCounters[rule.id] = 0;
      await query(
        'UPDATE alert_history SET resolved_at = NOW() WHERE alert_rule_id = $1 AND resolved_at IS NULL',
        [rule.id]
      );
    }
  }
}

async function createAlertRule(req, res) {
  const { error, value } = alertRuleSchema.validate(req.body);
  if (error) return res.status(400).json({ error: error.details[0].message });

  const tenantId = req.tenantId;
  if (!tenantId) return res.status(400).json({ error: 'Tenant context required' });

  const id = uuidv4();
  await query(
    `INSERT INTO alert_rules (id, tenant_id, sensor_id, name, conditions, hysteresis_count, time_window_start, time_window_end, severity, is_active, notification_channels)
     VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)`,
    [id, tenantId, value.sensor_id || null, value.name, JSON.stringify(value.conditions),
     value.hysteresis_count, value.time_window_start || null, value.time_window_end || null,
     value.severity, value.is_active, JSON.stringify(value.notification_channels)]
  );

  const { rows } = await query('SELECT * FROM alert_rules WHERE id = $1', [id]);
  return res.status(201).json(rows[0]);
}

async function listAlertRules(req, res) {
  const tenantId = req.tenantId;
  if (!tenantId) return res.status(400).json({ error: 'Tenant context required' });
  const { rows } = await query(
    'SELECT * FROM alert_rules WHERE tenant_id = $1 ORDER BY created_at DESC',
    [tenantId]
  );
  return res.json(rows);
}

async function updateAlertRule(req, res) {
  const { id } = req.params;
  const tenantId = req.tenantId;
  const { rows: existing } = await query('SELECT id FROM alert_rules WHERE id = $1 AND tenant_id = $2', [id, tenantId]);
  if (!existing.length) return res.status(404).json({ error: 'Alert rule not found' });

  const fields = [];
  const params = [];
  let idx = 1;
  const allowed = ['name', 'conditions', 'hysteresis_count', 'time_window_start', 'time_window_end', 'severity', 'is_active', 'notification_channels'];
  for (const key of allowed) {
    if (req.body[key] !== undefined) {
      const val = (key === 'conditions' || key === 'notification_channels') ? JSON.stringify(req.body[key]) : req.body[key];
      fields.push(`${key} = $${idx++}`);
      params.push(val);
    }
  }
  if (!fields.length) return res.status(400).json({ error: 'No fields to update' });
  fields.push(`updated_at = NOW()`);
  await query(`UPDATE alert_rules SET ${fields.join(', ')} WHERE id = $${idx}`, [...params, id]);
  const { rows } = await query('SELECT * FROM alert_rules WHERE id = $1', [id]);
  return res.json(rows[0]);
}

async function deleteAlertRule(req, res) {
  const { id } = req.params;
  const tenantId = req.tenantId;
  const { rows } = await query('SELECT id FROM alert_rules WHERE id = $1 AND tenant_id = $2', [id, tenantId]);
  if (!rows.length) return res.status(404).json({ error: 'Alert rule not found' });
  await query("UPDATE alert_rules SET is_active = false, updated_at = NOW() WHERE id = $1", [id]);
  return res.json({ message: 'Alert rule deactivated' });
}

module.exports = { createAlertRule, listAlertRules, updateAlertRule, deleteAlertRule, processAlert };
