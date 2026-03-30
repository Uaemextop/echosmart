# EchoSmart Hosting Configuration

## Domain & Hosting

| Item              | Value                                        |
|-------------------|----------------------------------------------|
| Domain            | echosmart.me                                 |
| Hosting Provider  | Namecheap (cPanel Shared Hosting)            |
| Server IP         | 68.65.123.247                                |
| cPanel URL        | https://business191.web-hosting.com:2083     |
| SSH Port          | 21098                                        |
| Webmail           | https://business191.web-hosting.com:2096     |

---

## SSL Certificate (Wildcard)

| Item                  | Value                                                    |
|-----------------------|----------------------------------------------------------|
| Type                  | Wildcard ECC (ec-256)                                    |
| Domains               | `echosmart.me` + `*.echosmart.me`                       |
| Issuer                | ZeroSSL ECC Domain Secure Site CA                        |
| Tool                  | acme.sh v3.1.3                                           |
| Cert Location         | `~/.acme.sh/echosmart.me_ecc/echosmart.me.cer`          |
| Key Location          | `~/.acme.sh/echosmart.me_ecc/echosmart.me.key`          |
| Full-chain Location   | `~/.acme.sh/echosmart.me_ecc/fullchain.cer`             |
| Deploy Hook           | `cpanel_uapi` (auto-installs to cPanel on renewal)      |
| DNS Validation Plugin | `dns_cpanel` (uses cPanel API token)                    |
| Auto-Renewal          | Daily cron at 8:52 AM via acme.sh `--cron`              |
| Next Renewal          | ~2026-04-27 (60 days before expiry, automatic)          |

### Manual Renewal (if needed)

```bash
~/.acme.sh/acme.sh --renew -d echosmart.me -d "*.echosmart.me" --ecc --force
~/.acme.sh/acme.sh --deploy -d echosmart.me -d "*.echosmart.me" --deploy-hook cpanel_uapi --ecc
```

---

## Email Accounts

| Email                    | Purpose                        |
|--------------------------|--------------------------------|
| admin@echosmart.me       | Admin / DMARC reports          |
| info@echosmart.me        | General inquiries              |
| support@echosmart.me     | Customer support               |
| noreply@echosmart.me     | System notifications           |
| enterprise@echosmart.me  | Enterprise inquiries           |

### Email Forwarders

- `info@echosmart.me` → `admin@echosmart.me`
- Default (catch-all) → `admin@echosmart.me`

### Mail Server Settings

| Setting       | Incoming (IMAP)                         | Outgoing (SMTP)                         |
|---------------|-----------------------------------------|-----------------------------------------|
| Server        | mail.echosmart.me                       | mail.echosmart.me                       |
| Port (SSL)    | 993                                     | 465                                     |
| Port (TLS)    | 143                                     | 587                                     |
| Auth          | Full email address                      | Full email address                      |

---

## DNS Records

| Type   | Name               | Value / Target                                                                 |
|--------|--------------------|--------------------------------------------------------------------------------|
| A      | echosmart.me       | 68.65.123.247                                                                  |
| A      | mail               | 68.65.123.247                                                                  |
| A      | ntp                | 68.65.123.247                                                                  |
| A      | ftp                | 68.65.123.247                                                                  |
| A      | cpanel             | 68.65.123.247                                                                  |
| A      | webmail            | 68.65.123.247                                                                  |
| A      | whm                | 68.65.123.247                                                                  |
| A      | cpcontacts         | 68.65.123.247                                                                  |
| A      | cpcalendars        | 68.65.123.247                                                                  |
| A      | api                | 68.65.123.247                                                                  |
| A      | app                | 68.65.123.247                                                                  |
| A      | * (wildcard)       | 68.65.123.247                                                                  |
| CNAME  | www                | echosmart.me                                                                   |
| MX     | echosmart.me       | mx1-hosting.jellyfish.systems (pri 5)                                          |
| MX     | echosmart.me       | mx2-hosting.jellyfish.systems (pri 10)                                         |
| MX     | echosmart.me       | mx3-hosting.jellyfish.systems (pri 20)                                         |
| TXT    | echosmart.me (SPF) | `v=spf1 +a +mx +ip4:68.65.123.247 +ip4:63.250.38.86 +ip4:68.65.123.176 include:spf.web-hosting.com -all` |
| TXT    | _dmarc (DMARC)     | `v=DMARC1; p=none; sp=none; adkim=r; aspf=r; rua=mailto:admin@echosmart.me; ruf=mailto:admin@echosmart.me; pct=100; fo=1;` |
| TXT    | default._domainkey | DKIM RSA 2048-bit public key                                                  |
| NS     | echosmart.me       | dns1.namecheaphosting.com                                                      |
| NS     | echosmart.me       | dns2.namecheaphosting.com                                                      |

