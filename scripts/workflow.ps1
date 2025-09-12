param(
    [ValidateSet("full", "full-without-git",
                  
                 
                 "markdown-lint", "perplexity", "steam-stats", "sync-cloud", 
                 "sync-gdoc-chesscom", "sync-gdoc-codeforces", "sync-gdoc-leetcode", 
                 "sync-gdoc-steam", "sync-gdoc-youtube", 
                 
    [string]$Action = "full-without-git",
    
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



$ErrorActionPreference = "Stop"
$PythonScript = "scripts/main.py"

function Get-ConfigValue {
    param([string]$Key)
    $Config = Get-Content "config.yaml" -Raw | ConvertFrom-Yaml
    return $Config[$Key]
}



function Write-StepHeader {
    param([string]$Title, [int]$StepNumber = 0)
    $separator = "=" * 60
    Write-Host ""
    Write-Host $separator
    if ($StepNumber -gt 0) {
        Write-Host " STEP $StepNumber`: $Title"
    } else {
        Write-Host " $Title"
    }
    Write-Host $separator
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message"
}

function Write-Warning {
    param([string]$Message)
    Write-Warning "[WARNING] $Message"
}

function Write-Error {
    param([string]$Message)
    Write-Error "[ERROR] $Message"
}



function Invoke-PythonFunction {
    param(
        [string]$FunctionName, 
        [string]$Description,
        [string]$DocId = ""
    )
    
    Write-Host "[SETUP] Ensuring Python dependencies are installed..."
    pip install -r scripts/requirements.txt --quiet
    
    Write-Host "[PYTHON] $Description..."
    try {
        $env:THEAUTOMATON_POWERSHELL_CALLER = '1'
        
        $pythonArgs = @($PythonScript, $FunctionName)
        if ($DocId) {
            $pythonArgs += "--doc_id", $DocId
        }
        
        python.exe $pythonArgs *>&1 | Write-Host

        if ($LASTEXITCODE -ne 0) {
            throw "Python script failed with exit code $LASTEXITCODE"
        }
        Remove-Item Env:THEAUTOMATON_POWERSHELL_CALLER -ErrorAction SilentlyContinue
        
        Write-Success "$Description completed."
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
        Write-Host "[GIT] Adding all changes to Git..."
        git add . *>&1 | Write-Host
        if ($LASTEXITCODE -ne 0) {
            throw "Git add failed"
        }
        
        Write-Host "[GIT] Committing with message: $Message"
        git commit -m "$Message" *>&1 | Write-Host
        if ($LASTEXITCODE -ne 0) {
            throw "Git commit failed"
        }
        
        Write-Host "[GIT] Pushing to remote repository..."
        git push *>&1 | Write-Host
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
    Write-Host "The-Automaton Repository Workflow Script"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "USAGE: .\scripts\workflow.ps1 [Action] [Options]"
    Write-Host ""
    Write-Host "ACTIONS:"
    Write-Host "  full                          Run complete workflow (default)"
    Write-Host "  full-without-git              Run complete workflow without Git operations"
    Write-Host "  chess-com                     Generate Chess.com profile"
    
    Write-Host "  codeforces                    Generate Codeforces profile"
    Write-Host "  generate-and-sync-profiles    Generate all profiles and sync to Google Docs"
    Write-Host "  git-commit                    Commit and push changes"
    Write-Host "  help                          Show this help"
    Write-Host "  leetcode                      Generate LeetCode profile"
    Write-Host "  markdown-lint                 Validate markdown files only"
    
    Write-Host "  steam-stats                   Fetch Steam gaming stats"
    Write-Host "  sync-cloud                    Sync all shared files to Google Docs"
    Write-Host "  sync-gdoc-chesscom            Sync Chess.com profile to Google Docs"
    Write-Host "  sync-gdoc-codeforces          Sync Codeforces profile to Google Docs"
    Write-Host "  sync-gdoc-leetcode            Sync LeetCode profile to Google Docs"
    Write-Host "  sync-gdoc-steam               Sync Steam stats to Google Docs"
    Write-Host "  sync-gdoc-youtube             Sync YouTube stats to Google Docs"
    
    Write-Host "  youtube                       Generate YouTube profile"
    Write-Host ""
    Write-Host "OPTIONS:"
    
    Write-Host "  -DocId          Specify Google Doc ID for a specific sync-gdoc action"
}

$success = $false
try {
    if ($Action -eq "help") {
        Show-Help
        exit 0
    }
    
    Write-StepHeader "The-Automaton Repository Workflow"
    Write-Host "Action: $Action"
    
    switch ($Action) {
        "chess-com" {
            Invoke-PythonFunction "chess-com" "Generating Chess.com profile"
        }

        

        "codeforces" {
            Invoke-PythonFunction "codeforces" "Generating Codeforces profile"
        }

        

        "leetcode" {
            Invoke-PythonFunction "leetcode" "Generating LeetCode profile"
        }

        "markdown-lint" {
            Invoke-PythonFunction "markdown-lint" "Running markdown-lint validation"
        }

        

        "steam-stats" {
            Invoke-PythonFunction "steam-stats" "Fetching Steam gaming stats"
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
            
            Write-Host "[INFO] Skipping Git operations"
            
            # Post-push steps
            Write-StepHeader "Post-Push Steps" 3
            Invoke-PythonFunction "sync-cloud" "Syncing all shared files to Google Docs"
        }

        "full" {
            # Pre-commit steps
            Write-StepHeader "Pre-Commit Steps" 1
            Invoke-PythonFunction "markdown-lint" "Linting Markdown files"
            Invoke-PythonFunction "codeforces" "Generating Codeforces profile"
            Invoke-PythonFunction "leetcode" "Generating LeetCode profile"
            Invoke-PythonFunction "steam-stats" "Fetching Steam gaming stats"
            Invoke-PythonFunction "youtube" "Generating YouTube profile"
            Invoke-PythonFunction "chess-com" "Generating Chess.com profile"
            
            # Post-push steps
            Write-StepHeader "Post-Push Steps" 3
            Invoke-PythonFunction "sync-cloud" "Syncing all shared files to Google Docs"
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
    
    $success = $false
}
finally {
    # No Stop-Transcript needed
}

if (-not $success) {
    exit 1
}