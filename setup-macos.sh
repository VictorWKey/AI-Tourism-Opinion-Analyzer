#!/usr/bin/env bash
# ============================================================
# TourlyAI — macOS Developer Setup Script
# ============================================================
# Sets up the local development environment on macOS.
#
# Usage:
#   chmod +x setup-macos.sh
#   ./setup-macos.sh
# ============================================================
set -euo pipefail

echo "╔══════════════════════════════════════════════════════╗"
echo "║         TourlyAI — macOS Developer Setup            ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── 1. Check Node.js ──
echo "[1/6] Checking Node.js..."
if ! command -v node &>/dev/null; then
  echo "  ✗ Node.js not found."
  echo "    Install via Homebrew: brew install node"
  echo "    Or download from: https://nodejs.org"
  exit 1
fi
NODE_VERSION=$(node --version)
echo "  ✓ Node.js ${NODE_VERSION}"

# ── 2. Check Python ──
echo ""
echo "[2/6] Checking Python..."
PYTHON_CMD=""
if command -v python3 &>/dev/null; then
  PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
  PY_VER=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
  if [[ "${PY_VER}" == 3.* ]]; then
    PYTHON_CMD="python"
  fi
fi

if [ -z "${PYTHON_CMD}" ]; then
  echo "  ✗ Python 3 not found."
  echo "    Install via Homebrew: brew install python@3.11"
  exit 1
fi
PY_VERSION=$(${PYTHON_CMD} --version)
echo "  ✓ ${PY_VERSION}"

# ── 3. Install Node dependencies ──
echo ""
echo "[3/6] Installing Node.js dependencies..."
npm install
echo "  ✓ npm install complete"

# ── 4. Create Python virtual environment ──
echo ""
echo "[4/6] Creating Python virtual environment..."
cd python

if [ -d "venv" ]; then
  echo "  ⚠ Virtual environment already exists. Skipping creation."
  echo "    To recreate, delete python/venv and run this script again."
else
  ${PYTHON_CMD} -m venv venv
  echo "  ✓ Virtual environment created"
fi

# ── 5. Install Python dependencies ──
echo ""
echo "[5/6] Installing Python dependencies (this may take several minutes)..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
echo "  ✓ Python dependencies installed"

cd ..

# ── 6. Generate icons ──
echo ""
echo "[6/6] Generating app icons..."
if [ -f "resources/icons/1024x1024_primary_background_white_logo.png" ]; then
  node scripts/generate-icons.mjs
  echo "  ✓ Icons generated"
else
  echo "  ⚠ Source logo not found, skipping icon generation"
fi

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║              Setup Complete! 🎉                      ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Start the app:  npm start                          ║"
echo "║  Run tests:      npm test                           ║"
echo "║  Build:          npm run make                       ║"
echo "╚══════════════════════════════════════════════════════╝"
