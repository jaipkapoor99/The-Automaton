# -*- coding: utf-8 -*-
"""
Generates profiles for various competitive programming and gaming platforms.
"""
import hashlib
import json
import random
import string
import time
from collections import Counter
from datetime import datetime
from typing import Any, Dict

import requests
from googleapiclient.errors import HttpError

from scripts.config import (
    CF_API_KEY,
    CF_API_SECRET,
    CF_HANDLE,
    CHESSCOM_API_ENDPOINT,
    CHESSCOM_ID,
    CODEFORCES_API_ENDPOINT,
    LEETCODE_API_ENDPOINT,
    LEETCODE_USERNAME,
    STEAM_API_ENDPOINT,
    STEAM_API_KEY,
    STEAM_ID,
)
from scripts.modules.google_auth import GoogleAuthenticator


class CodeforcesGenerator:
    """Generates a Codeforces profile."""

    def __init__(self, handle=CF_HANDLE, api_key=CF_API_KEY, api_secret=CF_API_SECRET):
        self.handle = handle
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = CODEFORCES_API_ENDPOINT

    def _generate_api_sig(self, method_name, params):
        """Generates the apiSig parameter for authorized methods."""
        rand_prefix = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=6)
        )

        # Parameters must be sorted alphabetically by key
        sorted_params = sorted(params.items())
        param_str = "&".join([f"{k}={v}" for k, v in sorted_params])

        hash_str = f"{rand_prefix}/{method_name}?{param_str}#{self.api_secret}"

        hasher = hashlib.sha512()
        hasher.update(hash_str.encode("utf-8"))

        return rand_prefix + hasher.hexdigest()

    def _fetch_data(self, method, params=None, authorized=False):
        if params is None:
            params = {}

        url = f"{self.base_url}/{method}"

        if authorized:
            if not self.api_key or not self.api_secret:
                # Fail gracefully if keys are not provided
                return None
            params["apiKey"] = self.api_key
            params["time"] = int(time.time())
            params["apiSig"] = self._generate_api_sig(method, params)

        try:
            response = requests.get(url, params=params, timeout=15)
            time.sleep(1)  # Respect API rate limits
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "OK":
                return data.get("result")
            else:
                print(f"API Error for {method}: {data.get('comment', 'Unknown error')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred fetching data from {method}: {e}")
            return None

    def generate(self):
        """Fetches and generates the Codeforces profile as structured data."""
        if not self.handle:
            print(
                "ERROR: Codeforces handle not set. Please set the CODEFORCES_ID in your .env file."
            )
            return {}
        print(f"Generating exhaustive Codeforces profile for {self.handle}...")

        profile_data = {}

        # User Info and Global Rank
        user_info = self._fetch_data("user.info", params={"handles": self.handle})
        if user_info:
            user = user_info[0]
            user_summary = [
                ["Metric", "Value"],
                ["Handle", user.get("handle", "N/A")],
                ["Rating", f"{user.get('rating', 'N/A')} ({user.get('rank', 'N/A')})"],
                [
                    "Max Rating",
                    f"{user.get('maxRating', 'N/A')} ({user.get('maxRank', 'N/A')})",
                ],
                ["Contribution", user.get("contribution", "N/A")],
                [
                    "Registered",
                    datetime.fromtimestamp(
                        user.get("registrationTimeSeconds", 0)
                    ).strftime("%Y-%m-%d"),
                ],
            ]

            rated_list = self._fetch_data(
                "user.ratedList", params={"activeOnly": "true"}
            )
            if rated_list:
                try:
                    rank = next(
                        (
                            i
                            for i, u in enumerate(rated_list)
                            if u["handle"] == self.handle
                        ),
                        -1,
                    )
                    if rank != -1:
                        user_summary.append(
                            ["Global Rank (Active)", f"{rank + 1} / {len(rated_list)}"]
                        )
                except (StopIteration, KeyError):
                    pass
            profile_data["User Summary"] = user_summary

        # Submissions Analysis (All submissions)
        all_submissions = self._fetch_data(
            "user.status", params={"handle": self.handle}
        )
        if all_submissions:
            verdicts = Counter(s["verdict"] for s in all_submissions)
            languages = Counter(s["programmingLanguage"] for s in all_submissions)
            tags = Counter(
                tag
                for s in all_submissions
                if "problem" in s
                for tag in s["problem"].get("tags", [])
            )

            verdicts_data = [["Verdict", "Count"]]
            for verdict, count in verdicts.most_common():
                verdicts_data.append([verdict, count])
            profile_data["Verdicts"] = verdicts_data

            languages_data = [["Language", "Count"]]
            for lang, count in languages.most_common():
                languages_data.append([lang, count])
            profile_data["Languages"] = languages_data

            tags_data = [["Tag", "Count"]]
            for tag, count in tags.most_common(15):
                tags_data.append([tag, count])
            profile_data["Problem Tags"] = tags_data

        # Contest Performance and Hacks
        rating_history = self._fetch_data("user.rating", params={"handle": self.handle})
        if rating_history:
            recent_contests_data = [
                ["Contest", "ID", "Rank", "Rating Change", "New Rating", "Hacks"]
            ]
            recent_contests = sorted(
                rating_history, key=lambda x: x["ratingUpdateTimeSeconds"], reverse=True
            )[:5]
            for contest in recent_contests:
                contest_id = contest["contestId"]
                hacks_summary = "N/A"
                hacks = self._fetch_data(
                    "contest.hacks", params={"contestId": contest_id}
                )
                if hacks:
                    user_hacks = [
                        h
                        for h in hacks
                        if h["hacker"]["members"][0]["handle"] == self.handle
                    ]
                    if user_hacks:
                        hacks_summary = "; ".join(
                            [
                                f"{h['problem']['index']}: {h['verdict']}"
                                for h in user_hacks
                            ]
                        )

                recent_contests_data.append(
                    [
                        contest["contestName"],
                        contest_id,
                        contest["rank"],
                        f"{contest['newRating'] - contest['oldRating']:+}",
                        contest["newRating"],
                        hacks_summary,
                    ]
                )
            profile_data["Recent Contest Performance"] = recent_contests_data

        # Friends
        friends = self._fetch_data(
            "user.friends", params={"onlyOnline": "false"}, authorized=True
        )
        if friends:
            profile_data["Friends"] = [["Friend Handle"]] + [[f] for f in friends]
        else:
            profile_data["Friends"] = [
                ["Friend Handle"],
                [
                    "Could not retrieve friends list. This method requires authorization, or the API keys are missing/invalid."
                ],
            ]

        # Problem Submission History
        if all_submissions:
            submissions_by_problem = {}
            for submission in all_submissions:
                problem = submission["problem"]
                problem_key = (
                    f"{problem.get('contestId', '')}-{problem.get('index', '')}"
                )
                if problem_key not in submissions_by_problem:
                    submissions_by_problem[problem_key] = {
                        "name": problem.get("name", "N/A"),
                        "tags": problem.get("tags", []),
                        "submissions": [],
                    }
                submissions_by_problem[problem_key]["submissions"].append(submission)

            if submissions_by_problem:
                problem_history_data = [
                    [
                        "Problem Name",
                        "Tags",
                        "Submission Time",
                        "Verdict",
                        "Language",
                        "Time (ms)",
                        "Memory (KB)",
                    ]
                ]

                def sort_key(item):
                    contest_id_str = item[0].split("-")[0]
                    problem_index = item[0].split("-")[1]
                    contest_id = (
                        int(contest_id_str)
                        if contest_id_str.isdigit()
                        else float("inf")
                    )
                    return (contest_id, problem_index)

                sorted_problems = sorted(submissions_by_problem.items(), key=sort_key)

                for _, problem_data in sorted_problems:
                    tags_str = ", ".join(problem_data["tags"])
                    sorted_submissions = sorted(
                        problem_data["submissions"],
                        key=lambda s: s["creationTimeSeconds"],
                    )

                    for sub in sorted_submissions:
                        submission_time = datetime.fromtimestamp(
                            sub.get("creationTimeSeconds", 0)
                        ).strftime("%Y-%m-%d %H:%M:%S")
                        problem_history_data.append(
                            [
                                problem_data["name"],
                                tags_str,
                                submission_time,
                                sub.get("verdict", "N/A"),
                                sub.get("programmingLanguage", "N/A"),
                                sub.get("timeConsumedMillis", "N/A"),
                                f"{sub.get('memoryConsumedBytes', 0) / 1024:.2f}",
                            ]
                        )
                profile_data["Problem Submission History"] = problem_history_data

        print(f"Successfully generated exhaustive Codeforces profile for {self.handle}")
        return {f"Codeforces - {k}": v for k, v in profile_data.items()}


