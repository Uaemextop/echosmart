'use strict';

const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const { query } = require('../config/database');
const { client: redis } = require('../config/redis');

const ACCESS_TOKEN_EXPIRY = '15m';
const REFRESH_TOKEN_EXPIRY = '7d';
const REFRESH_TOKEN_EXPIRY_MS = 7 * 24 * 60 * 60 * 1000;

function issueAccessToken(user) {
  return jwt.sign(
    { id: user.id, email: user.email, role: user.role, tenantId: user.tenant_id },
    process.env.JWT_SECRET,
    { expiresIn: ACCESS_TOKEN_EXPIRY }
  );
}

function issueRefreshToken(user) {
  return jwt.sign(
    { id: user.id },
    process.env.JWT_REFRESH_SECRET,
    { expiresIn: REFRESH_TOKEN_EXPIRY }
  );
}

function setCookies(res, accessToken, refreshToken) {
  res.cookie('accessToken', accessToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 15 * 60 * 1000,
  });
  res.cookie('refreshToken', refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: REFRESH_TOKEN_EXPIRY_MS,
    path: '/api/auth',
  });
}

async function login(req, res) {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password are required' });
  }

  const { rows } = await query('SELECT * FROM users WHERE email = $1 AND is_active = true', [email]);
  const user = rows[0];
  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  const valid = await bcrypt.compare(password, user.password_hash);
  if (!valid) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  const accessToken = issueAccessToken(user);
  const refreshToken = issueRefreshToken(user);
  const tokenHash = crypto.createHash('sha256').update(refreshToken).digest('hex');
  const expiresAt = new Date(Date.now() + REFRESH_TOKEN_EXPIRY_MS);

  await query(
    'INSERT INTO refresh_tokens (user_id, token_hash, expires_at) VALUES ($1, $2, $3)',
    [user.id, tokenHash, expiresAt]
  );

  setCookies(res, accessToken, refreshToken);
  return res.json({
    user: { id: user.id, email: user.email, role: user.role, tenantId: user.tenant_id },
  });
}

async function logout(req, res) {
  const refreshToken = req.cookies && req.cookies.refreshToken;
  if (refreshToken) {
    const tokenHash = crypto.createHash('sha256').update(refreshToken).digest('hex');
    await query('UPDATE refresh_tokens SET revoked = true WHERE token_hash = $1', [tokenHash]);
  }
  res.clearCookie('accessToken');
  res.clearCookie('refreshToken', { path: '/api/auth' });
  return res.json({ message: 'Logged out' });
}

async function refreshToken(req, res) {
  const token = req.cookies && req.cookies.refreshToken;
  if (!token) {
    return res.status(401).json({ error: 'No refresh token' });
  }

  let decoded;
  try {
    decoded = jwt.verify(token, process.env.JWT_REFRESH_SECRET);
  } catch {
    return res.status(401).json({ error: 'Invalid refresh token' });
  }

  const tokenHash = crypto.createHash('sha256').update(token).digest('hex');
  const { rows } = await query(
    'SELECT * FROM refresh_tokens WHERE token_hash = $1 AND revoked = false AND expires_at > NOW()',
    [tokenHash]
  );
  if (!rows.length) {
    return res.status(401).json({ error: 'Refresh token revoked or expired' });
  }

  const { rows: userRows } = await query('SELECT * FROM users WHERE id = $1', [decoded.id]);
  const user = userRows[0];
  if (!user) {
    return res.status(401).json({ error: 'User not found' });
  }

  await query('UPDATE refresh_tokens SET revoked = true WHERE token_hash = $1', [tokenHash]);

  const newAccessToken = issueAccessToken(user);
  const newRefreshToken = issueRefreshToken(user);
  const newTokenHash = crypto.createHash('sha256').update(newRefreshToken).digest('hex');
  const expiresAt = new Date(Date.now() + REFRESH_TOKEN_EXPIRY_MS);

  await query(
    'INSERT INTO refresh_tokens (user_id, token_hash, expires_at) VALUES ($1, $2, $3)',
    [user.id, newTokenHash, expiresAt]
  );

  setCookies(res, newAccessToken, newRefreshToken);
  return res.json({ message: 'Token refreshed' });
}

async function forgotPassword(req, res) {
  const { email } = req.body;
  if (!email) return res.status(400).json({ error: 'Email is required' });

  const { rows } = await query('SELECT id FROM users WHERE email = $1', [email]);
  if (!rows.length) {
    return res.json({ message: 'If that email exists, a reset link has been sent.' });
  }

  const user = rows[0];
  const resetToken = jwt.sign(
    { id: user.id, purpose: 'password_reset' },
    process.env.JWT_SECRET,
    { expiresIn: '1h' }
  );

  const resetUrl = `${process.env.FRONTEND_URL || 'http://localhost:5173'}/reset-password?token=${resetToken}`;
  await redis.lPush('email:queue', JSON.stringify({ type: 'password_reset', to: email, resetUrl }));

  return res.json({ message: 'If that email exists, a reset link has been sent.' });
}

async function resetPassword(req, res) {
  const { token, password } = req.body;
  if (!token || !password) {
    return res.status(400).json({ error: 'Token and password are required' });
  }
  if (password.length < 8) {
    return res.status(400).json({ error: 'Password must be at least 8 characters' });
  }

  let decoded;
  try {
    decoded = jwt.verify(token, process.env.JWT_SECRET);
  } catch {
    return res.status(400).json({ error: 'Invalid or expired reset token' });
  }

  if (decoded.purpose !== 'password_reset') {
    return res.status(400).json({ error: 'Invalid token purpose' });
  }

  const hash = await bcrypt.hash(password, 12);
  await query('UPDATE users SET password_hash = $1, updated_at = NOW() WHERE id = $2', [hash, decoded.id]);

  return res.json({ message: 'Password reset successful' });
}

async function verifyEmail(req, res) {
  const { token } = req.query;
  if (!token) return res.status(400).json({ error: 'Token required' });

  let decoded;
  try {
    decoded = jwt.verify(token, process.env.JWT_SECRET);
  } catch {
    return res.status(400).json({ error: 'Invalid or expired token' });
  }

  if (decoded.purpose !== 'email_verification') {
    return res.status(400).json({ error: 'Invalid token purpose' });
  }

  await query('UPDATE users SET email_verified = true, updated_at = NOW() WHERE id = $1', [decoded.userId]);
  return res.json({ message: 'Email verified successfully' });
}

async function getCurrentUser(req, res) {
  const { rows } = await query(
    'SELECT id, tenant_id, email, role, first_name, last_name, email_verified FROM users WHERE id = $1',
    [req.user.id]
  );
  if (!rows.length) return res.status(404).json({ error: 'User not found' });
  return res.json(rows[0]);
}

module.exports = { login, logout, refreshToken, forgotPassword, resetPassword, verifyEmail, getCurrentUser };