### DNS Zone Setup Commands (cPanel UAPI)

```bash
# Add A record for ntp subdomain (if wildcard doesn't cover it)
uapi DNS mass_edit_zone zone=echosmart.me serial=XXXXXXXXXX \
  add='{"dname":"ntp","ttl":14400,"record_type":"A","data":["68.65.123.247"]}'
```

---

## Auto-Renewal (Cron Jobs)

```
# SSL auto-renewal (daily at 8:52 AM)
52 8 * * * "/home/eduardoc3677/.acme.sh"/acme.sh --cron --home "/home/eduardoc3677/.acme.sh" > /dev/null

# WordPress cron (every 30 minutes)
6,36 * * * * /opt/alt/php82/usr/bin/php -q "/home/eduardoc3677/public_html/wp-cron.php"

# Softaculous auto-backup (daily at 2:34 PM)
34 14 * * * /usr/local/cpanel/3rdparty/bin/php -d disable_functions="" "/usr/local/cpanel/whostmgr/docroot/cgi/softaculous"/cli.php --backup --auto=1 --insid=26_29636
```

The acme.sh cron runs daily and automatically:
1. Checks if the certificate is due for renewal (within 30 days of expiry)
2. Issues a new certificate via ZeroSSL using DNS validation through the cPanel API
3. Deploys the renewed certificate to cPanel via the `cpanel_uapi` deploy hook

---

## Email Security (anti-spam)

The mail server at `mail.echosmart.me` uses the **wildcard SSL certificate** for secure
connections on all protocols:

| Protocol   | Port | Security | Server             |
|------------|------|----------|--------------------|
| IMAP       | 993  | SSL/TLS  | mail.echosmart.me  |
| IMAP       | 143  | STARTTLS | mail.echosmart.me  |
| SMTP       | 465  | SSL/TLS  | mail.echosmart.me  |
| SMTP       | 587  | STARTTLS | mail.echosmart.me  |

### Anti-Spam / Deliverability Records

| Record | Status | Details |
|--------|--------|---------|
| SPF    | ✅     | `v=spf1 +a +mx +ip4:68.65.123.247 ... -all` (hardfail) |
| DKIM   | ✅     | RSA 2048-bit key at `default._domainkey.echosmart.me` |
| DMARC  | ✅     | `p=none; sp=none; adkim=r; aspf=r; fo=1` (monitor mode for building reputation) |
| MX     | ✅     | 3 redundant MX servers (jellyfish.systems) |
| rDNS   | ⚠️    | `business191-3.web-hosting.com` (shared hosting limit) |

### Spam Filtering

- SpamAssassin enabled with spam box (spam goes to Spam folder, never auto-deleted)

---

## Email Branding (EchoSmart)

| Asset | URL |
|-------|-----|
| Branded Webmail Portal | https://echosmart.me/webmail/ |
| Email Signature Template | https://echosmart.me/email-assets/signature.html |
| Logo SVG | https://echosmart.me/email-assets/logo.svg |

The email signature template uses placeholders `{{NAME}}`, `{{TITLE}}`, `{{EMAIL}}`,
`{{PHONE}}` that each team member replaces with their own info.

---

## Web Application (Custom PHP + HTML/CSS/JS)

WordPress was removed and replaced with a custom-built web application.

### Pages

| URL                          | Description                                |
|------------------------------|--------------------------------------------|
| https://echosmart.me         | Landing page (hero, features, pricing, contact) |
| https://echosmart.me/login.html | User login                               |
| https://echosmart.me/register.html | User registration (serial + account)  |
| https://echosmart.me/dashboard.html | Dashboard with live sensor data      |
| https://echosmart.me/forgot-password.html | Password recovery              |
| https://echosmart.me/webmail/ | Branded webmail portal                    |

