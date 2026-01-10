#!/usr/bin/env python3
"""
Claude Code Statusline - Cross-platform statusline for Claude Code CLI.

Displays: Model | Project | Git Branch | Context Usage | API Usage (optional)

Supports: macOS, Linux, Windows (WSL)
"""

import json
import os
import platform
import subprocess
import sys
from pathlib import Path


def get_config():
    """Load configuration from ~/.claude/statusline-config.json"""
    config_path = Path.home() / ".claude" / "statusline-config.json"
    default_config = {
        "show_usage_limits": False,
        "show_git_branch": True,
        "show_context_bar": True,
        "show_model": True,
        "show_project": True,
    }

    if config_path.exists():
        try:
            with open(config_path) as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except (json.JSONDecodeError, IOError):
            pass

    return default_config


def get_credentials():
    """Get OAuth credentials based on the operating system."""
    system = platform.system()

    if system == "Darwin":  # macOS
        return get_credentials_macos()
    else:  # Linux, Windows (WSL), or other
        return get_credentials_file()


def get_credentials_macos():
    """Get credentials from macOS Keychain."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "Claude Code-credentials", "-w"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout.strip())
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return None


def get_credentials_file():
    """Get credentials from ~/.claude/.credentials.json file."""
    cred_path = Path.home() / ".claude" / ".credentials.json"

    if cred_path.exists():
        try:
            with open(cred_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return None


def get_usage_limits(access_token):
    """Fetch usage limits from the Anthropic API."""
    try:
        import urllib.request
        import urllib.error

        url = "https://api.anthropic.com/api/oauth/usage"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "anthropic-beta": "oauth-2025-04-20"
        }

        req = urllib.request.Request(url, headers=headers, method="GET")

        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            five_hour = data.get("five_hour", {}).get("utilization")
            seven_day = data.get("seven_day", {}).get("utilization")

            if five_hour is not None and seven_day is not None:
                return f"5h: {five_hour}% / 7d: {seven_day}%"
    except Exception:
        pass

    return None


def get_git_branch(cwd):
    """Get the current git branch for the given directory."""
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def create_progress_bar(percentage, width=20):
    """Create a visual progress bar."""
    filled = int(percentage / (100 / width))
    empty = width - filled
    return "\u2588" * filled + "\u2591" * empty


def format_tokens(tokens):
    """Format token count as K."""
    return f"{tokens // 1000}K"


def main():
    # ANSI color codes
    COLOR_MODEL = "\033[36m"      # Cyan
    COLOR_PROJECT = "\033[33m"    # Yellow
    COLOR_BRANCH = "\033[32m"     # Green
    COLOR_CONTEXT = "\033[35m"    # Magenta
    COLOR_USAGE = "\033[31m"      # Red
    COLOR_RESET = "\033[0m"
    SEPARATOR = f" \033[2m|\033[0m "  # Dimmed pipe

    # Load configuration
    config = get_config()

    # Read JSON input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)

    # Extract values from input
    model = input_data.get("model", {}).get("display_name", "")
    cwd = input_data.get("workspace", {}).get("current_dir", "")
    project_name = os.path.basename(cwd) if cwd else ""

    # Build output parts
    parts = []

    # Model name
    if config.get("show_model") and model:
        parts.append(f"{COLOR_MODEL}{model}{COLOR_RESET}")

    # Project name
    if config.get("show_project") and project_name:
        parts.append(f"{COLOR_PROJECT}{project_name}{COLOR_RESET}")

    # Git branch
    if config.get("show_git_branch") and cwd:
        branch = get_git_branch(cwd)
        if branch:
            parts.append(f"{COLOR_BRANCH}{branch}{COLOR_RESET}")

    # Context window usage
    if config.get("show_context_bar"):
        context_window = input_data.get("context_window", {})
        size = context_window.get("context_window_size", 200000)
        current_usage = context_window.get("current_usage", {})

        if current_usage:
            input_tokens = current_usage.get("input_tokens", 0)
            cache_creation = current_usage.get("cache_creation_input_tokens", 0)
            cache_read = current_usage.get("cache_read_input_tokens", 0)
            output_tokens = current_usage.get("output_tokens", 0)

            context_tokens = input_tokens + cache_creation + cache_read
            total_tokens = context_tokens + output_tokens
            percentage = min(100, int(context_tokens * 100 / size)) if size > 0 else 0

            bar = create_progress_bar(percentage)
            context_display = f"{percentage}% [{bar}] {format_tokens(total_tokens)}/{format_tokens(size)} tokens"
        else:
            bar = create_progress_bar(0)
            context_display = f"0% [{bar}] 0K/{format_tokens(size)} tokens"

        parts.append(f"{COLOR_CONTEXT}{context_display}{COLOR_RESET}")

    # Usage limits (optional)
    if config.get("show_usage_limits"):
        credentials = get_credentials()
        if credentials:
            oauth_data = credentials.get("claudeAiOauth", {})
            access_token = oauth_data.get("accessToken")

            if access_token:
                usage_display = get_usage_limits(access_token)
                if usage_display:
                    parts.append(f"{COLOR_USAGE}{usage_display}{COLOR_RESET}")

    # Output the final statusline
    if parts:
        print(SEPARATOR.join(parts), end="")


if __name__ == "__main__":
    main()
