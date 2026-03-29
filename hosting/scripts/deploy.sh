#!/usr/bin/env bash
# ============================================================
# EchoSmart — Deploy to cPanel Shared Hosting
# ============================================================
# Deploys WordPress configuration and assets to the
# Namecheap cPanel hosting via SSH/rsync.
#
# Usage:
#   ./deploy.sh [component]
#
# Components:
#   all       Deploy everything (default)
#   config    Deploy configuration files (.htaccess, wp-config-extra)
#   assets    Upload brand assets (logos, icons) to uploads
#   css       Deploy custom dark theme CSS
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment
ENV_FILE="${ROOT_DIR}/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    echo "❌ Error: ${ENV_FILE} not found."
    echo "   Copy .env.example to .env and fill in your credentials."
    exit 1
fi
# shellcheck source=/dev/null
source "$ENV_FILE"

# Validate required variables
for var in CPANEL_USER SERVER_IP SSH_PORT REMOTE_PUBLIC_HTML REMOTE_WP_CONTENT; do
    if [[ -z "${!var:-}" ]]; then
        echo "❌ Error: ${var} is not set in .env"
        exit 1
    fi
done

SSH_OPTS="-p ${SSH_PORT} -o StrictHostKeyChecking=accept-new"
if [[ -n "${SSH_KEY_FILE:-}" && -f "${ROOT_DIR}/${SSH_KEY_FILE}" ]]; then
    SSH_OPTS="${SSH_OPTS} -i ${ROOT_DIR}/${SSH_KEY_FILE}"
fi

SSH_TARGET="${CPANEL_USER}@${SERVER_IP}"
RSYNC_OPTS="-avz -e \"ssh ${SSH_OPTS}\""

log() { echo "$(date '+%H:%M:%S') ▸ $*"; }

# ---- Deploy functions ----

deploy_config() {
    log "⚙️  Deploying hosting configuration..."

    # Upload .htaccess
    eval rsync ${RSYNC_OPTS} \
        "${ROOT_DIR}/wordpress/.htaccess" \
        "${SSH_TARGET}:${REMOTE_PUBLIC_HTML}/.htaccess"

    # Upload wp-config additions
    eval rsync ${RSYNC_OPTS} \
        "${ROOT_DIR}/wordpress/wp-config-extra.php" \
        "${SSH_TARGET}:${REMOTE_PUBLIC_HTML}/wp-config-extra.php"

    log "✅ Configuration deployed."
}

deploy_assets() {
    log "🖼️  Deploying brand assets..."
    ASSETS_DIR="$(dirname "$ROOT_DIR")/assets"

    if [[ ! -d "$ASSETS_DIR" ]]; then
        log "⚠️  Assets directory not found at ${ASSETS_DIR}"
        return 1
    fi

    # Ensure remote directory exists
    ssh ${SSH_OPTS} "${SSH_TARGET}" "mkdir -p ${REMOTE_WP_CONTENT}/uploads/echosmart"

    # Upload logos
    eval rsync ${RSYNC_OPTS} \
        "${ASSETS_DIR}/logo/png/" \
        "${SSH_TARGET}:${REMOTE_WP_CONTENT}/uploads/echosmart/logos/"

    # Upload sensor icons
    eval rsync ${RSYNC_OPTS} \
        "${ASSETS_DIR}/icons/jpg/512/" \
        "${SSH_TARGET}:${REMOTE_WP_CONTENT}/uploads/echosmart/icons/"

    log "✅ Brand assets deployed."
}

deploy_css() {
    log "🎨 Deploying dark theme CSS..."
    ssh ${SSH_OPTS} "${SSH_TARGET}" "mkdir -p ${REMOTE_WP_CONTENT}/uploads/echosmart"

    # The CSS is managed on the server via mu-plugin.
    # This function can be extended to deploy updated CSS from the repo.
    log "ℹ️  CSS is managed via mu-plugin on the server."
    log "   Edit wp-content/uploads/echosmart/custom.css on the server."
    log "✅ CSS check complete."
}

# ---- Main ----

COMPONENT="${1:-all}"

log "🚀 EchoSmart Deploy → ${DOMAIN} (${COMPONENT})"
echo ""

case "$COMPONENT" in
    config)   deploy_config ;;
    assets)   deploy_assets ;;
    css)      deploy_css ;;
    all)
        deploy_config
        deploy_assets
        deploy_css
        echo ""
        log "🎉 Full deployment complete!"
        log "   🌐 Site: https://${DOMAIN}"
        log "   🔧 Admin: https://${DOMAIN}/wp-admin/"
        ;;
    *)
        echo "Unknown component: ${COMPONENT}"
        echo "Usage: ./deploy.sh [all|config|assets|css]"
        exit 1
        ;;
esac
