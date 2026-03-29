<?php
/**
 * EchoSmart - Contact Form API
 *
 * POST /api/contact.php
 *
 * @package EchoSmart
 */

require_once __DIR__ . '/../includes/Database.php';
require_once __DIR__ . '/../includes/Mailer.php';

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
header('Access-Control-Allow-Headers: Content-Type');
header('Access-Control-Max-Age: 86400');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

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

$name    = trim($input['name']    ?? '');
$email   = trim($input['email']   ?? '');
$subject = trim($input['subject'] ?? '');
$message = trim($input['message'] ?? '');

// ─── Validation ──────────────────────────────────────────────────────
$errors = [];

if (strlen($name) < 2 || strlen($name) > 100) {
    $errors[] = 'Name must be between 2 and 100 characters.';
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $errors[] = 'A valid email address is required.';
}
if (strlen($subject) < 2 || strlen($subject) > 200) {
    $errors[] = 'Subject must be between 2 and 200 characters.';
}
if (strlen($message) < 10 || strlen($message) > 5000) {
    $errors[] = 'Message must be between 10 and 5000 characters.';
}

if (!empty($errors)) {
    http_response_code(422);
    echo json_encode(['success' => false, 'message' => implode(' ', $errors)]);
    exit;
}

// ─── Rate limiting (simple IP-based, 5 messages per hour) ────────────
$ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
try {
    $recentCount = Database::fetchOne(
        'SELECT COUNT(*) AS cnt FROM contact_messages WHERE ip_address = ? AND created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)',
        [$ip]
    );

    if ($recentCount && (int)$recentCount['cnt'] >= 5) {
        http_response_code(429);
        echo json_encode(['success' => false, 'message' => 'Too many messages. Please try again later.']);
        exit;
    }
} catch (\Throwable $e) {
    error_log("Contact rate-limit check: " . $e->getMessage());
}

// ─── Save to database ───────────────────────────────────────────────
try {
    Database::insert('contact_messages', [
        'name'       => $name,
        'email'      => $email,
        'subject'    => $subject,
        'message'    => $message,
        'ip_address' => $ip,
        'created_at' => date('Y-m-d H:i:s'),
    ]);
} catch (\Throwable $e) {
    error_log("Contact save error: " . $e->getMessage());
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Could not save your message. Please try again.']);
    exit;
}

// ─── Send email notification ─────────────────────────────────────────
try {
    Mailer::sendContactNotification($name, $email, $subject, $message);
} catch (\Throwable $e) {
    error_log("Contact email error: " . $e->getMessage());
    // Don't fail the request; the message was saved to the DB
}

echo json_encode(['success' => true, 'message' => 'Thank you! Your message has been sent.']);
