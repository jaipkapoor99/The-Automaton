# -*- coding: utf-8 -*-
"""
Handles cloud synchronization tasks for The-Automaton repository, including syncing
to local directories and Google Drive.
"""
import time
import socket
from scripts.config import (
    GOOGLE_DOC_CODEFORCES_ID, GOOGLE_DOC_LEETCODE_ID, GOOGLE_DOC_STEAM_ID,
    GOOGLE_DOC_YOUTUBE_ID, GOOGLE_DOC_CHESSCOM_ID,
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


    def _sync_any_content_to_gdoc(self, content_string, doc_id, doc_id_source_name="provided", max_retries=5, initial_delay=1):
        """
        Generic function to sync a string content to a specific Google Doc.
        This function will completely overwrite the document's content.
        Includes retry logic with exponential backoff and content chunking for large inputs.
        """
        if not self.authenticator:
            print("ERROR: Google Authenticator not available.")
            return False
        if not doc_id:
            print(f"CRITICAL ERROR: Google Doc ID from {doc_id_source_name} not found. Skipping sync.")
            return False

        for attempt in range(max_retries):
            try:
                docs_service = self.authenticator.get_service("docs", "v1")
                if not docs_service:
                    return False

                # 1. Clear the document content first
                document = docs_service.documents().get(documentId=doc_id, fields="body(content)").execute()
                content = document.get('body', {}).get('content', [])
                if content:
                    end_of_doc_index = content[-1].get('endIndex', 0)
                    if end_of_doc_index > 2:
                        delete_request = {
                            "deleteContentRange": {
                                "range": {"startIndex": 1, "endIndex": end_of_doc_index - 1}
                            }
                        }
                        docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": [delete_request]}).execute()

                # 2. Insert new content in batches
                if content_string:
                    CHUNK_SIZE = 100000  # characters per chunk
                    REQUESTS_PER_BATCH = 10  # insert requests per batchUpdate call

                    chunks = [content_string[i:i + CHUNK_SIZE] for i in range(0, len(content_string), CHUNK_SIZE)]
                    
                    all_insert_requests = []
                    for chunk in chunks:
                        all_insert_requests.append({
                            "insertText": {
                                "endOfSegmentLocation": {},  # Appends to the end of the document body
                                "text": chunk
                            }
                        })
                    
                    for i in range(0, len(all_insert_requests), REQUESTS_PER_BATCH):
                        batch = all_insert_requests[i:i + REQUESTS_PER_BATCH]
                        docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": batch}).execute()
                else:
                    print("WARNING: Source content is empty. Google Doc is now empty.")

                print(f"Successfully synced content to Google Doc.")
                return True
            except (HttpError, socket.timeout) as err:
                if isinstance(err, HttpError) and err.resp.status in [403, 429, 500, 503] and attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    print(f"Google API error (status {err.resp.status}). Retrying in {delay} seconds...")
                    time.sleep(delay)
                elif isinstance(err, socket.timeout) and attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    print(f"A timeout occurred. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"A Google API error occurred after {attempt + 1} attempts: {err}")
                    return False
            except Exception as e:
                print(f"An unexpected error occurred during Google Doc sync after {attempt + 1} attempts: {e}")
                return False
        return False # All retries failed

    def sync_codeforces_to_gdoc(self, content):
        """Syncs the Codeforces profile to its Google Doc."""
        print_section_header("Sync Codeforces Profile to Google Doc")
        return self._sync_any_content_to_gdoc(content, GOOGLE_DOC_CODEFORCES_ID, "GOOGLE_DOC_CODEFORCES_ID")

    def sync_leetcode_to_gdoc(self, content):
        """Syncs the LeetCode profile to its Google Doc."""
        print_section_header("Sync LeetCode Profile to Google Doc")
        return self._sync_any_content_to_gdoc(content, GOOGLE_DOC_LEETCODE_ID, "GOOGLE_DOC_LEETCODE_ID")

    def sync_steam_to_gdoc(self, content):
        """Syncs the Steam stats to its Google Doc."""
        print_section_header("Sync Steam Stats to Google Doc")
        return self._sync_any_content_to_gdoc(content, GOOGLE_DOC_STEAM_ID, "GOOGLE_DOC_STEAM_ID")

    def sync_youtube_to_gdoc(self, content):
        """Syncs the YouTube stats to its Google Doc."""
        print_section_header("Sync YouTube Stats to Google Doc")
        return self._sync_any_content_to_gdoc(content, GOOGLE_DOC_YOUTUBE_ID, "GOOGLE_DOC_YOUTUBE_ID")

    def sync_chesscom_to_gdoc(self, content):
        """Syncs the Chess.com profile to its Google Doc."""
        print_section_header("Sync Chess.com Profile to Google Doc")
        return self._sync_any_content_to_gdoc(content, GOOGLE_DOC_CHESSCOM_ID, "GOOGLE_DOC_CHESSCOM_ID")

    def sync_all_profiles_to_gdocs(self, profiles_content):
        """Syncs all supported shared files to their respective Google Docs."""
        print_section_header("Sync All Shared Files to Google Docs")
        sync_map = {
            "codeforces": (self.sync_codeforces_to_gdoc, GOOGLE_DOC_CODEFORCES_ID),
            "leetcode": (self.sync_leetcode_to_gdoc, GOOGLE_DOC_LEETCODE_ID),
            "steam": (self.sync_steam_to_gdoc, GOOGLE_DOC_STEAM_ID),
            "youtube": (self.sync_youtube_to_gdoc, GOOGLE_DOC_YOUTUBE_ID),
            "chesscom": (self.sync_chesscom_to_gdoc, GOOGLE_DOC_CHESSCOM_ID)
        }
        
        all_successful = True
        for profile_type, (sync_func, doc_id) in sync_map.items():
            content = profiles_content.get(profile_type)
            if content is None:
                print(f"WARNING: No content provided for {profile_type}. Skipping sync.")
                continue
            
            try:
                if not sync_func(content):
                    all_successful = False
                    print(f"Sync failed for: {profile_type}")
            except Exception as e:
                all_successful = False
                print(f"An unexpected error occurred during sync for {profile_type}: {e}")
        
        return all_successful

    def sync_all_profiles_to_gdocs_from_files(self, codeforces_file, leetcode_file, steam_file, youtube_file, chesscom_file):
        """
        Reads content from files and then syncs all supported profiles to their respective Google Docs.
        """
        profiles_content = {}
        
        with open(codeforces_file, 'r', encoding='utf-8') as f:
            profiles_content['codeforces'] = f.read()
        with open(leetcode_file, 'r', encoding='utf-8') as f:
            profiles_content['leetcode'] = f.read()
        with open(steam_file, 'r', encoding='utf-8') as f:
            profiles_content['steam'] = f.read()
        with open(youtube_file, 'r', encoding='utf-8') as f:
            profiles_content['youtube'] = f.read()
        with open(chesscom_file, 'r', encoding='utf-8') as f:
            profiles_content['chesscom'] = f.read()
            
        return self.sync_all_profiles_to_gdocs(profiles_content)