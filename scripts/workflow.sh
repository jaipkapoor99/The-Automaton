#!/bin/bash

# This script is a Bash translation of the original workflow.ps1 PowerShell script.

# Default values
ACTION="full-without-git"

DOC_ID=""

# Parse command-line arguments. Supports flags like -CommitMessage "msg" and a positional action.
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        
        -DocId)
        DOC_ID="$2"
        shift 
        shift 
        ;;
        -h|--help) 
        ACTION="help"
        shift
        ;;
        *)    # Any other argument is treated as the Action
        if [[ ! "$key" =~ ^- ]]; then
            ACTION="$key"
        fi
        shift
        ;;
    esac
done

# Set the working directory to the project root to ensure the script runs correctly from any location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# --- Logging Setup ---


# Exit immediately if a command exits with a non-zero status.
set -e

PYTHON_SCRIPT="scripts/main.py"

# --- Helper Functions ---

# Function to parse a value from the config.yaml file.
# Uses a Python one-liner for robust YAML parsing.
get_config_value() {
    local key_path="$1"
    # key_path is a dot-separated path like "paths.temp"
    local python_code="import yaml; f = open('config.yaml'); d = yaml.safe_load(f); keys = '$key_path'.split('.'); val = d; [val := val.get(k, {}) for k in keys]; print(val if isinstance(val, str) else '' )"
    python3 -c "$python_code"
}

# --- Logging Functions ---
write_step_header() {
    local title="$1"
    local step_number="$2"
    local separator="============================================================"
    echo ""
    echo "$separator"
    if [[ -n "$step_number" && "$step_number" -gt 0 ]]; then
        echo " STEP $step_number: $title"
    else
        echo " $title"
    fi
    echo "$separator"
    echo ""
}

write_success() {
    echo "[SUCCESS] $1"
}

write_warning() {
    echo "[WARNING] $1"
}

write_error() {
    >&2 echo "[ERROR] $1"
}

# --- Error Handling ---
# Trap for logging errors before exit. This will be triggered by `set -e`.
handle_error() {
    local exit_code=$?
    local line_no=$1
    # The BASH_COMMAND variable contains the command that was executed.
    write_error "An error occurred on line $line_no: command exited with status $exit_code."
    
    exit "$exit_code"
}
trap 'handle_error $LINENO' ERR

# --- Core Functions ---



# Invokes a function within the main Python script.
invoke_python_function() {
    local function_name="$1"
    local description="$2"
    local doc_id_param="$3"
    
    echo "[SETUP] Ensuring Python dependencies are installed..."
    pip install -r scripts/requirements.txt --quiet
    
    echo "[PYTHON] $description..."
    
    export THEAUTOMATON_BASH_CALLER=\'1\'
    
    local python_args=("$PYTHON_SCRIPT" "$function_name")
    if [[ -n "$doc_id_param" ]]; then
        python_args+=("--doc_id" "$doc_id_param")
    fi
    
    # Execute python script, appending stdout and stderr to the log file.
    # The `set -e` and the ERR trap will handle any non-zero exit code.
    python3 "${python_args[@]}"
    
    unset THEAUTOMATON_BASH_CALLER
    
    write_success "$description completed."
}

# Handles Git operations: add, commit, and push.
invoke_git_operations() {
    local message="$1"
    
    write_step_header "Git Operations" 2
    
    echo "[GIT] Adding all changes to Git..."
    git add .
    
    echo "[GIT] Committing with message: $message"
    git commit -m "$message"
    
    echo "[GIT] Pushing to remote repository..."
    git push
    
    write_success "Git operations completed successfully"
}

