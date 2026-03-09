'use strict';

const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const routes = require('./routes/index');
const { apiLimiter } = require('./middleware/rateLimiter');
const { csrfProtection } = require('./middleware/csrf');

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

app.use(cookieParser());
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true }));

// Double-submit cookie CSRF protection: seeds token on GET, validates header on mutations.
// Bearer-only requests (gateway, server-to-server) are automatically exempt.
app.use(csrfProtection);

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
