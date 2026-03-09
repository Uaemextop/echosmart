'use strict';

const { Pool } = require('pg');

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

pool.on('error', (err) => {
  console.error('Unexpected PostgreSQL pool error', err);
});

async function testConnection() {
  const client = await pool.connect();
  try {
    await client.query('SELECT 1');
    console.log('PostgreSQL connection established');
  } finally {
    client.release();
  }
}

/**
 * @param {string} text
 * @param {unknown[]} [params]
 */
async function query(text, params) {
  return pool.query(text, params);
}

module.exports = { pool, query, testConnection };
