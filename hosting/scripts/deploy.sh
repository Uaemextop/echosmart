#!/usr/bin/env bash
# ============================================================
# EchoSmart — Deploy to cPanel Shared Hosting
# ============================================================
# Deploys WordPress theme, plugin, and configuration to the
# Namecheap cPanel hosting via SSH/rsync.
#
# Usage:
#   ./deploy.sh [component]
#
# Components:
#   all       Deploy everything (default)
#   theme     Deploy WordPress theme only
#   plugin    Deploy EchoSmart API plugin only
#   config    Deploy configuration files only
#   frontend  Build and deploy frontend as WP assets
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment
ENV_FILE="${SCRIPT_DIR}/.env"
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
if [[ -n "${SSH_KEY_FILE:-}" && -f "${SCRIPT_DIR}/${SSH_KEY_FILE}" ]]; then
    SSH_OPTS="${SSH_OPTS} -i ${SCRIPT_DIR}/${SSH_KEY_FILE}"
fi

SSH_TARGET="${CPANEL_USER}@${SERVER_IP}"
RSYNC_OPTS="-avz --delete -e \"ssh ${SSH_OPTS}\""

log() { echo "$(date '+%H:%M:%S') ▸ $*"; }

# ---- Deploy functions ----

deploy_theme() {
    log "🎨 Deploying EchoSmart WordPress theme..."
    eval rsync ${RSYNC_OPTS} \
        "${SCRIPT_DIR}/wordpress/theme/echosmart/" \
        "${SSH_TARGET}:${REMOTE_WP_CONTENT}/themes/echosmart/"
    log "✅ Theme deployed."
}

deploy_plugin() {
    log "🔌 Deploying EchoSmart API plugin..."
    eval rsync ${RSYNC_OPTS} \
        "${SCRIPT_DIR}/wordpress/plugins/echosmart-api/" \
        "${SSH_TARGET}:${REMOTE_WP_CONTENT}/plugins/echosmart-api/"
    log "✅ Plugin deployed."
}

deploy_config() {
    log "⚙️  Deploying hosting configuration..."

    # Upload .htaccess
    eval rsync ${RSYNC_OPTS} \
        "${SCRIPT_DIR}/wordpress/.htaccess" \
        "${SSH_TARGET}:${REMOTE_PUBLIC_HTML}/.htaccess"

    # Upload wp-config additions (to be included by wp-config.php)
    eval rsync ${RSYNC_OPTS} \
        "${SCRIPT_DIR}/wordpress/wp-config-extra.php" \
        "${SSH_TARGET}:${REMOTE_PUBLIC_HTML}/wp-config-extra.php"

    log "✅ Configuration deployed."
}

deploy_frontend() {
    log "🏗️  Building frontend..."
    cd "${ROOT_DIR}/frontend"
    npm ci --silent
    VITE_API_URL="https://${DOMAIN}/api" npm run build

    log "📦 Deploying frontend assets..."
    eval rsync ${RSYNC_OPTS} \
        "${ROOT_DIR}/frontend/dist/" \
        "${SSH_TARGET}:${REMOTE_WP_CONTENT}/themes/echosmart/app/"

    cd "${SCRIPT_DIR}"
    log "✅ Frontend assets deployed."
}

# ---- Main ----

COMPONENT="${1:-all}"

log "🚀 EchoSmart Deploy → ${DOMAIN} (${COMPONENT})"
echo ""

case "$COMPONENT" in
    theme)    deploy_theme ;;
    plugin)   deploy_plugin ;;
    config)   deploy_config ;;
    frontend) deploy_frontend ;;
    all)
        deploy_theme
        deploy_plugin
        deploy_config
        echo ""
        log "🎉 Full deployment complete!"
        log "   🌐 Site: https://${DOMAIN}"
        log "   🔧 Admin: https://${DOMAIN}/wp-admin/"
        ;;
    *)
        echo "Unknown component: ${COMPONENT}"
        echo "Usage: ./deploy.sh [all|theme|plugin|config|frontend]"
        exit 1
        ;;
esac
