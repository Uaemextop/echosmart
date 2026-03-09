'use strict';

const crypto = require('crypto');
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const routes = require('./routes/index');
const { apiLimiter } = require('./middleware/rateLimiter');

const app = express();

const CSRF_COOKIE = 'csrfToken';
const CSRF_HEADER = 'x-csrf-token';
const CSRF_SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS']);

const allowedOrigins = new Set([
  process.env.FRONTEND_URL || 'http://localhost:5173',
]);

app.use(helmet());
app.use(cors({
  origin: (origin, callback) => {
    // Allow requests with no origin (server-to-server, curl) or from allowed origins
    if (!origin || allowedOrigins.has(origin)) return callback(null, true);
    return callback(new Error('CORS: origin not allowed'));
  },
  credentials: true,
}));

app.use(cookieParser());
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true }));

// Double-submit cookie CSRF protection.
// Seed a non-httpOnly CSRF token cookie on safe requests so JS can read it;
// validate X-CSRF-Token header against the cookie on state-mutating requests.
app.use((req, res, next) => {
  if (CSRF_SAFE_METHODS.has(req.method)) {
    if (!req.cookies[CSRF_COOKIE]) {
      const token = crypto.randomBytes(32).toString('hex');
      res.cookie(CSRF_COOKIE, token, {
        httpOnly: false,
        sameSite: 'strict',
        secure: process.env.NODE_ENV === 'production',
        path: '/',
      });
    }
    return next();
  }
  // Only cookie-authenticated requests are subject to CSRF validation;
  // Bearer-token-only requests (gateway, server-to-server) are exempt.
  if (!req.cookies || !req.cookies.accessToken) return next();
  const cookieToken = req.cookies[CSRF_COOKIE];
  const headerToken = req.get(CSRF_HEADER);
  if (!cookieToken || !headerToken || cookieToken !== headerToken) {
    return res.status(403).json({ error: 'CSRF token invalid or missing' });
  }
  return next();
});

app.use('/api', apiLimiter);
app.use('/api', routes);

app.get('/health', (_req, res) => res.json({ status: 'ok', service: 'echosmart-backend' }));

// 404 handler
app.use((_req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// Global error handler
// eslint-disable-next-line no-unused-vars
app.use((err, _req, res, _next) => {
  console.error('Unhandled error:', err);
  res.status(err.status || 500).json({ error: err.message || 'Internal server error' });
});

module.exports = app;
