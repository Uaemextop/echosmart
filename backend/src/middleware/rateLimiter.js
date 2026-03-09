'use strict';

const rateLimit = require('express-rate-limit');
const { RedisStore } = require('rate-limit-redis');
const { client: redisClient } = require('../config/redis');

/** General API limiter: 100 req / 15 min per IP */
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  store: new RedisStore({
    sendCommand: (...args) => redisClient.sendCommand(args),
    prefix: 'rl:api:',
  }),
  message: { error: 'Too many requests, please try again later.' },
});

/** Auth limiter: 10 req / 15 min per IP (login / register) */
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  standardHeaders: true,
  legacyHeaders: false,
  store: new RedisStore({
    sendCommand: (...args) => redisClient.sendCommand(args),
    prefix: 'rl:auth:',
  }),
  message: { error: 'Too many authentication attempts, please try again later.' },
});

/** Per-tenant limiter: 1000 req / 15 min keyed by tenantId */
const tenantLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 1000,
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => (req.user && req.user.tenantId) ? req.user.tenantId : req.ip,
  store: new RedisStore({
    sendCommand: (...args) => redisClient.sendCommand(args),
    prefix: 'rl:tenant:',
  }),
  message: { error: 'Tenant rate limit exceeded.' },
});

module.exports = { apiLimiter, authLimiter, tenantLimiter };
