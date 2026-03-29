#!/usr/bin/env bash
# ============================================================
# EchoSmart — Initial cPanel Hosting Setup
# ============================================================
# Run this ONCE to configure the cPanel hosting environment.
# Sets up directory structure, SSL, cron jobs, and PHP settings.
#
# Usage:  ./setup.sh
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ENV_FILE="${SCRIPT_DIR}/../.env"
if [[ ! -f "$ENV_FILE" ]]; then
    echo "❌ Error: .env not found. Copy .env.example to .env first."
    exit 1
fi
# shellcheck source=/dev/null
source "$ENV_FILE"

SSH_OPTS="-p ${SSH_PORT} -o StrictHostKeyChecking=accept-new"
if [[ -n "${SSH_KEY_FILE:-}" && -f "${SCRIPT_DIR}/../${SSH_KEY_FILE}" ]]; then
    SSH_OPTS="${SSH_OPTS} -i ${SCRIPT_DIR}/../${SSH_KEY_FILE}"
fi

SSH_TARGET="${CPANEL_USER}@${SERVER_IP}"

log() { echo "$(date '+%H:%M:%S') ▸ $*"; }

log "🔧 EchoSmart — Initial Hosting Setup for ${DOMAIN}"
echo ""

# ---- 1. Create directory structure ----
log "📁 Creating directory structure on server..."
ssh ${SSH_OPTS} "${SSH_TARGET}" bash <<'REMOTE_SETUP'
set -euo pipefail

# WordPress content directories
mkdir -p ~/public_html/wp-content/themes/echosmart
mkdir -p ~/public_html/wp-content/plugins/echosmart-api
mkdir -p ~/public_html/wp-content/uploads
mkdir -p ~/public_html/wp-content/cache

# EchoSmart app assets directory
mkdir -p ~/public_html/wp-content/themes/echosmart/app
mkdir -p ~/public_html/wp-content/themes/echosmart/assets/img
mkdir -p ~/public_html/wp-content/themes/echosmart/assets/css
mkdir -p ~/public_html/wp-content/themes/echosmart/assets/js

# Logs and backups (outside public_html)
mkdir -p ~/logs
mkdir -p ~/backups

echo "✅ Directories created."
REMOTE_SETUP

# ---- 2. Set PHP version and settings ----
log "⚙️  Configuring PHP settings..."
ssh ${SSH_OPTS} "${SSH_TARGET}" bash <<'REMOTE_PHP'
# Create/update .htaccess with PHP settings
cat > ~/public_html/.user.ini <<'EOF'
; EchoSmart PHP Configuration
upload_max_filesize = 64M
post_max_size = 64M
max_execution_time = 300
max_input_time = 300
memory_limit = 256M
date.timezone = America/Mexico_City
EOF

echo "✅ PHP settings configured."
REMOTE_PHP

# ---- 3. Set file permissions ----
log "🔐 Setting file permissions..."
ssh ${SSH_OPTS} "${SSH_TARGET}" bash <<'REMOTE_PERMS'
# WordPress recommended permissions
find ~/public_html -type d -exec chmod 755 {} \;
find ~/public_html -type f -exec chmod 644 {} \;

# Writable directories for WordPress
chmod 755 ~/public_html/wp-content/uploads
chmod 755 ~/public_html/wp-content/cache

echo "✅ Permissions set."
REMOTE_PERMS

# ---- 4. Set up WP-CLI if available ----
log "🔧 Checking WP-CLI availability..."
ssh ${SSH_OPTS} "${SSH_TARGET}" bash <<REMOTE_WPCLI
if command -v wp &>/dev/null; then
    echo "✅ WP-CLI is available."

    cd ~/public_html

    # Enable EchoSmart theme
    wp theme activate echosmart 2>/dev/null || echo "⚠️  Theme not yet deployed."

    # Enable EchoSmart API plugin
    wp plugin activate echosmart-api 2>/dev/null || echo "⚠️  Plugin not yet deployed."

    # Set site title and description
    wp option update blogname "EchoSmart"
    wp option update blogdescription "Monitoreo Ambiental Inteligente para Invernaderos"

    # Set permalink structure for clean URLs
    wp rewrite structure '/%postname%/'
    wp rewrite flush

    # Disable comments globally
    wp option update default_comment_status closed

    # Set timezone
    wp option update timezone_string "America/Mexico_City"

    echo "✅ WordPress configured via WP-CLI."
else
    echo "⚠️  WP-CLI not found. WordPress must be configured via wp-admin."
fi
REMOTE_WPCLI

# ---- 5. Create cron job for WordPress ----
log "⏰ Setting up WordPress cron..."
ssh ${SSH_OPTS} "${SSH_TARGET}" bash <<REMOTE_CRON
# Disable WP built-in cron (use system cron instead for reliability)
CRON_CMD="*/5 * * * * /usr/local/bin/php ~/public_html/wp-cron.php > /dev/null 2>&1"
(crontab -l 2>/dev/null | grep -v "wp-cron" ; echo "\${CRON_CMD}") | crontab -
echo "✅ WordPress cron configured (every 5 minutes)."
REMOTE_CRON

echo ""
log "🎉 Initial hosting setup complete!"
log "   Next steps:"
log "   1. Run deploy.sh to deploy theme and plugin"
log "   2. Visit https://${DOMAIN}/wp-admin/ to verify"
log "   3. Activate EchoSmart theme and plugin if WP-CLI was not available"
