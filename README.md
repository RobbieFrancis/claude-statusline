# Claude Code Statusline

A custom statusline for [Claude Code](https://claude.ai/code) that displays useful context at a glance.

## Preview

```
Opus 4.5 | claude-statusline-backup | main | 14% [██░░░░░░░░░░░░░░░░░░] 28K/200K tokens | 5h: 47.0% / 7d: 17.0%
```

## Features

- **Model name** - Shows which Claude model is active (e.g., Opus 4.5)
- **Project name** - Current working directory/project
- **Git branch** - Current branch when in a git repository
- **Context window** - Visual progress bar showing token usage
- **API usage limits** - 5-hour and 7-day utilization percentages

## Installation

```bash
mkdir -p ~/.claude
curl -o ~/.claude/statusline-command.sh https://raw.githubusercontent.com/RobbieFrancis/claude-statusline/main/statusline-command.sh
curl -o ~/.claude/settings.json https://raw.githubusercontent.com/RobbieFrancis/claude-statusline/main/settings.json
chmod +x ~/.claude/statusline-command.sh
```

Or clone and copy:

```bash
git clone https://github.com/RobbieFrancis/claude-statusline.git /tmp/statusline
cp /tmp/statusline/statusline-command.sh /tmp/statusline/settings.json ~/.claude/
chmod +x ~/.claude/statusline-command.sh
```

## Requirements

- macOS (uses Keychain for API token)
- `jq` installed (`brew install jq`)
- Claude Code CLI

## Inspiration

This statusline was inspired by:

- [How to Show Claude Code Usage Limits in Your Statusline](https://codelynx.dev/posts/claude-code-usage-limits-statusline) by Melvynx - Great tutorial on displaying API usage limits in the statusline
- [Claude Clone Autonomous Coding Demo](https://www.youtube.com/watch?v=YW09hhnVqNM) by Leon - Video demonstrating autonomous coding with Claude Agent SDK, which sparked the idea of monitoring context window usage
