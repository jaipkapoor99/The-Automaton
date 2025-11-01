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
from scripts.config import GOOGLE_DOC_CODEFORCES_ID, GOOGLE_DOC_LEETCODE_ID, GOOGLE_DOC_STEAM_ID, GOOGLE_DOC_YOUTUBE_ID, GOOGLE_DOC_CHESSCOM_ID, TEMP_DIR


def _generate_profile(generator_class, output_file):
    profile_content = generator_class().generate()
    if profile_content:
        os.makedirs(TEMP_DIR, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(profile_content)
        return True
    return False

def _sync_profile(sync_method, doc_id, input_file):
    if not os.path.exists(input_file):
        print(f"[ERROR] Input file not found: {input_file}")
        return False
    with open(input_file, "r", encoding="utf-8") as f:
        content_to_sync = f.read()
    return sync_method(content_to_sync)

def main():
    """Main function that handles command line arguments and workflow execution."""
    if len(sys.argv) < 2:
        print("Usage: python main.py [workflow]")
        sys.exit(1)

    workflow = sys.argv[1]
    success = False

    cloud_syncer = CloudSyncer()

    workflows = {
        'chess-com': lambda: _generate_and_sync(ChessComGenerator, cloud_syncer.sync_chesscom_to_gdoc, GOOGLE_DOC_CHESSCOM_ID),
        'codeforces': lambda: _generate_and_sync(CodeforcesGenerator, cloud_syncer.sync_codeforces_to_gdoc, GOOGLE_DOC_CODEFORCES_ID),
        'leetcode': lambda: _generate_and_sync(LeetCodeGenerator, cloud_syncer.sync_leetcode_to_gdoc, GOOGLE_DOC_LEETCODE_ID),
        'steam-stats': lambda: _generate_and_sync(SteamStatsGenerator, cloud_syncer.sync_steam_to_gdoc, GOOGLE_DOC_STEAM_ID),
        'youtube': lambda: _generate_and_sync(YouTubeGenerator, cloud_syncer.sync_youtube_to_gdoc, GOOGLE_DOC_YOUTUBE_ID),
        
        'codeforces-generate': lambda: _generate_profile(CodeforcesGenerator, os.path.join(TEMP_DIR, "codeforces_profile.txt")),
        'codeforces-sync': lambda: _sync_profile(cloud_syncer.sync_codeforces_to_gdoc, GOOGLE_DOC_CODEFORCES_ID, os.path.join(TEMP_DIR, "codeforces_profile.txt")),
        'leetcode-generate': lambda: _generate_profile(LeetCodeGenerator, os.path.join(TEMP_DIR, "leetcode_profile.txt")),
        'leetcode-sync': lambda: _sync_profile(cloud_syncer.sync_leetcode_to_gdoc, GOOGLE_DOC_LEETCODE_ID, os.path.join(TEMP_DIR, "leetcode_profile.txt")),
        'steam-generate': lambda: _generate_profile(SteamStatsGenerator, os.path.join(TEMP_DIR, "steam_profile.txt")),
        'steam-sync': lambda: _sync_profile(cloud_syncer.sync_steam_to_gdoc, GOOGLE_DOC_STEAM_ID, os.path.join(TEMP_DIR, "steam_profile.txt")),
        'youtube-generate': lambda: _generate_profile(YouTubeGenerator, os.path.join(TEMP_DIR, "youtube_profile.txt")),
        'youtube-sync': lambda: _sync_profile(cloud_syncer.sync_youtube_to_gdoc, GOOGLE_DOC_YOUTUBE_ID, os.path.join(TEMP_DIR, "youtube_profile.txt")),
        'chesscom-generate': lambda: _generate_profile(ChessComGenerator, os.path.join(TEMP_DIR, "chesscom_profile.txt")),
        'chesscom-sync': lambda: _sync_profile(cloud_syncer.sync_chesscom_to_gdoc, GOOGLE_DOC_CHESSCOM_ID, os.path.join(TEMP_DIR, "chesscom_profile.txt")),
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
