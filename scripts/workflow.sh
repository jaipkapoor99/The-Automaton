#!/bin/bash

# This script is a Bash translation of the original workflow.ps1 PowerShell script.

# Default values
ACTION="full-without-git"
COMMIT_MESSAGE=""
DOC_ID=""

# Parse command-line arguments. Supports flags like -CommitMessage "msg" and a positional action.
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -CommitMessage)
        COMMIT_MESSAGE="$2"
        shift 
        shift 
        ;;
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
LOG_FILE="Temp/Logs.txt"
mkdir -p "$(dirname "$LOG_FILE")"
# Clear log file for the new run
true > "$LOG_FILE"

echo "============================================================" >> "$LOG_FILE"
echo "Workflow started at: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "============================================================" >> "$LOG_FILE"

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
    {
        echo ""
        echo "$separator"
        if [[ -n "$step_number" && "$step_number" -gt 0 ]]; then
            echo " STEP $step_number: $title"
        else
            echo " $title"
        fi
        echo "$separator"
        echo ""
    } >> "$LOG_FILE"
}

write_success() {
    echo "[SUCCESS] $1" >> "$LOG_FILE"
}

write_warning() {
    echo "[WARNING] $1" >> "$LOG_FILE"
}

write_error() {
    echo "[ERROR] $1" >> "$LOG_FILE"
}

# --- Error Handling ---
# Trap for logging errors before exit. This will be triggered by `set -e`.
handle_error() {
    local exit_code=$?
    local line_no=$1
    # The BASH_COMMAND variable contains the command that was executed.
    write_error "An error occurred on line $line_no: command exited with status $exit_code."
    echo "For help, run: ./scripts/workflow.sh --help" >> "$LOG_FILE"
    exit "$exit_code"
}
trap 'handle_error $LINENO' ERR

# --- Core Functions ---

# Reads a commit message from the configured file, ignoring comments and empty lines.
get_commit_message() {
    local file_path="$1"
    
    if [[ ! -f "$file_path" ]]; then
        write_warning "Commit message file not found. Creating it with default template."
        # Using -e to interpret newline characters
        echo -e "# Enter your commit message on the line below\n# Lines starting with # are treated as comments and will be ignored\n# The first non-comment line will be used as the commit message\n# Multi-line messages are supported\n" > "$file_path"
    fi
    
    # Use grep to filter out comments and empty lines. `|| true` prevents exit on no match.
    local content
    content=$(grep -vE '^\s*#|^\s*$' "$file_path" || true)
    
    if [[ -z "$content" ]]; then
        # This will trigger the error trap
        >&2 echo "No valid commit message found in $file_path"
        return 1
    fi
    
    echo "$content"
}

# Invokes a function within the main Python script.
invoke_python_function() {
    local function_name="$1"
    local description="$2"
    local doc_id_param="$3"
    
    echo "[SETUP] Ensuring Python dependencies are installed..." >> "$LOG_FILE"
    pip install -r scripts/requirements.txt --quiet
    
    echo "[PYTHON] $description..." >> "$LOG_FILE"
    
    export THEAUTOMATON_BASH_CALLER=\'1\'
    
    local python_args=("$PYTHON_SCRIPT" "$function_name")
    if [[ -n "$doc_id_param" ]]; then
        python_args+=("--doc_id" "$doc_id_param")
    fi
    
    # Execute python script, appending stdout and stderr to the log file.
    # The `set -e` and the ERR trap will handle any non-zero exit code.
    python3 "${python_args[@]}" >> "$LOG_FILE" 2>&1
    
    unset THEAUTOMATON_BASH_CALLER
    
    write_success "$description completed. See Temp/Logs.txt for details."
}

