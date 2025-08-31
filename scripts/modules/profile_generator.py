# -*- coding: utf-8 -*-
"""
Generates profiles for various competitive programming and gaming platforms.
"""
import requests
import time
import json
from datetime import datetime
from collections import Counter
import hashlib
import random
import string
from typing import Dict, Any
from scripts.config import (
    CF_HANDLE, CF_OUTPUT_FILE, LEETCODE_USERNAME, LEETCODE_OUTPUT_FILE,
    LEETCODE_API_ENDPOINT, STEAM_ID, STEAM_API_KEY, STEAM_API_ENDPOINT, STEAM_OUTPUT_FILE, YOUTUBE_CHANNEL_ID,
    YOUTUBE_OUTPUT_FILE, CF_API_KEY, CF_API_SECRET, CODEFORCES_API_ENDPOINT,
    CHESSCOM_ID, CHESSCOM_OUTPUT_FILE, CHESSCOM_API_ENDPOINT
)
from scripts.modules.google_auth import GoogleAuthenticator
from scripts.modules.file_operations import ensure_file_exists

class CodeforcesGenerator:
    """Generates a Codeforces profile."""

    def __init__(self, handle=CF_HANDLE, output_file=CF_OUTPUT_FILE, api_key=CF_API_KEY, api_secret=CF_API_SECRET):
        self.handle = handle
        self.output_file = output_file
        self.api_key = api_key
        self.api_secret = api_secret
        self.profile_content = []
        self.base_url = CODEFORCES_API_ENDPOINT
        self.section_counter = 1

    def _add_section_header(self, title):
        """Adds a formatted and numbered section header."""
        self.profile_content.append("\n" + "="*40 + "\n")
        self.profile_content.append(f"## {self.section_counter}. {title}\n")
        self.section_counter += 1

    def _generate_api_sig(self, method_name, params):
        """Generates the apiSig parameter for authorized methods."""
        rand_prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        # Parameters must be sorted alphabetically by key
        sorted_params = sorted(params.items())
        param_str = '&'.join([f'{k}={v}' for k, v in sorted_params])
        
        hash_str = f"{rand_prefix}/{method_name}?{param_str}#{self.api_secret}"
        
        hasher = hashlib.sha512()
        hasher.update(hash_str.encode('utf-8'))
        
        return rand_prefix + hasher.hexdigest()

    def _fetch_data(self, method, params=None, authorized=False):
        if params is None:
            params = {}
            
        url = f"{self.base_url}/{method}"

        if authorized:
            if not self.api_key or not self.api_secret:
                # Fail gracefully if keys are not provided
                return None
            params['apiKey'] = self.api_key
            params['time'] = int(time.time())
            params['apiSig'] = self._generate_api_sig(method, params)

        try:
            response = requests.get(url, params=params, timeout=15)
            time.sleep(1)  # Respect API rate limits
            response.raise_for_status()
            data = response.json()
            if data.get('status') == 'OK':
                return data.get('result')
            else:
                # Don't append error for user.friends as it's expected to fail without auth
                if method != 'user.friends':
                    self.profile_content.append(f"API Error for {method}: {data.get('comment', 'Unknown error')}")
                return None
        except requests.exceptions.RequestException as e:
            if method != 'user.friends':
                self.profile_content.append(f"An error occurred fetching data from {method}: {e}")
            return None

    def generate(self):
        """Fetches and generates the Codeforces profile."""
        if not self.handle:
            print("ERROR: Codeforces handle not set. Please set the CODEFORCES_ID in your .env file.")
            return False
        ensure_file_exists(self.output_file)
        print(f"Generating exhaustive Codeforces profile for {self.handle}...")

        self.profile_content.append(f"# Exhaustive Codeforces Profile: {self.handle}")
        self.profile_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. User Info and Global Rank
        user_info = self._fetch_data("user.info", params={"handles": self.handle})
        if user_info:
            user = user_info[0]
            self._add_section_header("User Summary")
            self.profile_content.append(f"- **Handle:** {user.get('handle', 'N/A')}")
            self.profile_content.append(f"- **Rating:** {user.get('rating', 'N/A')} ({user.get('rank', 'N/A')})")
            self.profile_content.append(f"- **Max Rating:** {user.get('maxRating', 'N/A')} ({user.get('maxRank', 'N/A')})")
            self.profile_content.append(f"- **Contribution:** {user.get('contribution', 'N/A')}")
            self.profile_content.append(f"- **Registered:** {datetime.fromtimestamp(user.get('registrationTimeSeconds', 0)).strftime('%Y-%m-%d')}")
            
            # Global Rank
            rated_list = self._fetch_data("user.ratedList", params={"activeOnly": "true"})
            if rated_list:
                try:
                    rank = next((i for i, u in enumerate(rated_list) if u['handle'] == self.handle), -1)
                    if rank != -1:
                        self.profile_content.append(f"- **Global Rank (Active):** {rank + 1} / {len(rated_list)}")
                except (StopIteration, KeyError):
                    pass # User not in active rated list

        # 2. Submissions Analysis (All submissions)
        all_submissions = self._fetch_data("user.status", params={"handle": self.handle})
        if all_submissions:
            self._add_section_header("Submissions Analysis (All Time)")
            verdicts = Counter(s['verdict'] for s in all_submissions)
            languages = Counter(s['programmingLanguage'] for s in all_submissions)
            tags = Counter(tag for s in all_submissions if 'problem' in s for tag in s['problem'].get('tags', []))
            
            self.profile_content.append("### Verdicts:")
            for verdict, count in verdicts.most_common():
                self.profile_content.append(f"- **{verdict}:** {count}")

            self.profile_content.append("\n### Languages:")
            for lang, count in languages.most_common():
                self.profile_content.append(f"- **{lang}:** {count}")

            self.profile_content.append("\n### Problem Tags (Top 15 Overall):")
            for tag, count in tags.most_common(15):
                self.profile_content.append(f"- **{tag}:** {count}")

        # 3. Contest Performance and Hacks
        rating_history = self._fetch_data("user.rating", params={"handle": self.handle})
        if rating_history:
            self._add_section_header("Recent Contest Performance")
            recent_contests = sorted(rating_history, key=lambda x: x['ratingUpdateTimeSeconds'], reverse=True)[:5]
            for contest in recent_contests:
                contest_id = contest['contestId']
                self.profile_content.append(f"- **Contest:** {contest['contestName']} (ID: {contest_id})")
                self.profile_content.append(f"  - **Rank:** {contest['rank']}")
                self.profile_content.append(f"  - **Rating Change:** {contest['newRating'] - contest['oldRating']:+})")
                self.profile_content.append(f"  - **New Rating:** {contest['newRating']}")
                
                # Hacks in this contest
                hacks = self._fetch_data("contest.hacks", params={"contestId": contest_id})
                if hacks:
                    user_hacks = [h for h in hacks if h['hacker']['members'][0]['handle'] == self.handle]
                    if user_hacks:
                        self.profile_content.append("  - **Hacks:**")
                        for hack in user_hacks:
                            self.profile_content.append(f"    - **Problem:** {hack['problem']['index']} | **Verdict:** {hack['verdict']}")

        # 4. Friends
        self._add_section_header("Friends")
        friends = self._fetch_data("user.friends", params={"onlyOnline": "false"}, authorized=True)
        if friends:
            self.profile_content.append("- " + ", ".join(friends))
        else:
            self.profile_content.append("- Could not retrieve friends list. This method requires authorization, or the API keys are missing/invalid.")

        # 5. Problem Submission History
        if all_submissions:
            submissions_by_problem = {}
            for submission in all_submissions:
                problem = submission['problem']
                problem_key = f"{problem.get('contestId', '')}-{problem.get('index', '')}"
                if problem_key not in submissions_by_problem:
                    submissions_by_problem[problem_key] = {
                        "name": problem.get('name', 'N/A'),
                        "tags": problem.get('tags', []),
                        "submissions": []
                    }
                submissions_by_problem[problem_key]['submissions'].append(submission)

            if submissions_by_problem:
                self._add_section_header("Problem Submission History")

                # Sort problems by contestId, then problem index if contestId is not None
                def sort_key(item):
                    contest_id_str = item[0].split('-')[0]
                    problem_index = item[0].split('-')[1]
                    contest_id = int(contest_id_str) if contest_id_str.isdigit() else float('inf')
                    return (contest_id, problem_index)

                sorted_problems = sorted(submissions_by_problem.items(), key=sort_key)

                for _, problem_data in sorted_problems:
                    tags_str = ", ".join(problem_data['tags'])
                    self.profile_content.append(f"### {problem_data['name']} (Tags: {tags_str})")
                    
                    # Sort submissions by time
                    sorted_submissions = sorted(problem_data['submissions'], key=lambda s: s['creationTimeSeconds'])
                    
                    for sub in sorted_submissions:
                        submission_time = datetime.fromtimestamp(sub.get('creationTimeSeconds', 0)).strftime('%Y-%m-%d %H:%M:%S')
                        self.profile_content.append(f"- **Submission Time:** {submission_time}")
                        self.profile_content.append(f"  - **Verdict:** {sub.get('verdict', 'N/A')}")
                        self.profile_content.append(f"  - **Language:** {sub.get('programmingLanguage', 'N/A')}")
                        self.profile_content.append(f"  - **Time:** {sub.get('timeConsumedMillis', 'N/A')} ms")
                        self.profile_content.append(f"  - **Memory:** {sub.get('memoryConsumedBytes', 0) / 1024:.2f} KB")
                    self.profile_content.append("") # Newline for spacing

        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.profile_content))
            print(f"Successfully generated exhaustive Codeforces profile at {self.output_file}")
            return True
        except IOError as e:
            print(f"Error writing to file {self.output_file}: {e}")
            return False