# Displays the help message.
show_help() {
    # Using a "here document" to print a block of text.
    cat << EOF
The-Automaton Repository Workflow Script
========================================

USAGE: ./scripts/workflow.sh [Action] [Options]

ACTIONS:
  full                          Run complete workflow
  full-without-git              Run workflow without Git operations (default)
  chess-com                     Generate Chess.com profile
  codeforces                    Generate Codeforces profile
  leetcode                      Generate LeetCode profile
  steam-stats                   Fetch Steam gaming stats
  youtube                       Generate YouTube profile
  
  codeforces-generate           Generate Codeforces profile
  codeforces-sync               Sync Codeforces profile to Google Docs
  leetcode-generate             Generate LeetCode profile
  leetcode-sync                 Sync LeetCode profile to Google Docs
  steam-generate                Generate Steam stats
  steam-sync                    Sync Steam stats to Google Docs
  youtube-generate              Generate YouTube profile
  youtube-sync                  Sync YouTube profile to Google Docs
  chesscom-generate             Generate Chess.com profile
  chesscom-sync                 Sync Chess.com profile to Google Docs
  
  help                          Show this help
  
OPTIONS:
  
  -DocId <id>                   Specify Google Doc ID for a sync-gdoc action
  -h, --help                    Show this help message
EOF
}

# --- Main Logic ---

# Handle 'help' action first, as it doesn\'t need logging.
if [[ "$ACTION" == "help" ]]; then
    show_help
    exit 0
fi

# Get paths from config


write_step_header "The-Automaton Repository Workflow"
echo "Action: $ACTION"

# Main control flow based on the action
case "$ACTION" in
    chess-com)
        invoke_python_function "chess-com" "Generating Chess.com profile and syncing to Google Docs"
        ;;
    codeforces)
        invoke_python_function "codeforces" "Generating Codeforces profile and syncing to Google Docs"
        ;;
    leetcode)
        invoke_python_function "leetcode" "Generating LeetCode profile and syncing to Google Docs"
        ;;
    steam-stats)
        invoke_python_function "steam-stats" "Generating Steam stats and syncing to Google Docs"
        ;;
    youtube)
        invoke_python_function "youtube" "Generating YouTube profile and syncing to Google Docs"
        ;;
    codeforces-generate)
        invoke_python_function "codeforces-generate" "Generating Codeforces profile"
        ;;
    codeforces-sync)
        invoke_python_function "codeforces-sync" "Syncing Codeforces profile to Google Docs"
        ;;
    leetcode-generate)
        invoke_python_function "leetcode-generate" "Generating LeetCode profile"
        ;;
    leetcode-sync)
        invoke_python_function "leetcode-sync" "Syncing LeetCode profile to Google Docs"
        ;;
    steam-generate)
        invoke_python_function "steam-generate" "Generating Steam stats"
        ;;
    steam-sync)
        invoke_python_function "steam-sync" "Syncing Steam stats to Google Docs"
        ;;
    youtube-generate)
        invoke_python_function "youtube-generate" "Generating YouTube profile"
        ;;
    youtube-sync)
        invoke_python_function "youtube-sync" "Syncing YouTube profile to Google Docs"
        ;;
    chesscom-generate)
        invoke_python_function "chesscom-generate" "Generating Chess.com profile"
        ;;
    chesscom-sync)
        invoke_python_function "chesscom-sync" "Syncing Chess.com profile to Google Docs"
        ;;
    full-without-git)
        write_step_header "Generating and Syncing All Profiles" 1
        invoke_python_function "codeforces" "Codeforces profile"
        invoke_python_function "leetcode" "LeetCode profile"
        invoke_python_function "steam-stats" "Steam stats"
        invoke_python_function "youtube" "YouTube profile"
        invoke_python_function "chess-com" "Chess.com profile"
        ;;
    full)
        write_step_header "Generating and Syncing All Profiles" 1
        invoke_python_function "codeforces" "Codeforces profile"
        invoke_python_function "leetcode" "LeetCode profile"
        invoke_python_function "steam-stats" "Steam stats"
        invoke_python_function "youtube" "YouTube profile"
        invoke_python_function "chess-com" "Chess.com profile"
        ;;
    *)
        # This will trigger the error trap
        >&2 echo "Unknown action: $ACTION"
        exit 1
        ;;
esac



exit 0
