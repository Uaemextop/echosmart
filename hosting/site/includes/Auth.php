<?php
/**
 * EchoSmart - Authentication Service
 *
 * @package EchoSmart
 */

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/Database.php';
require_once __DIR__ . '/Mailer.php';

class Auth
{
    private const SERIAL_PATTERN = '/^ES-\d{6}-\d{4}$/';
    private const TOKEN_BYTES    = 32;
    private const RESET_EXPIRY   = 3600; // 1 hour

    // ─── Registration ────────────────────────────────────────────────

    /**
     * Register a new user.
     *
     * @return array{success: bool, user?: array, message?: string}
     */
    public static function register(
        string $serial,
        string $name,
        string $email,
        string $password
    ): array {
        $serial = trim($serial);
        $name   = trim($name);
        $email  = trim(strtolower($email));

        // Validate serial number format
        if (!preg_match(self::SERIAL_PATTERN, $serial)) {
            return ['success' => false, 'message' => 'Invalid serial number format. Expected: ES-YYYYMM-XXXX'];
        }

        // Validate email
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            return ['success' => false, 'message' => 'Invalid email address.'];
        }

        // Validate name
        if (strlen($name) < 2 || strlen($name) > 100) {
            return ['success' => false, 'message' => 'Name must be between 2 and 100 characters.'];
        }

        // Validate password strength
        if (strlen($password) < 8) {
            return ['success' => false, 'message' => 'Password must be at least 8 characters.'];
        }

        // Check duplicate email
        $existing = Database::fetchOne(
            'SELECT id FROM users WHERE email = ?',
            [$email]
        );
        if ($existing) {
            return ['success' => false, 'message' => 'An account with this email already exists.'];
        }

        // Check duplicate serial
        $existingSerial = Database::fetchOne(
            'SELECT id FROM users WHERE serial_number = ?',
            [$serial]
        );
        if ($existingSerial) {
            return ['success' => false, 'message' => 'This serial number is already registered.'];
        }

        $hashedPassword = self::hashPassword($password);

