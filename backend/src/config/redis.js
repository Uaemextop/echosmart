'use strict';

const { createClient } = require('redis');

const client = createClient({
  url: process.env.REDIS_URL || 'redis://redis:6379',
  socket: {
    reconnectStrategy: (retries) => Math.min(retries * 100, 5000),
  },
});

client.on('error', (err) => console.error('Redis client error', err));
client.on('connect', () => console.log('Redis connected'));
client.on('reconnecting', () => console.log('Redis reconnecting'));

async function connectRedis() {
  if (!client.isOpen) {
    await client.connect();
  }
}

module.exports = { client, connectRedis };
