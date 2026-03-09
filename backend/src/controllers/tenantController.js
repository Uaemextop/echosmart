'use strict';

const Joi = require('joi');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const { query } = require('../config/database');
const { client: redis } = require('../config/redis');

const createTenantSchema = Joi.object({
  name: Joi.string().min(2).max(100).required(),
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required(),
  plan: Joi.string().valid('basic', 'pro', 'enterprise').required(),
  company_name: Joi.string().max(200).required(),
  first_name: Joi.string().max(100).optional(),
  last_name: Joi.string().max(100).optional(),
  max_sensors: Joi.number().integer().min(1).optional(),
  max_users: Joi.number().integer().min(1).optional(),
});

const planDefaults = {
  basic: { max_sensors: 10, max_users: 5 },
  pro: { max_sensors: 50, max_users: 25 },
  enterprise: { max_sensors: 500, max_users: 200 },
};

async function createTenant(req, res) {
  const { error, value } = createTenantSchema.validate(req.body);
  if (error) return res.status(400).json({ error: error.details[0].message });

  const { name, email, password, plan, company_name, first_name, last_name } = value;
  const defaults = planDefaults[plan];
  const max_sensors = value.max_sensors || defaults.max_sensors;
  const max_users = value.max_users || defaults.max_users;

  const { rows: existing } = await query('SELECT id FROM tenants WHERE name = $1', [name]);
  if (existing.length) return res.status(409).json({ error: 'Tenant name already exists' });

  const { rows: existingEmail } = await query('SELECT id FROM users WHERE email = $1', [email]);
  if (existingEmail.length) return res.status(409).json({ error: 'Email already registered' });

  const tenantId = uuidv4();
  const userId = uuidv4();

  await query(
    'INSERT INTO tenants (id, name, plan, status, max_sensors, max_users) VALUES ($1, $2, $3, $4, $5, $6)',
    [tenantId, name, plan, 'active', max_sensors, max_users]
  );

  await query(
    `INSERT INTO tenant_settings (tenant_id, company_name, primary_color, secondary_color, logo_url, email_signature_html, timezone, language)
     VALUES ($1, $2, '#22c55e', '#16a34a', '', '', 'UTC', 'en')`,
    [tenantId, company_name]
  );

  const passwordHash = await bcrypt.hash(password, 12);
  await query(
    `INSERT INTO users (id, tenant_id, email, password_hash, role, first_name, last_name, email_verified)
     VALUES ($1, $2, $3, $4, 'tenant_admin', $5, $6, false)`,
    [userId, tenantId, email, passwordHash, first_name || null, last_name || null]
  );

  const verificationToken = jwt.sign(
    { userId, purpose: 'email_verification' },
    process.env.JWT_SECRET,
    { expiresIn: '24h' }
  );
  const verificationUrl = `${process.env.FRONTEND_URL || 'http://localhost:5173'}/verify-email?token=${verificationToken}`;

  await redis.lPush('email:queue', JSON.stringify({
    type: 'welcome',
    to: email,
    verificationUrl,
    tenantName: name,
    companyName: company_name,
  }));

  return res.status(201).json({
    tenant: { id: tenantId, name, plan, status: 'active', max_sensors, max_users },
    user: { id: userId, email, role: 'tenant_admin', email_verified: false },
  });
}

async function listTenants(req, res) {
  const page = parseInt(req.query.page, 10) || 1;
  const limit = parseInt(req.query.limit, 10) || 10;
  const offset = (page - 1) * limit;
  const { status, plan, search } = req.query;

  let conditions = [];
  let params = [];
  let idx = 1;

  if (status) { conditions.push(`t.status = $${idx++}`); params.push(status); }
  if (plan) { conditions.push(`t.plan = $${idx++}`); params.push(plan); }
  if (search) { conditions.push(`t.name ILIKE $${idx++}`); params.push(`%${search}%`); }

  const where = conditions.length ? `WHERE ${conditions.join(' AND ')}` : '';

  const { rows: tenants } = await query(
    `SELECT t.*, ts.company_name FROM tenants t LEFT JOIN tenant_settings ts ON ts.tenant_id = t.id ${where} ORDER BY t.created_at DESC LIMIT $${idx++} OFFSET $${idx++}`,
    [...params, limit, offset]
  );
  const { rows: countRows } = await query(`SELECT COUNT(*) FROM tenants t ${where}`, params);

  return res.json({ tenants, total: parseInt(countRows[0].count, 10), page, limit });
}

