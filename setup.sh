#!/bin/bash
# Copilot Agent 365 - Mac/Linux Auto-Install Setup Script
# Save as setup.sh and run: bash setup.sh
# This script will automatically install missing dependencies

set -e

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
NC="\033[0m"

echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   Copilot Agent 365 - Setup (3.11)   ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    else
        echo "unknown"
    fi
}

OS_TYPE=$(detect_os)
echo -e "${CYAN}Detected OS: $OS_TYPE${NC}"
echo

check_python_version() {
    local cmd=$1
    if command_exists $cmd; then
        local version=$($cmd --version 2>&1 | grep -oE "[0-9]+\.[0-9]+" | head -1)
        local major=$(echo $version | cut -d. -f1)
        local minor=$(echo $version | cut -d. -f2)
        if [ "$major" -eq 3 ] && [ "$minor" -ge 9 ] && [ "$minor" -le 11 ]; then
            echo $cmd
            return 0
        fi
    fi
    return 1
}

install_homebrew() {
    if [[ "$OS_TYPE" == "macos" ]]; then
        if ! command_exists brew; then
            echo -e "${YELLOW}Installing Homebrew...${NC}"
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            if [[ -f "/opt/homebrew/bin/brew" ]]; then
                eval "$(/opt/homebrew/bin/brew shellenv)"
            fi
            echo -e "${GREEN}✓ Homebrew installed${NC}"
        else
            echo -e "${GREEN}✓ Found Homebrew${NC}"
        fi
    fi
}

install_python() {
    echo -e "${YELLOW}Installing Python 3.11...${NC}"
    if [[ "$OS_TYPE" == "macos" ]]; then
        brew install python@3.11
        echo -e "${GREEN}✓ Python 3.11 installed${NC}"
    elif [[ "$OS_TYPE" == "linux" ]]; then
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y python3.11 python3.11-venv python3-pip
            echo -e "${GREEN}✓ Python 3.11 installed${NC}"
        elif command_exists yum; then
            sudo yum install -y python311 python311-pip
            echo -e "${GREEN}✓ Python 3.11 installed${NC}"
        else
            echo -e "${RED}Unable to install Python automatically${NC}"
            exit 1
        fi
    fi
}

install_git() {
    echo -e "${YELLOW}Installing Git...${NC}"
    if [[ "$OS_TYPE" == "macos" ]]; then
        brew install git
        echo -e "${GREEN}✓ Git installed${NC}"
    elif [[ "$OS_TYPE" == "linux" ]]; then
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y git
            echo -e "${GREEN}✓ Git installed${NC}"
        elif command_exists yum; then
            sudo yum install -y git
            echo -e "${GREEN}✓ Git installed${NC}"
        else
            echo -e "${RED}Unable to install Git automatically${NC}"
            exit 1
        fi
    fi
}

install_nodejs() {
    echo -e "${YELLOW}Installing Node.js and npm...${NC}"
    if [[ "$OS_TYPE" == "macos" ]]; then
        brew install node
        echo -e "${GREEN}✓ Node.js and npm installed${NC}"
    elif [[ "$OS_TYPE" == "linux" ]]; then
        if command_exists apt-get; then
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            sudo apt-get install -y nodejs
            echo -e "${GREEN}✓ Node.js and npm installed${NC}"
        elif command_exists yum; then
            curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
            sudo yum install -y nodejs
            echo -e "${GREEN}✓ Node.js and npm installed${NC}"
        else
            echo -e "${RED}Unable to install Node.js automatically${NC}"
            exit 1
        fi
    fi
}

install_func_tools() {
    echo -e "${YELLOW}Installing Azure Functions Core Tools...${NC}"
    if [[ "$OS_TYPE" == "macos" ]]; then
        brew tap azure/functions
        brew install azure-functions-core-tools@4
        echo -e "${GREEN}✓ Azure Functions Core Tools installed${NC}"
    else
        if sudo npm install -g azure-functions-core-tools@4 --unsafe-perm true; then
            echo -e "${GREEN}✓ Azure Functions Core Tools installed${NC}"
        else
            npm install -g azure-functions-core-tools@4
            echo -e "${GREEN}✓ Azure Functions Core Tools installed${NC}"
        fi
    fi
}

echo -e "${YELLOW}▶ Checking and installing prerequisites...${NC}"

if [[ "$OS_TYPE" == "macos" ]]; then
    install_homebrew
fi

PYTHON_CMD=""
for cmd in python3.11 python3.10 python3.9 python3 python; do
    if result=$(check_python_version $cmd); then
        PYTHON_CMD=$result
        PYTHON_VERSION=$($cmd --version 2>&1)
        echo -e "${GREEN}✓ Found $PYTHON_VERSION${NC}"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${YELLOW}Python 3.9-3.11 not found, installing...${NC}"
    install_python
    for cmd in python3.11 python3.10 python3.9 python3 python; do
        if result=$(check_python_version $cmd); then
            PYTHON_CMD=$result
            PYTHON_VERSION=$($cmd --version 2>&1)
            echo -e "${GREEN}✓ Found $PYTHON_VERSION${NC}"
            break
        fi
    done
    if [ -z "$PYTHON_CMD" ]; then
        echo -e "${RED}Failed to install Python${NC}"
        exit 1
    fi
fi

if ! command_exists git; then
    echo -e "${YELLOW}Git not found, installing...${NC}"
    install_git
fi
if ! command_exists git; then
    echo -e "${RED}Failed to install Git${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Found Git${NC}"

