param(
    [ValidateSet("full", "full-without-git",
                 "chess-com", "clear-temp", 
                 "codeforces", "generate-and-sync-profiles", "help", "leetcode", "git-commit",
                 "markdown-lint", "perplexity", "steam-stats", "sync-cloud", 
                 "sync-gdoc-chesscom", "sync-gdoc-codeforces", "sync-gdoc-leetcode", 
                 "sync-gdoc-steam", "sync-gdoc-youtube", 
                 "sync-local", "youtube")]
    [string]$Action = "full-without-git",
    [string]$CommitMessage = "",
    [string]$DocId = ""
)

# Set the working directory to the project root to ensure the script runs correctly from any location
if ($PSScriptRoot) {
    $ScriptDir = $PSScriptRoot
} else {
    $ScriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
}
$ProjectRoot = Split-Path -Path $ScriptDir -Parent
Set-Location -Path $ProjectRoot

$LogFile = "Temp/Logs.txt"
if (Test-Path $LogFile) {
    Clear-Content -Path $LogFile
}

"============================================================
Workflow started at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
============================================================" | Out-File -FilePath $LogFile -Append

$ErrorActionPreference = "Stop"
$PythonScript = "scripts/main.py"

function Get-ConfigValue {
    param([string]$Key)
    $Config = Get-Content "config.yaml" -Raw | ConvertFrom-Yaml
    return $Config[$Key]
}

$CommitMessageFile = Join-Path -Path (Get-ConfigValue "paths")["temp"] -ChildPath (Get-ConfigValue "paths")["commit_message_file"]

function Write-StepHeader {
    param([string]$Title, [int]$StepNumber = 0)
    $separator = "=" * 60
    "" | Out-File -FilePath $LogFile -Append
    $separator | Out-File -FilePath $LogFile -Append
    if ($StepNumber -gt 0) {
        " STEP $StepNumber`: $Title" | Out-File -FilePath $LogFile -Append
    } else {
        " $Title" | Out-File -FilePath $LogFile -Append
    }
    $separator | Out-File -FilePath $LogFile -Append
    "" | Out-File -FilePath $LogFile -Append
}

function Write-Success {
    param([string]$Message)
    "[SUCCESS] $Message" | Out-File -FilePath $LogFile -Append
}

function Write-Warning {
    param([string]$Message)
    "[WARNING] $Message" | Out-File -FilePath $LogFile -Append
}

function Write-Error {
    param([string]$Message)
    "[ERROR] $Message" | Out-File -FilePath $LogFile -Append
}

function Get-CommitMessage {
    param([string]$FilePath)
    
    if (-not (Test-Path $FilePath)) {
        Write-Warning "Commit message file not found. Creating it with default template."
        $defaultContent = "# Enter your commit message on the line below`n# Lines starting with # are treated as comments and will be ignored`n# The first non-comment line will be used as the commit message`n# Multi-line messages are supported`n"
        Set-Content -Path $FilePath -Value $defaultContent
    }
    
    $content = Get-Content $FilePath -Raw
    if (-not $content) {
        throw "Commit message file is empty: $FilePath"
    }
    
    $lines = $content -split "`r?`n"
    $commitLines = @()
    
    foreach ($line in $lines) {
        $trimmed = $line.Trim()
        if ($trimmed -eq "" -or $trimmed.StartsWith("#")) {
            continue
        }
        $commitLines += $trimmed
    }
    
    if ($commitLines.Count -eq 0) {
        throw "No valid commit message found in $FilePath"
    }
    
    return $commitLines -join "`n"
}

function Invoke-PythonFunction {
    param(
        [string]$FunctionName, 
        [string]$Description,
        [string]$DocId = ""
    )
    
    "[SETUP] Ensuring Python dependencies are installed..." | Out-File -FilePath $LogFile -Append
    pip install -r scripts/requirements.txt --quiet
    
    "[PYTHON] $Description..." | Out-File -FilePath $LogFile -Append
    try {
        $env:THEAUTOMATON_POWERSHELL_CALLER = '1'
        
        $pythonArgs = @($PythonScript, $FunctionName)
        if ($DocId) {
            $pythonArgs += "--doc_id", $DocId
        }
        
        python.exe $pythonArgs *>&1 | Out-File -FilePath $LogFile -Append

        if ($LASTEXITCODE -ne 0) {
            throw "Python script failed with exit code $LASTEXITCODE"
        }
        Remove-Item Env:THEAUTOMATON_POWERSHELL_CALLER -ErrorAction SilentlyContinue
        
        Write-Success "$Description completed. See Temp/Logs.txt for details."
        return $true
    }
    catch {
        Write-Error "$Description failed with a PowerShell exception: $($_.Exception.Message)"
        return $false
    }
}



