# -*- coding: utf-8 -*-
"""
Handles cloud synchronization tasks for The-Automaton repository, including syncing
to local directories and Google Drive.
"""
import socket
import time

from scripts.config import (
    print_section_header,
)
from scripts.modules.google_auth import GOOGLE_LIBS_AVAILABLE, GoogleAuthenticator

if GOOGLE_LIBS_AVAILABLE:
    from googleapiclient.errors import HttpError


class CloudSyncer:
    """A class to handle cloud synchronization."""

    def __init__(self):
        try:
            self.authenticator = GoogleAuthenticator()
        except ImportError:
            self.authenticator = None

    def _sync_any_content_to_gsheet(
        self,
        content_dict,
        sheet_id,
        sheet_id_source_name="provided",
        max_retries=5,
        initial_delay=1,
    ):
        """
        Generic function to sync a dictionary of content (sheet_name -> list of lists) to a specific Google Sheet.
        This function will create new sheets (tabs) within the spreadsheet and overwrite their content.
        Includes retry logic with exponential backoff.
        """
        if not self.authenticator:
            print("ERROR: Google Authenticator not available.")
            return False
        if not sheet_id:
            print(
                f"CRITICAL ERROR: Google Sheet ID from {sheet_id_source_name} not found. Skipping sync."
            )
            return False

        for attempt in range(max_retries):
            try:
                sheets_service = self.authenticator.get_service("sheets", "v4")
                if not sheets_service:
                    return False

                # Get existing sheets to check if we need to create new ones
                spreadsheet_metadata = (
                    sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
                )
                existing_sheets = {
                    s["properties"]["title"]: s["properties"]["sheetId"]
                    for s in spreadsheet_metadata.get("sheets", [])
                }

                requests = []
                for sheet_name, data in content_dict.items():
                    if sheet_name not in existing_sheets:
                        # Add request to create new sheet
                        requests.append(
                            {"addSheet": {"properties": {"title": sheet_name}}}
                        )

                if requests:
                    sheets_service.spreadsheets().batchUpdate(
                        spreadsheetId=sheet_id, body={"requests": requests}
                    ).execute()
                    # Re-fetch metadata to get new sheet IDs
                    spreadsheet_metadata = (
                        sheets_service.spreadsheets()
                        .get(spreadsheetId=sheet_id)
                        .execute()
                    )
                    existing_sheets = {
                        s["properties"]["title"]: s["properties"]["sheetId"]
                        for s in spreadsheet_metadata.get("sheets", [])
                    }

                for sheet_name, data in content_dict.items():
                    # Clear existing content in the sheet
                    clear_range = f"'{sheet_name}'!A:Z"  # Clear a wide range
                    sheets_service.spreadsheets().values().clear(
                        spreadsheetId=sheet_id, range=clear_range, body={}
                    ).execute()

                    # Write new content
                    if data:
                        body = {"values": data}
                        sheets_service.spreadsheets().values().update(
                            spreadsheetId=sheet_id,
                            range=f"'{sheet_name}'!A1",
                            valueInputOption="RAW",
                            body=body,
                        ).execute()
                    else:
                        print(
                            f"WARNING: No content provided for sheet '{sheet_name}'. Sheet is now empty."
                        )

                print(f"Successfully synced content to Google Sheet ID: {sheet_id}.")
                return True
            except (HttpError, socket.timeout) as err:
                if (
                    isinstance(err, HttpError)
                    and err.resp.status in [403, 429, 500, 503]
                    and attempt < max_retries - 1
                ):
                    delay = initial_delay * (2**attempt)
                    print(
                        f"Google API error (status {err.resp.status}). Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)
                elif isinstance(err, socket.timeout) and attempt < max_retries - 1:
                    delay = initial_delay * (2**attempt)
                    print(f"A timeout occurred. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(
                        f"A Google API error occurred after {attempt + 1} attempts: {err}"
                    )
                    return False
            except Exception as e:
                print(
                    f"An unexpected error occurred during Google Sheet sync after {attempt + 1} attempts: {e}"
                )
                return False
        return False  # All retries failed

    def sync_all_profiles_to_gsheet(self, profiles_content_dict):
        """Syncs all supported shared files to their respective Google Sheets."""
        print_section_header("Sync All Shared Files to Google Sheets")

        # Import GOOGLE_SHEET_ID here to avoid circular import issues at the top level
        from scripts.config import GOOGLE_SHEET_ID

        all_successful = True
        if not self._sync_any_content_to_gsheet(
            profiles_content_dict, GOOGLE_SHEET_ID, "GOOGLE_SHEET_ID"
        ):
            all_successful = False

        return all_successful
