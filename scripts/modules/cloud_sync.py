# -*- coding: utf-8 -*-
"""
Handles cloud synchronization tasks for The-Automaton repository, including syncing
to local directories and Google Drive.
"""
import socket
import time

from scripts.config import (GOOGLE_SHEET_CHESSCOM_ID,
                            GOOGLE_SHEET_CODEFORCES_ID,
                            GOOGLE_SHEET_LEETCODE_ID, GOOGLE_SHEET_STEAM_ID,
                            GOOGLE_SHEET_YOUTUBE_ID, print_section_header)
from scripts.modules.google_auth import (GOOGLE_LIBS_AVAILABLE,
                                         GoogleAuthenticator)

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

    def sync_codeforces_to_gsheet(self, content_dict):
        """Syncs the Codeforces profile to its Google Sheet."""
        print_section_header("Sync Codeforces Profile to Google Sheet")
        return self._sync_any_content_to_gsheet(
            content_dict, GOOGLE_SHEET_CODEFORCES_ID, "GOOGLE_SHEET_CODEFORCES_ID"
        )

    def sync_leetcode_to_gsheet(self, content_dict):
        """Syncs the LeetCode profile to its Google Sheet."""
        print_section_header("Sync LeetCode Profile to Google Sheet")
        return self._sync_any_content_to_gsheet(
            content_dict, GOOGLE_SHEET_LEETCODE_ID, "GOOGLE_SHEET_LEETCODE_ID"
        )

    def sync_steam_to_gsheet(self, content_dict):
        """Syncs the Steam stats to its Google Sheet."""
        print_section_header("Sync Steam Stats to Google Sheet")
        return self._sync_any_content_to_gsheet(
            content_dict, GOOGLE_SHEET_STEAM_ID, "GOOGLE_SHEET_STEAM_ID"
        )

    def sync_youtube_to_gsheet(self, content_dict):
        """Syncs the YouTube stats to its Google Sheet."""
        print_section_header("Sync YouTube Stats to Google Sheet")
        return self._sync_any_content_to_gsheet(
            content_dict, GOOGLE_SHEET_YOUTUBE_ID, "GOOGLE_SHEET_YOUTUBE_ID"
        )

    def sync_chesscom_to_gsheet(self, content_dict):
        """Syncs the Chess.com profile to its Google Sheet."""
        print_section_header("Sync Chess.com Profile to Google Sheet")
        return self._sync_any_content_to_gsheet(
            content_dict, GOOGLE_SHEET_CHESSCOM_ID, "GOOGLE_SHEET_CHESSCOM_ID"
        )

    def sync_all_profiles_to_gsheets(self, profiles_content_dict):
        """Syncs all supported shared files to their respective Google Sheets."""
        print_section_header("Sync All Shared Files to Google Sheets")
        sync_map = {
            "codeforces": (self.sync_codeforces_to_gsheet, GOOGLE_SHEET_CODEFORCES_ID),
            "leetcode": (self.sync_leetcode_to_gsheet, GOOGLE_SHEET_LEETCODE_ID),
            "steam": (self.sync_steam_to_gsheet, GOOGLE_SHEET_STEAM_ID),
            "youtube": (self.sync_youtube_to_gsheet, GOOGLE_SHEET_YOUTUBE_ID),
            "chesscom": (self.sync_chesscom_to_gsheet, GOOGLE_SHEET_CHESSCOM_ID),
        }

        all_successful = True
        for profile_type, (sync_func, sheet_id) in sync_map.items():
            content_dict = profiles_content_dict.get(profile_type)
            if content_dict is None:
                print(
                    f"WARNING: No content provided for {profile_type}. Skipping sync."
                )
                continue

            try:
                if not sync_func(content_dict):
                    all_successful = False
                    print(f"Sync failed for: {profile_type}")
            except Exception as e:
                all_successful = False
                print(
                    f"An unexpected error occurred during sync for {profile_type}: {e}"
                )

        return all_successful

    def sync_all_profiles_to_gsheets_from_files(
        self, codeforces_file, leetcode_file, steam_file, youtube_file, chesscom_file
    ):
        """
        Reads content from files and then syncs all supported profiles to their respective Google Sheets.
        """
        profiles_content_dict = {}

        # For now, we'll read as strings and pass them. The profile_generator will convert to dict.
        with open(codeforces_file, "r", encoding="utf-8") as f:
            profiles_content_dict["codeforces"] = f.read()
        with open(leetcode_file, "r", encoding="utf-8") as f:
            profiles_content_dict["leetcode"] = f.read()
        with open(steam_file, "r", encoding="utf-8") as f:
            profiles_content_dict["steam"] = f.read()
        with open(youtube_file, "r", encoding="utf-8") as f:
            profiles_content_dict["youtube"] = f.read()
        with open(chesscom_file, "r", encoding="utf-8") as f:
            profiles_content_dict["chesscom"] = f.read()

        return self.sync_all_profiles_to_gsheets(profiles_content_dict)
