# -*- coding: utf-8 -*-
"""
Main entry point for The-Mind Repository Automation Workflow.
"""
import json
import os
import sys
from typing import Callable, Type, Union

from config import TEMP_DIR
from modules.cloud_sync import CloudSyncer
from modules.profile_generator import (ChessComGenerator, CodeforcesGenerator,
                                       LeetCodeGenerator, SteamStatsGenerator)


def _generate_profile(
    generator_class: Union[
        Type[CodeforcesGenerator],
        Type[LeetCodeGenerator],
        Type[SteamStatsGenerator],
        Type[ChessComGenerator],
    ],
    output_file: str,
):
    """Generates a single profile and saves it to a file."""
    profile_data = generator_class().generate()
    if profile_data:
        os.makedirs(TEMP_DIR, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=4)
        return True
    return False


def _sync_profile(sync_function: Callable, json_file: str):
    """Syncs a single profile from a JSON file."""
    if not os.path.exists(json_file):
        print(f"[ERROR] JSON file not found: {json_file}")
        return False
    with open(json_file, "r", encoding="utf-8") as f:
        content_to_sync = json.load(f)
    return sync_function(content_to_sync)


def main():
    """Main function that handles command line arguments and workflow execution."""
    if len(sys.argv) < 2:
        print("Usage: python main.py [workflow]")
        sys.exit(1)

    workflow = sys.argv[1]
    success = False

    cloud_syncer = CloudSyncer()

    workflows = {
        "generate-codeforces": lambda: _generate_profile(
            CodeforcesGenerator, os.path.join(TEMP_DIR, "codeforces_profile.json")
        ),
        "generate-leetcode": lambda: _generate_profile(
            LeetCodeGenerator, os.path.join(TEMP_DIR, "leetcode_profile.json")
        ),
        "generate-steam": lambda: _generate_profile(
            SteamStatsGenerator, os.path.join(TEMP_DIR, "steam_profile.json")
        ),
        "generate-chesscom": lambda: _generate_profile(
            ChessComGenerator, os.path.join(TEMP_DIR, "chesscom_profile.json")
        ),
        "sync-codeforces": lambda: _sync_profile(
            cloud_syncer.sync_codeforces_to_gsheet,
            os.path.join(TEMP_DIR, "codeforces_profile.json"),
        ),
        "sync-leetcode": lambda: _sync_profile(
            cloud_syncer.sync_leetcode_to_gsheet,
            os.path.join(TEMP_DIR, "leetcode_profile.json"),
        ),
        "sync-steam": lambda: _sync_profile(
            cloud_syncer.sync_steam_to_gsheet,
            os.path.join(TEMP_DIR, "steam_profile.json"),
        ),
        "sync-chesscom": lambda: _sync_profile(
            cloud_syncer.sync_chesscom_to_gsheet,
            os.path.join(TEMP_DIR, "chesscom_profile.json"),
        ),
    }

    if workflow in workflows:
        if "generate" in workflow:
            data = workflows[workflow]()
            if data:
                success = True
        elif "sync" in workflow:
            success = workflows[workflow]()
    else:
        print(
            f"[ERROR] Unknown or unsupported workflow for this script version: {workflow}"
        )
        sys.exit(1)

    if not success:
        print(f"\n[ERROR] Workflow '{workflow}' failed.")
        sys.exit(1)
    else:
        print(f"\n[SUCCESS] Workflow '{workflow}' completed successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
