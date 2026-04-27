#!/bin/bash
#
# install_fresh.sh — Full VPS setup for Agent Install customers
#
# This script is for customers who just got a new Contabo VPS (or any Ubuntu VPS)
# and need everything set up from scratch.
#
# Usage: curl -sSL https://raw.githubusercontent.com/USER/hermes-agent-install/main/scripts/install_fresh.sh | bash
#   OR:  git clone https://github.com/USER/hermes-agent-install.git && cd hermes-agent-install && bash scripts/install_fresh.sh
#

set -euo pipefail

# ─── Colors ─────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ─── Header ─────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  HERMES AGENT INSTALL — Fresh VPS Setup"
echo "════════════════════════════════════════════════════════════"
echo ""

# ─── System Check ───────────────────────────────────────────────────────────
info "Checking system requirements..."

# Check Ubuntu
if ! grep -q "Ubuntu" /etc/os-release 2>/dev/null; then
    warn "This script is designed for Ubuntu. It may work on other Debian-based systems but is untested."
fi

# Check RAM (need at least 2GB)
TOTAL_RAM_MB=$(free -m | awk '/^Mem:/{print $2}')
if [ "$TOTAL_RAM_MB" -lt 1800 ]; then
    error "Need at least 2GB RAM. Found: ${TOTAL_RAM_MB}MB. Please upgrade your VPS."
fi
ok "RAM: ${TOTAL_RAM_MB}MB"

# Check disk (need at least 10GB free)
AVAIL_DISK_GB=$(df -BG / | awk 'NR==2{print $4}' | tr -d 'G')
if [ "$AVAIL_DISK_GB" -lt 10 ]; then
    error "Need at least 10GB free disk. Found: ${AVAIL_DISK_GB}GB."
fi
ok "Disk: ${AVAIL_DISK_GB}GB available"

# Check root
if [ "$EUID" -ne 0 ]; then
    error "Please run as root (sudo bash scripts/install_fresh.sh)"
fi
ok "Running as root"

# ─── Install Docker ────────────────────────────────────────────────────────
if command -v docker &> /dev/null; then
    ok "Docker already installed: $(docker --version)"
else
    info "Installing Docker..."
    apt-get update -qq
    apt-get install -y -qq ca-certificates curl gnupg lsb-release > /dev/null

    # Add Docker's official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg 2>/dev/null || true
    chmod a+r /etc/apt/keyrings/docker.gpg

    # Add the repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin > /dev/null

    # Start Docker
    systemctl enable docker
    systemctl start docker

    ok "Docker installed: $(docker --version)"
fi

# ─── Install Python 3 (for provisioning script) ────────────────────────────
if command -v python3 &> /dev/null; then
    ok "Python3 already installed: $(python3 --version)"
else
    info "Installing Python3..."
    apt-get install -y -qq python3 > /dev/null
    ok "Python3 installed: $(python3 --version)"
fi

# ─── Clone the repo ────────────────────────────────────────────────────────
INSTALL_DIR="$HOME/hermes-agent-install"

if [ -d "$INSTALL_DIR" ]; then
    ok "Install repo already exists at $INSTALL_DIR"
    cd "$INSTALL_DIR"
    git pull 2>/dev/null || true
else
    info "Cloning hermes-agent-install repo..."
    # TODO: Replace with actual repo URL
    git clone https://github.com/USER/hermes-agent-install.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    ok "Repo cloned to $INSTALL_DIR"
fi

# ─── Create customer directory ──────────────────────────────────────────────
CUSTOMERS_DIR="$HOME/hermes-customers"
mkdir -p "$CUSTOMERS_DIR"
ok "Customer directory: $CUSTOMERS_DIR"

# ─── Run the provisioning script ───────────────────────────────────────────
echo ""
info "Starting Captain Protocol provisioning..."
echo ""
python3 scripts/install_captain.py

# ─── Done ───────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✓ SETUP COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  Your AI agent is running. Check your Telegram!"
echo ""
echo "  Useful commands:"
echo "    Check status:   docker ps"
echo "    View logs:      docker logs hermes-\$CUSTOMER_NAME -f"
echo "    Restart:        cd $CUSTOMERS_DIR/\$CUSTOMER_NAME && docker compose restart"
echo "    Stop:           cd $CUSTOMERS_DIR/\$CUSTOMER_NAME && docker compose down"
echo ""
echo "  Need help? Message your agent installer or email support."
echo ""