class LeetCodeGenerator:
    """Generates a LeetCode profile."""

    def __init__(self, username=LEETCODE_USERNAME, output_file=LEETCODE_OUTPUT_FILE):
        self.username = username
        self.output_file = output_file
        self.profile_content = []

    def _fetch_graphql_data(self, query, variables):
        try:
            response = requests.post(LEETCODE_API_ENDPOINT, json={"query": query, "variables": variables}, timeout=15)
            time.sleep(1)
            response.raise_for_status()
            return response.json().get('data')
        except requests.exceptions.RequestException as e:
            self.profile_content.append(f"An error occurred fetching data: {e}")
            return None
        except json.JSONDecodeError:
            self.profile_content.append(f"Error decoding LeetCode API response (status {response.status_code})")
            return None

    def generate(self):
        """Fetches and generates the LeetCode profile."""
        if not self.username:
            print("ERROR: LeetCode username not set.")
            return False
        ensure_file_exists(self.output_file)
        print(f"Generating exhaustive LeetCode profile for {self.username}...")

        query = """
        query getUserProfile($username: String!) {
          allQuestionsCount { difficulty count }
          matchedUser(username: $username) {
            username
            contributions { points }
            profile { realName ranking }
            submissionCalendar
            submitStats: submitStatsGlobal {
              acSubmissionNum { difficulty count submissions }
            }
          }
        }
        """
        variables = {"username": self.username}
        data = self._fetch_graphql_data(query, variables)

        self.profile_content.append(f"# Exhaustive LeetCode Profile: {self.username}")
        self.profile_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.profile_content.append("\n" + "="*40 + "\n")

        if data and data.get('matchedUser'):
            user = data['matchedUser']
            self.profile_content.append("## 1. User Summary\n")
            self.profile_content.append(f"- **Username:** {user.get('username', 'N/A')}")
            self.profile_content.append(f"- **Real Name:** {user.get('profile', {}).get('realName', 'N/A')}")
            self.profile_content.append(f"- **Global Ranking:** {user.get('profile', {}).get('ranking', 'N/A')}")
            self.profile_content.append(f"- **Contribution Points:** {user.get('contributions', {}).get('points', 'N/A')}")
            self.profile_content.append("\n" + "="*40 + "\n")

            self.profile_content.append("## 2. Problem Stats\n")
            stats = user.get('submitStats', {}).get('acSubmissionNum', [])
            total_solved = sum(s['count'] for s in stats)
            self.profile_content.append(f"**Total Solved:** {total_solved}\n")
            for s in stats:
                self.profile_content.append(f"- **{s['difficulty']}:** {s['count']} solved / {s['submissions']} submissions")
            self.profile_content.append("\n" + "="*40 + "\n")

            self.profile_content.append("## 3. Submission Calendar\n")
            try:
                calendar_data = json.loads(user.get('submissionCalendar', '{}'))
                total_active_days = sum(1 for count in calendar_data.values() if int(count) > 0)
                self.profile_content.append(f"- **Total Active Days:** {total_active_days}")
                # You can add more detailed calendar parsing here if needed
            except (json.JSONDecodeError, TypeError):
                self.profile_content.append("- Calendar data not available.")

        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.profile_content))
            print(f"Successfully generated exhaustive LeetCode profile at {self.output_file}")
            return True
        except IOError as e:
            print(f"Error writing to file {self.output_file}: {e}")
            return False

