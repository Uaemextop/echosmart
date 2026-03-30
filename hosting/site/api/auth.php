<?php
/**
 * EchoSmart - Authentication REST API
 *
 * POST /api/auth.php
 * Actions: register, login, logout, me, forgot-password, reset-password
 *
 * @package EchoSmart
 */

require_once __DIR__ . '/../includes/Auth.php';

// ─── CORS & Headers ──────────────────────────────────────────────────
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
$allowed = [SITE_URL, 'https://www.echosmart.me'];
if (in_array($origin, $allowed, true)) {
    header("Access-Control-Allow-Origin: {$origin}");
} else {
    header('Access-Control-Allow-Origin: ' . SITE_URL);
}

header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Access-Control-Max-Age: 86400');

// Handle CORS preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

// ─── Only accept POST ────────────────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed.']);
    exit;
}

// ─── Parse input ─────────────────────────────────────────────────────
$contentType = $_SERVER['CONTENT_TYPE'] ?? '';
if (stripos($contentType, 'application/json') !== false) {
    $input = json_decode(file_get_contents('php://input'), true) ?? [];
} else {
    $input = $_POST;
}

$action = $input['action'] ?? '';

// ─── Route actions ───────────────────────────────────────────────────
try {
    switch ($action) {

        // ── Register ─────────────────────────────────────────────
        case 'register':
            $serial   = $input['serial_number'] ?? '';
            $name     = $input['full_name']     ?? '';
            $email    = $input['email']         ?? '';
            $password = $input['password']      ?? '';

            if (!$serial || !$name || !$email || !$password) {
                jsonResponse(false, 'All fields are required: serial_number, full_name, email, password.', 422);
            }

            $result = Auth::register($serial, $name, $email, $password);
            jsonResponse(
                $result['success'],
                $result['message'] ?? 'Registration successful.',
                $result['success'] ? 201 : 422,
                $result['success'] ? ['user' => $result['user']] : []
            );
            break;

        // ── Login ────────────────────────────────────────────────
        case 'login':
            $email    = $input['email']    ?? '';
            $password = $input['password'] ?? '';

            if (!$email || !$password) {
                jsonResponse(false, 'Email and password are required.', 422);
            }

            $result = Auth::login($email, $password);
            jsonResponse(
                $result['success'],
                $result['message'] ?? 'Login successful.',
                $result['success'] ? 200 : 401,
                $result['success'] ? ['token' => $result['token'], 'user' => $result['user']] : []
            );
            break;

        // ── Logout ───────────────────────────────────────────────
        case 'logout':
            $token = Auth::getBearerToken() ?? ($input['token'] ?? '');
            if (!$token) {
                jsonResponse(false, 'Token is required.', 401);
            }

            $result = Auth::logout($token);
            jsonResponse($result['success'], $result['message']);
            break;

        // ── Get current user ─────────────────────────────────────
        case 'me':
            $token = Auth::getBearerToken();
            if (!$token) {
                jsonResponse(false, 'Authorization token is required.', 401);
            }

            $user = Auth::getUser($token);
            if (!$user) {
                jsonResponse(false, 'Invalid or expired session.', 401);
            }

            jsonResponse(true, 'Authenticated.', 200, ['user' => $user]);
            break;

        // ── Forgot password ──────────────────────────────────────
        case 'forgot-password':
            $email = $input['email'] ?? '';
            if (!$email) {
                jsonResponse(false, 'Email is required.', 422);
            }

            $result = Auth::forgotPassword($email);
            jsonResponse($result['success'], $result['message']);
            break;

        // ── Reset password ───────────────────────────────────────
        case 'reset-password':
            $token       = $input['token']    ?? '';
            $newPassword = $input['password'] ?? '';

            if (!$token || !$newPassword) {
                jsonResponse(false, 'Token and new password are required.', 422);
            }

            $result = Auth::resetPassword($token, $newPassword);
            jsonResponse(
                $result['success'],
                $result['message'],
                $result['success'] ? 200 : 400
            );
            break;

        // ── Unknown action ───────────────────────────────────────
        default:
            jsonResponse(false, 'Unknown action. Valid: register, login, logout, me, forgot-password, reset-password.', 400);
    }
} catch (\Throwable $e) {
    error_log("API auth error: " . $e->getMessage());
    jsonResponse(false, 'An internal error occurred. Please try again later.', 500);
}

// ─── JSON response helper ────────────────────────────────────────────

function jsonResponse(bool $success, string $message, int $httpCode = 200, array $extra = []): void
{
    http_response_code($httpCode);
    echo json_encode(array_merge(['success' => $success, 'message' => $message], $extra), JSON_UNESCAPED_UNICODE);
    exit;
}
