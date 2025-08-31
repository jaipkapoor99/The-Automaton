# -*- coding: utf-8 -*-
"""
Handles Git operations for The-Mind repository.
"""
import subprocess
from scripts.config import ROOT_DIR, COMMIT_MESSAGE_FILE
from scripts.modules.file_operations import FileManager


class GitManager:
    """A class to handle Git operations."""

    def __init__(self, root_dir=ROOT_DIR):
        self.root_dir = root_dir

    def get_commit_message(self, file_path=COMMIT_MESSAGE_FILE):
        """Reads the commit message from the specified file."""
        FileManager().ensure_file_exists(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if not line.strip().startswith('#') and line.strip()]
        
        if not lines:
            raise ValueError("No valid commit message found in commit_message.txt")
            
        return "\n".join(lines)

    def commit_and_push(self):
        """Adds, commits, and pushes changes to the remote repository."""
        print("Starting Git operations...")
        try:
            commit_message = self.get_commit_message()
            
            print("Adding all changes to Git...")
            subprocess.run(['git', 'add', '.'], check=True, cwd=self.root_dir)
            
            print(f"Committing with message:\n{commit_message}")
            subprocess.run(['git', 'commit', '-m', commit_message], check=True, cwd=self.root_dir)
            
            print("Pushing to remote repository...")
            subprocess.run(['git', 'push'], check=True, cwd=self.root_dir)
            
            print("SUCCESS: Git operations completed successfully.")
            return True
        except FileNotFoundError:
            print("ERROR: 'git' command not found. Please ensure Git is installed and in your PATH.")
            return False
        except subprocess.CalledProcessError as e:
            print(f"ERROR: A Git command failed with exit code {e.returncode}.")
            print(f"Stderr: {e.stderr}")
            return False
        except ValueError as e:
            print(f"ERROR: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during Git operations: {e}")
            return False
