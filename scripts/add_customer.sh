#!/bin/bash
#
# add_customer.sh — Add a new customer instance to an existing VPS
#
# This script is for Nick (the installer) to add a new customer instance
# to a VPS that already has Hermes/Docker running.
#
# Usage: bash scripts/add_customer.sh --name "Sarah" --website "https://example.com" --bot-token "123:ABC..." --api-key "sk-..." --chat-id "123456789" --path A
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
echo "  ADD NEW CUSTOMER INSTANCE"
echo "════════════════════════════════════════════════════════════"
echo ""

# ─── Check prerequisites ────────────────────────────────────────────────────
command -v docker &> /dev/null || error "Docker not found. Run install_fresh.sh first."
command -v python3 &> /dev/null || error "Python3 not found."

INSTALL_DIR="$HOME/hermes-agent-install"
[ -d "$INSTALL_DIR" ] || error "Install repo not found at $INSTALL_DIR. Clone it first."
[ -f "$INSTALL_DIR/scripts/install_captain.py" ] || error "install_captain.py not found in $INSTALL_DIR/scripts/"

# ─── Pass all arguments to install_captain.py ───────────────────────────────
info "Running provisioning script..."
echo ""
python3 "$INSTALL_DIR/scripts/install_captain.py" "$@"

echo ""
ok "Customer instance added. Check docker ps to verify it's running."
echo ""
