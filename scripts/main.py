# -*- coding: utf-8 -*-
"""
Main entry point for The-Mind Repository Automation Workflow.
"""
import os
import sys

# Ensure the script can find the modules directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json

from scripts.config import (GOOGLE_SHEET_CHESSCOM_ID,
                            GOOGLE_SHEET_CODEFORCES_ID,
                            GOOGLE_SHEET_LEETCODE_ID, GOOGLE_SHEET_STEAM_ID,
                            GOOGLE_SHEET_YOUTUBE_ID, TEMP_DIR)
from scripts.modules.cloud_sync import CloudSyncer
from scripts.modules.profile_generator import (ChessComGenerator,
                                               CodeforcesGenerator,
                                               LeetCodeGenerator,
                                               SteamStatsGenerator,
                                               YouTubeGenerator)


def _generate_profile(generator_class, output_file):
    profile_content_dict = generator_class().generate()
    if profile_content_dict:
        os.makedirs(TEMP_DIR, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(profile_content_dict, f, indent=4)
        return True
    return False


def _sync_profile(sync_method, sheet_id, input_file):
    if not os.path.exists(input_file):
        print(f"[ERROR] Input file not found: {input_file}")
        return False
    with open(input_file, "r", encoding="utf-8") as f:
        content_to_sync = json.load(f)
    return sync_method(content_to_sync)


def _generate_and_sync(generator_class, sync_method, sheet_id):
    output_file = os.path.join(
        TEMP_DIR,
        f"{generator_class.__name__.replace('Generator', '').lower()}_profile.json",
    )
    if _generate_profile(generator_class, output_file):
        return _sync_profile(sync_method, sheet_id, output_file)
    return False


def main():
    """Main function that handles command line arguments and workflow execution."""
    if len(sys.argv) < 2:
        print("Usage: python main.py [workflow]")
        sys.exit(1)

    workflow = sys.argv[1]
    success = False

    cloud_syncer = CloudSyncer()

    workflows = {
        "chess-com": lambda: _generate_and_sync(
            ChessComGenerator,
            cloud_syncer.sync_chesscom_to_gsheet,
            GOOGLE_SHEET_CHESSCOM_ID,
        ),
        "codeforces": lambda: _generate_and_sync(
            CodeforcesGenerator,
            cloud_syncer.sync_codeforces_to_gsheet,
            GOOGLE_SHEET_CODEFORCES_ID,
        ),
        "leetcode": lambda: _generate_and_sync(
            LeetCodeGenerator,
            cloud_syncer.sync_leetcode_to_gsheet,
            GOOGLE_SHEET_LEETCODE_ID,
        ),
        "steam-stats": lambda: _generate_and_sync(
            SteamStatsGenerator,
            cloud_syncer.sync_steam_to_gsheet,
            GOOGLE_SHEET_STEAM_ID,
        ),
        "youtube": lambda: _generate_and_sync(
            YouTubeGenerator,
            cloud_syncer.sync_youtube_to_gsheet,
            GOOGLE_SHEET_YOUTUBE_ID,
        ),
        "codeforces-generate": lambda: _generate_profile(
            CodeforcesGenerator, os.path.join(TEMP_DIR, "codeforces_profile.json")
        ),
        "codeforces-sync": lambda: _sync_profile(
            cloud_syncer.sync_codeforces_to_gsheet,
            GOOGLE_SHEET_CODEFORCES_ID,
            os.path.join(TEMP_DIR, "codeforces_profile.json"),
        ),
        "leetcode-generate": lambda: _generate_profile(
            LeetCodeGenerator, os.path.join(TEMP_DIR, "leetcode_profile.json")
        ),
        "leetcode-sync": lambda: _sync_profile(
            cloud_syncer.sync_leetcode_to_gsheet,
            GOOGLE_SHEET_LEETCODE_ID,
            os.path.join(TEMP_DIR, "leetcode_profile.json"),
        ),
        "steam-generate": lambda: _generate_profile(
            SteamStatsGenerator, os.path.join(TEMP_DIR, "steam_profile.json")
        ),
        "steam-sync": lambda: _sync_profile(
            cloud_syncer.sync_steam_to_gsheet,
            GOOGLE_SHEET_STEAM_ID,
            os.path.join(TEMP_DIR, "steam_profile.json"),
        ),
        "youtube-generate": lambda: _generate_profile(
            YouTubeGenerator, os.path.join(TEMP_DIR, "youtube_profile.json")
        ),
        "youtube-sync": lambda: _sync_profile(
            cloud_syncer.sync_youtube_to_gsheet,
            GOOGLE_SHEET_YOUTUBE_ID,
            os.path.join(TEMP_DIR, "youtube_profile.json"),
        ),
        "chesscom-generate": lambda: _generate_profile(
            ChessComGenerator, os.path.join(TEMP_DIR, "chesscom_profile.json")
        ),
        "chesscom-sync": lambda: _sync_profile(
            cloud_syncer.sync_chesscom_to_gsheet,
            GOOGLE_SHEET_CHESSCOM_ID,
            os.path.join(TEMP_DIR, "chesscom_profile.json"),
        ),
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
