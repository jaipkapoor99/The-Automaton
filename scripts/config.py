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
load_dotenv(dotenv_path=os.path.join(ROOT_DIR, '.env'))

# --- Load YAML Configuration ---
# Load the static configuration from the YAML file.
CONFIG_YAML_PATH = os.path.join(ROOT_DIR, 'config.yaml')
with open(CONFIG_YAML_PATH, 'r') as f:
    cfg = yaml.safe_load(f)

# --- User IDs ---
EMAIL_ID = os.environ.get("EMAIL_ID")
CF_HANDLE = os.environ.get("CODEFORCES_ID")
LEETCODE_USERNAME = os.environ.get("LEETCODE_ID")
CHESSCOM_ID = os.environ.get("CHESSCOM_ID")
STEAM_ID = os.environ.get("STEAM_ID")
YOUTUBE_CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID")
GITHUB_ID = os.environ.get("GITHUB_ID")

# --- General Paths (constructed from YAML) ---
TEMP_DIR = os.path.join(ROOT_DIR, cfg['paths']['temp'])

# --- Codeforces ---
CF_API_KEY = os.environ.get("CODEFORCES_API_KEY")
CF_API_SECRET = os.environ.get("CODEFORCES_API_SECRET")


# --- LeetCode ---

LEETCODE_API_ENDPOINT = cfg['api_endpoints']['leetcode']
CODEFORCES_API_ENDPOINT = cfg['api_endpoints']['codeforces']

# --- Chess.com ---
CHESSCOM_API_ENDPOINT = cfg['api_endpoints']['chesscom']


# --- Steam ---
STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
STEAM_API_ENDPOINT = cfg['api_endpoints']['steam']


# --- YouTube ---


# --- Cloud Sync ---
SCOPES = cfg['cloud']['google_scopes']
TOKEN_FILE = os.path.join(ROOT_DIR, cfg['paths']['token_file'])
GOOGLE_DOC_ID = os.environ.get("GOOGLE_DOC_ID")
GOOGLE_DOC_CODEFORCES_ID = os.environ.get("GOOGLE_DOC_CODEFORCES_ID")
GOOGLE_DOC_LEETCODE_ID = os.environ.get("GOOGLE_DOC_LEETCODE_ID")
GOOGLE_DOC_STEAM_ID = os.environ.get("GOOGLE_DOC_STEAM_ID")
GOOGLE_DOC_YOUTUBE_ID = os.environ.get("GOOGLE_DOC_YOUTUBE_ID")
GOOGLE_DOC_CHESSCOM_ID = os.environ.get("GOOGLE_DOC_CHESSCOM_ID")

# --- Google OAuth (from .env) ---
GOOGLE_AUTH_URL_FILE = os.path.join(TEMP_DIR, cfg['auth']['url_file'])
GOOGLE_AUTH_CODE_FILE = os.path.join(TEMP_DIR, cfg['auth']['code_file'])
GOOGLE_PROJECT_ID = os.environ.get("GOOGLE_PROJECT_ID")
GOOGLE_AUTH_URI = os.environ.get("GOOGLE_AUTH_URI")
GOOGLE_TOKEN_URI = os.environ.get("GOOGLE_TOKEN_URI")
GOOGLE_AUTH_PROVIDER_X509_CERT_URL = os.environ.get("GOOGLE_AUTH_PROVIDER_X509_CERT_URL")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URIS = os.environ.get("GOOGLE_REDIRECT_URIS")



# --- GitHub ---
CODING_DIR = os.path.dirname(ROOT_DIR)



# --- File Operations ---


def print_section_header(title):
    """Prints a formatted section header."""
    try:
        print("\n" + "="*20)
        print(f" {title.upper()} ")
        print("="*20)
    except UnicodeEncodeError:
        # Fallback for Windows console encoding issues
        print("\n" + "="*20)
        print(f" {title.upper()} ")
        print("="*20)
