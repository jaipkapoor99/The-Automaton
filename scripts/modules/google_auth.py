# -*- coding: utf-8 -*-
"""
Handles Google API Authentication using OAuth 2.0.
"""
import os
from scripts.config import (
    TOKEN_FILE, SCOPES,
    GOOGLE_PROJECT_ID, GOOGLE_AUTH_URI, GOOGLE_TOKEN_URI, GOOGLE_AUTH_PROVIDER_X509_CERT_URL,
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URIS
)

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False

class GoogleAuthenticator:
    """A class to handle Google API authentication."""

    def __init__(self):
        if not GOOGLE_LIBS_AVAILABLE:
            raise ImportError("Google client libraries not installed.")
        self.creds = self._authenticate()

    def _authenticate(self):
        """Authenticates the user for Google APIs and returns credentials."""
        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = None
            
            if not creds:
                if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_PROJECT_ID]):
                    print("CRITICAL ERROR: Google OAuth environment variables (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_PROJECT_ID) are not set.")
                    return None
                
                # Construct the client_config dictionary from environment variables
                client_config = {
                    "installed": {
                        "client_id": GOOGLE_CLIENT_ID,
                        "project_id": GOOGLE_PROJECT_ID,
                        "auth_uri": GOOGLE_AUTH_URI,
                        "token_uri": GOOGLE_TOKEN_URI,
                        "auth_provider_x509_cert_url": GOOGLE_AUTH_PROVIDER_X509_CERT_URL,
                        "client_secret": GOOGLE_CLIENT_SECRET,
                        "redirect_uris": [GOOGLE_REDIRECT_URIS]
                    }
                }
                
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
        return creds

    def get_service(self, service_name, version):
        """Builds and returns an authorized API service object."""
        if not self.creds:
            print("Authentication failed. Cannot create service.")
            return None
        try:
            service = build(service_name, version, credentials=self.creds)
            return service
        except Exception as e:
            print(f"Failed to create service {service_name} v{version}: {e}")
            return None
