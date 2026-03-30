<?php
/**
 * EchoSmart FakeNTP — PHP HTTP Time Server
 *
 * Serves current time over HTTP/HTTPS for IoT devices that cannot
 * reach standard NTP servers (port 123/UDP).
 *
 * Deploy to: public_html/ntp.echosmart.me/
 * Subdomain: ntp.echosmart.me
 *
 * Endpoints:
 *   GET /            — HTML status page with live clock
 *   GET /time        — JSON time response
 *   GET /time?fmt=unix — Plain Unix timestamp
 *   GET /time?fmt=iso  — Plain ISO 8601
 *   GET /health      — Health check
 *
 * @package EchoSmart
 */

date_default_timezone_set('UTC');

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$path = rtrim($path, '/') ?: '/';

// ─── CORS + Cache headers ────────────────────────────────────────────
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, HEAD, OPTIONS');
header('Cache-Control: no-store, no-cache, must-revalidate');
header('X-Content-Type-Options: nosniff');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

// ─── Routing ─────────────────────────────────────────────────────────

switch ($path) {
    case '/time':
        handleTime();
        break;
    case '/health':
        handleHealth();
        break;
    case '/':
    case '/index.php':
        handleIndex();
        break;
    default:
        sendJson(['error' => 'Not Found'], 404);
}

// ─── Handlers ────────────────────────────────────────────────────────

function handleTime(): void
{
    $now    = microtime(true);
    $dt     = new DateTimeImmutable('@' . sprintf('%.6f', $now));
    $iso    = $dt->format('Y-m-d\TH:i:s.u\Z');
    $fmt    = $_GET['fmt'] ?? 'json';

    if ($fmt === 'unix') {
        sendText(sprintf('%.6f', $now));
        return;
    }
    if ($fmt === 'iso') {
        sendText($iso);
        return;
    }

    sendJson([
        'unix'     => round($now, 6),
        'iso'      => $iso,
        'date'     => $dt->format('Y-m-d'),
        'time'     => $dt->format('H:i:s.u'),
        'timezone' => 'UTC',
        'server'   => 'EchoSmart FakeNTP',
        'version'  => '1.0.0',
    ]);
}

function handleHealth(): void
{
    sendJson([
        'status'  => 'ok',
        'service' => 'fakentp',
        'version' => '1.0.0',
    ]);
}

function handleIndex(): void
{
    $now  = new DateTimeImmutable('now', new DateTimeZone('UTC'));
    $unix = microtime(true);
    $time = $now->format('H:i:s');
    $date = $now->format('l, F j, Y');
    $ver  = '1.0.0';

    header('Content-Type: text/html; charset=utf-8');
    echo <<<HTML
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EchoSmart FakeNTP</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:#000;color:#E0E0E0;font-family:-apple-system,BlinkMacSystemFont,
       'Segoe UI',Roboto,sans-serif;display:flex;justify-content:center;
       align-items:center;min-height:100vh}
  .card{background:#111;border-radius:16px;padding:48px;max-width:520px;
        width:90%;box-shadow:0 4px 24px rgba(0,230,118,0.08);text-align:center}
  h1{color:#00E676;font-size:28px;margin-bottom:8px}
  .subtitle{color:#888;font-size:14px;margin-bottom:32px}
  .time{font-size:48px;font-weight:700;color:#00E676;
        font-variant-numeric:tabular-nums;margin:24px 0}
  .date{font-size:18px;color:#bbb;margin-bottom:24px}
  .unix{font-size:14px;color:#666;font-family:monospace}
  .api{margin-top:32px;text-align:left;background:#0a0a0a;
       border-radius:8px;padding:20px}
  .api h3{color:#00E676;font-size:14px;margin-bottom:12px}
  .api code{display:block;color:#888;font-size:12px;margin:4px 0;font-family:monospace}
  .api a{color:#00BCD4;text-decoration:none}
  .badge{display:inline-block;background:#00E676;color:#000;font-size:11px;
         font-weight:600;padding:2px 8px;border-radius:4px;margin-left:8px}
</style>
</head>
<body>
<div class="card">
  <h1>EchoSmart FakeNTP</h1>
  <p class="subtitle">HTTP-based Time Server for IoT Devices</p>
  <div class="time" id="clock">{$time}</div>
  <div class="date" id="date">{$date}</div>
  <div class="unix">Unix: <span id="unix">{$unix}</span></div>
  <div class="api">
    <h3>API Endpoints <span class="badge">v{$ver}</span></h3>
    <code>GET <a href="/time">/time</a> — JSON (unix + iso + date)</code>
    <code>GET <a href="/time?fmt=unix">/time?fmt=unix</a> — Plain Unix timestamp</code>
    <code>GET <a href="/time?fmt=iso">/time?fmt=iso</a> — Plain ISO 8601</code>
    <code>GET <a href="/health">/health</a> — Health check</code>
  </div>
</div>
<script>
function tick(){
  const now=new Date();
  document.getElementById('clock').textContent=now.toISOString().slice(11,19);
  document.getElementById('date').textContent=
    now.toLocaleDateString('en-US',{weekday:'long',year:'numeric',month:'long',day:'numeric'});
  document.getElementById('unix').textContent=(now.getTime()/1000).toFixed(6);
}
setInterval(tick,200);
</script>
</body>
</html>
HTML;
}

// ─── Response helpers ────────────────────────────────────────────────

function sendJson(array $data, int $status = 200): void
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
}

function sendText(string $text, int $status = 200): void
{
    http_response_code($status);
    header('Content-Type: text/plain; charset=utf-8');
    echo $text;
}