class SteamStatsGenerator:
    """Generates a comprehensive Steam profile based on a detailed plan."""

    def __init__(self, api_key=STEAM_API_KEY, steam_id=STEAM_ID, output_file=STEAM_OUTPUT_FILE):
        self.api_key = api_key
        self.steam_id = steam_id
        self.output_file = output_file
        self.profile_content = []
        self.base_url = STEAM_API_ENDPOINT

    def _make_api_call(self, interface, method, version, params=None):
        """Makes a call to the Steam Web API."""
        if not self.api_key:
            self.profile_content.append("API Error: Steam API Key is missing.")
            return None
        
        url = f"{self.base_url}/{interface}/{method}/v{version}/"
        
        base_params = {'key': self.api_key, 'steamid': self.steam_id, 'format': 'json'}
        if params:
            base_params.update(params)
            
        try:
            response = requests.get(url, params=base_params, timeout=30)
            time.sleep(0.5) # Rate limiting
            if response.status_code == 403:
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def _get_player_summaries(self):
        return self._make_api_call('ISteamUser', 'GetPlayerSummaries', 2, {'steamids': self.steam_id})

    def _get_owned_games(self):
        return self._make_api_call('IPlayerService', 'GetOwnedGames', 1, {'include_appinfo': True, 'include_played_free_games': True})

    def _get_player_achievements(self, app_id):
        return self._make_api_call('ISteamUserStats', 'GetPlayerAchievements', 1, {'appid': app_id})

    def _get_user_stats_for_game(self, app_id):
        return self._make_api_call('ISteamUserStats', 'GetUserStatsForGame', 2, {'appid': app_id})

    def _get_player_level(self):
        return self._make_api_call('IPlayerService', 'GetSteamLevel', 1)

    def _get_player_badges(self):
        return self._make_api_call('IPlayerService', 'GetBadges', 1)
        
    def _get_community_badge_progress(self):
        return self._make_api_call('IPlayerService', 'GetCommunityBadgeProgress', 1)

    def generate(self):
        """Fetches and generates the Steam profile according to the specified plan."""
        if not self.api_key or not self.steam_id:
            print("ERROR: Steam API Key or Steam ID not set.")
            return False
        ensure_file_exists(self.output_file)
        print(f"Generating Steam profile for Steam ID: {self.steam_id}...")

        self.profile_content.append(f"# Steam Profile Analysis")
        self.profile_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.profile_content.append("\n" + "="*40 + "\n")

        # 1. Profile Summary
        self.profile_content.append("## 1. Profile Summary\n")
        player_summary = self._get_player_summaries()
        if player_summary and player_summary.get('response', {}).get('players'):
            player = player_summary['response']['players'][0]
            self.profile_content.append(f"- **Username:** {player.get('personaname', 'N/A')}")
        else:
            self.profile_content.append("- **Username:** Could not fetch.")

        level_data = self._get_player_level()
        if level_data and level_data.get('response'):
            self.profile_content.append(f"- **Steam Level:** {level_data['response'].get('player_level', 'N/A')}")

        badges_data = self._get_player_badges()
        if badges_data and badges_data.get('response'):
            self.profile_content.append(f"- **Total Badges:** {len(badges_data['response'].get('badges', []))}")
            self.profile_content.append(f"- **Total XP:** {badges_data['response'].get('player_xp', 'N/A')}")
            
        badge_progress = self._get_community_badge_progress()
        if badge_progress and badge_progress.get('response', {}).get('quests'):
            completed_quests = sum(1 for q in badge_progress['response']['quests'] if q.get('completed'))
            self.profile_content.append(f"- **Community Quests Completed:** {completed_quests}/{len(badge_progress['response']['quests'])}")
        
        self.profile_content.append("\n" + "="*40 + "\n")

        # 2. Game Library Analysis
        self.profile_content.append("## 2. Game Library & Per-Game Statistics\n")
        owned_games = self._get_owned_games()
        if owned_games and owned_games.get('response', {}).get('games'):
            games = sorted(owned_games['response']['games'], key=lambda x: x.get('playtime_forever', 0), reverse=True)
            self.profile_content.append(f"**Total Games:** {owned_games['response'].get('game_count', len(games))}\n")

            for game in games:
                appid = game.get('appid')
                playtime_hours = game.get('playtime_forever', 0) / 60
                self.profile_content.append(f"### {game.get('name', 'Unknown Game')}")
                self.profile_content.append(f"- **Playtime:** {playtime_hours:.2f} hours")

                # Achievements
                achievements = self._get_player_achievements(appid)
                if achievements and achievements.get('playerstats', {}).get('success') and 'achievements' in achievements['playerstats']:
                    achieved = [a for a in achievements['playerstats']['achievements'] if a.get('achieved')]
                    total = len(achievements['playerstats']['achievements'])
                    self.profile_content.append(f"- **Achievements:** {len(achieved)} / {total}")
                else:
                    self.profile_content.append("- **Achievements:** Game data could not be retrieved.")

                # User Stats
                user_stats = self._get_user_stats_for_game(appid)
                if user_stats and user_stats.get('playerstats', {}).get('success') and 'stats' in user_stats['playerstats']:
                    self.profile_content.append("- **Game Stats:**")
                    for stat in user_stats['playerstats']['stats']:
                        self.profile_content.append(f"  - {stat.get('name', 'N/A')}: {stat.get('value', 'N/A')}")
                self.profile_content.append("") # Add a newline for spacing
        else:
            self.profile_content.append("Could not retrieve game library. Profile may be private.")

        # 3. Finalize
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.profile_content))
            print(f"Successfully generated Steam profile at {self.output_file}")
            return True
        except IOError as e:
            print(f"Error writing to file {self.output_file}: {e}")
            return False

