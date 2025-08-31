#!/bin/bash

# Default action
ACTION=${1:-full-without-git}
COMMIT_MESSAGE=${2:-""}
DOC_ID=${3:-""}

# Set the working directory to the project root
PROJECT_ROOT=$(dirname "$(realpath "$0")")
cd "$PROJECT_ROOT"

LOG_FILE="Temp/Logs.txt"
mkdir -p Temp
# Clear previous log file
> "$LOG_FILE"

# Logging functions
log() {
    echo "$@" >> "$LOG_FILE"
}

write_step_header() {
    local title=$1
    local step_number=${2:-0}
    local separator="============================================================"
    log ""
    log "$separator"
    if [ "$step_number" -gt 0 ]; then
        log " STEP $step_number: $title"
    else
        log " $title"
    fi
    log "$separator"
    log ""
}

write_success() {
    log "[SUCCESS] $1"
}

write_warning() {
    log "[WARNING] $1"
}

write_error() {
    log "[ERROR] $1"
}

# Python script path
PYTHON_SCRIPT="scripts/main.py"

invoke_python_function() {
    local function_name=$1
    local description=$2

    log "[SETUP] Ensuring Python dependencies are installed..."
    pip install -r scripts/requirements.txt --quiet

    log "[PYTHON] $description..."
    export THEAUTOMATON_POWERSHELL_CALLER='1'

    if python3 "$PYTHON_SCRIPT" "$function_name"; then
        unset THEAUTOMATON_POWERSHELL_CALLER
        write_success "$description completed."
        return 0
    else
        unset THEAUTOMATON_POWERSHELL_CALLER
        write_error "$description failed."
        return 1
    fi
}

invoke_git_operations() {
    local message=$1

    write_step_header "Git Operations" 2

    log "[GIT] Adding all changes to Git..."
    git add . >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        write_error "Git add failed"
        return 1
    fi

    log "[GIT] Committing with message: $message"
    git commit -m "$message" >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        write_error "Git commit failed"
        return 1
    fi

    log "[GIT] Pushing to remote repository..."
    git push >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        write_error "Git push failed"
        return 1
    fi

    write_success "Git operations completed successfully"
    return 0
}

show_help() {
    echo "The-Automaton Repository Workflow Script"
    echo "========================================"
    echo ""
    echo "USAGE: ./workflow.sh [Action] [Options]"
    echo ""
    echo "ACTIONS:"
    echo "  full                          Run complete workflow"
    echo "  full-without-git              Run complete workflow without Git operations (default)"
    echo "  chess-com                     Generate Chess.com profile"
    echo "  clear-temp                    Clear Temp directory"
    echo "  codeforces                    Generate Codeforces profile"
    echo "  generate-and-sync-profiles    Generate all profiles and sync to Google Docs"
    echo "  git-commit                    Commit and push changes"
    echo "  help                          Show this help"
    echo "  leetcode                      Generate LeetCode profile"
    echo "  markdown-lint                 Validate markdown files only"
    echo "  perplexity                    Run Perplexity query"
    echo "  steam-stats                   Fetch Steam gaming stats"
    echo "  sync-cloud                    Sync all shared files to Google Docs"
    echo "  sync-gdoc-chesscom            Sync Chess.com profile to Google Docs"
    echo "  sync-gdoc-codeforces          Sync Codeforces profile to Google Docs"
    echo "  sync-gdoc-leetcode            Sync LeetCode profile to Google Docs"
    echo "  sync-gdoc-steam               Sync Steam stats to Google Docs"
    echo "  sync-gdoc-youtube             Sync YouTube stats to Google Docs"
    echo "  sync-local                    Sync files to local cloud client (e.g., OneDrive)"
    echo "  youtube                       Generate YouTube profile"
    echo ""
    echo "OPTIONS:"
    echo "  [CommitMessage]  Specify commit message (as a second argument)"
    echo "  [DocId]          Specify Google Doc ID for a specific sync-gdoc action (as a third argument)"
}

# Main script execution
log "============================================================"
log "Workflow started at: $(date '+%Y-%m-%d %H:%M:%S')"
log "============================================================"
log "Action: $ACTION"

case "$ACTION" in
    "help")
        show_help
        ;;
    "full")
        # Pre-commit steps
        write_step_header "Pre-Commit Steps" 1
        invoke_python_function "markdown-lint" "Linting Markdown files" && \
        invoke_python_function "codeforces" "Generating Codeforces profile" && \
        invoke_python_function "leetcode" "Generating LeetCode profile" && \
        invoke_python_function "steam-stats" "Fetching Steam gaming stats" && \
        invoke_python_function "youtube" "Generating YouTube profile" && \
        invoke_python_function "chess-com" "Generating Chess.com profile"

        # Git operations
        if [ -z "$COMMIT_MESSAGE" ]; then
            config_file="config.yaml"
            temp_dir=$(grep 'temp:' "$config_file" | awk '{print $2}' | tr -d '"')
            commit_file=$(grep 'commit_message_file:' "$config_file" | awk '{print $2}' | tr -d '"')
            commit_message_path="$temp_dir/$commit_file"
            if [ -f "$commit_message_path" ]; then
                COMMIT_MESSAGE=$(grep -v '^#' "$commit_message_path" | head -n 1)
            else
                write_error "Commit message file not found at $commit_message_path"
                exit 1
            fi
        fi
        invoke_git_operations "$COMMIT_MESSAGE"

        # Post-push steps
        write_step_header "Post-Push Steps" 3
        invoke_python_function "sync-local" "Syncing outputs to local cloud client" && \
        invoke_python_function "sync-cloud" "Syncing all shared files to Google Docs"
        ;;
    "full-without-git")
        # Pre-commit steps
        write_step_header "Pre-Commit Steps" 1
        invoke_python_function "markdown-lint" "Linting Markdown files" && \
        invoke_python_function "codeforces" "Generating Codeforces profile" && \
        invoke_python_function "leetcode" "Generating LeetCode profile" && \
        invoke_python_function "steam-stats" "Fetching Steam gaming stats" && \
        invoke_python_function "youtube" "Generating YouTube profile" && \
        invoke_python_function "chess-com" "Generating Chess.com profile"

        log "[INFO] Skipping Git operations"

        # Post-push steps
        write_step_header "Post-Push Steps" 3
        invoke_python_function "sync-local" "Syncing outputs to local cloud client" && \
        invoke_python_function "sync-cloud" "Syncing all shared files to Google Docs"
        ;;
    "chess-com"|"clear-temp"|"codeforces"|"generate-and-sync-profiles"|"git-commit"|"leetcode"|"markdown-lint"|"perplexity"|"steam-stats"|"sync-cloud"|"sync-gdoc-chesscom"|"sync-gdoc-codeforces"|"sync-gdoc-leetcode"|"sync-gdoc-steam"|"sync-gdoc-youtube"|"sync-local"|"youtube")
        invoke_python_function "$ACTION" "Running $ACTION"
        ;;
    *)
        write_error "Unknown action: $ACTION"
        show_help
        exit 1
        ;;
esac

if [ $? -eq 0 ]; then
    write_success "Workflow '$ACTION' completed successfully."
    exit 0
else
    write_error "Workflow '$ACTION' failed."
    exit 1
fi
