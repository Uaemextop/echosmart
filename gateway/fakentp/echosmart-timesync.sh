#!/usr/bin/env bash
# ─── EchoSmart Time Sync ─────────────────────────────────────────────
#
# Synchronize system clock from EchoSmart FakeNTP HTTP time server.
# Alternative to standard NTP for environments where port 123/UDP
# is blocked or unavailable.
#
# Usage:
#   sudo ./echosmart-timesync.sh              # sync once
#   sudo ./echosmart-timesync.sh --check      # show drift without setting
#   sudo ./echosmart-timesync.sh --install     # install systemd timer
#   sudo ./echosmart-timesync.sh --uninstall   # remove systemd timer
#
# Server: https://ntp.echosmart.me/time
# Requires: curl, date, bash
#
# @package EchoSmart
# ──────────────────────────────────────────────────────────────────────

set -euo pipefail

readonly TIMESYNC_URL="${ECHOSMART_NTP_URL:-https://ntp.echosmart.me/time?fmt=unix}"
readonly TIMESYNC_TIMEOUT="${ECHOSMART_NTP_TIMEOUT:-10}"
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ─── Colors ───────────────────────────────────────────────────────────

if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    RED='\033[0;31m'
    CYAN='\033[0;36m'
    NC='\033[0m'
else
    GREEN='' YELLOW='' RED='' CYAN='' NC=''
fi

log_info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ─── Fetch server time ────────────────────────────────────────────────

fetch_server_time() {
    local unix_ts
    unix_ts=$(curl -sS --max-time "$TIMESYNC_TIMEOUT" \
        --retry 2 --retry-delay 1 \
        "$TIMESYNC_URL" 2>/dev/null)

    if [[ -z "$unix_ts" ]] || [[ ! "$unix_ts" =~ ^[0-9]+\.[0-9]+$ ]]; then
        log_error "Failed to fetch time from $TIMESYNC_URL"
        log_error "Response: ${unix_ts:-<empty>}"
        return 1
    fi

    echo "$unix_ts"
}

# ─── Calculate drift ─────────────────────────────────────────────────

calc_drift() {
    local server_ts="$1"
    local local_ts
    local_ts=$(date +%s.%N)

    # Use bc for floating-point arithmetic, fall back to integer
    if command -v bc &>/dev/null; then
        echo "scale=3; $local_ts - $server_ts" | bc
    else
        local s_int=${server_ts%%.*}
        local l_int=${local_ts%%.*}
        echo $(( l_int - s_int ))
    fi
}

# ─── Sync time ────────────────────────────────────────────────────────

do_sync() {
    log_info "Fetching time from EchoSmart FakeNTP..."
    log_info "URL: $TIMESYNC_URL"

    local server_ts
    server_ts=$(fetch_server_time) || exit 1

    local drift
    drift=$(calc_drift "$server_ts")
    log_info "Server epoch: $server_ts"
    log_info "Local  epoch: $(date +%s.%N)"
    log_info "Drift: ${drift}s"

    # Convert epoch to date string for 'date -s'
    local epoch_int=${server_ts%%.*}

    if [[ $(id -u) -ne 0 ]]; then
        log_error "Root privileges required to set system time."
        log_error "Run: sudo $0"
        exit 1
    fi

    # Set the system clock
    date -s "@${epoch_int}" >/dev/null 2>&1
    log_info "System clock set to: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    log_info "${GREEN}Time synchronized successfully!${NC}"

    # Sync hardware clock if available
    if command -v hwclock &>/dev/null; then
        hwclock --systohc 2>/dev/null && \
            log_info "Hardware clock updated." || \
            log_warn "Could not update hardware clock (VM/container?)."
    fi
}

# ─── Check drift (no-op) ─────────────────────────────────────────────