async function getTenantById(req, res) {
  const { rows } = await query(
    'SELECT t.*, ts.* FROM tenants t LEFT JOIN tenant_settings ts ON ts.tenant_id = t.id WHERE t.id = $1',
    [req.params.id]
  );
  if (!rows.length) return res.status(404).json({ error: 'Tenant not found' });
  return res.json(rows[0]);
}

async function updateTenant(req, res) {
  const { name, plan, status, settings: tenantSettings } = req.body;
  const { id } = req.params;

  const { rows } = await query('SELECT id FROM tenants WHERE id = $1', [id]);
  if (!rows.length) return res.status(404).json({ error: 'Tenant not found' });

  if (name || plan || status) {
    const fields = [];
    const params = [];
    let idx = 1;
    if (name) { fields.push(`name = $${idx++}`); params.push(name); }
    if (plan) { fields.push(`plan = $${idx++}`); params.push(plan); }
    if (status) { fields.push(`status = $${idx++}`); params.push(status); }
    fields.push(`updated_at = NOW()`);
    await query(`UPDATE tenants SET ${fields.join(', ')} WHERE id = $${idx}`, [...params, id]);
  }

  if (tenantSettings) {
    const { primary_color, secondary_color, logo_url, company_name, timezone, language, notification_email, email_signature_html } = tenantSettings;
    const fields = [];
    const params = [];
    let idx = 1;
    if (primary_color !== undefined) { fields.push(`primary_color = $${idx++}`); params.push(primary_color); }
    if (secondary_color !== undefined) { fields.push(`secondary_color = $${idx++}`); params.push(secondary_color); }
    if (logo_url !== undefined) { fields.push(`logo_url = $${idx++}`); params.push(logo_url); }
    if (company_name !== undefined) { fields.push(`company_name = $${idx++}`); params.push(company_name); }
    if (timezone !== undefined) { fields.push(`timezone = $${idx++}`); params.push(timezone); }
    if (language !== undefined) { fields.push(`language = $${idx++}`); params.push(language); }
    if (notification_email !== undefined) { fields.push(`notification_email = $${idx++}`); params.push(notification_email); }
    if (email_signature_html !== undefined) { fields.push(`email_signature_html = $${idx++}`); params.push(email_signature_html); }
    if (fields.length) {
      fields.push(`updated_at = NOW()`);
      await query(`UPDATE tenant_settings SET ${fields.join(', ')} WHERE tenant_id = $${idx}`, [...params, id]);
    }
  }

  return res.json({ message: 'Tenant updated' });
}

async function deleteTenant(req, res) {
  const { id } = req.params;
  const { rows } = await query('SELECT id FROM tenants WHERE id = $1', [id]);
  if (!rows.length) return res.status(404).json({ error: 'Tenant not found' });
  await query("UPDATE tenants SET status = 'deleted', updated_at = NOW() WHERE id = $1", [id]);
  return res.json({ message: 'Tenant deleted' });
}

async function getTenantHealth(req, res) {
  const { id } = req.params;
  const [sensorsRes, usersRes, alertsRes] = await Promise.all([
    query('SELECT COUNT(*) FROM sensors WHERE tenant_id = $1', [id]),
    query('SELECT COUNT(*) FROM users WHERE tenant_id = $1', [id]),
    query("SELECT COUNT(*) FROM alert_history WHERE tenant_id = $1 AND resolved_at IS NULL AND acknowledged = false", [id]),
  ]);
  return res.json({
    tenant_id: id,
    sensors: parseInt(sensorsRes.rows[0].count, 10),
    users: parseInt(usersRes.rows[0].count, 10),
    active_alerts: parseInt(alertsRes.rows[0].count, 10),
  });
}

module.exports = { createTenant, listTenants, getTenantById, updateTenant, deleteTenant, getTenantHealth };
