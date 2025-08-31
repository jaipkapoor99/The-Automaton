# -*- coding: utf-8 -*-
"""
Main entry point for The-Mind Repository Automation Workflow.
"""
import sys
import os

# Ensure the script can find the modules directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import print_section_header
from scripts.modules.validation import Validator
from scripts.modules.profile_generator import CodeforcesGenerator, LeetCodeGenerator, SteamStatsGenerator, YouTubeGenerator, ChessComGenerator
from scripts.modules.file_operations import FileManager
from scripts.modules.cloud_sync import CloudSyncer
from scripts.modules.perplexity import Perplexity
from scripts.modules.git_operations import GitManager

def main():
    """Main function that handles command line arguments and workflow execution."""
    if len(sys.argv) < 2:
        print("Usage: python main.py [workflow]")
        sys.exit(1)

    workflow = sys.argv[1]
    success = False

    workflows = {
        'chess-com': ChessComGenerator().generate,
        
        'clear-temp': FileManager().clear_temp_directory,
        'codeforces': CodeforcesGenerator().generate,
        
        
        'git-commit': GitManager().commit_and_push,
        'generate-and-sync-profiles': lambda: (lambda gen_cf: gen_cf and CodeforcesGenerator().generate() and LeetCodeGenerator().generate() and SteamStatsGenerator().generate() and YouTubeGenerator().generate() and ChessComGenerator().generate())(True) and CloudSyncer().sync_shared_files_to_gdocs(),
        'leetcode': LeetCodeGenerator().generate,
        'markdown-lint': Validator().lint_markdown_files,
        'perplexity': Perplexity().run,
        'steam-stats': SteamStatsGenerator().generate,
        'sync-cloud': CloudSyncer().sync_shared_files_to_gdocs,
        'sync-gdoc-chesscom': CloudSyncer().sync_chesscom_to_gdoc,
        'sync-gdoc-codeforces': CloudSyncer().sync_codeforces_to_gdoc,
        'sync-gdoc-leetcode': CloudSyncer().sync_leetcode_to_gdoc,
        'sync-gdoc-steam': CloudSyncer().sync_steam_to_gdoc,
        
        'sync-gdoc-youtube': CloudSyncer().sync_youtube_to_gdoc,
        'sync-local': CloudSyncer()._sync_shared_dir_to_local,
        
        'youtube': YouTubeGenerator().generate,
    }

    if workflow in workflows:
        # Special handling for 'generate-and-sync-profiles' to match original logic
        if workflow == 'generate-and-sync-profiles':
            print_section_header("Generate and Sync Profiles")
            profiles_generated = CodeforcesGenerator().generate() and LeetCodeGenerator().generate() and SteamStatsGenerator().generate() and YouTubeGenerator().generate() and ChessComGenerator().generate()
            if profiles_generated:
                print("All profiles generated successfully. Now syncing to Google Docs...")
                success = CloudSyncer().sync_shared_files_to_gdocs()
            else:
                print("Profile generation failed. Skipping sync.")
                success = False
        else:
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