class YouTubeGenerator:
    """Generates a YouTube profile."""

    def __init__(self, channel_id=YOUTUBE_CHANNEL_ID, output_file=YOUTUBE_OUTPUT_FILE):
        self.channel_id = channel_id
        self.output_file = output_file
        self.profile_content = []
        self.youtube_service = GoogleAuthenticator().get_service('youtube', 'v3')

    def _get_channel_stats(self):
        if not self.youtube_service:
            return None
        request = self.youtube_service.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        )
        response = request.execute()
        return response.get('items', [{}])[0]

    def _get_playlists(self):
        if not self.youtube_service:
            return []
        playlists = []
        request = self.youtube_service.playlists().list(
            part="snippet,contentDetails",
            mine=True,
            maxResults=50
        )
        while request:
            response = request.execute()
            playlists.extend(response.get('items', []))
            request = self.youtube_service.playlists().list_next(request, response)
        return playlists

    def _get_playlist_videos(self, playlist_id):
        if not self.youtube_service:
            return []
        videos = []
        request = self.youtube_service.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50
        )
        while request and len(videos) < 500:
            response = request.execute()
            videos.extend(response.get('items', []))
            request = self.youtube_service.playlistItems().list_next(request, response)
        return videos

    def _get_video_stats(self, video_id):
        if not self.youtube_service:
            return None
        request = self.youtube_service.videos().list(
            part="statistics",
            id=video_id
        )
        response = request.execute()
        return response.get('items', [{}])[0].get('statistics', {})

    def _get_special_playlist(self, playlist_id, limit=500):
        if not self.youtube_service:
            return []
        videos = []
        try:
            request = self.youtube_service.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50
            )
            while request and len(videos) < limit:
                response = request.execute()
                videos.extend(response.get('items', []))
                request = self.youtube_service.playlistItems().list_next(request, response)
        except Exception as e:
            print(f"Could not fetch playlist {playlist_id}. It might be private or disabled. Error: {e}")
            return []
        return videos

    def _get_subscriptions(self):
        if not self.youtube_service:
            return []
        subscriptions = []
        request = self.youtube_service.subscriptions().list(
            part="snippet",
            mine=True,
            maxResults=50
        )
        while request:
            response = request.execute()
            subscriptions.extend(response.get('items', []))
            request = self.youtube_service.subscriptions().list_next(request, response)
        return subscriptions

    def generate(self):
        """Fetches and generates the YouTube profile."""
        if not self.channel_id:
            print("ERROR: YouTube Channel ID not set.")
            return False
        ensure_file_exists(self.output_file)
        print(f"Generating YouTube profile for channel {self.channel_id}...")

        channel_data = self._get_channel_stats()
        if not channel_data:
            print("Could not fetch channel data.")
            return False

        stats = channel_data.get('statistics', {})
        snippet = channel_data.get('snippet', {})
        
        self.profile_content.append(f"# YouTube Channel Stats: {snippet.get('title', 'N/A')}")
        self.profile_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.profile_content.append("\n" + "="*40 + "\n")
        self.profile_content.append("## 1. Channel Summary\n")
        self.profile_content.append(f"- **Subscribers:** {stats.get('subscriberCount', 'N/A')}")
        self.profile_content.append(f"- **Total Views:** {stats.get('viewCount', 'N/A')}")
        self.profile_content.append(f"- **Total Videos:** {stats.get('videoCount', 'N/A')}")
        self.profile_content.append(f"- **Published At:** {snippet.get('publishedAt', 'N/A')}")
        self.profile_content.append("\n" + "="*40 + "\n")

        playlists = self._get_playlists()
        if playlists:
            self.profile_content.append("## 2. Playlists\n")
            for playlist in playlists:
                playlist_snippet = playlist.get('snippet', {})
                self.profile_content.append(f"### {playlist_snippet.get('title', 'N/A')}\n")
                videos = self._get_playlist_videos(playlist.get('id'))
                for video in videos:
                    video_snippet = video.get('snippet', {})
                    video_stats = self._get_video_stats(video_snippet.get('resourceId', {}).get('videoId'))
                    self.profile_content.append(f"- **{video_snippet.get('title', 'N/A')}**")
                    self.profile_content.append(f"  - Views: {video_stats.get('viewCount', 'N/A')}")
                    self.profile_content.append(f"  - Likes: {video_stats.get('likeCount', 'N/A')}")
                    self.profile_content.append(f"  - Comments: {video_stats.get('commentCount', 'N/A')}")
        
        liked_videos = self._get_special_playlist('LL')
        if liked_videos:
            self.profile_content.append("\n## 3. Liked Videos (Last 500)\n")
            for item in liked_videos:
                snippet = item.get('snippet', {})
                title = snippet.get('title', 'N/A')
                channel = snippet.get('videoOwnerChannelTitle', 'N/A')
                self.profile_content.append(f"- **{title}** by {channel}")

        watch_history = self._get_special_playlist('HL')
        if watch_history:
            self.profile_content.append("\n## 4. Watch History (Last 500 Videos)\n")
            for item in watch_history:
                snippet = item.get('snippet', {})
                title = snippet.get('title', 'N/A')
                channel = snippet.get('videoOwnerChannelTitle', 'N/A')
                self.profile_content.append(f"- **{title}** by {channel}")

        subscriptions = self._get_subscriptions()
        if subscriptions:
            self.profile_content.append("\n## 5. Subscriptions\n")
            for item in subscriptions:
                snippet = item.get('snippet', {})
                title = snippet.get('title', 'N/A')
                self.profile_content.append(f"- {title}")

        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.profile_content))
            print(f"Successfully generated YouTube profile at {self.output_file}")
            return True
        except IOError as e:
            print(f"Error writing to file {self.output_file}: {e}")
            return False

