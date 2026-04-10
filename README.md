# Claude Code Statusline

A simple, cross-platform statusline for [Claude Code](https://claude.ai/code) that displays useful context at a glance.

**Supports:** macOS, Linux, Windows (WSL)

```
Opus 4.5 | my-project | main *3 (+1,~2) ↑2 ↓1 | 14% [███░░░░░░░░░░░░░░░░░] 28K/200K tokens | 1h 23m | 42 msgs
```

## Features

- **Model name** - Active Claude model
- **Project name** - Current working directory
- **Git branch + status** - Branch, modified/staged/untracked counts, ahead/behind remote
- **Context window** - Visual progress bar showing token usage
- **API usage limits** - 5-hour and 7-day utilization (optional, requires OAuth)
- **Session duration** and **message count**

## Install

1. Copy the script:

```bash
curl -o ~/.claude/statusline.py https://raw.githubusercontent.com/RobbieFrancis/claude-statusline/main/statusline.py
```

2. Add to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py"
  }
}
```

3. Restart Claude Code.

## Configuration

Optionally create `~/.claude/statusline-config.json` to toggle sections:

```json
{
  "show_title": false,
  "show_model": true,
  "show_project": true,
  "show_git_branch": true,
  "show_git_status": true,
  "show_git_ahead_behind": true,
  "show_context_bar": true,
  "show_usage_limits": false,
  "show_session_duration": true,
  "show_message_count": true
}
```

## Requirements

- Python 3.6+
- Claude Code CLI
- No pip dependencies (stdlib only)

## License

MIT
