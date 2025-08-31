# -*- coding: utf-8 -*-
"""
Handles file operations for The-Mind repository, such as concatenation,
clearing files, and updating timestamps.
"""
import os
from scripts.config import ROOT_DIR, EXCLUDED_DIRS, EXCLUDED_FILES


class FileManager:
    """A class to handle file operations."""

    def __init__(self, root_dir=ROOT_DIR):
        self.root_dir = root_dir
        self.EXCLUDED_DIRS = EXCLUDED_DIRS
        self.EXCLUDED_FILES = EXCLUDED_FILES

    def ensure_file_exists(self, file_path):
        """
        Ensures that a file exists at the given path. If the directory for the file
        does not exist, it will be created. If the file does not exist, it will be
        created as an empty file.
        """
        if not file_path:
            return
        try:
            dir_name = os.path.dirname(file_path)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8'):
                    pass  # Create an empty file
        except Exception as e:
            print(f"Error ensuring file exists at {file_path}: {e}")

    def clear_temp_directory(self):
        """Clears the content of all files in the Temp directory, preserving .gitignore."""
        print("Clearing Temp directory...")
        try:
            temp_dir = os.path.join(self.root_dir, "Temp")
            if not os.path.exists(temp_dir):
                print(f"[ERROR] Temp directory not found at: {temp_dir}")
                return False

            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                if os.path.isfile(item_path) and item.lower() != ".gitignore":
                    try:
                        with open(item_path, 'w'):
                            # Opening in 'w' mode and closing truncates the file
                            pass
                        print(f"Cleared content of: {item}")
                    except Exception as e:
                        print(f"Failed to clear {item_path}. Reason: {e}")
            
            print("Successfully cleared Temp directory.")
            return True
        except Exception as e:
            print(f"An error occurred while clearing the Temp directory: {e}")
            return False