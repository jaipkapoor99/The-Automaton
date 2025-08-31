# -*- coding: utf-8 -*-
"""
Handles validation tasks for The-Mind repository, such as checking file 
references and linting Markdown files.
"""
import subprocess
from pathlib import Path
from scripts.config import ROOT_DIR, print_section_header

class Validator:
    """A class to handle validation tasks."""

    def __init__(self, root_dir=ROOT_DIR):
        """Initializes the Validator."""
        self.root_dir = Path(root_dir)

    def lint_markdown_files(self):
        """
        Lints and fixes all Markdown files, reporting the number of fixes and remaining issues.
        """
        print_section_header("Markdown Linting")
        try:
            md_files = [str(p) for p in self.root_dir.rglob('*.md') if ".git" not in str(p) and "node_modules" not in str(p)]

            if not md_files:
                print("No Markdown files found to lint.")
                return True
                
            print(f"Found {len(md_files)} Markdown files to lint and fix.")
            
            # Initial scan to count issues
            scan_command = ['pymarkdown', 'scan'] + md_files
            scan_result = subprocess.run(scan_command, capture_output=True, text=True, check=False)
            
            initial_issues = scan_result.stdout.strip()
            initial_issue_count = len(initial_issues.splitlines()) if initial_issues else 0

            if scan_result.returncode != 0 and "command not found" in scan_result.stderr.lower():
                 print("[ERROR] 'pymarkdown' command not found.")
                 print("Please ensure it is installed and in your PATH: pip install pymarkdown-linter")
                 return False

            if initial_issue_count > 0:
                print(f"[INFO] Found {initial_issue_count} initial markdown issues.")
                print("----- Initial Issues -----")
                print(initial_issues)
                print("--------------------------")

            # Attempt to fix the issues
            print("\n[INFO] Attempting to automatically fix issues...")
            fix_command = ['pymarkdown', 'fix'] + md_files
            fix_result = subprocess.run(fix_command, capture_output=True, text=True, check=False)
            
            if fix_result.returncode != 0:
                print("[WARNING] The 'pymarkdown fix' command encountered an error.")
                print(fix_result.stderr)

            # Rescan to see what issues remain
            print("\n[INFO] Re-scanning files after fix attempt...")
            rescan_result = subprocess.run(scan_command, capture_output=True, text=True, check=False)
            
            remaining_issues = rescan_result.stdout.strip()
            remaining_issue_count = len(remaining_issues.splitlines()) if remaining_issues else 0
            fixed_count = initial_issue_count - remaining_issue_count
            
            if fixed_count > 0:
                print(f"[SUCCESS] Automatically fixed {fixed_count} markdown issue(s).")
            
            if remaining_issue_count > 0:
                print(f"\n[WARNING] {remaining_issue_count} markdown issues remain:")
                print("----- Remaining Issues -----")
                print(remaining_issues)
                print("----------------------------")
                return False
            else:
                print("\n[SUCCESS] All Markdown files are valid.")
                return True
                
        except FileNotFoundError:
            print("[ERROR] 'pymarkdown' command not found.")
            print("Please ensure it is installed and in your PATH: pip install pymarkdown-linter")
            return False
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred during Markdown linting: {e}")
            return False
