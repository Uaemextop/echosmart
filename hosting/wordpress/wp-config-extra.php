<?php
/**
 * EchoSmart — WordPress Extra Configuration
 * ------------------------------------------
 * Include this file from wp-config.php by adding:
 *
 *   if ( file_exists( __DIR__ . '/wp-config-extra.php' ) ) {
 *       require_once __DIR__ . '/wp-config-extra.php';
 *   }
 *
 * Place this BEFORE the "That's all, stop editing!" comment.
 */

// ---- Performance ----
define( 'WP_CACHE', true );
define( 'WP_MEMORY_LIMIT', '256M' );
define( 'WP_MAX_MEMORY_LIMIT', '512M' );

// ---- Security ----
define( 'DISALLOW_FILE_EDIT', true );        // Disable theme/plugin file editor
define( 'FORCE_SSL_ADMIN', true );           // Force HTTPS for wp-admin
define( 'WP_AUTO_UPDATE_CORE', 'minor' );    // Only auto-update minor versions

// ---- Disable WordPress cron (use system cron via cPanel) ----
define( 'DISABLE_WP_CRON', true );

// ---- Post revisions and autosave ----
define( 'WP_POST_REVISIONS', 5 );
define( 'AUTOSAVE_INTERVAL', 120 ); // seconds

// ---- Debug (disable in production) ----
define( 'WP_DEBUG', false );
define( 'WP_DEBUG_LOG', false );
define( 'WP_DEBUG_DISPLAY', false );

// ---- Trash ----
define( 'EMPTY_TRASH_DAYS', 14 );

// ---- EchoSmart Backend API Configuration ----
define( 'ECHOSMART_API_URL', 'https://api.echosmart.me' );
define( 'ECHOSMART_API_VERSION', 'v1' );
define( 'ECHOSMART_DOMAIN', 'echosmart.me' );