if ! command_exists node || ! command_exists npm; then
    echo -e "${YELLOW}Node.js/npm not found, installing...${NC}"
    install_nodejs
fi
if ! command_exists node || ! command_exists npm; then
    echo -e "${RED}Failed to install Node.js/npm${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Found Node.js $(node --version)${NC}"
echo -e "${GREEN}✓ Found npm $(npm --version)${NC}"

if ! command_exists func; then
    install_func_tools
fi
if command_exists func; then
    echo -e "${GREEN}✓ Found Azure Functions Core Tools${NC}"
else
    echo -e "${YELLOW}⚠ Azure Functions Core Tools not available${NC}"
fi

echo
echo -e "${YELLOW}▶ Setting up project...${NC}"

# Preserve existing local.settings.json if it exists
LOCAL_SETTINGS_BACKUP=""
if [ -f "local.settings.json" ]; then
    echo -e "${YELLOW}Backing up existing local.settings.json...${NC}"
    LOCAL_SETTINGS_BACKUP=$(mktemp)
    cp local.settings.json "$LOCAL_SETTINGS_BACKUP"
fi

# Clone or update repository
if [ -f "function_app.py" ]; then
    echo -e "${GREEN}✓ Project files already exist${NC}"
    if [ -d ".git" ]; then
        echo -e "${YELLOW}Pulling latest updates...${NC}"
        git pull 2>/dev/null || echo -e "${YELLOW}Could not pull updates${NC}"
    fi
elif [ -d ".git" ]; then
    echo -e "${YELLOW}Git repository exists, pulling updates...${NC}"
    git pull
else
    # Need to clone - create temp dir, clone, copy files
    echo -e "${YELLOW}Cloning repository...${NC}"
    TEMP_DIR=$(mktemp -d)
    git clone https://github.com/kody-w/Copilot-Agent-365.git "$TEMP_DIR"

    # Copy all files from cloned repo to current directory
    echo -e "${YELLOW}Copying project files...${NC}"
    cp -r "$TEMP_DIR"/* . 2>/dev/null || true
    cp -r "$TEMP_DIR"/.[^.]* . 2>/dev/null || true

    # Clean up temp directory
    rm -rf "$TEMP_DIR"
    echo -e "${GREEN}✓ Project files installed${NC}"
fi

# Restore local.settings.json if we backed it up
if [ -n "$LOCAL_SETTINGS_BACKUP" ] && [ -f "$LOCAL_SETTINGS_BACKUP" ]; then
    echo -e "${YELLOW}Restoring your local.settings.json...${NC}"
    cp "$LOCAL_SETTINGS_BACKUP" local.settings.json
    rm -f "$LOCAL_SETTINGS_BACKUP"
    echo -e "${GREEN}✓ Configuration restored${NC}"
fi

echo -e "${YELLOW}▶ Checking configuration...${NC}"
if [ -f "local.settings.json" ]; then
    echo -e "${GREEN}✓ local.settings.json already exists${NC}"
else
    if [ -f "local.settings.template.json" ]; then
        echo -e "${YELLOW}Creating local.settings.json from template...${NC}"
        cp local.settings.template.json local.settings.json
        echo -e "${GREEN}✓ Configuration created from template${NC}"
        echo -e "${YELLOW}⚠ Please update local.settings.json with your Azure credentials${NC}"
    else
        echo -e "${YELLOW}Creating default local.settings.json...${NC}"
        cat > local.settings.json << 'EOF'
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_OPENAI_API_KEY": "<your-openai-api-key>",
    "AZURE_OPENAI_ENDPOINT": "https://<your-openai-service>.openai.azure.com/",
    "AZURE_OPENAI_API_VERSION": "2024-02-01",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-deployment",
    "AZURE_STORAGE_ACCOUNT_NAME": "<your-storage-account-name>",
    "AZURE_FILES_SHARE_NAME": "<your-file-share-name>",
    "ASSISTANT_NAME": "Copilot Agent 365",
    "CHARACTERISTIC_DESCRIPTION": "Enterprise AI assistant integrated with Microsoft 365"
  },
  "Host": {
    "CORS": "*",
    "CORSCredentials": false
  }
}
EOF
        echo -e "${GREEN}✓ Configuration template created${NC}"
        echo -e "${YELLOW}⚠ Please update local.settings.json with your Azure credentials${NC}"
    fi
fi

echo -e "${YELLOW}▶ Setting up Python environment...${NC}"
rm -rf .venv 2>/dev/null || true
$PYTHON_CMD -m venv .venv
source .venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed from requirements.txt${NC}"
else
    echo -e "${YELLOW}No requirements.txt found, installing core packages...${NC}"
    pip install openai==1.55.3 httpx==0.27.2 azure-functions==1.18.0 azure-identity azure-storage-file-share pydantic==1.10.13
    echo -e "${GREEN}✓ Core dependencies installed${NC}"
fi

cat > run.sh << 'RUNSCRIPT'
#!/bin/bash
source .venv/bin/activate
echo "Starting Copilot Agent 365..."
echo "Local URL: http://localhost:7071/api/businessinsightbot_function"
func start
RUNSCRIPT
chmod +x run.sh

echo
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✨ Setup Complete! ✨${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo -e "${CYAN}Next steps:${NC}"
echo "  1. Update local.settings.json with your Azure credentials (if needed)"
echo "  2. Run: ./run.sh"
echo
echo -e "${CYAN}To run locally:${NC} ./run.sh"
echo
