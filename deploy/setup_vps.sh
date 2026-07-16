#!/bin/bash
# WellGuard AI — Full VPS Setup Script
# Run once on a fresh Ubuntu 22.04 server
# Usage: bash deploy/setup_vps.sh

set -e
echo "======================================"
echo "  WellGuard AI — VPS Setup Script"
echo "======================================"

APP_DIR="/opt/wellguard"
REPO_URL="https://github.com/JihadFathi/wellguard-ai.git"

# ── 1. System packages ────────────────────────────────────────────────
echo ""
echo "[1/6] Installing system packages..."
apt-get update -qq
apt-get install -y -qq \
    python3-pip python3-venv python3-dev \
    nginx supervisor git curl \
    build-essential libssl-dev

# ── 2. Clone / update repo ────────────────────────────────────────────
echo ""
echo "[2/6] Setting up application directory..."
if [ -d "$APP_DIR/.git" ]; then
    echo "  Repo exists — pulling latest..."
    cd "$APP_DIR"
    git fetch origin main
    git reset --hard origin/main
else
    echo "  Cloning fresh copy..."
    mkdir -p "$APP_DIR"
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

# ── 3. Python virtual environment ─────────────────────────────────────
echo ""
echo "[3/6] Creating Python virtual environment..."
cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "  Streamlit version: $(streamlit --version)"

# ── 4. Log directory ──────────────────────────────────────────────────
echo ""
echo "[4/6] Creating log directory..."
mkdir -p /var/log/wellguard

# ── 5. Supervisor ─────────────────────────────────────────────────────
echo ""
echo "[5/6] Configuring Supervisor..."
cp "$APP_DIR/deploy/supervisor/wellguard.conf" /etc/supervisor/conf.d/wellguard.conf
supervisorctl reread
supervisorctl update
supervisorctl start wellguard || supervisorctl restart wellguard
sleep 3
supervisorctl status wellguard

# ── 6. Nginx ──────────────────────────────────────────────────────────
echo ""
echo "[6/6] Configuring Nginx..."
cp "$APP_DIR/deploy/nginx/wellguard.conf" /etc/nginx/sites-available/wellguard
ln -sf /etc/nginx/sites-available/wellguard /etc/nginx/sites-enabled/wellguard
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
systemctl enable nginx

# ── Health check ──────────────────────────────────────────────────────
echo ""
echo "======================================"
echo "  Waiting for app to start..."
sleep 5
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/_stcore/health || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "  ✅ App is HEALTHY (HTTP $HTTP_CODE)"
else
    echo "  ⚠️  App returned HTTP $HTTP_CODE — check logs:"
    echo "     tail -50 /var/log/wellguard/err.log"
fi

PUBLIC_IP=$(curl -s ifconfig.me || echo "46.202.130.253")
echo ""
echo "======================================"
echo "  🚀 WellGuard AI is live!"
echo "  URL: http://$PUBLIC_IP"
echo "======================================"
