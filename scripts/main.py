# -*- coding: utf-8 -*-
"""
Main entry point for The-Mind Repository Automation Workflow.
"""
import sys
import os

# Ensure the script can find the modules directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.modules.validation import Validator
from scripts.modules.profile_generator import CodeforcesGenerator, LeetCodeGenerator, SteamStatsGenerator, YouTubeGenerator, ChessComGenerator
from scripts.modules.cloud_sync import CloudSyncer
from scripts.config import GOOGLE_DOC_CODEFORCES_ID, GOOGLE_DOC_LEETCODE_ID, GOOGLE_DOC_STEAM_ID, GOOGLE_DOC_YOUTUBE_ID, GOOGLE_DOC_CHESSCOM_ID


def main():
    """Main function that handles command line arguments and workflow execution."""
    if len(sys.argv) < 2:
        print("Usage: python main.py [workflow]")
        sys.exit(1)

    workflow = sys.argv[1]
    success = False

    cloud_syncer = CloudSyncer()

    def _generate_and_sync(generator_class, sync_method, doc_id):
        profile_content = generator_class().generate()
        if profile_content:
            return sync_method(profile_content)
        return False

    workflows = {
        'chess-com': lambda: _generate_and_sync(ChessComGenerator, cloud_syncer.sync_chesscom_to_gdoc, GOOGLE_DOC_CHESSCOM_ID),
        'codeforces': lambda: _generate_and_sync(CodeforcesGenerator, cloud_syncer.sync_codeforces_to_gdoc, GOOGLE_DOC_CODEFORCES_ID),
        'leetcode': lambda: _generate_and_sync(LeetCodeGenerator, cloud_syncer.sync_leetcode_to_gdoc, GOOGLE_DOC_LEETCODE_ID),
        'steam-stats': lambda: _generate_and_sync(SteamStatsGenerator, cloud_syncer.sync_steam_to_gdoc, GOOGLE_DOC_STEAM_ID),
        'youtube': lambda: _generate_and_sync(YouTubeGenerator, cloud_syncer.sync_youtube_to_gdoc, GOOGLE_DOC_YOUTUBE_ID),
    }

    if workflow in workflows:
        success = workflows[workflow]()
    else:
        print(f"[ERROR] Unknown workflow: {workflow}")
        sys.exit(1)

    if not success:
        print(f"\n[ERROR] Workflow '{workflow}' failed.")
        sys.exit(1)
    else:
        print(f"\n[SUCCESS] Workflow '{workflow}' completed successfully.")
        sys.exit(0)

if __name__ == "__main__":
    main()
