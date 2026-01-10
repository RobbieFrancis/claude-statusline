#!/bin/bash
#
# Claude Code Statusline Installer
# One-liner: curl -sSL https://raw.githubusercontent.com/RobbieFrancis/claude-statusline/main/install.sh | bash
#

set -e

REPO_URL="https://raw.githubusercontent.com/RobbieFrancis/claude-statusline/main"
CLAUDE_DIR="$HOME/.claude"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "=========================================="
echo "  Claude Code Statusline Installer"
echo "=========================================="
echo ""

# Detect OS
OS="unknown"
case "$(uname -s)" in
    Darwin*)    OS="macOS" ;;
    Linux*)     OS="Linux" ;;
    CYGWIN*|MINGW*|MSYS*) OS="Windows" ;;
esac

echo -e "${GREEN}Detected OS:${NC} $OS"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    echo ""
    case "$OS" in
        macOS)   echo "Install with: brew install python3" ;;
        Linux)   echo "Install with: sudo apt install python3  (or your package manager)" ;;
        Windows) echo "Install from: https://www.python.org/downloads/" ;;
    esac
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo -e "${GREEN}Python:${NC} $PYTHON_VERSION"

# Create .claude directory if it doesn't exist
mkdir -p "$CLAUDE_DIR"

# Download statusline.py
echo ""
echo "Downloading statusline.py..."
curl -sSL "$REPO_URL/statusline.py" -o "$CLAUDE_DIR/statusline.py"
chmod +x "$CLAUDE_DIR/statusline.py"
echo -e "${GREEN}Downloaded:${NC} $CLAUDE_DIR/statusline.py"

# Create default config if it doesn't exist
CONFIG_FILE="$CLAUDE_DIR/statusline-config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating default configuration..."
    cat > "$CONFIG_FILE" << 'EOF'
{
  "title": "Statusline_Pro",
  "show_title": true,
  "show_usage_limits": false,
  "show_git_branch": true,
  "show_git_status": true,
  "show_git_ahead_behind": true,
  "show_context_bar": true,
  "show_model": true,
  "show_project": true,
  "show_message_count": true,
  "show_session_duration": true
}
EOF
    echo -e "${GREEN}Created:${NC} $CONFIG_FILE"
else
    echo -e "${YELLOW}Config exists:${NC} $CONFIG_FILE (not overwritten)"
fi

# Update settings.json
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
if [ -f "$SETTINGS_FILE" ]; then
    # Check if statusLine is already configured
    if grep -q '"statusLine"' "$SETTINGS_FILE" 2>/dev/null; then
        echo -e "${YELLOW}Settings:${NC} statusLine already configured in $SETTINGS_FILE"
        echo -e "${YELLOW}         You may need to manually update the command to:${NC}"
        echo '         "command": "python3 ~/.claude/statusline.py"'
    else
        # Backup and update
        cp "$SETTINGS_FILE" "$SETTINGS_FILE.backup"
        # Simple JSON merge - add statusLine to existing settings
        python3 << 'PYTHON_SCRIPT'
import json
import os

settings_path = os.path.expanduser("~/.claude/settings.json")
with open(settings_path) as f:
    settings = json.load(f)

settings["statusLine"] = {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py"
}

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
PYTHON_SCRIPT
        echo -e "${GREEN}Updated:${NC} $SETTINGS_FILE"
    fi
else
    # Create new settings.json
    cat > "$SETTINGS_FILE" << 'EOF'
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py"
  }
}
EOF
    echo -e "${GREEN}Created:${NC} $SETTINGS_FILE"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Installation complete!${NC}"
echo "=========================================="
echo ""
echo "Restart Claude Code to see your new statusline."
echo ""
echo "To enable API usage limits display, edit:"
echo "  $CONFIG_FILE"
echo "and set \"show_usage_limits\": true"
echo ""