class LeetCodeGenerator:
    """Generates a LeetCode profile."""

    def __init__(self, username=LEETCODE_USERNAME):
        self.username = username

    def _fetch_graphql_data(self, query, variables):
        try:
            response = requests.post(
                LEETCODE_API_ENDPOINT,
                json={"query": query, "variables": variables},
                timeout=15,
            )
            time.sleep(1)
            response.raise_for_status()
            return response.json().get("data")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred fetching data: {e}")
            return None
        except json.JSONDecodeError:
            print(
                f"Error decoding LeetCode API response (status {response.status_code})"
            )
            return None

    def generate(self):
        """Fetches and generates the LeetCode profile as structured data."""
        if not self.username:
            print("ERROR: LeetCode username not set.")
            return {}
        print(f"Generating exhaustive LeetCode profile for {self.username}...")

        profile_data = {}

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

        if data and data.get("matchedUser"):
            user = data["matchedUser"]

            # User Summary
            user_summary = [
                ["Metric", "Value"],
                ["Username", user.get("username", "N/A")],
                ["Real Name", user.get("profile", {}).get("realName", "N/A")],
                ["Global Ranking", user.get("profile", {}).get("ranking", "N/A")],
                [
                    "Contribution Points",
                    user.get("contributions", {}).get("points", "N/A"),
                ],
                ["Generated On", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ]
            profile_data["User Summary"] = user_summary

            # Problem Stats
            problem_stats = [["Difficulty", "Solved", "Submissions"]]
            stats = user.get("submitStats", {}).get("acSubmissionNum", [])
            total_solved = sum(s["count"] for s in stats)
            problem_stats.append(["Total Solved", total_solved, "N/A"])
            for s in stats:
                problem_stats.append([s["difficulty"], s["count"], s["submissions"]])
            profile_data["Problem Stats"] = problem_stats

            # Submission Calendar
            submission_calendar_data = [["Metric", "Value"]]
            try:
                calendar_data = json.loads(user.get("submissionCalendar", "{}"))
                total_active_days = sum(
                    1 for count in calendar_data.values() if int(count) > 0
                )
                submission_calendar_data.append(
                    ["Total Active Days", total_active_days]
                )
                # Add more detailed calendar parsing here if needed
            except (json.JSONDecodeError, TypeError):
                submission_calendar_data.append(["Calendar Data", "Not available."])
            profile_data["Submission Calendar"] = submission_calendar_data

        return {f"LeetCode - {k}": v for k, v in profile_data.items()}


class SteamStatsGenerator:
    """Generates a comprehensive Steam profile based on a detailed plan."""

    def __init__(self, api_key=STEAM_API_KEY, steam_id=STEAM_ID):
        self.api_key = api_key
        self.steam_id = steam_id
        self.base_url = STEAM_API_ENDPOINT

    def _make_api_call(self, interface, method, version, params=None):
        """Makes a call to the Steam Web API."""
        if not self.api_key:
            print("API Error: Steam API Key is missing.")
            return None

        url = f"{self.base_url}/{interface}/{method}/v{version}/"

        base_params = {"key": self.api_key, "steamid": self.steam_id, "format": "json"}
        if params:
            base_params.update(params)

        try:
            response = requests.get(url, params=base_params, timeout=30)
            time.sleep(0.5)  # Rate limiting
            if response.status_code == 403:
                print(
                    "API Error: Access Denied (403). Profile may be private or API key invalid."
                )
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred fetching data from Steam API: {e}")
            return None

    def _get_player_summaries(self):
        return self._make_api_call(
            "ISteamUser", "GetPlayerSummaries", 2, {"steamids": self.steam_id}
        )

    def _get_owned_games(self):
        return self._make_api_call(
            "IPlayerService",
            "GetOwnedGames",
            1,
            {"include_appinfo": True, "include_played_free_games": True},
        )

    def _get_player_achievements(self, app_id):
        return self._make_api_call(
            "ISteamUserStats", "GetPlayerAchievements", 1, {"appid": app_id}
        )

    def _get_user_stats_for_game(self, app_id):
        return self._make_api_call(
            "ISteamUserStats", "GetUserStatsForGame", 2, {"appid": app_id}
        )

    def _get_player_level(self):
        return self._make_api_call("IPlayerService", "GetSteamLevel", 1)

    def _get_player_badges(self):
        return self._make_api_call("IPlayerService", "GetBadges", 1)

    def _get_community_badge_progress(self):
        return self._make_api_call("IPlayerService", "GetCommunityBadgeProgress", 1)

    def generate(self):
        """Fetches and generates the Steam profile as structured data."""
        if not self.api_key or not self.steam_id:
            print("ERROR: Steam API Key or Steam ID not set.")
            return {}
        print(f"Generating Steam profile for Steam ID: {self.steam_id}...")

        profile_data = {}

        # Profile Summary
        summary_sheet = [["Metric", "Value"]]
        summary_sheet.append(
            ["Generated On", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        )

        player_summary = self._get_player_summaries()
        if player_summary and player_summary.get("response", {}).get("players"):
            player = player_summary["response"]["players"][0]
            summary_sheet.append(["Username", player.get("personaname", "N/A")])
        else:
            summary_sheet.append(["Username", "Could not fetch."])

        level_data = self._get_player_level()
        if level_data and level_data.get("response"):
            summary_sheet.append(
                ["Steam Level", level_data["response"].get("player_level", "N/A")]
            )

        badges_data = self._get_player_badges()
        if badges_data and badges_data.get("response"):
            summary_sheet.append(
                ["Total Badges", len(badges_data["response"].get("badges", []))]
            )
            summary_sheet.append(
                ["Total XP", badges_data["response"].get("player_xp", "N/A")]
            )

        badge_progress = self._get_community_badge_progress()
        if badge_progress and badge_progress.get("response", {}).get("quests"):
            completed_quests = sum(
                1 for q in badge_progress["response"]["quests"] if q.get("completed")
            )
            summary_sheet.append(
                [
                    "Community Quests Completed",
                    f"{completed_quests}/{len(badge_progress['response']['quests'])}",
                ]
            )
        profile_data["Profile Summary"] = summary_sheet

        # Game Library Analysis
        game_library_sheet = [
            [
                "Game Name",
                "Playtime (hours)",
                "Achievements (Achieved/Total)",
                "Custom Stats",
            ]
        ]
        owned_games = self._get_owned_games()
        if owned_games and owned_games.get("response", {}).get("games"):
            games = sorted(
                owned_games["response"]["games"],
                key=lambda x: x.get("playtime_forever", 0),
                reverse=True,
            )

            for game in games:
                appid = game.get("appid")
                playtime_hours = game.get("playtime_forever", 0) / 60

                achievements_summary = "N/A"
                achievements = self._get_player_achievements(appid)
                if (
                    achievements
                    and achievements.get("playerstats", {}).get("success")
                    and "achievements" in achievements["playerstats"]
                ):
                    achieved = [
                        a
                        for a in achievements["playerstats"]["achievements"]
                        if a.get("achieved")
                    ]
                    total = len(achievements["playerstats"]["achievements"])
                    achievements_summary = f"{len(achieved)} / {total}"

                user_stats_summary = "N/A"
                user_stats = self._get_user_stats_for_game(appid)
                if (
                    user_stats
                    and user_stats.get("playerstats", {}).get("success")
                    and "stats" in user_stats["playerstats"]
                ):
                    user_stats_summary = "; ".join(
                        [
                            f"{stat.get('name', 'N/A')}: {stat.get('value', 'N/A')}"
                            for stat in user_stats["playerstats"]["stats"]
                        ]
                    )

                game_library_sheet.append(
                    [
                        game.get("name", "Unknown Game"),
                        f"{playtime_hours:.2f}",
                        achievements_summary,
                        user_stats_summary,
                    ]
                )
        else:
            game_library_sheet.append(
                ["Could not retrieve game library. Profile may be private.", "", "", ""]
            )
        profile_data["Game Library"] = game_library_sheet

        return {f"Steam - {k}": v for k, v in profile_data.items()}


class YouTubeGenerator:
    """Generates a YouTube profile."""

    def __init__(self):
        self.youtube_service = GoogleAuthenticator().get_user_service("youtube", "v3")

    def _get_channel_stats(self):
        if not self.youtube_service:
            return None
        try:
            request = self.youtube_service.channels().list(
                part="snippet,contentDetails,statistics", mine=True
            )
            response = request.execute()
            return response.get("items", [{}])[0]
        except HttpError as err:
            print(f"YouTube API HttpError: {err.resp.status} - {err.content}")
            return None
        except Exception as e:
            print(f"Error fetching YouTube channel stats: {e}")
            return None

    def _get_playlists(self):
        if not self.youtube_service:
            return []
        playlists = []
        request = self.youtube_service.playlists().list(
            part="snippet,contentDetails", mine=True, maxResults=50
        )
        while request:
            response = request.execute()
            playlists.extend(response.get("items", []))
            request = self.youtube_service.playlists().list_next(request, response)
        return playlists

    def _get_playlist_videos(self, playlist_id):
        if not self.youtube_service:
            return []
        videos = []
        request = self.youtube_service.playlistItems().list(
            part="snippet,contentDetails", playlistId=playlist_id, maxResults=50
        )
        while request and len(videos) < 500:
            response = request.execute()
            videos.extend(response.get("items", []))
            request = self.youtube_service.playlistItems().list_next(request, response)
        return videos

    def _get_video_stats(self, video_id):
        if not self.youtube_service:
            return None
        request = self.youtube_service.videos().list(part="statistics", id=video_id)
        response = request.execute()
        return response.get("items", [{}])[0].get("statistics", {})

    def _get_special_playlist(self, playlist_id, limit=500):
        if not self.youtube_service:
            return []
        videos = []
        try:
            request = self.youtube_service.playlistItems().list(
                part="snippet", playlistId=playlist_id, maxResults=50
            )
            while request and len(videos) < limit:
                response = request.execute()
                videos.extend(response.get("items", []))
                request = self.youtube_service.playlistItems().list_next(
                    request, response
                )
        except Exception as e:
            print(
                f"Could not fetch playlist {playlist_id}. It might be private or disabled. Error: {e}"
            )
            return []
        return videos

    def _get_subscriptions(self):
        if not self.youtube_service:
            return []
        subscriptions = []
        request = self.youtube_service.subscriptions().list(
            part="snippet", mine=True, maxResults=50
        )
        while request:
            response = request.execute()
            subscriptions.extend(response.get("items", []))
            request = self.youtube_service.subscriptions().list_next(request, response)
        return subscriptions

    def generate(self):
        """Fetches and generates the YouTube profile as structured data."""
        print(f"Generating YouTube profile...")

        profile_data = {}
        channel_data = self._get_channel_stats()
        if not channel_data:
            print("Could not fetch channel data.")
            return {}

        stats = channel_data.get("statistics", {})
        snippet = channel_data.get("snippet", {})

        # Channel Summary
        channel_summary_sheet = [
            ["Metric", "Value"],
            ["Channel Name", snippet.get("title", "N/A")],
            ["Generated On", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Subscribers", stats.get("subscriberCount", "N/A")],
            ["Total Views", stats.get("viewCount", "N/A")],
            ["Total Videos", stats.get("videoCount", "N/A")],
            ["Published At", snippet.get("publishedAt", "N/A")],
        ]
        profile_data["Channel Summary"] = channel_summary_sheet

        # Playlists
        playlists_sheet = [
            ["Playlist Title", "Video Title", "Views", "Likes", "Comments"]
        ]
        playlists = self._get_playlists()
        if playlists:
            for playlist in playlists:
                playlist_snippet = playlist.get("snippet", {})
                playlist_title = playlist_snippet.get("title", "N/A")
                videos = self._get_playlist_videos(playlist.get("id"))
                if videos:
                    for video in videos:
                        video_snippet = video.get("snippet", {})
                        video_stats = self._get_video_stats(
                            video_snippet.get("resourceId", {}).get("videoId")
                        )
                        playlists_sheet.append(
                            [
                                playlist_title,
                                video_snippet.get("title", "N/A"),
                                video_stats.get("viewCount", "N/A"),
                                video_stats.get("likeCount", "N/A"),
                                video_stats.get("commentCount", "N/A"),
                            ]
                        )
                else:
                    playlists_sheet.append(
                        [playlist_title, "No videos found.", "", "", ""]
                    )
        else:
            playlists_sheet.append(["No playlists found.", "", "", "", ""])
        profile_data["Playlists"] = playlists_sheet

        # Liked Videos
        liked_videos_sheet = [["Video Title", "Channel Name"]]
        liked_videos = self._get_special_playlist("LL")
        if liked_videos:
            for item in liked_videos:
                snippet = item.get("snippet", {})
                liked_videos_sheet.append(
                    [
                        snippet.get("title", "N/A"),
                        snippet.get("videoOwnerChannelTitle", "N/A"),
                    ]
                )
        else:
            liked_videos_sheet.append(["No liked videos found.", ""])
        profile_data["Liked Videos"] = liked_videos_sheet

        # Watch History
        watch_history_sheet = [["Video Title", "Channel Name"]]
        watch_history = self._get_special_playlist("HL")
        if watch_history:
            for item in watch_history:
                snippet = item.get("snippet", {})
                watch_history_sheet.append(
                    [
                        snippet.get("title", "N/A"),
                        snippet.get("videoOwnerChannelTitle", "N/A"),
                    ]
                )
        else:
            watch_history_sheet.append(["No watch history found.", ""])
        profile_data["Watch History"] = watch_history_sheet

        # Subscriptions
        subscriptions_sheet = [["Channel Name"]]
        subscriptions = self._get_subscriptions()
        if subscriptions:
            for item in subscriptions:
                snippet = item.get("snippet", {})
                subscriptions_sheet.append([snippet.get("title", "N/A")])
        else:
            subscriptions_sheet.append(["No subscriptions found."])
        profile_data["Subscriptions"] = subscriptions_sheet

        return {f"YouTube - {k}": v for k, v in profile_data.items()}


class ChessComGenerator:
    """Generates a Chess.com profile."""

    def __init__(self, username: str = CHESSCOM_ID):
        self.username = username
        self.base_url = CHESSCOM_API_ENDPOINT

    def _fetch_data(self, endpoint: str) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        headers = {"User-Agent": "The-Automaton"}
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred fetching data from {endpoint}: {e}")
            return {}

    def generate(self) -> Dict[str, Any]:
        """Fetches and generates the Chess.com profile as structured data."""
        print(f"Generating Chess.com profile for {self.username}...")
        if not self.username:
            print("ERROR: Chess.com username not set.")
            return {}

        profile_data = {}

        # Player Profile
        profile_summary_sheet = [["Metric", "Value"]]
        profile_summary_sheet.append(
            ["Generated On", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        )

        player_profile_data = self._fetch_data(f"player/{self.username}")
        if player_profile_data:
            profile_summary_sheet.append(
                ["Username", player_profile_data.get("username", "N/A")]
            )
            profile_summary_sheet.append(
                ["Name", player_profile_data.get("name", "N/A")]
            )
            profile_summary_sheet.append(
                ["Country", player_profile_data.get("country", "N/A").split("/")[-1]]
            )
            profile_summary_sheet.append(
                ["Followers", player_profile_data.get("followers", "N/A")]
            )
            if "last_online" in player_profile_data:
                last_online = datetime.fromtimestamp(
                    player_profile_data["last_online"]
                ).strftime("%Y-%m-%d %H:%M:%S")
                profile_summary_sheet.append(["Last Online", last_online])
        profile_data["Player Profile"] = profile_summary_sheet

        # Detailed Stats
        stats_sheet = [
            [
                "Category",
                "Current Rating",
                "Best Rating",
                "Best Rating Date",
                "Wins",
                "Losses",
                "Draws",
            ]
        ]
        stats_data = self._fetch_data(f"player/{self.username}/stats")
        if stats_data:
            for category, stats in stats_data.items():
                if "last" in stats and "rating" in stats["last"]:
                    stats_sheet.append(
                        [
                            category.replace("chess_", "").replace("_", " ").title(),
                            stats["last"]["rating"],
                            stats["best"]["rating"],
                            datetime.fromtimestamp(stats["best"]["date"]).strftime(
                                "%Y-%m-%d"
                            ),
                            stats["record"]["win"],
                            stats["record"]["loss"],
                            stats["record"]["draw"],
                        ]
                    )

            if "tactics" in stats_data:
                tactics_stats = stats_data["tactics"]
                highest_tactics = tactics_stats.get("highest", {})
                lowest_tactics = tactics_stats.get("lowest", {})
                stats_sheet.append(
                    [
                        "Tactics",
                        "N/A",
                        highest_tactics.get("rating", "N/A"),
                        (
                            datetime.fromtimestamp(highest_tactics["date"]).strftime(
                                "%Y-%m-%d"
                            )
                            if "date" in highest_tactics
                            else "N/A"
                        ),
                        "N/A",
                        "N/A",
                        "N/A",
                    ]
                )

            if "puzzle_rush" in stats_data and "best" in stats_data["puzzle_rush"]:
                puzzle_rush_stats = stats_data["puzzle_rush"]["best"]
                stats_sheet.append(
                    [
                        "Puzzle Rush",
                        "N/A",
                        puzzle_rush_stats.get("score", "N/A"),
                        "N/A",
                        "N/A",
                        "N/A",
                        "N/A",
                    ]
                )
        profile_data["Detailed Stats"] = stats_sheet

        # Clubs
        clubs_sheet = [["Club Name"]]
        clubs_data = self._fetch_data(f"player/{self.username}/clubs")
        if clubs_data and clubs_data.get("clubs"):
            for club in clubs_data["clubs"]:
                clubs_sheet.append([club.get("name", "N/A")])
        else:
            clubs_sheet.append(["No clubs found."])
        profile_data["Clubs"] = clubs_sheet

        # Recent Games from Archives
        archives_data = self._fetch_data(f"player/{self.username}/games/archives")
        if archives_data and archives_data.get("archives"):
            rapid_games_sheet = [["PGN"]]
            blitz_games_sheet = [["PGN"]]
            rapid_games = []
            blitz_games = []
            for archive_url in reversed(archives_data["archives"]):
                if len(rapid_games) >= 100 and len(blitz_games) >= 100:
                    break
                games_data = self._fetch_data(
                    archive_url.replace(self.base_url + "/", "")
                )
                if games_data and games_data.get("games"):
                    for game in reversed(games_data["games"]):
                        time_class = game.get("time_class")
                        if time_class == "rapid" and len(rapid_games) < 100:
                            rapid_games.append(game.get("pgn", "PGN not available"))
                        elif time_class == "blitz" and len(blitz_games) < 100:
                            blitz_games.append(game.get("pgn", "PGN not available"))

            for pgn in rapid_games:
                rapid_games_sheet.append([pgn])
            profile_data["Rapid Games"] = rapid_games_sheet

            for pgn in blitz_games:
                blitz_games_sheet.append([pgn])
            profile_data["Blitz Games"] = blitz_games_sheet

        print(f"Successfully generated Chess.com profile for {self.username}")
        return {f"Chess.com - {k}": v for k, v in profile_data.items()}
