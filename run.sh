#!/bin/bash

# Copilot Agent 365 - Local Development Runner
# Requires Python 3.11 for Azure Functions v4 compatibility

set -e

REQUIRED_PYTHON_VERSION="3.11"
VENV_DIR=".venv"

# Color output helpers
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
echo_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Function to check if a Python version is 3.11.x
is_python_311() {
    local python_cmd=$1
    if command -v "$python_cmd" &> /dev/null; then
        local version=$("$python_cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
        if [[ "$version" == "3.11" ]]; then
            return 0
        fi
    fi
    return 1
}

# Function to find Python 3.11
find_python_311() {
    # Check common Python 3.11 commands
    for cmd in python3.11 python311 python3 python; do
        if is_python_311 "$cmd"; then
            echo "$cmd"
            return 0
        fi
    done

    # Check Homebrew paths on macOS
    if [[ "$(uname)" == "Darwin" ]]; then
        for brew_path in /opt/homebrew/bin/python3.11 /usr/local/bin/python3.11; do
            if [[ -x "$brew_path" ]] && is_python_311 "$brew_path"; then
                echo "$brew_path"
                return 0
            fi
        done
    fi

    return 1
}

# Function to install Python 3.11
install_python_311() {
    echo_info "Python 3.11 not found. Attempting to install..."

    if [[ "$(uname)" == "Darwin" ]]; then
        # macOS - use Homebrew
        if command -v brew &> /dev/null; then
            echo_info "Installing Python 3.11 via Homebrew..."
            brew install python@3.11

            # Add Homebrew Python to PATH for this session
            export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

            if command -v python3.11 &> /dev/null; then
                echo_info "Python 3.11 installed successfully"
                return 0
            fi
        else
            echo_error "Homebrew not found. Please install Homebrew first:"
            echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "Then run: brew install python@3.11"
            return 1
        fi
    elif [[ -f /etc/debian_version ]]; then
        # Debian/Ubuntu
        echo_info "Installing Python 3.11 via apt..."
        sudo apt-get update
        sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
        return 0
    elif [[ -f /etc/redhat-release ]]; then
        # RHEL/CentOS/Fedora
        echo_info "Installing Python 3.11 via dnf..."
        sudo dnf install -y python3.11 python3.11-devel
        return 0
    else
        echo_error "Unsupported OS. Please install Python 3.11 manually."
        echo "  Visit: https://www.python.org/downloads/"
        return 1
    fi
}

# Main script starts here
echo "========================================"
echo "  Copilot Agent 365 - Local Runner"
echo "========================================"
echo ""

# Check for Python 3.11
PYTHON_CMD=$(find_python_311)

if [[ -z "$PYTHON_CMD" ]]; then
    echo_warn "Python 3.11 not found on system."

    read -p "Would you like to install Python 3.11? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_python_311
        PYTHON_CMD=$(find_python_311)
        if [[ -z "$PYTHON_CMD" ]]; then
            echo_error "Failed to install Python 3.11. Please install manually."
            exit 1
        fi
    else
        echo_error "Python 3.11 is required for Azure Functions v4 compatibility."
        echo "Please install Python 3.11 and try again."
        exit 1
    fi
fi

echo_info "Using Python: $PYTHON_CMD ($($PYTHON_CMD --version))"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo_info "Creating virtual environment with Python 3.11..."
    $PYTHON_CMD -m venv "$VENV_DIR"
fi

# Verify venv uses Python 3.11
VENV_PYTHON=""
if [ -f "$VENV_DIR/bin/python" ]; then
    VENV_PYTHON="$VENV_DIR/bin/python"
elif [ -f "$VENV_DIR/Scripts/python.exe" ]; then
    VENV_PYTHON="$VENV_DIR/Scripts/python.exe"
fi

if [[ -n "$VENV_PYTHON" ]]; then
    VENV_VERSION=$($VENV_PYTHON --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    if [[ "$VENV_VERSION" != "3.11" ]]; then
        echo_warn "Existing virtual environment uses Python $VENV_VERSION, recreating with Python 3.11..."
        rm -rf "$VENV_DIR"
        $PYTHON_CMD -m venv "$VENV_DIR"
    fi
fi

# Activate virtual environment
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
else
    echo_error "Could not find virtual environment activation script"
    exit 1
fi

echo_info "Virtual environment activated"
echo_info "Python version: $(python --version)"

# Install dependencies if requirements.txt exists and packages not installed
if [ -f "requirements.txt" ]; then
    # Check if azure-functions is installed (quick check)
    if ! python -c "import azure.functions" 2>/dev/null; then
        echo_info "Installing dependencies..."
        pip install --upgrade pip -q
        pip install -r requirements.txt -q
        echo_info "Dependencies installed"
    fi
fi

# Check for Azure Functions Core Tools
if ! command -v func &> /dev/null; then
    echo_error "Azure Functions Core Tools not found."
    echo ""
    echo "Install with:"
    if [[ "$(uname)" == "Darwin" ]]; then
        echo "  brew tap azure/functions"
        echo "  brew install azure-functions-core-tools@4"
    else
        echo "  npm install -g azure-functions-core-tools@4"
    fi
    echo ""
    echo "Or visit: https://docs.microsoft.com/azure/azure-functions/functions-run-local"
    exit 1
fi

# Check for local.settings.json
if [ ! -f "local.settings.json" ]; then
    echo_error "local.settings.json not found."
    echo "Please run the deployment script first or create local.settings.json manually."
    echo "See CLAUDE.md for required configuration."
    exit 1
fi

echo ""
echo_info "Starting Copilot Agent 365..."
echo_info "Local URL: http://localhost:7071/api/businessinsightbot_function"
echo_info "Press Ctrl+C to stop"
echo ""

func start
