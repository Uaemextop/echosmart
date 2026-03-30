<?php
/**
 * EchoSmart - Configuration Template
 *
 * Copy this file to config.php and fill in your credentials.
 *   cp config.example.php config.php
 *
 * @package EchoSmart
 */

// ─── Database ────────────────────────────────────────────────────────
define('DB_HOST', getenv('ES_DB_HOST') ?: 'localhost');
define('DB_NAME', getenv('ES_DB_NAME') ?: 'your_database');
define('DB_USER', getenv('ES_DB_USER') ?: 'your_db_user');
define('DB_PASS', getenv('ES_DB_PASS') ?: 'your_db_password');
define('DB_CHARSET', 'utf8mb4');

// ─── SMTP ────────────────────────────────────────────────────────────
// Primary delivery uses authenticated SMTP on 127.0.0.1:465 (IPv4).
// Exim DKIM-signs and avoids Sender header mismatch.
// Fallback: PHP mail() with -f envelope sender.
define('SMTP_HOST', 'mail.echosmart.me');
define('SMTP_PORT', 465);
define('SMTP_USER', getenv('ES_SMTP_USER') ?: 'noreply@echosmart.me');
define('SMTP_PASS', getenv('ES_SMTP_PASS') ?: 'your_smtp_password');
define('SMTP_FROM_NAME', 'EchoSmart');
define('SMTP_SECURE', 'ssl');

// ─── Application ─────────────────────────────────────────────────────
define('SITE_NAME', 'EchoSmart');
define('SITE_URL', 'https://echosmart.me');
define('SECRET_KEY', getenv('ES_SECRET_KEY') ?: 'CHANGE_ME_GENERATE_WITH_bin2hex_random_bytes_32');
define('ADMIN_EMAIL', 'admin@echosmart.me');

// ─── Sessions ────────────────────────────────────────────────────────
define('SESSION_LIFETIME', 7 * 24 * 60 * 60);
define('SESSION_NAME', 'ECHOSMART_SID');

// ─── Error Reporting (production) ────────────────────────────────────
error_reporting(0);
ini_set('display_errors', '0');
ini_set('log_errors', '1');
ini_set('error_log', __DIR__ . '/../logs/php_errors.log');

// ─── PHP Session Hardening ───────────────────────────────────────────
ini_set('session.cookie_httponly', '1');
ini_set('session.cookie_secure', '1');
ini_set('session.cookie_samesite', 'Strict');
ini_set('session.use_strict_mode', '1');
ini_set('session.name', SESSION_NAME);

// ─── Timezone ────────────────────────────────────────────────────────
date_default_timezone_set('America/Mexico_City');
