# -*- coding: utf-8 -*-
"""
Handles cloud synchronization tasks for The-Automaton repository, including syncing
to local directories and Google Drive.
"""
import os
import shutil
from scripts.config import (
    SHARED_DIR, LOCAL_SYNC_DIR,
    CF_OUTPUT_FILE, GOOGLE_DOC_CODEFORCES_ID, LEETCODE_OUTPUT_FILE,
    GOOGLE_DOC_LEETCODE_ID, STEAM_OUTPUT_FILE, GOOGLE_DOC_STEAM_ID,
    YOUTUBE_OUTPUT_FILE, GOOGLE_DOC_YOUTUBE_ID,
    CHESSCOM_OUTPUT_FILE, GOOGLE_DOC_CHESSCOM_ID,
    print_section_header
)
from scripts.modules.google_auth import GoogleAuthenticator, GOOGLE_LIBS_AVAILABLE

if GOOGLE_LIBS_AVAILABLE:
    from googleapiclient.errors import HttpError

class CloudSyncer:
    """A class to handle cloud synchronization."""

    def __init__(self):
        try:
            self.authenticator = GoogleAuthenticator()
        except ImportError:
            self.authenticator = None

    def sync_cloud_outputs(self):
        """Syncs the Shared directory to a local directory and Google Drive."""
        print_section_header("Cloud Sync")
        
        print("Starting local sync...")
        local_sync_success = self._sync_shared_dir_to_local()
        print(f"Local sync completed with status: {local_sync_success}")
        
        gdoc_success = False
        if self.authenticator:
            print("Starting Google Docs sync...")
            gdoc_success = self.sync_shared_files_to_gdocs()
            print(f"Google Docs sync completed with status: {gdoc_success}")
        else:
            print("\nGoogle client libraries not installed. Skipping Google Drive sync.")
        
        final_success = local_sync_success and gdoc_success
        print(f"Overall cloud sync status: {final_success}")
        return final_success

    def _sync_shared_dir_to_local(self):
        """
        Copies the entire Shared directory to the configured local sync directory,
        creating it if it doesn't exist and overwriting existing files.
        """
        source_dir = SHARED_DIR
        dest_dir = LOCAL_SYNC_DIR
        
        if not os.path.exists(source_dir):
            print(f"WARNING: Source directory '{source_dir}' not found. Skipping local sync.")
            return True

        if not dest_dir:
            print("WARNING: Local sync directory is not configured. Skipping local sync.")
            return True

        try:
            dest_path = os.path.join(dest_dir, 'The-Automaton-Shared')
            os.makedirs(dest_path, exist_ok=True)
            
            for item in os.listdir(source_dir):
                source_item = os.path.join(source_dir, item)
                dest_item = os.path.join(dest_path, item)
                if os.path.isdir(source_item):
                    if os.path.exists(dest_item):
                        shutil.rmtree(dest_item)
                    shutil.copytree(source_item, dest_item)
                else:
                    shutil.copy2(source_item, dest_item)

            print(f"Successfully synced '{os.path.basename(source_dir)}' directory to: {dest_path}")
            return True
        except Exception as e:
            print(f"An error occurred while syncing the Shared directory: {e}")
            return False


    def _sync_any_file_to_gdoc(self, source_path, doc_id, doc_id_source_name="provided"):
        """
        Generic function to sync a file's content to a specific Google Doc.
        This function will completely overwrite the document's content.
        """
        if not self.authenticator:
            print("ERROR: Google Authenticator not available.")
            return False
        if not doc_id:
            print(f"CRITICAL ERROR: Google Doc ID from {doc_id_source_name} not found. Skipping sync.")
            return False
        if not os.path.exists(source_path):
            print(f"CRITICAL ERROR: Source file not found at {source_path}. Skipping sync.")
            return False

        try:
            docs_service = self.authenticator.get_service("docs", "v1")
            if not docs_service:
                return False
            
            with open(source_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            if not file_content:
                print(f"WARNING: Source file '{os.path.basename(source_path)}' is empty. Clearing Google Doc.")
            
            document = docs_service.documents().get(documentId=doc_id, fields="body(content)").execute()
            content = document.get('body', {}).get('content', [])
            
            requests = []
            # To clear the document, we delete content from the beginning (index 1)
            # to the end of the document's body. The end index is retrieved from the
            # last structural element. We subtract 1 because the final newline
            # character of a document cannot be deleted, and an API error would occur.
            if content:
                end_of_doc_index = content[-1].get('endIndex', 0)
                if end_of_doc_index > 2:  # An empty doc has an endIndex of 2. Only delete if there's content.
                    requests.append({
                        "deleteContentRange": {
                            "range": {
                                "startIndex": 1,
                                "endIndex": end_of_doc_index - 1
                            }
                        }
                    })

            # If there is new content from the source file, add an insert request.
            if file_content:
                requests.append({
                    "insertText": {
                        "location": {"index": 1},
                        "text": file_content
                    }
                })

            # If there are any requests (either to delete or insert), execute them.
            if requests:
                docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
            
            print(f"Successfully synced '{os.path.basename(source_path)}' to Google Doc.")
            return True
        except HttpError as err:
            print(f"A Google API error occurred: {err}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during Google Doc sync: {e}")
            return False

    def sync_codeforces_to_gdoc(self):
        """Syncs the Codeforces profile to its Google Doc."""
        print_section_header("Sync Codeforces Profile to Google Doc")
        return self._sync_any_file_to_gdoc(CF_OUTPUT_FILE, GOOGLE_DOC_CODEFORCES_ID, "GOOGLE_DOC_CODEFORCES_ID")

    def sync_leetcode_to_gdoc(self):
        """Syncs the LeetCode profile to its Google Doc."""
        print_section_header("Sync LeetCode Profile to Google Doc")
        return self._sync_any_file_to_gdoc(LEETCODE_OUTPUT_FILE, GOOGLE_DOC_LEETCODE_ID, "GOOGLE_DOC_LEETCODE_ID")

    def sync_steam_to_gdoc(self):
        """Syncs the Steam stats to its Google Doc."""
        print_section_header("Sync Steam Stats to Google Doc")
        return self._sync_any_file_to_gdoc(STEAM_OUTPUT_FILE, GOOGLE_DOC_STEAM_ID, "GOOGLE_DOC_STEAM_ID")

    def sync_youtube_to_gdoc(self):
        """Syncs the YouTube stats to its Google Doc."""
        print_section_header("Sync YouTube Stats to Google Doc")
        return self._sync_any_file_to_gdoc(YOUTUBE_OUTPUT_FILE, GOOGLE_DOC_YOUTUBE_ID, "GOOGLE_DOC_YOUTUBE_ID")

    def sync_chesscom_to_gdoc(self):
        """Syncs the Chess.com profile to its Google Doc."""
        print_section_header("Sync Chess.com Profile to Google Doc")
        return self._sync_any_file_to_gdoc(CHESSCOM_OUTPUT_FILE, GOOGLE_DOC_CHESSCOM_ID, "GOOGLE_DOC_CHESSCOM_ID")

    def sync_shared_files_to_gdocs(self):
        """Syncs all supported shared files to their respective Google Docs."""
        print_section_header("Sync All Shared Files to Google Docs")
        sync_functions = [
            self.sync_codeforces_to_gdoc,
            self.sync_leetcode_to_gdoc,
            self.sync_steam_to_gdoc,
            self.sync_youtube_to_gdoc,
            self.sync_chesscom_to_gdoc
        ]
        
        all_successful = True
        for func in sync_functions:
            try:
                if not func():
                    all_successful = False
                    print(f"Sync failed for: {func.__name__}")
            except Exception as e:
                all_successful = False
                print(f"An unexpected error occurred in {func.__name__}: {e}")
        
        return all_successful
