#!/bin/bash

# Read JSON input from stdin
input=$(cat)

# Write debug output to file for inspection
echo "$input" | jq '.' > /tmp/statusline-debug.json 2>/dev/null

# Extract values
model=$(echo "$input" | jq -r '.model.display_name')
cwd=$(echo "$input" | jq -r '.workspace.current_dir')
project_name=$(basename "$cwd")

# Get git branch if in a git repo
git_branch=""
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
    branch=$(git -C "$cwd" branch --show-current 2>/dev/null)
    if [ -n "$branch" ]; then
        git_branch="$branch"
    fi
fi

# ANSI color codes for status line
COLOR_MODEL="\033[36m"      # Cyan for model
COLOR_PROJECT="\033[33m"    # Yellow for project
COLOR_BRANCH="\033[32m"     # Green for branch
COLOR_CONTEXT="\033[35m"    # Magenta for context
COLOR_USAGE="\033[31m"      # Red for usage limits
COLOR_RESET="\033[0m"
SEPARATOR=" \033[2m|\033[0m "  # Dimmed pipe separator

# Get Claude usage limits from API
usage_display=""
# Try to get access token from keychain
keychain_data=$(security find-generic-password -s "Claude Code-credentials" -w 2>/dev/null)
if [ -n "$keychain_data" ]; then
    access_token=$(echo "$keychain_data" | jq -r '.claudeAiOauth.accessToken' 2>/dev/null)

    if [ -n "$access_token" ] && [ "$access_token" != "null" ]; then
        # Call Anthropic usage API
        usage_response=$(curl -s -X GET "https://api.anthropic.com/api/oauth/usage" \
            -H "Accept: application/json" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $access_token" \
            -H "anthropic-beta: oauth-2025-04-20" 2>/dev/null)

        if [ -n "$usage_response" ]; then
            five_hour=$(echo "$usage_response" | jq -r '.five_hour.utilization' 2>/dev/null)
            seven_day=$(echo "$usage_response" | jq -r '.seven_day.utilization' 2>/dev/null)

            if [ "$five_hour" != "null" ] && [ "$seven_day" != "null" ]; then
                usage_display="5h: ${five_hour}% / 7d: ${seven_day}%"
            fi
        fi
    fi
fi

# Calculate context window usage and create progress bar
size=$(echo "$input" | jq '.context_window.context_window_size')
current_usage=$(echo "$input" | jq '.context_window.current_usage')

# Calculate actual context being used (includes cache tokens from current context)
if [ "$current_usage" != "null" ]; then
    # Current context includes: input_tokens + cache_creation + cache_read
    input_tokens=$(echo "$current_usage" | jq '.input_tokens')
    cache_creation=$(echo "$current_usage" | jq '.cache_creation_input_tokens')
    cache_read=$(echo "$current_usage" | jq '.cache_read_input_tokens')
    output_tokens=$(echo "$current_usage" | jq '.output_tokens')

    # Total context tokens (what's actually in the context window)
    context_tokens=$((input_tokens + cache_creation + cache_read))

    # Calculate percentage based on actual context
    pct=$((context_tokens * 100 / size))

    # Create progress bar (20 characters wide)
    filled=$((pct / 5))
    empty=$((20 - filled))
    bar=$(printf "%${filled}s" | tr ' ' '█')$(printf "%${empty}s" | tr ' ' '░')

    # Format with maximum tokens shown
    total_tokens=$((context_tokens + output_tokens))
    size_k=$((size / 1000))
    tokens_k=$((total_tokens / 1000))

    context_display="${pct}% [${bar}] ${tokens_k}K/${size_k}K tokens"
else
    size_k=$((size / 1000))
    context_display="0% [░░░░░░░░░░░░░░░░░░░░] 0K/${size_k}K tokens"
fi

# Build status line with colors and separators
output=""

if [ -n "$model" ]; then
    output="${COLOR_MODEL}${model}${COLOR_RESET}"
fi

if [ -n "$project_name" ]; then
    if [ -n "$output" ]; then
        output="${output}${SEPARATOR}"
    fi
    output="${output}${COLOR_PROJECT}${project_name}${COLOR_RESET}"
fi

if [ -n "$git_branch" ]; then
    if [ -n "$output" ]; then
        output="${output}${SEPARATOR}"
    fi
    output="${output}${COLOR_BRANCH}${git_branch}${COLOR_RESET}"
fi

if [ -n "$output" ]; then
    output="${output}${SEPARATOR}"
fi
output="${output}${COLOR_CONTEXT}${context_display}${COLOR_RESET}"

# Add usage limits if available
if [ -n "$usage_display" ]; then
    output="${output}${SEPARATOR}${COLOR_USAGE}${usage_display}${COLOR_RESET}"
fi

# Output the final status line
printf "%b" "$output"