class ChessComGenerator:
    """Generates a Chess.com profile."""

    def __init__(self, username: str = CHESSCOM_ID, output_file: str = CHESSCOM_OUTPUT_FILE):
        self.username = username
        self.output_file = output_file
        self.profile_content = []
        self.base_url = CHESSCOM_API_ENDPOINT

    def _fetch_data(self, endpoint: str) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'User-Agent': 'The-Automaton'
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.profile_content.append(f"An error occurred fetching data from {endpoint}: {e}")
            return {}

    def _add_header(self, text: str, level: int = 1):
        """Adds a formatted header to the profile content."""
        self.profile_content.append(f"\n{text}")
        if level == 1:
            self.profile_content.append("=" * len(text))
        else:
            self.profile_content.append("-" * len(text))

    def _format_game_entry(self, game: Dict[str, Any]) -> str:
        """Formats a single game entry to return only the PGN with a header."""
        pgn = game.get('pgn', 'PGN not available')
        return f"--- PGN ---\n{pgn}\n--- End Game ---"

    def generate(self) -> bool:
        """Fetches and generates the Chess.com profile."""
        print(f"Generating Chess.com profile for {self.username}...")
        if not self.username:
            print("ERROR: Chess.com username not set.")
            return False

        title = f"Chess.com Profile: {self.username}"
        self.profile_content.append(title)
        self.profile_content.append("=" * len(title))
        self.profile_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. Player Profile
        profile_data = self._fetch_data(f"player/{self.username}")
        stats_data = self._fetch_data(f"player/{self.username}/stats")
        clubs_data = self._fetch_data(f"player/{self.username}/clubs")
        archives_data = self._fetch_data(f"player/{self.username}/games/archives")

        if profile_data:
            self._add_header("1. Player Profile", 2)
            self.profile_content.append(f"- Username: {profile_data.get('username', 'N/A')}")
            self.profile_content.append(f"- Name: {profile_data.get('name', 'N/A')}")
            self.profile_content.append(f"- Country: {profile_data.get('country', 'N/A').split('/')[-1]}")
            self.profile_content.append(f"- Followers: {profile_data.get('followers', 'N/A')}")
            if 'last_online' in profile_data:
                last_online = datetime.fromtimestamp(profile_data['last_online']).strftime('%Y-%m-%d %H:%M:%S')
                self.profile_content.append(f"- Last Online: {last_online}")

        if stats_data:
            self._add_header("Detailed Stats", 2)
            for category, stats in stats_data.items():
                if 'last' in stats and 'rating' in stats['last']:
                    self.profile_content.append(f"- {category.replace('chess_', '').replace('_', ' ').title()}:")
                    self.profile_content.append(f"  - Current Rating: {stats['last']['rating']}")
                    self.profile_content.append(f"  - Best Rating: {stats['best']['rating']} ({datetime.fromtimestamp(stats['best']['date']).strftime('%Y-%m-%d')})")
                    self.profile_content.append(f"  - Record: {stats['record']['win']}W / {stats['record']['loss']}L / {stats['record']['draw']}D")
            
            if 'tactics' in stats_data:
                tactics_stats = stats_data['tactics']
                self.profile_content.append("- Tactics:")
                if 'highest' in tactics_stats:
                    self.profile_content.append(f"  - Highest Rating: {tactics_stats['highest']['rating']} ({datetime.fromtimestamp(tactics_stats['highest']['date']).strftime('%Y-%m-%d')})")
                if 'lowest' in tactics_stats:
                     self.profile_content.append(f"  - Lowest Rating: {tactics_stats['lowest']['rating']} ({datetime.fromtimestamp(tactics_stats['lowest']['date']).strftime('%Y-%m-%d')})")

            if 'puzzle_rush' in stats_data and 'best' in stats_data['puzzle_rush']:
                puzzle_rush_stats = stats_data['puzzle_rush']['best']
                self.profile_content.append("- Puzzle Rush:")
                self.profile_content.append(f"  - Best Score: {puzzle_rush_stats.get('score', 'N/A')}")

        # 2. Clubs
        if clubs_data and clubs_data.get('clubs'):
            self._add_header("2. Clubs", 2)
            for club in clubs_data['clubs']:
                self.profile_content.append(f"- {club.get('name', 'N/A')}")

        # 3. Recent Games from Archives
        if archives_data and archives_data.get('archives'):
            self._add_header("3. Recent Games from Archives", 2)
            rapid_games = []
            blitz_games = []
            for archive_url in reversed(archives_data['archives']):
                if len(rapid_games) >= 100 and len(blitz_games) >= 100:
                    break
                games_data = self._fetch_data(archive_url.replace(self.base_url + '/', ''))
                if games_data and games_data.get('games'):
                    for game in reversed(games_data['games']):
                        time_class = game.get('time_class')
                        if time_class == 'rapid' and len(rapid_games) < 100:
                            rapid_games.append(game)
                        elif time_class == 'blitz' and len(blitz_games) < 100:
                            blitz_games.append(game)

            if rapid_games:
                self._add_header("Last 100 Rapid Games (PGN)", 3)
                for game in rapid_games:
                    self.profile_content.append(self._format_game_entry(game))

            if blitz_games:
                self._add_header("Last 100 Blitz Games (PGN)", 3)
                for game in blitz_games:
                    self.profile_content.append(self._format_game_entry(game))

        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.profile_content))
            print(f"Successfully generated Chess.com profile at {self.output_file}")
            return True
        except IOError as e:
            print(f"Error writing to file {self.output_file}: {e}")
            return False