        try {
            $userId = Database::insert('users', [
                'serial_number' => $serial,
                'full_name'     => $name,
                'email'         => $email,
                'password_hash' => $hashedPassword,
                'created_at'    => date('Y-m-d H:i:s'),
                'updated_at'    => date('Y-m-d H:i:s'),
            ]);

            Mailer::sendWelcome($email, $name);

            $user = Database::fetchOne(
                'SELECT id, serial_number, full_name, email, created_at FROM users WHERE id = ?',
                [$userId]
            );

            return ['success' => true, 'user' => $user];
        } catch (\PDOException $e) {
            error_log("Auth::register error: " . $e->getMessage());
            return ['success' => false, 'message' => 'Registration failed. Please try again.'];
        }
    }

    // ─── Login ───────────────────────────────────────────────────────

    /**
     * Authenticate a user and create a session token.
     *
     * @return array{success: bool, token?: string, user?: array, message?: string}
     */
    public static function login(string $email, string $password): array
    {
        $email = trim(strtolower($email));

        $user = Database::fetchOne(
            'SELECT id, serial_number, full_name, email, password_hash, role, created_at FROM users WHERE email = ?',
            [$email]
        );

        if (!$user || !self::verifyPassword($password, $user['password_hash'])) {
            return ['success' => false, 'message' => 'Invalid email or password.'];
        }

        $token     = self::generateToken();
        $expiresAt = date('Y-m-d H:i:s', time() + SESSION_LIFETIME);

        Database::insert('sessions', [
            'user_id'    => $user['id'],
            'token'      => hash('sha256', $token),
            'ip_address' => $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0',
            'user_agent' => substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 255),
            'expires_at' => $expiresAt,
            'created_at' => date('Y-m-d H:i:s'),
        ]);

        // Update last login timestamp
        Database::update('users', ['last_login' => date('Y-m-d H:i:s')], 'id = ?', [$user['id']]);

        unset($user['password_hash']);

        return [
            'success' => true,
            'token'   => $token,
            'user'    => $user,
        ];
    }

    // ─── Logout ──────────────────────────────────────────────────────

    /**
     * Destroy a session by its token.
     */
    public static function logout(string $token): array
    {
        $hashed = hash('sha256', $token);
        $rows   = Database::delete('sessions', 'token = ?', [$hashed]);

        return $rows > 0
            ? ['success' => true, 'message' => 'Logged out successfully.']
            : ['success' => false, 'message' => 'Session not found or already expired.'];
    }

    // ─── Get Authenticated User ──────────────────────────────────────

    /**
     * Retrieve the user associated with a session token.
     *
     * @return array|null  User data (without password) or null if invalid/expired.
     */
    public static function getUser(string $token): ?array
    {
        $hashed = hash('sha256', $token);

        $session = Database::fetchOne(
            'SELECT user_id, expires_at FROM sessions WHERE token = ?',
            [$hashed]
        );

        if (!$session) {
            return null;
        }

        // Check expiry
        if (strtotime($session['expires_at']) < time()) {
            Database::delete('sessions', 'token = ?', [$hashed]);
            return null;
        }

        $user = Database::fetchOne(
            'SELECT id, serial_number, full_name, email, role, created_at, last_login FROM users WHERE id = ?',
            [$session['user_id']]
        );

        return $user ?: null;
    }

    // ─── Forgot Password ─────────────────────────────────────────────

    /**
     * Generate a password-reset token and email it.
     */
    public static function forgotPassword(string $email): array
    {
        $email = trim(strtolower($email));

        $user = Database::fetchOne(
            'SELECT id, full_name, email FROM users WHERE email = ?',
            [$email]
        );

        // Always return success to prevent user enumeration
        if (!$user) {
            return ['success' => true, 'message' => 'If that email exists, a reset link has been sent.'];
        }

        $token     = self::generateToken();
        $expiresAt = date('Y-m-d H:i:s', time() + self::RESET_EXPIRY);

        // Invalidate any previous reset tokens for this user
        Database::delete('password_resets', 'user_id = ?', [$user['id']]);

        Database::insert('password_resets', [
            'user_id'    => $user['id'],
            'token'      => hash('sha256', $token),
            'expires_at' => $expiresAt,
            'created_at' => date('Y-m-d H:i:s'),
        ]);

        $resetLink = SITE_URL . '/reset-password?token=' . urlencode($token);
        Mailer::sendPasswordReset($user['email'], $user['full_name'], $resetLink);

        return ['success' => true, 'message' => 'If that email exists, a reset link has been sent.'];
    }

    // ─── Reset Password ──────────────────────────────────────────────

    /**
     * Validate a reset token and set a new password.
     */
    public static function resetPassword(string $token, string $newPassword): array
    {
        if (strlen($newPassword) < 8) {
            return ['success' => false, 'message' => 'Password must be at least 8 characters.'];
        }

        $hashed = hash('sha256', $token);

        $reset = Database::fetchOne(
            'SELECT user_id, expires_at FROM password_resets WHERE token = ?',
            [$hashed]
        );

        if (!$reset) {
            return ['success' => false, 'message' => 'Invalid or expired reset token.'];
        }

        if (strtotime($reset['expires_at']) < time()) {
            Database::delete('password_resets', 'token = ?', [$hashed]);
            return ['success' => false, 'message' => 'Reset token has expired. Please request a new one.'];
        }

        Database::update(
            'users',
            [
                'password_hash' => self::hashPassword($newPassword),
                'updated_at'    => date('Y-m-d H:i:s'),
            ],
            'id = ?',
            [$reset['user_id']]
        );

        // Consume the token
        Database::delete('password_resets', 'token = ?', [$hashed]);

        // Invalidate all existing sessions for security
        Database::delete('sessions', 'user_id = ?', [$reset['user_id']]);

        return ['success' => true, 'message' => 'Password has been reset. Please log in with your new password.'];
    }

    // ─── Helpers ─────────────────────────────────────────────────────

    /**
     * Hash a password using bcrypt.
     */
    public static function hashPassword(string $password): string
    {
        return password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);
    }

    /**
     * Verify a password against a bcrypt hash.
     */
    public static function verifyPassword(string $password, string $hash): bool
    {
        return password_verify($password, $hash);
    }

    /**
     * Generate a cryptographically secure hex token.
     */
    public static function generateToken(): string
    {
        return bin2hex(random_bytes(self::TOKEN_BYTES));
    }

    // ─── Token extraction helper ─────────────────────────────────────

    /**
     * Extract Bearer token from the Authorization header.
     */
    public static function getBearerToken(): ?string
    {
        $header = $_SERVER['HTTP_AUTHORIZATION']
            ?? $_SERVER['REDIRECT_HTTP_AUTHORIZATION']
            ?? '';

        if (preg_match('/^Bearer\s+(.+)$/i', $header, $matches)) {
            return $matches[1];
        }

        return null;
    }
}
