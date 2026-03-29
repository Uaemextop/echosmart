<?php
/**
 * EchoSmart - Database Initialization Script
 *
 * Creates the required tables and seeds the admin user.
 * Run once via CLI:  php init.php
 *
 * SECURITY: This file is blocked by .htaccess and must NEVER be
 *           accessible from the web. Delete it after first run.
 *
 * @package EchoSmart
 */

// Only allow CLI execution
if (php_sapi_name() !== 'cli') {
    http_response_code(403);
    exit('Forbidden');
}

require_once __DIR__ . '/includes/Database.php';

echo "╔══════════════════════════════════════════╗\n";
echo "║    EchoSmart - Database Initialization   ║\n";
echo "╚══════════════════════════════════════════╝\n\n";

$pdo = Database::getInstance();

// ─── Create Tables ───────────────────────────────────────────────────

$tables = [

    'users' => "
        CREATE TABLE IF NOT EXISTS `users` (
            `id`            INT UNSIGNED    NOT NULL AUTO_INCREMENT,
            `serial_number` VARCHAR(20)     NOT NULL,
            `full_name`     VARCHAR(100)    NOT NULL,
            `email`         VARCHAR(255)    NOT NULL,
            `password_hash` VARCHAR(255)    NOT NULL,
            `role`          ENUM('user','admin') NOT NULL DEFAULT 'user',
            `last_login`    DATETIME        NULL DEFAULT NULL,
            `created_at`    DATETIME        NOT NULL,
            `updated_at`    DATETIME        NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `uq_email` (`email`),
            UNIQUE KEY `uq_serial` (`serial_number`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    ",

    'sessions' => "
        CREATE TABLE IF NOT EXISTS `sessions` (
            `id`         INT UNSIGNED NOT NULL AUTO_INCREMENT,
            `user_id`    INT UNSIGNED NOT NULL,
            `token`      VARCHAR(64)  NOT NULL COMMENT 'SHA-256 of the bearer token',
            `ip_address` VARCHAR(45)  NOT NULL,
            `user_agent` VARCHAR(255) NOT NULL DEFAULT '',
            `expires_at` DATETIME     NOT NULL,
            `created_at` DATETIME     NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `uq_token` (`token`),
            KEY `idx_user` (`user_id`),
            KEY `idx_expires` (`expires_at`),
            CONSTRAINT `fk_sessions_user` FOREIGN KEY (`user_id`)
                REFERENCES `users` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    ",

    'password_resets' => "
        CREATE TABLE IF NOT EXISTS `password_resets` (
            `id`         INT UNSIGNED NOT NULL AUTO_INCREMENT,
            `user_id`    INT UNSIGNED NOT NULL,
            `token`      VARCHAR(64)  NOT NULL COMMENT 'SHA-256 of the reset token',
            `expires_at` DATETIME     NOT NULL,
            `created_at` DATETIME     NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `uq_token` (`token`),
            KEY `idx_user` (`user_id`),
            CONSTRAINT `fk_resets_user` FOREIGN KEY (`user_id`)
                REFERENCES `users` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    ",

    'contact_messages' => "
        CREATE TABLE IF NOT EXISTS `contact_messages` (
            `id`         INT UNSIGNED  NOT NULL AUTO_INCREMENT,
            `name`       VARCHAR(100)  NOT NULL,
            `email`      VARCHAR(255)  NOT NULL,
            `subject`    VARCHAR(200)  NOT NULL,
            `message`    TEXT          NOT NULL,
            `ip_address` VARCHAR(45)   NOT NULL DEFAULT '0.0.0.0',
            `is_read`    TINYINT(1)    NOT NULL DEFAULT 0,
            `created_at` DATETIME      NOT NULL,
            PRIMARY KEY (`id`),
            KEY `idx_created` (`created_at`),
            KEY `idx_read` (`is_read`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    ",
];

foreach ($tables as $name => $sql) {
    try {
        $pdo->exec($sql);
        echo "  ✓ Table `{$name}` ready\n";
    } catch (PDOException $e) {
        echo "  ✗ Table `{$name}` FAILED: " . $e->getMessage() . "\n";
    }
}

// ─── Seed Admin User ─────────────────────────────────────────────────

echo "\n── Seeding admin user ──\n";

$adminEmail    = 'admin@echosmart.me';
$adminSerial   = 'ES-202501-0001';
$adminName     = 'EchoSmart Admin';

// Read password from environment or prompt
$adminPassword = getenv('ES_ADMIN_PASS') ?: '';
if ($adminPassword === '') {
    echo "  Enter admin password (or set ES_ADMIN_PASS env var): ";
    $adminPassword = trim(fgets(STDIN));
}
if (strlen($adminPassword) < 8) {
    echo "  ✗ Password must be at least 8 characters.\n";
    exit(1);
}

$existing = Database::fetchOne('SELECT id FROM users WHERE email = ?', [$adminEmail]);

if ($existing) {
    // Update password hash in case algorithm/cost changed
    Database::update(
        'users',
        [
            'password_hash' => password_hash($adminPassword, PASSWORD_BCRYPT, ['cost' => 12]),
            'role'          => 'admin',
            'updated_at'    => date('Y-m-d H:i:s'),
        ],
        'id = ?',
        [$existing['id']]
    );
    echo "  ✓ Admin user updated (password re-hashed)\n";
} else {
    Database::insert('users', [
        'serial_number' => $adminSerial,
        'full_name'     => $adminName,
        'email'         => $adminEmail,
        'password_hash' => password_hash($adminPassword, PASSWORD_BCRYPT, ['cost' => 12]),
        'role'          => 'admin',
        'created_at'    => date('Y-m-d H:i:s'),
        'updated_at'    => date('Y-m-d H:i:s'),
    ]);
    echo "  ✓ Admin user created\n";
}

// ─── Cleanup: purge expired sessions & resets ────────────────────────

echo "\n── Cleanup ──\n";

try {
    $purgedSessions = Database::delete('sessions', 'expires_at < NOW()', []);
    echo "  ✓ Purged {$purgedSessions} expired session(s)\n";

    $purgedResets = Database::delete('password_resets', 'expires_at < NOW()', []);
    echo "  ✓ Purged {$purgedResets} expired reset token(s)\n";
} catch (PDOException $e) {
    echo "  ⚠ Cleanup skipped: " . $e->getMessage() . "\n";
}

echo "\n══ Done. Delete this file from the server. ══\n";
