# -*- coding: utf-8 -*-
"""
Configuration for The-Mind Repository Automation Scripts
"""
import os

import yaml
from dotenv import load_dotenv

# --- Foundational Paths ---
# Establish the root directory first, as other paths depend on it.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Load Environment Variables ---
# This will load the .env file in the root directory
load_dotenv(dotenv_path=os.path.join(ROOT_DIR, ".env"))

# --- Load YAML Configuration ---
# Load the static configuration from the YAML file.
CONFIG_YAML_PATH = os.path.join(ROOT_DIR, "config.yaml")
with open(CONFIG_YAML_PATH, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

# --- User IDs ---
EMAIL_ID = os.environ.get("EMAIL_ID")
CF_HANDLE = os.environ.get("CODEFORCES_ID")
LEETCODE_USERNAME = os.environ.get("LEETCODE_ID")
CHESSCOM_ID = os.environ.get("CHESSCOM_ID")
STEAM_ID = os.environ.get("STEAM_ID")
GITHUB_ID = os.environ.get("GITHUB_ID")

# --- General Paths (constructed from YAML) ---
TEMP_DIR = os.path.join(ROOT_DIR, cfg["paths"]["temp"])

# --- Codeforces ---
CF_API_KEY = os.environ.get("CODEFORCES_API_KEY")
CF_API_SECRET = os.environ.get("CODEFORCES_API_SECRET")


# --- LeetCode ---

LEETCODE_API_ENDPOINT = cfg["api_endpoints"]["leetcode"]
CODEFORCES_API_ENDPOINT = cfg["api_endpoints"]["codeforces"]

# --- Chess.com ---
CHESSCOM_API_ENDPOINT = cfg["api_endpoints"]["chesscom"]


# --- Steam ---
STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
STEAM_API_ENDPOINT = cfg["api_endpoints"]["steam"]


# --- Cloud Sync ---
SCOPES = cfg["cloud"]["google_scopes"]
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")

# --- Google Sheets ---
GOOGLE_SHEETS_CONFIG = cfg.get("google_sheets", {})
GOOGLE_SHEETS_TIMEOUT = GOOGLE_SHEETS_CONFIG.get("timeout", 60)
GOOGLE_SHEETS_FOLDER_ID = GOOGLE_SHEETS_CONFIG.get("folder_id")

# --- Google Service Account ---
GOOGLE_SERVICE_ACCOUNT_KEY_PATH = os.path.join(
    ROOT_DIR, "Temp", "service_account_key.json"
)


# --- GitHub ---
CODING_DIR = os.path.dirname(ROOT_DIR)


# --- File Operations ---


def print_section_header(title: str):
    """Prints a formatted section header.

    Args:
        title (str): The title to be printed in the header.
    """
    try:
        print("\n" + "=" * 20)
        print(f" {title.upper()} ")
        print("=" * 20)
    except UnicodeEncodeError:
        # Fallback for Windows console encoding issues
        print("\n" + "=" * 20)
        print(f" {title.upper()} ")
        print("=" * 20)
