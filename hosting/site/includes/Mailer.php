<?php
/**
 * EchoSmart - Mailer (authenticated SMTP primary)
 *
 * Primary: Authenticated SMTP via 127.0.0.1:465 (IPv4, as noreply@echosmart.me).
 *          This ensures Exim DKIM-signs the email and does NOT add a mismatched
 *          Sender header (which causes spam).
 * Fallback: PHP mail() with -f envelope sender.
 *
 * Key anti-spam measures:
 * - Authenticated SMTP = proper DKIM signing by Exim
 * - No Sender header mismatch (mail() adds Sender: cpaneluser@hostname)
 * - Clean readable plain-text alternative
 * - No Precedence:bulk (that marks as marketing = spam)
 * - List-Unsubscribe for Gmail compliance
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
        $subject  = 'Welcome to EchoSmart';
        $dashUrl  = SITE_URL . '/dashboard';

        $plain = "Welcome to EchoSmart!\n\n"
               . "Hi {$name},\n\n"
               . "Your account has been created successfully. You can now access\n"
               . "your EchoSmart dashboard to monitor your IoT devices.\n\n"
               . "Dashboard: {$dashUrl}\n\n"
               . "If you did not create this account, please ignore this email.\n\n"
               . "-- \nEchoSmart\nhttps://echosmart.me\n";

        $html = self::wrapHtml("
            <h1 style='color:#00C853;margin:0 0 16px'>Welcome to EchoSmart!</h1>
            <p>Hi <strong>" . htmlspecialchars($name, ENT_QUOTES, 'UTF-8') . "</strong>,</p>
            <p>Your account has been created successfully. You can now access your
               EchoSmart dashboard to monitor your IoT devices in real time.</p>
            <p style='margin:24px 0'>
                <a href='{$dashUrl}'
                   style='background:#00C853;color:#fff;padding:12px 28px;
                          text-decoration:none;border-radius:6px;font-weight:600'>
                    Go to Dashboard
                </a>
            </p>
            <p style='color:#888;font-size:13px'>
                If you did not create this account, please ignore this email.
            </p>
        ");

        return self::sendEmail($email, $subject, $plain, $html);
    }

    /**
     * Send a password-reset email with a unique link.
     */
    public static function sendPasswordReset(string $email, string $name, string $resetLink): bool
    {
        $subject = 'Reset your EchoSmart password';

        $plain = "Password Reset\n\n"
               . "Hi {$name},\n\n"
               . "We received a request to reset your password. Use the link\n"
               . "below to choose a new one. This link expires in 1 hour.\n\n"
               . "Reset: {$resetLink}\n\n"
               . "If you did not request this, you can safely ignore this email.\n"
               . "Your password will remain unchanged.\n\n"
               . "-- \nEchoSmart\nhttps://echosmart.me\n";

        $html = self::wrapHtml("
            <h1 style='color:#00C853;margin:0 0 16px'>Password Reset</h1>
            <p>Hi <strong>" . htmlspecialchars($name, ENT_QUOTES, 'UTF-8') . "</strong>,</p>
            <p>We received a request to reset your password. Click the button below
               to choose a new one. This link expires in 1 hour.</p>
            <p style='margin:24px 0'>
                <a href='" . htmlspecialchars($resetLink, ENT_QUOTES, 'UTF-8') . "'
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

        return self::sendEmail($email, $subject, $plain, $html);
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
        $safeName  = htmlspecialchars($name, ENT_QUOTES, 'UTF-8');
        $safeEmail = htmlspecialchars($email, ENT_QUOTES, 'UTF-8');
        $safeSubj  = htmlspecialchars($subject, ENT_QUOTES, 'UTF-8');
        $safeMsg   = nl2br(htmlspecialchars($message, ENT_QUOTES, 'UTF-8'));

        $plain = "New Contact Message\n\n"
               . "Name:    {$name}\n"
               . "Email:   {$email}\n"
               . "Subject: {$subject}\n\n"
               . "Message:\n{$message}\n\n"
               . "-- \nEchoSmart\nhttps://echosmart.me\n";

        $html = self::wrapHtml("
            <h1 style='color:#00C853;margin:0 0 16px'>New Contact Message</h1>
            <table style='width:100%;border-collapse:collapse'>
                <tr>
                    <td style='padding:8px;border-bottom:1px solid #eee;font-weight:600;width:120px'>Name</td>
                    <td style='padding:8px;border-bottom:1px solid #eee'>{$safeName}</td>
                </tr>
                <tr>
                    <td style='padding:8px;border-bottom:1px solid #eee;font-weight:600'>Email</td>
                    <td style='padding:8px;border-bottom:1px solid #eee'>{$safeEmail}</td>
                </tr>
                <tr>
                    <td style='padding:8px;border-bottom:1px solid #eee;font-weight:600'>Subject</td>
                    <td style='padding:8px;border-bottom:1px solid #eee'>{$safeSubj}</td>
                </tr>
            </table>
            <div style='margin-top:16px;padding:16px;background:#f8f9fa;border-radius:6px'>
                {$safeMsg}
            </div>
        ");

        return self::sendEmail(ADMIN_EMAIL, "Contact from {$name}", $plain, $html);
    }

    // ─── Core: authenticated SMTP (primary) ─────────────────────────

    /**
     * Send email. Tries authenticated SMTP first (DKIM-signed), then mail().
     */
    private static function sendEmail(string $to, string $subject, string $plainText, string $htmlBody): bool
    {
        // Primary: authenticated SMTP → Exim DKIM-signs the message
        $sent = self::sendViaSmtp($to, $subject, $plainText, $htmlBody);

        if (!$sent) {
            error_log("Mailer: SMTP failed, falling back to mail() for {$to}");
            return self::sendViaMail($to, $subject, $plainText, $htmlBody);
        }

        return true;
    }

    // ─── Authenticated SMTP via IPv4 loopback ───────────────────────

    private static function sendViaSmtp(string $to, string $subject, string $plainText, string $htmlBody): bool
    {
        $from     = SMTP_USER;
        $fromName = SMTP_FROM_NAME;
        $port     = SMTP_PORT;
        $user     = SMTP_USER;
        $pass     = SMTP_PASS;

        $boundary = bin2hex(random_bytes(16));
        $msgId    = bin2hex(random_bytes(16)) . '.' . time();

        // ── Build RFC 5322 message ──
        $msg  = "MIME-Version: 1.0\r\n";
        $msg .= "From: {$fromName} <{$from}>\r\n";
        $msg .= "To: <{$to}>\r\n";
        $msg .= "Reply-To: <" . ADMIN_EMAIL . ">\r\n";
        $msg .= "Subject: {$subject}\r\n";
        $msg .= "Date: " . gmdate('r') . "\r\n";
        $msg .= "Message-ID: <{$msgId}@echosmart.me>\r\n";
        $msg .= "Content-Type: multipart/alternative; boundary=\"{$boundary}\"\r\n";
        $msg .= "List-Unsubscribe: <mailto:" . ADMIN_EMAIL . "?subject=unsubscribe>\r\n";
        $msg .= "List-Unsubscribe-Post: List-Unsubscribe=One-Click\r\n";
        $msg .= "\r\n";

        // Plain text part
        $msg .= "--{$boundary}\r\n";
        $msg .= "Content-Type: text/plain; charset=UTF-8\r\n";
        $msg .= "Content-Transfer-Encoding: quoted-printable\r\n\r\n";
        $msg .= quoted_printable_encode($plainText) . "\r\n\r\n";

        // HTML part
        $msg .= "--{$boundary}\r\n";
        $msg .= "Content-Type: text/html; charset=UTF-8\r\n";
        $msg .= "Content-Transfer-Encoding: quoted-printable\r\n\r\n";
        $msg .= quoted_printable_encode($htmlBody) . "\r\n\r\n";

        $msg .= "--{$boundary}--\r\n";

        try {
            $ctx = stream_context_create([
                'ssl' => [
                    'verify_peer'       => false,
                    'verify_peer_name'  => false,
                    'allow_self_signed' => true,
                ],
            ]);
            $socket = @stream_socket_client(
                "ssl://127.0.0.1:{$port}",
                $errno, $errstr, 30,
                STREAM_CLIENT_CONNECT,
                $ctx
            );
            if (!$socket) {
                error_log("Mailer SMTP: connect failed 127.0.0.1:{$port} - {$errstr} ({$errno})");
                return false;
            }

            stream_set_timeout($socket, 30);

            self::smtpRead($socket);
            self::smtpCommand($socket, "EHLO echosmart.me", 250);
            self::smtpCommand($socket, "AUTH LOGIN", 334);
            self::smtpCommand($socket, base64_encode($user), 334);
            self::smtpCommand($socket, base64_encode($pass), 235);
            self::smtpCommand($socket, "MAIL FROM:<{$from}>", 250);
            self::smtpCommand($socket, "RCPT TO:<{$to}>", 250);
            self::smtpCommand($socket, "DATA", 354);
            fwrite($socket, $msg . "\r\n.\r\n");
            self::smtpExpect($socket, 250);
            fwrite($socket, "QUIT\r\n");
            fclose($socket);
            return true;

        } catch (\Exception $e) {
            error_log("Mailer SMTP: " . $e->getMessage());
            if (isset($socket) && is_resource($socket)) {
                fclose($socket);
            }
            return false;
        }
    }

    // ─── Fallback: PHP mail() ───────────────────────────────────────

    private static function sendViaMail(string $to, string $subject, string $plainText, string $htmlBody): bool
    {
        $from     = SMTP_USER;
        $fromName = SMTP_FROM_NAME;
        $boundary = bin2hex(random_bytes(16));
        $msgId    = bin2hex(random_bytes(16)) . '.' . time();

        $headers  = "From: {$fromName} <{$from}>\r\n";
        $headers .= "Reply-To: " . ADMIN_EMAIL . "\r\n";
        $headers .= "MIME-Version: 1.0\r\n";
        $headers .= "Date: " . gmdate('r') . "\r\n";
        $headers .= "Message-ID: <{$msgId}@echosmart.me>\r\n";
        $headers .= "Content-Type: multipart/alternative; boundary=\"{$boundary}\"\r\n";
        $headers .= "List-Unsubscribe: <mailto:" . ADMIN_EMAIL . "?subject=unsubscribe>\r\n";
        $headers .= "List-Unsubscribe-Post: List-Unsubscribe=One-Click\r\n";

        $body  = "--{$boundary}\r\n";
        $body .= "Content-Type: text/plain; charset=UTF-8\r\n";
        $body .= "Content-Transfer-Encoding: quoted-printable\r\n\r\n";
        $body .= quoted_printable_encode($plainText) . "\r\n\r\n";
        $body .= "--{$boundary}\r\n";
        $body .= "Content-Type: text/html; charset=UTF-8\r\n";
        $body .= "Content-Transfer-Encoding: quoted-printable\r\n\r\n";
        $body .= quoted_printable_encode($htmlBody) . "\r\n\r\n";
        $body .= "--{$boundary}--\r\n";

        $sent = @mail($to, $subject, $body, $headers, "-f {$from}");
        if (!$sent) {
            error_log("Mailer mail(): failed for {$to}");
        }
        return (bool) $sent;
    }

    // ─── SMTP helpers ────────────────────────────────────────────────

    private static function smtpRead($socket): string
    {
        $response = '';
        while ($line = fgets($socket, 512)) {
            $response .= $line;
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
        <tr>
            <td style="background:linear-gradient(135deg,#00C853 0%,#00E676 100%);padding:28px 32px;text-align:center">
                <h2 style="color:#fff;margin:0;font-size:22px;letter-spacing:1px">EchoSmart</h2>
                <p style="color:rgba(255,255,255,0.85);margin:4px 0 0;font-size:13px">Smart IoT Monitoring</p>
            </td>
        </tr>
        <tr>
            <td style="padding:32px">{$content}</td>
        </tr>
        <tr>
            <td style="padding:20px 32px;background:#fafafa;border-top:1px solid #eee;text-align:center">
                <p style="color:#aaa;font-size:12px;margin:0">
                    &copy; {$year} EchoSmart<br>
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
