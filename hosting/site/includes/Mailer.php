<?php
/**
 * EchoSmart - SMTP Mailer (socket-based, no Composer required)
 *
 * Sends emails via an SSL socket connection to the SMTP server.
 *
 * @package EchoSmart
 */

require_once __DIR__ . '/config.php';

class Mailer
{
    // ─── Public API ──────────────────────────────────────────────────

    /**
     * Send a welcome email to a new user.
     */
    public static function sendWelcome(string $email, string $name): bool
    {
        $subject = 'Welcome to EchoSmart!';
        $body = self::wrapHtml("
            <h1 style='color:#00C853;margin:0 0 16px'>Welcome to EchoSmart!</h1>
            <p>Hi <strong>{$name}</strong>,</p>
            <p>Your account has been created successfully. You can now access your
               EchoSmart dashboard to monitor your IoT devices in real time.</p>
            <p style='margin:24px 0'>
                <a href='" . SITE_URL . "/dashboard'
                   style='background:#00C853;color:#fff;padding:12px 28px;
                          text-decoration:none;border-radius:6px;font-weight:600'>
                    Go to Dashboard
                </a>
            </p>
            <p style='color:#888;font-size:13px'>
                If you did not create this account, please ignore this email.
            </p>
        ");

        return self::sendEmail($email, $subject, $body);
    }

    /**
     * Send a password-reset email with a unique link.
     */
    public static function sendPasswordReset(string $email, string $name, string $resetLink): bool
    {
        $subject = 'Reset Your EchoSmart Password';
        $body = self::wrapHtml("
            <h1 style='color:#00C853;margin:0 0 16px'>Password Reset</h1>
            <p>Hi <strong>{$name}</strong>,</p>
            <p>We received a request to reset your password. Click the button below
               to choose a new one. This link expires in 1 hour.</p>
            <p style='margin:24px 0'>
                <a href='{$resetLink}'
                   style='background:#00C853;color:#fff;padding:12px 28px;
                          text-decoration:none;border-radius:6px;font-weight:600'>
                    Reset Password
                </a>
            </p>
            <p style='color:#888;font-size:13px'>
                If you did not request this, you can safely ignore this email.
                Your password will remain unchanged.
            </p>
        ");

        return self::sendEmail($email, $subject, $body);
    }

    /**
     * Notify the admin about a new contact-form submission.
     */
    public static function sendContactNotification(
        string $name,
        string $email,
        string $subject,
        string $message
    ): bool {
        $safeMsg = nl2br(htmlspecialchars($message, ENT_QUOTES, 'UTF-8'));
        $body = self::wrapHtml("
            <h1 style='color:#00C853;margin:0 0 16px'>New Contact Message</h1>
            <table style='width:100%;border-collapse:collapse'>
                <tr>
                    <td style='padding:8px;border-bottom:1px solid #eee;font-weight:600;width:120px'>Name</td>
                    <td style='padding:8px;border-bottom:1px solid #eee'>" . htmlspecialchars($name, ENT_QUOTES, 'UTF-8') . "</td>
                </tr>
                <tr>
                    <td style='padding:8px;border-bottom:1px solid #eee;font-weight:600'>Email</td>
                    <td style='padding:8px;border-bottom:1px solid #eee'>" . htmlspecialchars($email, ENT_QUOTES, 'UTF-8') . "</td>
                </tr>
                <tr>
                    <td style='padding:8px;border-bottom:1px solid #eee;font-weight:600'>Subject</td>
                    <td style='padding:8px;border-bottom:1px solid #eee'>" . htmlspecialchars($subject, ENT_QUOTES, 'UTF-8') . "</td>
                </tr>
            </table>
            <div style='margin-top:16px;padding:16px;background:#f8f9fa;border-radius:6px'>
                {$safeMsg}
            </div>
        ");

        return self::sendEmail(ADMIN_EMAIL, "[EchoSmart] Contact: {$subject}", $body);
    }

    // ─── Core SMTP sender ────────────────────────────────────────────

    /**
     * Send an email via raw SMTP over an SSL socket.
     */
    private static function sendEmail(string $to, string $subject, string $htmlBody): bool
    {
        $from     = SMTP_USER;
        $fromName = SMTP_FROM_NAME;
        $host     = SMTP_HOST;
        $port     = SMTP_PORT;
        $user     = SMTP_USER;
        $pass     = SMTP_PASS;

        $boundary = bin2hex(random_bytes(16));

        // Build MIME message
        $headers  = "MIME-Version: 1.0\r\n";
        $headers .= "From: {$fromName} <{$from}>\r\n";
        $headers .= "To: {$to}\r\n";
        $headers .= "Subject: {$subject}\r\n";
        $headers .= "Date: " . date('r') . "\r\n";
        $headers .= "Message-ID: <" . bin2hex(random_bytes(16)) . "@echosmart.me>\r\n";
        $headers .= "Content-Type: multipart/alternative; boundary=\"{$boundary}\"\r\n";
        $headers .= "\r\n";

        $plainText = strip_tags(str_replace(['<br>', '<br/>', '<br />'], "\n", $htmlBody));

        $body  = "--{$boundary}\r\n";
        $body .= "Content-Type: text/plain; charset=UTF-8\r\n";
        $body .= "Content-Transfer-Encoding: 8bit\r\n\r\n";
        $body .= $plainText . "\r\n\r\n";
        $body .= "--{$boundary}\r\n";
        $body .= "Content-Type: text/html; charset=UTF-8\r\n";
        $body .= "Content-Transfer-Encoding: 8bit\r\n\r\n";
        $body .= $htmlBody . "\r\n\r\n";
        $body .= "--{$boundary}--\r\n";

        $message = $headers . $body;

        try {
            $socket = @fsockopen("ssl://{$host}", $port, $errno, $errstr, 30);
            if (!$socket) {
                error_log("Mailer: could not connect to {$host}:{$port} – {$errstr} ({$errno})");
                return false;
            }

            stream_set_timeout($socket, 30);

            // Read greeting
            self::smtpRead($socket);

            // EHLO
            self::smtpCommand($socket, "EHLO echosmart.me", 250);

            // AUTH LOGIN
            self::smtpCommand($socket, "AUTH LOGIN", 334);
            self::smtpCommand($socket, base64_encode($user), 334);
            self::smtpCommand($socket, base64_encode($pass), 235);

            // Envelope
            self::smtpCommand($socket, "MAIL FROM:<{$from}>", 250);
            self::smtpCommand($socket, "RCPT TO:<{$to}>", 250);

            // DATA
            self::smtpCommand($socket, "DATA", 354);
            fwrite($socket, $message . "\r\n.\r\n");
            self::smtpExpect($socket, 250);

            // QUIT
            fwrite($socket, "QUIT\r\n");
            fclose($socket);

            return true;
        } catch (\Exception $e) {
            error_log("Mailer: " . $e->getMessage());
            if (isset($socket) && is_resource($socket)) {
                fclose($socket);
            }
            return false;
        }
    }

    // ─── SMTP helpers ────────────────────────────────────────────────

    private static function smtpRead($socket): string
    {
        $response = '';
        while ($line = fgets($socket, 512)) {
            $response .= $line;
            // A space at position 3 means this is the last line of the response
            if (isset($line[3]) && $line[3] === ' ') {
                break;
            }
        }
        return $response;
    }

    private static function smtpCommand($socket, string $command, int $expectedCode): string
    {
        fwrite($socket, $command . "\r\n");
        return self::smtpExpect($socket, $expectedCode);
    }

    private static function smtpExpect($socket, int $expectedCode): string
    {
        $response = self::smtpRead($socket);
        $code = (int)substr($response, 0, 3);
        if ($code !== $expectedCode) {
            throw new \RuntimeException(
                "SMTP error: expected {$expectedCode}, got {$code}. Response: {$response}"
            );
        }
        return $response;
    }

    // ─── HTML template wrapper ───────────────────────────────────────

    private static function wrapHtml(string $content): string
    {
        $year = date('Y');
        return <<<HTML
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f5;padding:32px 0">
<tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.06)">
        <!-- Header -->
        <tr>
            <td style="background:linear-gradient(135deg,#00C853 0%,#00E676 100%);padding:28px 32px;text-align:center">
                <h2 style="color:#fff;margin:0;font-size:22px;letter-spacing:1px">🌿 EchoSmart</h2>
                <p style="color:rgba(255,255,255,0.85);margin:4px 0 0;font-size:13px">Smart IoT Monitoring Solutions</p>
            </td>
        </tr>
        <!-- Body -->
        <tr>
            <td style="padding:32px">{$content}</td>
        </tr>
        <!-- Footer -->
        <tr>
            <td style="padding:20px 32px;background:#fafafa;border-top:1px solid #eee;text-align:center">
                <p style="color:#aaa;font-size:12px;margin:0">
                    &copy; {$year} EchoSmart &mdash; Smart IoT Monitoring Solutions<br>
                    <a href="https://echosmart.me" style="color:#00C853;text-decoration:none">echosmart.me</a>
                </p>
            </td>
        </tr>
    </table>
</td></tr>
</table>
</body>
</html>
HTML;
    }
}