function Invoke-GitOperations {
    param([string]$Message)
    
    Write-StepHeader "Git Operations" 2
    
    try {
        "[GIT] Adding all changes to Git..." | Out-File -FilePath $LogFile -Append
        git add . *>&1 | Out-File -FilePath $LogFile -Append
        if ($LASTEXITCODE -ne 0) {
            throw "Git add failed"
        }
        
        "[GIT] Committing with message: $Message" | Out-File -FilePath $LogFile -Append
        git commit -m "$Message" *>&1 | Out-File -FilePath $LogFile -Append
        if ($LASTEXITCODE -ne 0) {
            throw "Git commit failed"
        }
        
        "[GIT] Pushing to remote repository..." | Out-File -FilePath $LogFile -Append
        git push *>&1 | Out-File -FilePath $LogFile -Append
        if ($LASTEXITCODE -ne 0) {
            throw "Git push failed"
        }
        
        Write-Success "Git operations completed successfully"
        return $true
    }
    catch {
        Write-Error "Git operations failed: $_"
        return $false
    }
}

function Show-Help {
    "The-Automaton Repository Workflow Script" | Out-File -FilePath $LogFile -Append
    "========================================" | Out-File -FilePath $LogFile -Append
    "" | Out-File -FilePath $LogFile -Append
    "USAGE: .\scripts\workflow.ps1 [Action] [Options]" | Out-File -FilePath $LogFile -Append
    "" | Out-File -FilePath $LogFile -Append
    "ACTIONS:" | Out-File -FilePath $LogFile -Append
    "  full                          Run complete workflow (default)" | Out-File -FilePath $LogFile -Append
    "  full-without-git              Run complete workflow without Git operations" | Out-File -FilePath $LogFile -Append
    "  chess-com                     Generate Chess.com profile" | Out-File -FilePath $LogFile -Append
    "  clear-temp                    Clear Temp directory" | Out-File -FilePath $LogFile -Append
    "  codeforces                    Generate Codeforces profile" | Out-File -FilePath $LogFile -Append
    "  generate-and-sync-profiles    Generate all profiles and sync to Google Docs" | Out-File -FilePath $LogFile -Append
    "  git-commit                    Commit and push changes" | Out-File -FilePath $LogFile -Append
    "  help                          Show this help" | Out-File -FilePath $LogFile -Append
    "  leetcode                      Generate LeetCode profile" | Out-File -FilePath $LogFile -Append
    "  markdown-lint                 Validate markdown files only" | Out-File -FilePath $LogFile -Append
    "  perplexity                    Run Perplexity query" | Out-File -FilePath $LogFile -Append
    "  steam-stats                   Fetch Steam gaming stats" | Out-File -FilePath $LogFile -Append
    "  sync-books                    Sync local book PDFs to Google Drive" | Out-File -FilePath $LogFile -Append
    "  sync-cloud                    Sync all shared files to Google Docs" | Out-File -FilePath $LogFile -Append
    "  sync-gdoc-chesscom            Sync Chess.com profile to Google Docs" | Out-File -FilePath $LogFile -Append
    "  sync-gdoc-codeforces          Sync Codeforces profile to Google Docs" | Out-File -FilePath $LogFile -Append
    "  sync-gdoc-leetcode            Sync LeetCode profile to Google Docs" | Out-File -FilePath $LogFile -Append
    "  sync-gdoc-steam               Sync Steam stats to Google Docs" | Out-File -FilePath $LogFile -Append
    "  sync-gdoc-youtube             Sync YouTube stats to Google Docs" | Out-File -FilePath $LogFile -Append
    "  sync-local                    Sync files to local cloud client (e.g., OneDrive)" | Out-File -FilePath $LogFile -Append
    "  youtube                       Generate YouTube profile" | Out-File -FilePath $LogFile -Append
    "" | Out-File -FilePath $LogFile -Append
    "OPTIONS:" | Out-File -FilePath $LogFile -Append
    "  -CommitMessage  Specify commit message" | Out-File -FilePath $LogFile -Append
    "  -DocId          Specify Google Doc ID for a specific sync-gdoc action" | Out-File -FilePath $LogFile -Append
}