### Backend API

| Endpoint               | Method | Description                          |
|------------------------|--------|--------------------------------------|
| `/api/auth.php`        | POST   | Auth (login, register, logout, me, forgot-password, reset-password) |
| `/api/contact.php`     | POST   | Contact form submission              |

### Database

| Item     | Value                     |
|----------|---------------------------|
| Name     | eduardoc3677_esmart       |
| User     | eduardoc3677_esmart       |
| Engine   | MariaDB / InnoDB          |
| Tables   | users, sessions, password_resets, contact_messages |

### SMTP (Email Sending)

Transactional emails sent via **authenticated SMTP** on `127.0.0.1:465` (IPv4):
- **Primary:** Authenticated SMTP as `noreply@echosmart.me` → Exim DKIM-signs
- **Fallback:** PHP `mail()` with `-f noreply@echosmart.me` envelope sender
- **From:** `EchoSmart <noreply@echosmart.me>`
- **Reply-To:** `admin@echosmart.me`
- **Emails:** Welcome, password reset, contact notification
- **Email routing:** `local` (set via `uapi Email set_always_accept mxcheck=local`)
- **EHLO:** Uses server hostname (matches rDNS for SPF alignment)
- **Anti-spam headers:** `Auto-Submitted: auto-generated` (RFC 3834), `X-Auto-Response-Suppress: All`
- **Transfer encoding:** `quoted-printable`

> **Spam fix history:**
>
> **Round 1 (2026-03-29):**
> 1. **Sender header mismatch** — `mail()` caused Exim to add
>    `Sender: eduardoc3677@business191.web-hosting.com` which mismatches From.
>    Fixed by switching to authenticated SMTP as primary sender.
> 2. **No DKIM signing** — local `mail()` pipe didn't trigger DKIM signing.
>    Authenticated SMTP ensures Exim signs with the domain's DKIM key.
> 3. **SPF softfail** — `~all` changed to `-all` (hardfail).
> 4. **DMARC quarantine** — `p=quarantine` changed to `p=none` for reputation building.
> 5. **Precedence:bulk** header was marking emails as marketing/bulk.
> 6. **Unreadable plain text** — was stripped HTML garbage; now human-written text.
>
> **Round 2 (2026-03-29):**
> 7. **List-Unsubscribe on transactional emails** — `List-Unsubscribe` and
>    `List-Unsubscribe-Post` headers are for marketing/bulk emails. Having them
>    on transactional emails (welcome, password reset) signals to spam filters
>    that the email is marketing. Removed in favor of `Auto-Submitted: auto-generated`.
> 8. **EHLO mismatch** — EHLO was `echosmart.me` but rDNS for the IP is
>    `business191-3.web-hosting.com`. Changed to `gethostname()` (server hostname)
>    so EHLO matches rDNS for better SPF alignment.
> 9. **Missing transactional markers** — Added `Auto-Submitted: auto-generated`
>    (RFC 3834) and `X-Auto-Response-Suppress: All` to mark emails as automated
>    transactional rather than bulk/marketing.
> All fixes applied via SSH + cPanel UAPI.

### Security

| Setting | Status |
|---------|--------|
| HTTPS Forced | ✅ via `.htaccess` |
| HSTS Header | ✅ `max-age=31536000; includeSubDomains; preload` |
| X-Content-Type-Options | ✅ `nosniff` |
| X-Frame-Options | ✅ `SAMEORIGIN` |
| X-XSS-Protection | ✅ `1; mode=block` |
| includes/ blocked | ✅ via `.htaccess` |
| Password hashing | ✅ bcrypt via `password_hash()` |
| Session tokens | ✅ `bin2hex(random_bytes(32))` with 7-day expiry |

---

## SSH Connection

```bash
ssh -i hosting/id_rsa -p 21098 eduardoc3677@68.65.123.247
```

---

## Troubleshooting

### SMTP Error 550: "Your IP: ::1 : Your domain echosmart.me is not allowed in header From"

