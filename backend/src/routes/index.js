'use strict';

const express = require('express');
const router = express.Router();

const authController = require('../controllers/authController');
const tenantController = require('../controllers/tenantController');
const sensorController = require('../controllers/sensorController');
const alertController = require('../controllers/alertController');
const { verifyToken, requireRole } = require('../middleware/auth');
const { enforceTenantIsolation } = require('../middleware/tenant');
const { authLimiter } = require('../middleware/rateLimiter');

// Auth routes
router.post('/auth/login', authLimiter, authController.login);
router.post('/auth/logout', authController.logout);
router.post('/auth/refresh', authController.refreshToken);
router.post('/auth/forgot-password', authLimiter, authController.forgotPassword);
router.post('/auth/reset-password', authLimiter, authController.resetPassword);
router.get('/auth/verify-email', authController.verifyEmail);
router.get('/auth/me', verifyToken, authController.getCurrentUser);

// Tenant routes (superadmin only)
router.post('/tenants', verifyToken, requireRole('superadmin'), tenantController.createTenant);
router.get('/tenants', verifyToken, requireRole('superadmin'), tenantController.listTenants);
router.get('/tenants/:id', verifyToken, requireRole('superadmin'), tenantController.getTenantById);
router.put('/tenants/:id', verifyToken, requireRole('superadmin'), tenantController.updateTenant);
router.delete('/tenants/:id', verifyToken, requireRole('superadmin'), tenantController.deleteTenant);
router.get('/tenants/:id/health', verifyToken, requireRole('superadmin'), tenantController.getTenantHealth);

// Sensor routes
router.post('/sensors/register', sensorController.registerSensor);
router.get('/sensors', verifyToken, enforceTenantIsolation, sensorController.getSensors);
router.get('/sensors/:id', verifyToken, enforceTenantIsolation, sensorController.getSensorById);
router.get('/sensors/:id/data', verifyToken, enforceTenantIsolation, sensorController.getSensorData);
router.put('/sensors/:id/config', verifyToken, enforceTenantIsolation, sensorController.updateSensorConfig);

// Alert routes
router.post('/alerts', verifyToken, enforceTenantIsolation, alertController.createAlertRule);
router.get('/alerts', verifyToken, enforceTenantIsolation, alertController.listAlertRules);
router.put('/alerts/:id', verifyToken, enforceTenantIsolation, alertController.updateAlertRule);
router.delete('/alerts/:id', verifyToken, enforceTenantIsolation, alertController.deleteAlertRule);

module.exports = router;
