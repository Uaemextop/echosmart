'use strict';

require('dotenv').config();

const winston = require('winston');
const app = require('./app');
const { testConnection } = require('./config/database');
const { connectRedis } = require('./config/redis');
const mqttService = require('./services/mqttService');
const { processEmailQueue } = require('./services/emailService');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.printf(({ timestamp, level, message }) => `${timestamp} [${level.toUpperCase()}] ${message}`)
  ),
  transports: [new winston.transports.Console()],
});

// Expose logger for other modules
require('./config/logger');
global.logger = logger;

const PORT = parseInt(process.env.PORT, 10) || 3000;

async function start() {
  try {
    await testConnection();
    logger.info('Database connected');

    await connectRedis();
    logger.info('Redis connected');

    mqttService.connect();
    logger.info('MQTT service started');

    processEmailQueue().catch((err) => logger.error('Email queue fatal error: ' + err.message));
    logger.info('Email queue processor started');

    app.listen(PORT, () => {
      logger.info(`EchoSmart backend listening on port ${PORT}`);
    });
  } catch (err) {
    logger.error('Startup error: ' + err.message);
    process.exit(1);
  }
}

start();
