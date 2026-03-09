'use strict';

const jwt = require('jsonwebtoken');

/**
 * Middleware: verify JWT from cookie or Authorization header.
 * Attaches req.user = { id, email, role, tenantId }.
 */
function verifyToken(req, res, next) {
  let token = null;

  if (req.cookies && req.cookies.accessToken) {
    token = req.cookies.accessToken;
  } else {
    const authHeader = req.headers['authorization'] || '';
    if (authHeader.startsWith('Bearer ')) {
      token = authHeader.slice(7);
    }
  }

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = {
      id: decoded.id,
      email: decoded.email,
      role: decoded.role,
      tenantId: decoded.tenantId || null,
    };
    return next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
}

/**
 * Middleware factory: restrict access to specific roles.
 * @param {...string} roles
 */
function requireRole(...roles) {
  return function (req, res, next) {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    return next();
  };
}

module.exports = { verifyToken, requireRole };
