---
description: Configure statusline display options with visual UI
---

You are helping the user configure their Claude Code statusline. Follow these steps:

## Step 1: Read Current Config
Read the config file at `~/.claude/statusline-config.json`. If it doesn't exist, use these defaults:
```json
{
  "title": "Statusline_Pro",
  "show_title": true,
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

## Step 2: Display Current Settings
Show the current configuration visually using this format:

```
╔══════════════════════════════════════════════════════════════╗
║  Statusline Configuration                                    ║
╠══════════════════════════════════════════════════════════════╣
║  Title: "Statusline_Pro"                                     ║
╠══════════════════════════════════════════════════════════════╣
║  ✓ Show Title          ✓ Show Model          ✓ Show Project  ║
║  ✓ Git Branch          ✓ Git Status          ✓ Ahead/Behind  ║
║  ✓ Context Bar         ✗ Usage Limits        ✓ Duration      ║
║  ✓ Message Count                                             ║
╠══════════════════════════════════════════════════════════════╣
║  Preview:                                                    ║
║  Statusline_Pro | Opus 4.5 | project | main *3 | 15% [███░░] ║
╚══════════════════════════════════════════════════════════════╝
```

Use ✓ for enabled options and ✗ for disabled options.

Generate a realistic preview based on which options are enabled.

## Step 3: Ask What to Change
Use the AskUserQuestion tool with multi-select to let the user choose which options to toggle:

Question: "Which options would you like to toggle? (Currently enabled options will be disabled, disabled will be enabled)"
Header: "Toggle"
Options should include all 10 boolean options plus "Change title" and "Done - save and exit"

## Step 4: Apply Changes
- If user selects options to toggle, flip their boolean values
- If user selects "Change title", ask for the new title text
- Write the updated config to `~/.claude/statusline-config.json`
- Show the updated visual display with new preview
- Repeat from Step 3 until user selects "Done"

## Step 5: Confirm Save
When user selects "Done", confirm the changes were saved and remind them that changes take effect immediately (no restart needed).

IMPORTANT: Always use the visual box format to display settings. Make the preview realistic based on enabled options.