**Root cause (two issues):**
1. Email routing was auto-detected as `remote` because MX records point to
   `mx*-hosting.jellyfish.systems` (which Exim sees as external servers)
2. PHP connected via `mail.echosmart.me` which resolved to IPv6 `::1`

**Fix applied:**
1. Set email routing to `local` via cPanel API:
   ```bash
   uapi Email set_always_accept domain=echosmart.me mxcheck=local
   ```
2. Changed `Mailer.php` to use PHP `mail()` (local Exim pipe) instead of
   raw SMTP sockets. Fallback uses `127.0.0.1` (IPv4) if `mail()` fails.

### Emails going to Spam (Gmail, Outlook, etc.)

**Root causes (identified across multiple rounds):**
1. SPF used `~all` (softfail) — receivers treat this as "suspicious"
2. DMARC used `p=quarantine` — tells receivers to put emails in spam
3. `mail()` caused Exim to add mismatched `Sender:` header
4. `mail()` didn't trigger DKIM signing
5. `List-Unsubscribe` on transactional emails signaled marketing/bulk
6. EHLO hostname didn't match server rDNS

**All fixes applied (see Spam fix history above in SMTP section):**
1. SPF changed to `-all` (hardfail)
2. DMARC changed to `p=none` (reputation building)
3. Switched from `mail()` to authenticated SMTP as primary
4. EHLO uses `gethostname()` to match server rDNS
5. Removed `List-Unsubscribe` / `Precedence:bulk` (transactional, not marketing)
6. Added `Auto-Submitted: auto-generated` (RFC 3834) for transactional marker
7. Added clean human-readable plain-text alternatives
8. Changed encoding to `quoted-printable`
9. Enabled DKIM signing: `uapi EmailAuth enable_dkim domain=echosmart.me`

### Webmail: Cannot send to external addresses (Gmail, Outlook, etc.)

If webmail (Roundcube/Horde via cPanel) cannot send to external addresses:

1. **Check SPF record** — must include the server IP with `-all`:
   ```
   v=spf1 +a +mx +ip4:68.65.123.247 include:spf.web-hosting.com -all
   ```
