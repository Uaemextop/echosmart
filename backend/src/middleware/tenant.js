'use strict';

/**
 * Enforce tenant isolation based on JWT role.
 * - Non-superadmin: req.tenantId is always from req.user.tenantId
 * - Superadmin: may pass tenantId via query param or body
 * Attaches req.tenantFilter = { tenant_id: req.tenantId } for DB queries.
 */
function enforceTenantIsolation(req, res, next) {
  if (!req.user) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  if (req.user.role === 'superadmin') {
    const tenantId =
      req.query.tenantId ||
      (req.body && req.body.tenantId) ||
      req.user.tenantId ||
      null;
    req.tenantId = tenantId;
  } else {
    req.tenantId = req.user.tenantId;
  }

  req.tenantFilter = req.tenantId ? { tenant_id: req.tenantId } : {};
  return next();
}

module.exports = { enforceTenantIsolation };
