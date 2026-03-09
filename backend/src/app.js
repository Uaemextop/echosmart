'use strict';

const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const routes = require('./routes/index');
const { apiLimiter } = require('./middleware/rateLimiter');

const app = express();

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

// CSRF protection: for state-mutating cookie-authenticated requests, verify
// the Origin header matches the allowed frontend origin.
app.use((req, res, next) => {
  const safeMethods = ['GET', 'HEAD', 'OPTIONS'];
  if (safeMethods.includes(req.method)) return next();
  if (!req.cookies || !req.cookies.accessToken) return next(); // not cookie-authenticated
  const origin = req.get('origin') || req.get('referer') || '';
  const allowed = process.env.FRONTEND_URL || 'http://localhost:5173';
  if (origin && !origin.startsWith(allowed)) {
    return res.status(403).json({ error: 'CSRF check failed' });
  }
  return next();
});

app.use(cookieParser());
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true }));

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
