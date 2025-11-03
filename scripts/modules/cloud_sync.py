# -*- coding: utf-8 -*-
"""
Handles cloud synchronization tasks for The-Automaton repository, including syncing
to local directories and Google Drive.
"""
import socket
import time
from typing import Any, List

from config import GOOGLE_SHEET_ID, print_section_header
from googleapiclient.errors import HttpError
from modules.google_auth import GoogleAuthenticator


class CloudSyncer:
    """A class to handle cloud synchronization."""

    def __init__(self):
        try:
            self.authenticator = GoogleAuthenticator()
        except ImportError:
            self.authenticator = None

    def _create_and_clear_sheet(self, sheets_service, sheet_id, sheet_name):
        """Creates a new sheet if it doesn't exist and clears its content."""
        spreadsheet_metadata = (
            sheets_service.spreadsheets()
            .get(spreadsheetId=sheet_id)
            .execute()  # pylint: disable=no-member
        )
        existing_sheets = {
            s["properties"]["title"]: s["properties"]["sheetId"]
            for s in spreadsheet_metadata.get("sheets", [])
        }
        if sheet_name not in existing_sheets:
            requests = [{"addSheet": {"properties": {"title": sheet_name}}}]
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id, body={"requests": requests}
            ).execute()
        clear_range = f"'{sheet_name}'!A:Z"
        sheets_service.spreadsheets().values().clear(
            spreadsheetId=sheet_id, range=clear_range, body={}
        ).execute()

    def _sync_any_content_to_gsheet(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        sheet_name,
        data,
        sheet_id,
        sheet_id_source_name="provided",
        max_retries=5,
        initial_delay=1,
    ):
        """
        Generic function to sync a dictionary of content to a specific Google Sheet.
        """
        if not self.authenticator:
            print("ERROR: Google Authenticator not available.")
            return False
        if not sheet_id:
            print(
                f"CRITICAL ERROR: Google Sheet ID from {sheet_id_source_name} not found. Skipping sync."
            )
            return False

        success = False
        for attempt in range(max_retries):
            try:
                sheets_service = self.authenticator.get_service("sheets", "v4")
                if not sheets_service:
                    break

                self._create_and_clear_sheet(sheets_service, sheet_id, sheet_name)

                if data:
                    body = {"values": data}
                    sheets_service.spreadsheets().values().update(  # pylint: disable=no-member
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
                success = True
                break
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
                    break
            except (IOError, OSError) as e:
                print(
                    f"An unexpected error occurred during Google Sheet sync after {attempt + 1} attempts: {e}"
                )
                break
        return success

    def sync_codeforces_to_gsheet(self, content_dict: List[List[Any]]):
        """Syncs the Codeforces profile to its Google Sheet."""
        print_section_header("Sync Codeforces Profile to Google Sheet")
        return self._sync_any_content_to_gsheet(
            "Codeforces", content_dict, GOOGLE_SHEET_ID, "GOOGLE_SHEET_ID"
        )

    def sync_leetcode_to_gsheet(self, content_dict: List[List[Any]]):
        """Syncs the LeetCode profile to its Google Sheet."""
        print_section_header("Sync LeetCode Profile to Google Sheet")
        return self._sync_any_content_to_gsheet(
            "LeetCode", content_dict, GOOGLE_SHEET_ID, "GOOGLE_SHEET_ID"
        )

    def sync_steam_to_gsheet(self, content_dict: List[List[Any]]):
        """Syncs the Steam stats to its Google Sheet."""
        print_section_header("Sync Steam Stats to Google Sheet")
        return self._sync_any_content_to_gsheet(
            "Steam", content_dict, GOOGLE_SHEET_ID, "GOOGLE_SHEET_ID"
        )

    def sync_chesscom_to_gsheet(self, content_dict: List[List[Any]]):
        """Syncs the Chess.com profile to its Google Sheet."""
        print_section_header("Sync Chess.com Profile to Google Sheet")
        return self._sync_any_content_to_gsheet(
            "Chess.com", content_dict, GOOGLE_SHEET_ID, "GOOGLE_SHEET_ID"
        )
