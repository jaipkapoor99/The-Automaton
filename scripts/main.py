# -*- coding: utf-8 -*-
"""
Main entry point for The-Mind Repository Automation Workflow.
"""
import os
import sys

# Ensure the script can find the modules directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json

from scripts.config import TEMP_DIR
from scripts.modules.cloud_sync import CloudSyncer
from scripts.modules.profile_generator import (
    ChessComGenerator,
    CodeforcesGenerator,
    LeetCodeGenerator,
    SteamStatsGenerator,
    YouTubeGenerator,
)


def _generate_all_profiles():
    """Generates all profiles and returns a combined dictionary."""
    all_profiles_data = {}
    generators = [
        CodeforcesGenerator,
        LeetCodeGenerator,
        SteamStatsGenerator,
        YouTubeGenerator,
        ChessComGenerator,
    ]
    for gen_class in generators:
        profile_data = gen_class().generate()
        all_profiles_data.update(profile_data)
    return all_profiles_data


def main():
    """Main function that handles command line arguments and workflow execution."""
    if len(sys.argv) < 2:
        print("Usage: python main.py [workflow]")
        sys.exit(1)

    workflow = sys.argv[1]
    success = False

    cloud_syncer = CloudSyncer()

    if workflow == "generate-all":
        all_data = _generate_all_profiles()
        if all_data:
            os.makedirs(TEMP_DIR, exist_ok=True)
            output_file = os.path.join(TEMP_DIR, "all_profiles.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_data, f, indent=4)
            success = True
    elif workflow == "sync-all":
        json_file = os.path.join(TEMP_DIR, "all_profiles.json")
        if not os.path.exists(json_file):
            print("[INFO] 'all_profiles.json' not found. Generating first...")
            all_data = _generate_all_profiles()
            if all_data:
                os.makedirs(TEMP_DIR, exist_ok=True)
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(all_data, f, indent=4)
            else:
                print("[ERROR] Failed to generate profiles.")
                sys.exit(1)

        with open(json_file, "r", encoding="utf-8") as f:
            content_to_sync = json.load(f)

        success = cloud_syncer.sync_all_profiles_to_gsheet(content_to_sync)
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
