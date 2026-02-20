#!/usr/bin/env bash
# ============================================================
# TourlyAI — Linux Developer Setup Script
# ============================================================
# Sets up the local development environment on Linux.
# Supports: Ubuntu/Debian, Fedora/RHEL, Arch Linux, openSUSE
#
# Usage:
#   chmod +x setup-linux.sh
#   ./setup-linux.sh
# ============================================================
set -euo pipefail

echo "╔══════════════════════════════════════════════════════╗"
echo "║         TourlyAI — Linux Developer Setup            ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── Detect package manager ──
PM=""
if command -v apt &>/dev/null; then
  PM="apt"
elif command -v dnf &>/dev/null; then
  PM="dnf"
elif command -v pacman &>/dev/null; then
  PM="pacman"
elif command -v zypper &>/dev/null; then
  PM="zypper"
fi

# ── 1. Check / Install system dependencies ──
echo "[1/7] Checking system dependencies..."

# Check for build essentials needed by native Node modules
NEED_INSTALL=()
for cmd in gcc g++ make; do
  if ! command -v ${cmd} &>/dev/null; then
    NEED_INSTALL+=(${cmd})
  fi
done

if [ ${#NEED_INSTALL[@]} -gt 0 ]; then
  echo "  Installing build tools: ${NEED_INSTALL[*]}"
  case "${PM}" in
    apt)    sudo apt update && sudo apt install -y build-essential ;;
    dnf)    sudo dnf groupinstall -y "Development Tools" ;;
    pacman) sudo pacman -Sy --noconfirm base-devel ;;
    zypper) sudo zypper install -y -t pattern devel_basis ;;
    *)      echo "  ⚠ Unknown package manager. Please install build-essential manually." ;;
  esac
fi
echo "  ✓ Build tools available"

# ── 2. Check Node.js ──
echo ""
echo "[2/7] Checking Node.js..."
if ! command -v node &>/dev/null; then
  echo "  ✗ Node.js not found."
  echo "    Install via your package manager or nvm:"
  echo "      curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash"
  echo "      nvm install --lts"
  exit 1
fi
NODE_VERSION=$(node --version)
echo "  ✓ Node.js ${NODE_VERSION}"

# ── 3. Check Python ──
echo ""
echo "[3/7] Checking Python..."
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
  echo "  ✗ Python 3 not found. Installing..."
  case "${PM}" in
    apt)    sudo apt install -y python3 python3-venv python3-pip python3-dev ;;
    dnf)    sudo dnf install -y python3 python3-pip python3-devel ;;
    pacman) sudo pacman -Sy --noconfirm python python-pip ;;
    zypper) sudo zypper install -y python3 python3-pip python3-venv python3-devel ;;
    *)      echo "  ✗ Cannot auto-install Python. Install python3 manually." && exit 1 ;;
  esac
  PYTHON_CMD="python3"
fi
PY_VERSION=$(${PYTHON_CMD} --version)
echo "  ✓ ${PY_VERSION}"

# Check for python3-venv (Debian/Ubuntu may not include it)
if ! ${PYTHON_CMD} -m venv --help &>/dev/null; then
  echo "  Installing python3-venv..."
  case "${PM}" in
    apt) sudo apt install -y python3-venv ;;
    *)   ;;
  esac
fi

# ── 4. Install RPM/DEB build dependencies ──
echo ""
echo "[4/7] Checking Electron build dependencies..."
case "${PM}" in
  apt)
    # dpkg and fakeroot are needed for MakerDeb
    sudo apt install -y dpkg fakeroot 2>/dev/null || true
    ;;
  dnf)
    # rpm-build is needed for MakerRpm
    sudo dnf install -y rpm-build 2>/dev/null || true
    ;;
  *)
    ;;
esac
echo "  ✓ Electron build dependencies checked"

# ── 5. Install Node dependencies ──
echo ""
echo "[5/7] Installing Node.js dependencies..."
npm install
echo "  ✓ npm install complete"

# ── 6. Create Python virtual environment & install deps ──
echo ""
echo "[6/7] Setting up Python virtual environment..."
cd python

if [ -d "venv" ]; then
  echo "  ⚠ Virtual environment already exists. Skipping creation."
  echo "    To recreate, delete python/venv and run this script again."
else
  ${PYTHON_CMD} -m venv venv
  echo "  ✓ Virtual environment created"
fi

echo "  Installing Python dependencies (this may take several minutes)..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
echo "  ✓ Python dependencies installed"

cd ..

# ── 7. Generate icons ──
echo ""
echo "[7/7] Generating app icons..."
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
echo "║  Build DEB:      npm run make:linux                 ║"
echo "╚══════════════════════════════════════════════════════╝"