# Handles Git operations: add, commit, and push.
invoke_git_operations() {
    local message="$1"
    
    write_step_header "Git Operations" 2
    
    echo "[GIT] Adding all changes to Git..." >> "$LOG_FILE"
    git add . >> "$LOG_FILE" 2>&1
    
    echo "[GIT] Committing with message: $message" >> "$LOG_FILE"
    git commit -m "$message" >> "$LOG_FILE" 2>&1
    
    echo "[GIT] Pushing to remote repository..." >> "$LOG_FILE"
    git push >> "$LOG_FILE" 2>&1
    
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
  clear-temp                    Clear Temp directory
  codeforces                    Generate Codeforces profile
  generate-and-sync-profiles    Generate all profiles and sync to Google Docs
  git-commit                    Commit and push changes
  help                          Show this help
  leetcode                      Generate LeetCode profile
  markdown-lint                 Validate markdown files only
  perplexity                    Run Perplexity query
  steam-stats                   Fetch Steam gaming stats
  sync-cloud                    Sync all shared files to Google Docs
  sync-gdoc-chesscom            Sync Chess.com profile to Google Docs
  sync-gdoc-codeforces          Sync Codeforces profile to Google Docs
  sync-gdoc-leetcode            Sync LeetCode profile to Google Docs
  sync-gdoc-steam               Sync Steam stats to Google Docs
  sync-gdoc-youtube             Sync YouTube stats to Google Docs
  sync-local                    Sync files to local cloud client (e.g., OneDrive)
  youtube                       Generate YouTube profile

OPTIONS:
  -CommitMessage <message>      Specify commit message for \'full\' action
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
TEMP_DIR=$(get_config_value "paths.temp")
COMMIT_MSG_FILENAME=$(get_config_value "paths.commit_message_file")
COMMIT_MESSAGE_FILE="$TEMP_DIR/$COMMIT_MSG_FILENAME"

write_step_header "The-Automaton Repository Workflow"
echo "Action: $ACTION" >> "$LOG_FILE"

# Main control flow based on the action
case "$ACTION" in
    chess-com)
        invoke_python_function "chess-com" "Generating Chess.com profile"
        ;;
    clear-temp)
        invoke_python_function "clear-temp" "Clearing Temp directory"
        ;;
    codeforces)
        invoke_python_function "codeforces" "Generating Codeforces profile"
        ;;
    generate-and-sync-profiles)
        invoke_python_function "generate-and-sync-profiles" "Generating and syncing all profiles"
        ;;
    git-commit)
        invoke_python_function "git-commit" "Committing and pushing changes"
        ;;
    leetcode)
        invoke_python_function "leetcode" "Generating LeetCode profile"
        ;;
    markdown-lint)
        invoke_python_function "markdown-lint" "Running markdown-lint validation"
        ;;
    perplexity)
        invoke_python_function "perplexity" "Running Perplexity query"
        ;;
    steam-stats)
        invoke_python_function "steam-stats" "Fetching Steam gaming stats"
        ;;
    sync-cloud)
        invoke_python_function "sync-cloud" "Syncing with cloud storage"
        ;;
    sync-gdoc-chesscom)
        invoke_python_function "sync-gdoc-chesscom" "Syncing Chess.com profile to Google Docs" "$DOC_ID"
        ;;
    sync-gdoc-codeforces)
        invoke_python_function "sync-gdoc-codeforces" "Syncing Codeforces profile to Google Docs" "$DOC_ID"
        ;;
    sync-gdoc-leetcode)
        invoke_python_function "sync-gdoc-leetcode" "Syncing LeetCode profile to Google Docs" "$DOC_ID"
        ;;
    sync-gdoc-steam)
        invoke_python_function "sync-gdoc-steam" "Syncing Steam stats to Google Docs" "$DOC_ID"
        ;;
    sync-gdoc-youtube)
        invoke_python_function "sync-gdoc-youtube" "Syncing YouTube stats to Google Docs" "$DOC_ID"
        ;;
    sync-local)
        invoke_python_function "sync-local" "Syncing files to local cloud client"
        ;;
    youtube)
        invoke_python_function "youtube" "Generating YouTube profile"
        ;;
    full-without-git)
        write_step_header "Pre-Commit Steps" 1
        invoke_python_function "markdown-lint" "Linting Markdown files"
        invoke_python_function "codeforces" "Generating Codeforces profile"
        invoke_python_function "leetcode" "Generating LeetCode profile"
        invoke_python_function "steam-stats" "Fetching Steam gaming stats"
        invoke_python_function "youtube" "Generating YouTube profile"
        invoke_python_function "chess-com" "Generating Chess.com profile"
        
        echo "[INFO] Skipping Git operations as per action." >> "$LOG_FILE"
        
        write_step_header "Post-Push Steps" 3
        invoke_python_function "sync-local" "Syncing outputs to local cloud client"
        invoke_python_function "sync-cloud" "Syncing all shared files to Google Docs"
        ;;
    full)
        MESSAGE=""
        if [[ -n "$COMMIT_MESSAGE" ]]; then
            MESSAGE="$COMMIT_MESSAGE"
        else
            echo "[INFO] Reading commit message from $COMMIT_MESSAGE_FILE..." >> "$LOG_FILE"
            # get_commit_message will cause the script to exit on failure
            MESSAGE=$(get_commit_message "$COMMIT_MESSAGE_FILE")
        fi
        echo "[INFO] Using commit message: $MESSAGE" >> "$LOG_FILE"
        
        write_step_header "Pre-Commit Steps" 1
        invoke_python_function "markdown-lint" "Linting Markdown files"
        invoke_python_function "codeforces" "Generating Codeforces profile"
        invoke_python_function "leetcode" "Generating LeetCode profile"
        invoke_python_function "steam-stats" "Fetching Steam gaming stats"
        invoke_python_function "youtube" "Generating YouTube profile"
        invoke_python_function "chess-com" "Generating Chess.com profile"
        
        invoke_git_operations "$MESSAGE"
        
        write_step_header "Post-Push Steps" 3
        invoke_python_function "sync-local" "Syncing outputs to local cloud client"
        invoke_python_function "sync-cloud" "Syncing all shared files to Google Docs"
        ;;
    *)
        # This will trigger the error trap
        >&2 echo "Unknown action: $ACTION"
        exit 1
        ;;
esac

# --- Final Success Message ---
{
    echo ""
    echo "============================================================"
    echo "Workflow finished successfully at: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "============================================================"
} >> "$LOG_FILE"

exit 0
