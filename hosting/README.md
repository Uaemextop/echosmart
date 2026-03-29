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
| TXT    | echosmart.me (SPF) | `v=spf1 +a +mx +ip4:63.250.38.86 +ip4:68.65.123.176 include:spf.web-hosting.com ~all` |
| TXT    | _dmarc (DMARC)     | `v=DMARC1; p=quarantine; rua=mailto:admin@echosmart.me; ruf=mailto:admin@echosmart.me; pct=100;` |
| TXT    | default._domainkey | DKIM RSA 2048-bit public key                                                  |
| NS     | echosmart.me       | dns1.namecheaphosting.com                                                      |
| NS     | echosmart.me       | dns2.namecheaphosting.com                                                      |

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
| SPF    | ✅     | `v=spf1 +a +mx ... include:spf.web-hosting.com ~all` |
| DKIM   | ✅     | RSA 2048-bit key at `default._domainkey.echosmart.me` |
| DMARC  | ✅     | `p=quarantine; rua/ruf=admin@echosmart.me; pct=100` |
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

## WordPress

| Item       | URL / Value                                |
|------------|--------------------------------------------|
| Site       | https://echosmart.me                       |
| Admin      | https://echosmart.me/wp-admin/             |
| PHP        | 8.2.30                                     |
| Site Name  | EchoSmart                                  |
| Tagline    | Smart IoT Monitoring Solutions             |
| Timezone   | America/Mexico_City                        |
| Admin Email| admin@echosmart.me                         |

### WordPress Security

| Setting | Status |
|---------|--------|
| Force SSL Admin | ✅ `FORCE_SSL_ADMIN = true` |
| Disable File Editing | ✅ `DISALLOW_FILE_EDIT = true` |
| XML-RPC Blocked | ✅ via `.htaccess` |
| HSTS Header | ✅ `max-age=31536000; includeSubDomains; preload` |
| X-Content-Type-Options | ✅ `nosniff` |
| X-Frame-Options | ✅ `SAMEORIGIN` |
| X-XSS-Protection | ✅ `1; mode=block` |
| wp-admin Basic Auth | ✅ Password-protected directory |
| LiteSpeed Cache | ✅ Active |

### WordPress SMTP (Secure Email Sending)

WordPress sends all emails via authenticated SMTP over SSL:
- **From:** `noreply@echosmart.me` (EchoSmart)
- **Server:** `mail.echosmart.me:465` (SSL)
- **Plugins:** WP Mail SMTP + GoSMTP Pro

---

## SSH Connection

```bash
ssh -i hosting/id_rsa -p 21098 eduardoc3677@68.65.123.247
```