do_check() {
    log_info "Checking time drift (no changes will be made)..."
    log_info "URL: $TIMESYNC_URL"

    local server_ts
    server_ts=$(fetch_server_time) || exit 1

    local drift
    drift=$(calc_drift "$server_ts")

    local server_date
    server_date=$(date -u -d "@${server_ts%%.*}" '+%Y-%m-%d %H:%M:%S UTC' 2>/dev/null || \
                  date -u -r "${server_ts%%.*}" '+%Y-%m-%d %H:%M:%S UTC' 2>/dev/null || \
                  echo "N/A")

    echo ""
    echo -e "  ${CYAN}Server time:${NC}  $server_date"
    echo -e "  ${CYAN}Local time:${NC}   $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo -e "  ${CYAN}Drift:${NC}        ${drift}s"
    echo -e "  ${CYAN}Server epoch:${NC} $server_ts"
    echo ""

    # Classify drift
    local abs_drift=${drift#-}  # remove sign
    abs_drift=${abs_drift%%.*}  # integer part
    abs_drift=${abs_drift:-0}

    if (( abs_drift < 2 )); then
        log_info "${GREEN}Clock is synchronized (drift < 2s)${NC}"
    elif (( abs_drift < 60 )); then
        log_warn "Clock drift is ${drift}s — consider syncing."
    else
        log_error "Clock drift is ${drift}s — sync recommended!"
        log_error "Run: sudo $0"
    fi
}

# ─── Install systemd timer ───────────────────────────────────────────

do_install() {
    if [[ $(id -u) -ne 0 ]]; then
        log_error "Root privileges required for installation."
        log_error "Run: sudo $0 --install"
        exit 1
    fi

    log_info "Installing EchoSmart time sync service..."

    # Copy script to system location
    local install_path="/usr/local/bin/echosmart-timesync"
    cp "$(readlink -f "$0")" "$install_path"
    chmod +x "$install_path"
    log_info "Script installed: $install_path"

    # Create systemd service
    cat > /etc/systemd/system/echosmart-timesync.service << 'EOF'
[Unit]
Description=EchoSmart HTTP Time Sync
Documentation=https://ntp.echosmart.me
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/echosmart-timesync
TimeoutStartSec=30

[Install]
WantedBy=multi-user.target
EOF
    log_info "Service unit created: /etc/systemd/system/echosmart-timesync.service"

    # Create systemd timer (every 15 minutes)
    cat > /etc/systemd/system/echosmart-timesync.timer << 'EOF'
[Unit]
Description=EchoSmart HTTP Time Sync Timer
Documentation=https://ntp.echosmart.me

[Timer]
OnBootSec=30
OnUnitActiveSec=15min
RandomizedDelaySec=60
Persistent=true

[Install]
WantedBy=timers.target
EOF
    log_info "Timer unit created: /etc/systemd/system/echosmart-timesync.timer"

    # Enable and start
    systemctl daemon-reload
    systemctl enable --now echosmart-timesync.timer
    log_info "${GREEN}Timer enabled — syncing every 15 minutes.${NC}"

    # Run initial sync
    log_info "Running initial sync..."
    systemctl start echosmart-timesync.service || true

    echo ""
    log_info "Status: systemctl status echosmart-timesync.timer"
    log_info "Logs:   journalctl -u echosmart-timesync.service"
}

# ─── Uninstall ────────────────────────────────────────────────────────

do_uninstall() {
    if [[ $(id -u) -ne 0 ]]; then
        log_error "Root privileges required."
        exit 1
    fi

    log_info "Removing EchoSmart time sync..."

    systemctl disable --now echosmart-timesync.timer 2>/dev/null || true
    systemctl disable echosmart-timesync.service 2>/dev/null || true
    rm -f /etc/systemd/system/echosmart-timesync.service
    rm -f /etc/systemd/system/echosmart-timesync.timer
    rm -f /usr/local/bin/echosmart-timesync
    systemctl daemon-reload

    log_info "${GREEN}Uninstalled successfully.${NC}"
}

# ─── Help ─────────────────────────────────────────────────────────────

do_help() {
    cat << EOF
EchoSmart Time Sync — HTTP-based time synchronization

Usage: $SCRIPT_NAME [OPTION]

Options:
  (none)        Sync system clock from ntp.echosmart.me (requires sudo)
  --check       Show clock drift without making changes
  --install     Install systemd timer for automatic sync every 15 min
  --uninstall   Remove systemd timer and service
  --help        Show this help message

Environment Variables:
  ECHOSMART_NTP_URL      Override time server URL
                         (default: https://ntp.echosmart.me/time?fmt=unix)
  ECHOSMART_NTP_TIMEOUT  HTTP timeout in seconds (default: 10)

Examples:
  # Check drift
  ./echosmart-timesync.sh --check

  # Sync once
  sudo ./echosmart-timesync.sh

  # Install auto-sync (every 15 min)
  sudo ./echosmart-timesync.sh --install

  # Use custom server
  ECHOSMART_NTP_URL=https://my-server.com/time?fmt=unix ./echosmart-timesync.sh --check

Server: https://ntp.echosmart.me
Docs:   https://github.com/Uaemextop/echosmart
EOF
}

# ─── Main ─────────────────────────────────────────────────────────────

case "${1:-}" in
    --check)     do_check ;;
    --install)   do_install ;;
    --uninstall) do_uninstall ;;
    --help|-h)   do_help ;;
    "")          do_sync ;;
    *)
        log_error "Unknown option: $1"
        do_help
        exit 1
        ;;
esac