2. **Check DKIM** — verify `default._domainkey.echosmart.me` TXT record exists
3. **Check DMARC** — `_dmarc.echosmart.me` should use `p=none` initially
4. **Check server IP reputation** — shared hosting IPs can be blocklisted.
   Test at [mxtoolbox.com/blacklists](https://mxtoolbox.com/blacklists.aspx)

### Email Configuration for Mail Clients

| Setting     | Value                |
|-------------|----------------------|
| IMAP Server | mail.echosmart.me    |
| IMAP Port   | 993 (SSL/TLS)        |
| SMTP Server | mail.echosmart.me    |
| SMTP Port   | 465 (SSL/TLS)        |
| Username    | full email address   |
| Password    | account password     |

### Port 123 (NTP) — Cannot Be Opened

Port 123 (NTP, UDP) **cannot be opened** on this shared hosting plan:

| Check                     | Result                                      |
|---------------------------|---------------------------------------------|
| Bind to port 123          | ❌ `Permission denied` (ports < 1024 need root) |
| Root / sudo access        | ❌ Not available on shared hosting           |
| Firewall (iptables)       | ❌ Not accessible to cPanel users            |
| Custom services           | ❌ Only HTTP/HTTPS/email ports allowed       |

**Why?** Shared hosting (Namecheap cPanel) runs multiple customers on the same
server. Only the hosting provider (root) can open system ports. Port 123 is a
privileged port (< 1024) requiring root access.

**Solution: FakeNTP (HTTP-based time server)**

Instead of port 123/UDP, EchoSmart uses **FakeNTP** — an HTTP-based time server
at `ntp.echosmart.me` that IoT devices can query over HTTPS (port 443):

```bash
# Get time as JSON
curl https://ntp.echosmart.me/time

# Get Unix timestamp only
curl https://ntp.echosmart.me/time?fmt=unix

# Get ISO 8601 only
curl https://ntp.echosmart.me/time?fmt=iso
```

See [FakeNTP Subdomain Setup](#fakentp-subdomain-ntpechosmart) below.

---

## FakeNTP Subdomain (ntp.echosmart.me)

HTTP-based time server for IoT devices at `https://ntp.echosmart.me`.

### Architecture

FakeNTP runs as a **Flask web application** on cPanel with CloudLinux Passenger.
It provides NTP-like time synchronization over HTTPS (not UDP port 123).

> **Important:** On shared hosting, Passenger manages process lifecycle — no
> persistent UDP server is possible. The "running" state is a flag persisted
> in `fakentp_config.json`. The actual time is served via HTTP endpoints.

| Component                   | Description                                      |
|-----------------------------|--------------------------------------------------|
| Web Framework               | Flask 3.x + CloudLinux Passenger (lswsgi)        |
| Python Version              | 3.12 (virtualenv at `~/virtualenv/.../3.12/`)    |
| Config Storage              | `~/ntp.echosmart.me/fakentp/fakentp/fakentp_config.json` |
| Activity Logs               | `~/ntp.echosmart.me/fakentp/fakentp/fakentp_activity.log` |
| WSGI Entry Point            | `~/ntp.echosmart.me/fakentp/passenger_wsgi.py`   |
| Document Root               | `~/ntp.echosmart.me/`                            |

### Why No UDP Server?

Shared hosting (Namecheap cPanel) cannot run persistent background processes:

- Passenger spawns multiple worker processes → port binding conflicts
- Workers are recycled on idle → UDP threads die
- Ports < 1024 (like NTP port 123) require root access
- Even ports > 1024 (e.g. 8123) fail with "Address already in use"

**Solution:** Pure HTTP time service. IoT devices query `https://ntp.echosmart.me/time`
instead of using NTP protocol.

### Subdomain Setup (cPanel)

1. **Create subdomain** in cPanel → Domains → Subdomains:
   - Subdomain: `ntp`
   - Domain: `echosmart.me`
   - Document Root: `public_html/ntp.echosmart.me`

   Or via SSH:
   ```bash
   uapi SubDomain addsubdomain domain=ntp rootdomain=echosmart.me dir=public_html/ntp.echosmart.me
   ```

2. **Add DNS A record** (if wildcard `*` doesn't already cover it):
   ```bash
   uapi DNS mass_edit_zone zone=echosmart.me serial=XXXXXXXXXX \
     add='{"dname":"ntp","ttl":14400,"record_type":"A","data":["68.65.123.247"]}'
   ```

3. **Create Python app** via cPanel → Setup Python App:
   - Python version: 3.12
   - App root: `ntp.echosmart.me/fakentp`
   - App URL: `/`
   - Startup file: `passenger_wsgi.py`
   - Entry point: `application`

4. **SSL** is automatically covered by the wildcard certificate (`*.echosmart.me`).

### API Endpoints

| Endpoint               | Response     | Description                            |
|------------------------|-------------|----------------------------------------|
| `GET /`                | HTML         | Dashboard with live clock + controls   |
| `GET /time`            | JSON         | Full time data (unix + iso + date)     |
| `GET /time?fmt=unix`   | text/plain   | Unix timestamp (e.g. `1711756800.123`) |
| `GET /time?fmt=iso`    | text/plain   | ISO 8601 (e.g. `2026-03-30T00:00:00Z`)|
| `GET /health`          | JSON         | Health check + running status          |
| `GET /api/config`      | JSON         | Full config + current time + state     |
| `POST /api/config`     | JSON         | Save config / start / stop / toggle    |
| `GET /api/logs`        | JSON         | Activity log entries                   |
| `GET /api/timezones`   | JSON         | Available timezone list                |

### IoT Device Usage (ESP32)

```cpp
// Arduino / ESP32
HTTPClient http;
http.begin("https://ntp.echosmart.me/time?fmt=unix");
if (http.GET() == 200) {
    unsigned long epoch = http.getString().toFloat();
    // Set RTC with epoch
}
http.end();
```

### Files

| File                        | Description                              |
|-----------------------------|------------------------------------------|
| `hosting/ntp/index.php`     | PHP time server (standalone fallback)    |
| `hosting/ntp/.htaccess`     | URL routing + security headers           |
| `gateway/fakentp/fakentp.py`| Python standalone server (VPS/dev)       |
| `gateway/fakentp/README.md` | FakeNTP documentation                    |
