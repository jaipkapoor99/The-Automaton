# -*- coding: utf-8 -*-
"""
Handles Google API Authentication using OAuth 2.0.
"""
import os
import socket
from typing import Optional

from config import (GOOGLE_AUTH_PROVIDER_X509_CERT_URL, GOOGLE_AUTH_URI,
                    GOOGLE_AUTH_URL_FILE, GOOGLE_CLIENT_ID,
                    GOOGLE_CLIENT_SECRET, GOOGLE_PROJECT_ID,
                    GOOGLE_REDIRECT_URIS, GOOGLE_SERVICE_ACCOUNT_KEY_PATH,
                    GOOGLE_SHEETS_TIMEOUT, GOOGLE_TOKEN_URI, SCOPES, TEMP_DIR,
                    TOKEN_FILE)

try:
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import Resource, build

    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False


class GoogleAuthenticator:
    """A class to handle Google API authentication."""

    def __init__(self):
        if not GOOGLE_LIBS_AVAILABLE:
            raise ImportError("Google client libraries not installed.")
        self.creds = None

    def _authenticate_service_account(self):
        """Authenticates using a service account and returns credentials."""
        if GOOGLE_SERVICE_ACCOUNT_KEY_PATH and os.path.exists(
            GOOGLE_SERVICE_ACCOUNT_KEY_PATH
        ):
            try:
                creds = service_account.Credentials.from_service_account_file(
                    GOOGLE_SERVICE_ACCOUNT_KEY_PATH, scopes=SCOPES
                )
                print("Authenticated using Service Account.")
                return creds
            except (ValueError, IOError) as e:
                print(f"Service Account authentication failed: {e}")
        return None

    def _authenticate_user_oauth(self):
        """Authenticates using user-based OAuth 2.0 and returns credentials."""
        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except (ValueError, IOError) as e:
                    print(f"Token refresh failed: {e}")
                    creds = None

            if not creds:
                if os.environ.get("CI"):
                    print(
                        "CRITICAL ERROR: Running in CI environment. "
                        "Invalid or missing token.json and interactive auth is not possible."
                    )
                    return None

                if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_PROJECT_ID]):
                    print(
                        "CRITICAL ERROR: Google OAuth environment variables (GOOGLE_CLIENT_ID, "
                        "GOOGLE_CLIENT_SECRET, GOOGLE_PROJECT_ID) are not set. "
                        "Cannot perform user OAuth."
                    )
                    return None

                client_config = {
                    "installed": {
                        "client_id": GOOGLE_CLIENT_ID,
                        "project_id": GOOGLE_PROJECT_ID,
                        "auth_uri": GOOGLE_AUTH_URI,
                        "token_uri": GOOGLE_TOKEN_URI,
                        "auth_provider_x509_cert_url": GOOGLE_AUTH_PROVIDER_X509_CERT_URL,
                        "client_secret": GOOGLE_CLIENT_SECRET,
                        "redirect_uris": [GOOGLE_REDIRECT_URIS],
                    }
                }

                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)

                os.makedirs(TEMP_DIR, exist_ok=True)  # Ensure TEMP_DIR exists
                auth_url, _ = flow.authorization_url(prompt="consent")
                with open(GOOGLE_AUTH_URL_FILE, "w", encoding="utf-8") as f:
                    f.write(auth_url)

                flow.run_local_server(port=0)
                creds = flow.credentials

            with open(TOKEN_FILE, "w", encoding="utf-8") as token:
                token.write(creds.to_json())
        return creds

    def get_service(self, service_name: str, version: str) -> Optional[Resource]:
        """Builds and returns an authorized API service object using service account credentials."""
        if not self.creds:
            self.creds = self._authenticate_service_account()

        if not self.creds:
            print("Service account authentication failed. Cannot create service.")
            return None

        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(GOOGLE_SHEETS_TIMEOUT)
        try:
            service = build(
                service_name, version, credentials=self.creds, cache_discovery=False
            )
            return service
        except (ValueError, IOError) as e:
            print(
                f"Failed to create service {service_name} v{version} with service account: {e}"
            )
            return None
        finally:
            socket.setdefaulttimeout(original_timeout)

    def get_user_service(self, service_name: str, version: str) -> Optional[Resource]:
        """Builds and returns an authorized API service object using user-based OAuth credentials."""
        user_creds = self._authenticate_user_oauth()
        if not user_creds:
            print("User OAuth authentication failed. Cannot create service.")
            return None

        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(GOOGLE_SHEETS_TIMEOUT)
        try:
            service = build(
                service_name, version, credentials=user_creds, cache_discovery=False
            )
            return service
        except (ValueError, IOError) as e:
            print(
                f"Failed to create service {service_name} v{version} with user OAuth: {e}"
            )
            return None
        finally:
            socket.setdefaulttimeout(original_timeout)
