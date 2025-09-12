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
        'generate-and-sync-profiles': lambda: (
            lambda cf_content, lc_content, steam_content, yt_content, chess_content:
                CloudSyncer().sync_all_profiles_to_gdocs({
                    "codeforces": cf_content,
                    "leetcode": lc_content,
                    "steam": steam_content,
                    "youtube": yt_content,
                    "chesscom": chess_content
                })
        )(
            CodeforcesGenerator().generate(),
            LeetCodeGenerator().generate(),
            SteamStatsGenerator().generate(),
            YouTubeGenerator().generate(),
            ChessComGenerator().generate()
        ),
        'leetcode': LeetCodeGenerator().generate,
        'markdown-lint': Validator().lint_markdown_files,
        
        'steam-stats': SteamStatsGenerator().generate,
        'sync-cloud': CloudSyncer().sync_all_profiles_to_gdocs,
        'sync-local': CloudSyncer()._sync_shared_dir_to_local,
        
        'youtube': YouTubeGenerator().generate,
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
