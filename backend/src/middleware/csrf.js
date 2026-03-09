'use strict';

const crypto = require('crypto');

const CSRF_COOKIE = 'csrfToken';
const CSRF_HEADER = 'x-csrf-token';
const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS']);

/**
 * Double-submit cookie CSRF protection.
 *
 * On every GET, a random CSRF token is set as a non-httpOnly cookie so the
 * frontend JavaScript can read it.  On every state-mutating request the
 * middleware verifies that the submitted X-CSRF-Token header matches the
 * cookie value (constant-time comparison to prevent timing attacks).
 */
function csrfProtection(req, res, next) {
  // Refresh (or seed) the CSRF token on safe requests
  if (SAFE_METHODS.has(req.method)) {
    if (!req.cookies[CSRF_COOKIE]) {
      const token = crypto.randomBytes(32).toString('hex');
      res.cookie(CSRF_COOKIE, token, {
        httpOnly: false,   // must be readable by JS
        sameSite: 'strict',
        secure: process.env.NODE_ENV === 'production',
        path: '/',
      });
    }
    return next();
  }

  // Skip CSRF check for requests that are NOT cookie-authenticated
  // (e.g. gateway API-key requests, server-to-server calls with Bearer token only)
  if (!req.cookies || !req.cookies.accessToken) return next();

  const cookieToken = req.cookies[CSRF_COOKIE];
  const headerToken = req.get(CSRF_HEADER);

  if (!cookieToken || !headerToken) {
    return res.status(403).json({ error: 'CSRF token missing' });
  }

  // Constant-time comparison to prevent timing attacks
  const cookieBuf = Buffer.from(cookieToken);
  const headerBuf = Buffer.from(headerToken);
  if (
    cookieBuf.length !== headerBuf.length ||
    !crypto.timingSafeEqual(cookieBuf, headerBuf)
  ) {
    return res.status(403).json({ error: 'CSRF token invalid' });
  }

  return next();
}

module.exports = { csrfProtection, CSRF_COOKIE, CSRF_HEADER };
