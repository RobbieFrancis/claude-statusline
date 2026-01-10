# Claude Code Statusline

A cross-platform statusline for [Claude Code](https://claude.ai/code) that displays useful context at a glance.

**Supports:** macOS, Linux, Windows (WSL)

## Preview

```
Opus 4.5 | my-project | main | 14% [███░░░░░░░░░░░░░░░░░] 28K/200K tokens | 5h: 47.0% / 7d: 17.0%
```

## Features

- **Model name** - Shows which Claude model is active (e.g., Opus 4.5, Sonnet 4)
- **Project name** - Current working directory/project
- **Git branch** - Current branch when in a git repository
- **Context window** - Visual progress bar showing token usage
- **API usage limits** - 5-hour and 7-day utilization percentages (optional)

## Quick Install

```bash
curl -sSL https://raw.githubusercontent.com/RobbieFrancis/claude-statusline/main/install.sh | bash
```

Then restart Claude Code.

## Manual Installation

### 1. Download the script

```bash
mkdir -p ~/.claude
curl -o ~/.claude/statusline.py https://raw.githubusercontent.com/RobbieFrancis/claude-statusline/main/statusline.py
chmod +x ~/.claude/statusline.py
```

### 2. Configure Claude Code

Add this to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py"
  }
}
```

### 3. Restart Claude Code

## Configuration

Create `~/.claude/statusline-config.json` to customize the statusline:

```json
{
  "show_usage_limits": false,
  "show_git_branch": true,
  "show_context_bar": true,
  "show_model": true,
  "show_project": true
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `show_usage_limits` | `false` | Display API usage (5h/7d percentages). Requires OAuth. |
| `show_git_branch` | `true` | Show current git branch |
| `show_context_bar` | `true` | Show context window usage with progress bar |
| `show_model` | `true` | Show the active Claude model |
| `show_project` | `true` | Show the current project/directory name |

### Enabling Usage Limits

To show API usage limits, set `"show_usage_limits": true` in your config.

This feature reads your Claude Code OAuth credentials:
- **macOS**: From Keychain
- **Linux/WSL**: From `~/.claude/.credentials.json`

## Requirements

- Python 3.6+
- Claude Code CLI
- No additional pip dependencies (uses Python stdlib only)

## Platform Notes

### macOS

Works out of the box. Credentials are read from macOS Keychain.

### Linux

Works out of the box. Credentials are read from `~/.claude/.credentials.json`.

### Windows

Use Windows Subsystem for Linux (WSL). Install Claude Code in WSL and run the install script there.

## Troubleshooting

### Statusline not appearing

1. Make sure `~/.claude/settings.json` has the correct `statusLine` configuration
2. Check that Python 3 is installed: `python3 --version`
3. Restart Claude Code

### Usage limits not showing

1. Set `"show_usage_limits": true` in `~/.claude/statusline-config.json`
2. Make sure you're logged in to Claude Code (`claude login`)
3. Check credentials exist:
   - macOS: `security find-generic-password -s "Claude Code-credentials" -w`
   - Linux: `cat ~/.claude/.credentials.json`

## Files

| File | Location | Purpose |
|------|----------|---------|
| `statusline.py` | `~/.claude/` | Main statusline script |
| `statusline-config.json` | `~/.claude/` | Optional configuration |
| `settings.json` | `~/.claude/` | Claude Code settings |

## Legacy Bash Version

The original macOS-only bash script is available as `statusline-command.sh` for reference.

## Inspiration

This statusline was inspired by:

- [How to Show Claude Code Usage Limits in Your Statusline](https://codelynx.dev/posts/claude-code-usage-limits-statusline) by Melvynx
- [Claude Clone Autonomous Coding Demo](https://www.youtube.com/watch?v=YW09hhnVqNM) by Leon

## License

MIT License - Feel free to use, modify, and share!

## Contributing

Contributions welcome! Please open an issue or pull request.