$success = $false
try {
    if ($Action -eq "help") {
        Show-Help
        exit 0
    }
    
    Write-StepHeader "The-Automaton Repository Workflow"
    "Action: $Action" | Out-File -FilePath $LogFile -Append
    
    switch ($Action) {
        "chess-com" {
            Invoke-PythonFunction "chess-com" "Generating Chess.com profile"
        }

        "clear-temp" {
            Invoke-PythonFunction "clear-temp" "Clearing Temp directory"
        }

        "codeforces" {
            Invoke-PythonFunction "codeforces" "Generating Codeforces profile"
        }

        "generate-and-sync-profiles" {
            Invoke-PythonFunction "generate-and-sync-profiles" "Generating and syncing all profiles"
        }

        "help" {
            Show-Help
        }

        "git-commit" {
            Invoke-PythonFunction "git-commit" "Committing and pushing changes"
        }

        "leetcode" {
            Invoke-PythonFunction "leetcode" "Generating LeetCode profile"
        }

        "markdown-lint" {
            Invoke-PythonFunction "markdown-lint" "Running markdown-lint validation"
        }

        "perplexity" {
            Invoke-PythonFunction "perplexity" "Running Perplexity query"
        }

        "steam-stats" {
            Invoke-PythonFunction "steam-stats" "Fetching Steam gaming stats"
        }

        "sync-books" {
            Invoke-PythonFunction "sync-books" "Syncing local book PDFs to Google Drive"
        }

        "sync-cloud" {
            Invoke-PythonFunction "sync-cloud" "Syncing with cloud storage"
        }

        "sync-gdoc-chesscom" {
            Invoke-PythonFunction "sync-gdoc-chesscom" "Syncing Chess.com profile to Google Docs"
        }

        "sync-gdoc-codeforces" {
            Invoke-PythonFunction "sync-gdoc-codeforces" "Syncing Codeforces profile to Google Docs"
        }

        "sync-gdoc-leetcode" {
            Invoke-PythonFunction "sync-gdoc-leetcode" "Syncing LeetCode profile to Google Docs"
        }

        "sync-gdoc-steam" {
            Invoke-PythonFunction "sync-gdoc-steam" "Syncing Steam stats to Google Docs"
        }

        "sync-gdoc-youtube" {
            Invoke-PythonFunction "sync-gdoc-youtube" "Syncing YouTube stats to Google Docs"
        }

        "sync-local" {
            Invoke-PythonFunction "sync-local" "Syncing files to local cloud client"
        }

        "youtube" {
            Invoke-PythonFunction "youtube" "Generating YouTube profile"
        }

        "full-without-git" {
            # Pre-commit steps
            Write-StepHeader "Pre-Commit Steps" 1
            Invoke-PythonFunction "markdown-lint" "Linting Markdown files"
            Invoke-PythonFunction "codeforces" "Generating Codeforces profile"
            Invoke-PythonFunction "leetcode" "Generating LeetCode profile"
            Invoke-PythonFunction "steam-stats" "Fetching Steam gaming stats"
            Invoke-PythonFunction "youtube" "Generating YouTube profile"
            Invoke-PythonFunction "chess-com" "Generating Chess.com profile"
            
            "[INFO] Skipping Git operations" | Out-File -FilePath $LogFile -Append
            
            # Post-push steps
            Write-StepHeader "Post-Push Steps" 3
            Invoke-PythonFunction "sync-local" "Syncing outputs to local cloud client"
            Invoke-PythonFunction "sync-cloud" "Syncing all shared files to Google Docs"
            Invoke-PythonFunction "sync-books" "Syncing books to Google Drive"
        }

        "full" {
            $Message = ""
            if ($CommitMessage -ne "") {
                $Message = $CommitMessage
            } else {
                "[INFO] Reading commit message from $CommitMessageFile..." | Out-File -FilePath $LogFile -Append
                $Message = Get-CommitMessage -FilePath $CommitMessageFile
            }
            "[INFO] Commit message: $Message" | Out-File -FilePath $LogFile -Append
            
            # Pre-commit steps
            Write-StepHeader "Pre-Commit Steps" 1
            Invoke-PythonFunction "markdown-lint" "Linting Markdown files"
            Invoke-PythonFunction "codeforces" "Generating Codeforces profile"
            Invoke-PythonFunction "leetcode" "Generating LeetCode profile"
            Invoke-PythonFunction "steam-stats" "Fetching Steam gaming stats"
            Invoke-PythonFunction "youtube" "Generating YouTube profile"
            Invoke-PythonFunction "chess-com" "Generating Chess.com profile"
            
            # Git operations
            Invoke-GitOperations -Message $Message
            
            # Post-push steps
            Write-StepHeader "Post-Push Steps" 3
            Invoke-PythonFunction "sync-local" "Syncing outputs to local cloud client"
            Invoke-PythonFunction "sync-cloud" "Syncing all shared files to Google Docs"
            Invoke-PythonFunction "sync-books" "Syncing books to Google Drive"
        }
        
        default {
            Write-Error "Unknown action: $Action"
            Show-Help
            exit 1
        }
    }
    $success = $true
} catch {
    Write-Error "An error occurred: $_"
    "For help, run: .\scripts\workflow.ps1 help" | Out-File -FilePath $LogFile -Append
    $success = $false
}
finally {
    # No Stop-Transcript needed
}

if (-not $success) {
    exit 1
}
