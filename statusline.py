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
        "title": "Statusline_Pro",
        "show_title": True,
        "show_usage_limits": False,
        "show_git_branch": True,
        "show_git_status": True,
        "show_git_ahead_behind": True,
        "show_context_bar": True,
        "show_model": True,
        "show_project": True,
        "show_message_count": True,
        "show_session_duration": True,
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


def get_git_status(cwd):
    """Get git status information: modified files, staged files, untracked files."""
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "--no-optional-locks", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if not lines or lines == ['']:
                return {'modified': 0, 'staged': 0, 'untracked': 0}

            modified = 0
            staged = 0
            untracked = 0

            for line in lines:
                if len(line) < 2:
                    continue

                index_status = line[0]
                work_tree_status = line[1]

                # Staged changes (index status)
                if index_status in ['M', 'A', 'D', 'R', 'C']:
                    staged += 1

                # Modified in working tree
                if work_tree_status == 'M':
                    modified += 1

                # Untracked files
                if index_status == '?' and work_tree_status == '?':
                    untracked += 1

            return {'modified': modified, 'staged': staged, 'untracked': untracked}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def get_git_ahead_behind(cwd):
    """Get how many commits ahead/behind the remote branch."""
    try:
        # First check if there's an upstream branch
        result = subprocess.run(
            ["git", "-C", cwd, "--no-optional-locks", "rev-parse", "--abbrev-ref", "@{upstream}"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode != 0:
            return None  # No upstream branch

        # Get ahead/behind counts
        result = subprocess.run(
            ["git", "-C", cwd, "--no-optional-locks", "rev-list", "--left-right", "--count", "HEAD...@{upstream}"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            counts = result.stdout.strip().split()
            if len(counts) == 2:
                ahead = int(counts[0])
                behind = int(counts[1])
                return {'ahead': ahead, 'behind': behind}
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
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


def get_message_count(transcript_path):
    """Count the number of messages in the transcript file."""
    try:
        if not transcript_path or not Path(transcript_path).exists():
            return 0

        with open(transcript_path, 'r') as f:
            transcript = json.load(f)
            messages = transcript.get("messages", [])
            return len(messages)
    except (json.JSONDecodeError, IOError, FileNotFoundError):
        return 0


def get_session_duration(transcript_path):
    """Calculate session duration from transcript timestamps."""
    try:
        if not transcript_path or not Path(transcript_path).exists():
            return None

        with open(transcript_path, 'r') as f:
            transcript = json.load(f)
            messages = transcript.get("messages", [])

            if not messages:
                return None

            # Find the first message timestamp
            first_timestamp = None
            for message in messages:
                if "timestamp" in message:
                    first_timestamp = message["timestamp"]
                    break

            if not first_timestamp:
                return None

            # Calculate duration from first message to now
            from datetime import datetime

            # Parse ISO timestamp
            first_time = datetime.fromisoformat(first_timestamp.replace('Z', '+00:00'))
            current_time = datetime.now(first_time.tzinfo)

            duration_seconds = int((current_time - first_time).total_seconds())

            # Format duration
            if duration_seconds < 60:
                return f"{duration_seconds}s"

            minutes = duration_seconds // 60
            if minutes < 60:
                return f"{minutes}m"

            hours = minutes // 60
            remaining_minutes = minutes % 60

            if remaining_minutes > 0:
                return f"{hours}h {remaining_minutes}m"
            else:
                return f"{hours}h"

    except (json.JSONDecodeError, IOError, FileNotFoundError, ValueError):
        return None


def main():
    # ANSI color codes
    COLOR_TITLE = "\033[1;97m"    # Bold white
    COLOR_MODEL = "\033[36m"      # Cyan
    COLOR_PROJECT = "\033[33m"    # Yellow
    COLOR_BRANCH = "\033[32m"     # Green
    COLOR_MODIFIED = "\033[33m"   # Yellow (for modified files)
    COLOR_AHEAD = "\033[32m"      # Green (for ahead commits)
    COLOR_BEHIND = "\033[31m"     # Red (for behind commits)
    COLOR_CONTEXT = "\033[35m"    # Magenta
    COLOR_USAGE = "\033[31m"      # Red
    COLOR_MESSAGE = "\033[34m"    # Blue
    COLOR_DURATION = "\033[36m"   # Cyan
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
    transcript_path = input_data.get("transcript_path", "")

    # Build output parts
    parts = []

    # Title
    if config.get("show_title"):
        title = config.get("title", "Statusline_Pro")
        parts.append(f"{COLOR_TITLE}{title}{COLOR_RESET}")

    # Model name
    if config.get("show_model") and model:
        parts.append(f"{COLOR_MODEL}{model}{COLOR_RESET}")

    # Project name
    if config.get("show_project") and project_name:
        parts.append(f"{COLOR_PROJECT}{project_name}{COLOR_RESET}")

    # Git branch with status
    if config.get("show_git_branch") and cwd:
        branch = get_git_branch(cwd)
        if branch:
            git_info = f"{COLOR_BRANCH}{branch}{COLOR_RESET}"

            # Add git status (modified, staged, untracked files)
            if config.get("show_git_status"):
                status = get_git_status(cwd)
                if status:
                    status_indicators = []
                    total_changes = status['modified'] + status['staged'] + status['untracked']

                    if total_changes > 0:
                        # Show total uncommitted changes
                        status_indicators.append(f"{COLOR_MODIFIED}*{total_changes}{COLOR_RESET}")

                        # Optionally show breakdown
                        details = []
                        if status['staged'] > 0:
                            details.append(f"+{status['staged']}")
                        if status['modified'] > 0:
                            details.append(f"~{status['modified']}")
                        if status['untracked'] > 0:
                            details.append(f"?{status['untracked']}")

                        if details:
                            status_indicators.append(f"{COLOR_MODIFIED}({','.join(details)}){COLOR_RESET}")

                    if status_indicators:
                        git_info += " " + " ".join(status_indicators)

            # Add ahead/behind indicators
            if config.get("show_git_ahead_behind"):
                ahead_behind = get_git_ahead_behind(cwd)
                if ahead_behind:
                    ab_indicators = []
                    if ahead_behind['ahead'] > 0:
                        ab_indicators.append(f"{COLOR_AHEAD}↑{ahead_behind['ahead']}{COLOR_RESET}")
                    if ahead_behind['behind'] > 0:
                        ab_indicators.append(f"{COLOR_BEHIND}↓{ahead_behind['behind']}{COLOR_RESET}")

                    if ab_indicators:
                        git_info += " " + " ".join(ab_indicators)

            parts.append(git_info)

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

    # Session duration
    if config.get("show_session_duration"):
        session_duration = get_session_duration(transcript_path)
        if session_duration:
            parts.append(f"{COLOR_DURATION}{session_duration}{COLOR_RESET}")

    # Message count
    if config.get("show_message_count"):
        message_count = get_message_count(transcript_path)
        if message_count > 0:
            parts.append(f"{COLOR_MESSAGE}{message_count} msgs{COLOR_RESET}")

    # Output the final statusline
    if parts:
        print(SEPARATOR.join(parts), end="")


if __name__ == "__main__":
    main()
