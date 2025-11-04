# -*- coding: utf-8 -*-
"""
Handles Google API Authentication using Service Account.
"""
from __future__ import annotations

import os
import socket
from typing import Callable, Optional, cast

from config import (GOOGLE_SERVICE_ACCOUNT_KEY_PATH, GOOGLE_SHEETS_TIMEOUT,
                    SCOPES)
from google.auth.credentials import Credentials as GoogleAuthCredentials
from google.oauth2 import service_account
from googleapiclient.discovery import Resource, build  # type: ignore[import-untyped]

BuildCallable = Callable[..., Resource]
build_service = cast(BuildCallable, build)


class GoogleAuthenticator:  # pylint: disable=too-few-public-methods
    """A class to handle Google API authentication."""

    def __init__(self):
        self.creds: Optional[GoogleAuthCredentials] = None

    def _authenticate_service_account(self) -> Optional[GoogleAuthCredentials]:
        """Authenticates using a service account and returns credentials."""
        if not GOOGLE_SERVICE_ACCOUNT_KEY_PATH:
            print("ERROR: GOOGLE_SERVICE_ACCOUNT_KEY_PATH is not set.")
            return None

        if not os.path.exists(GOOGLE_SERVICE_ACCOUNT_KEY_PATH):
            print(f"ERROR: Service account key file not found at {GOOGLE_SERVICE_ACCOUNT_KEY_PATH}")
            return None

        try:
            creds = service_account.Credentials.from_service_account_file(  # type: ignore[attr-defined]
                GOOGLE_SERVICE_ACCOUNT_KEY_PATH, scopes=SCOPES
            )
            print("Authenticated using Service Account.")
            return creds
        except (ValueError, OSError) as exc:
            print(f"Service Account authentication failed: {exc}")
            return None

    def get_service(self, service_name: str, version: str) -> Optional[Resource]:
        """Build and return a service object using service-account credentials."""
        if not self.creds:
            self.creds = self._authenticate_service_account()

        if not self.creds:
            print("Service account authentication failed. Cannot create service.")
            return None

        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(GOOGLE_SHEETS_TIMEOUT)
        try:
            service_obj = build_service(
                service_name,
                version,
                credentials=self.creds,
                cache_discovery=False,
            )
            return service_obj
        except (ValueError, OSError) as exc:
            print(
                f"Failed to create service {service_name} v{version} with service account: {exc}"
            )
            return None
        finally:
            socket.setdefaulttimeout(original_timeout)
