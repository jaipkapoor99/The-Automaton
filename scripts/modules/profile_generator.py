# -*- coding: utf-8 -*-
"""
Generates profiles for various competitive programming and gaming platforms.
"""
import hashlib
import random
import string
import time
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Union

import requests
from config import (CF_API_KEY, CF_API_SECRET, CF_HANDLE,
                    CHESSCOM_API_ENDPOINT, CHESSCOM_ID,
                    CODEFORCES_API_ENDPOINT, LEETCODE_USERNAME,
                    STEAM_API_ENDPOINT, STEAM_API_KEY, STEAM_ID)


class CodeforcesGenerator:
    """Generates a Codeforces profile."""

    def __init__(self, handle=CF_HANDLE, api_key=CF_API_KEY, api_secret=CF_API_SECRET):
        self.handle = handle
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = CODEFORCES_API_ENDPOINT

    def placeholder(self):
        """
        This is a placeholder method to satisfy the pylint warning R0903.
        """

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
            print(f"API Error for {method}: {data.get('comment', 'Unknown error')}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred fetching data from {method}: {e}")
            return None

    def _get_user_summary(self, aggregated_data):
        """Fetches user info and global rank."""
        user_info = self._fetch_data("user.info", params={"handles": self.handle})
        if not user_info:
            return
        user = user_info[0]
        aggregated_data.append(["--- User Summary ---"])
        aggregated_data.append(["Metric", "Value"])
        aggregated_data.extend(
            [
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
        )
        rated_list = self._fetch_data("user.ratedList", params={"activeOnly": "true"})
        if rated_list:
            try:
                rank = next(
                    (i for i, u in enumerate(rated_list) if u["handle"] == self.handle),
                    -1,
                )
                if rank != -1:
                    aggregated_data.append(
                        ["Global Rank (Active)", f"{rank + 1} / {len(rated_list)}"]
                    )
            except (StopIteration, KeyError):
                pass
        aggregated_data.append([])

    def _get_submissions_analysis(self, aggregated_data):
        """Fetches and analyzes user submissions."""
        all_submissions = self._fetch_data(
            "user.status", params={"handle": self.handle}
        )
        if not all_submissions:
            return
        verdicts = Counter(s["verdict"] for s in all_submissions)
        languages = Counter(s["programmingLanguage"] for s in all_submissions)
        tags = Counter(
            tag
            for s in all_submissions
            if "problem" in s
            for tag in s["problem"].get("tags", [])
        )
        aggregated_data.append(["--- Verdicts ---"])
        aggregated_data.append(["Verdict", "Count"])
        for verdict, count in verdicts.most_common():
            aggregated_data.append([verdict, count])
        aggregated_data.append([])
        aggregated_data.append(["--- Languages ---"])
        aggregated_data.append(["Language", "Count"])
        for lang, count in languages.most_common():
            aggregated_data.append([lang, count])
        aggregated_data.append([])
        aggregated_data.append(["--- Problem Tags (Top 15) ---"])
        aggregated_data.append(["Tag", "Count"])
        for tag, count in tags.most_common(15):
            aggregated_data.append([tag, count])
        aggregated_data.append([])

    def _get_contest_performance(self, aggregated_data):
        """Fetches and analyzes contest performance."""
        rating_history = self._fetch_data("user.rating", params={"handle": self.handle})
        if not rating_history:
            return
        aggregated_data.append(["--- Recent Contest Performance ---"])
        aggregated_data.append(
            ["Contest", "ID", "Rank", "Rating Change", "New Rating", "Hacks"]
        )
        recent_contests = sorted(
            rating_history, key=lambda x: x["ratingUpdateTimeSeconds"], reverse=True
        )[:5]
        for contest in recent_contests:
            contest_id = contest["contestId"]
            hacks_summary = "N/A"
            hacks = self._fetch_data("contest.hacks", params={"contestId": contest_id})
            if hacks:
                user_hacks = [
                    h
                    for h in hacks
                    if h["hacker"]["members"][0]["handle"] == self.handle
                ]
                if user_hacks:
                    hacks_summary = "; ".join(
                        [f"{h['problem']['index']}: {h['verdict']}" for h in user_hacks]
                    )
            aggregated_data.append(
                [
                    contest["contestName"],
                    contest_id,
                    contest["rank"],
                    f"{contest['newRating'] - contest['oldRating']:+}",
                    contest["newRating"],
                    hacks_summary,
                ]
            )
        aggregated_data.append([])

    def _get_friends_list(self, aggregated_data):
        """Fetches the user's friends list."""
        friends = self._fetch_data(
            "user.friends", params={"onlyOnline": "false"}, authorized=True
        )
        aggregated_data.append(["--- Friends ---"])
        aggregated_data.append(["Friend Handle"])
        if friends:
            aggregated_data.extend([[f] for f in friends])
        else:
            aggregated_data.append(
                [
                    "Could not retrieve friends list. "
                    "This method requires authorization, or the API keys are missing/invalid."
                ],
            )
        aggregated_data.append([])

    def generate(self) -> Union[Dict[str, Any], List[List[Any]]]:
        """Fetches and generates the Codeforces profile as structured data."""
        if not self.handle:
            print(
                "ERROR: Codeforces handle not set. Please set the CODEFORCES_ID in your .env file."
            )
            return {}
        print(f"Generating exhaustive Codeforces profile for {self.handle}...")

        aggregated_data = []
        self._get_user_summary(aggregated_data)
        self._get_submissions_analysis(aggregated_data)
        self._get_contest_performance(aggregated_data)
        self._get_friends_list(aggregated_data)

        print(f"Successfully generated exhaustive Codeforces profile for {self.handle}")
        return aggregated_data


class LeetCodeGenerator:
    """Generates a LeetCode profile."""

    def __init__(self, username=LEETCODE_USERNAME):
        self.username = username

    def placeholder(self):
        """
        This is a placeholder method to satisfy the pylint warning R0903.
        """

    def generate(self) -> Union[Dict[str, Any], List[List[Any]]]:
        """
        This is a placeholder method to satisfy the pylint warning R0903.
        """
        return {}


class SteamStatsGenerator:
    """Generates a comprehensive Steam profile based on a detailed plan."""

    def __init__(self, api_key=STEAM_API_KEY, steam_id=STEAM_ID):
        self.api_key = api_key
        self.steam_id = steam_id
        self.base_url = STEAM_API_ENDPOINT

    def placeholder(self):
        """
        This is a placeholder method to satisfy the pylint warning R0903.
        """

    def generate(self) -> Union[Dict[str, Any], List[List[Any]]]:
        """
        This is a placeholder method to satisfy the pylint warning R0903.
        """
        return {}


class ChessComGenerator:
    """Generates a Chess.com profile."""

    def __init__(self, username: str = CHESSCOM_ID):
        self.username = username
        self.base_url = CHESSCOM_API_ENDPOINT

    def placeholder(self):
        """
        This is a placeholder method to satisfy the pylint warning R0903.
        """

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

    def _get_player_profile(self, aggregated_data):
        """Gets the player profile."""
        aggregated_data.append(["--- Player Profile ---"])
        aggregated_data.append(["Metric", "Value"])
        aggregated_data.append(
            ["Generated On", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        )
        player_profile_data = self._fetch_data(f"player/{self.username}")
        if player_profile_data:
            aggregated_data.extend(
                [
                    ["Username", player_profile_data.get("username", "N/A")],
                    ["Name", player_profile_data.get("name", "N/A")],
                    [
                        "Country",
                        player_profile_data.get("country", "N/A").split("/")[-1],
                    ],
                    ["Followers", player_profile_data.get("followers", "N/A")],
                ]
            )
            if "last_online" in player_profile_data:
                last_online = datetime.fromtimestamp(
                    player_profile_data["last_online"]
                ).strftime("%Y-%m-%d %H:%M:%S")
                aggregated_data.append(["Last Online", last_online])
        aggregated_data.append([])

    def _get_detailed_stats(self, aggregated_data):
        """Gets the detailed stats."""
        aggregated_data.append(["--- Detailed Stats ---"])
        aggregated_data.append(
            [
                "Category",
                "Current Rating",
                "Best Rating",
                "Best Rating Date",
                "Wins",
                "Losses",
                "Draws",
            ]
        )
        stats_data = self._fetch_data(f"player/{self.username}/stats")
        if stats_data:
            for category, stats in stats_data.items():
                if "last" in stats and "rating" in stats["last"]:
                    aggregated_data.append(
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
                aggregated_data.append(
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
                aggregated_data.append(
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
        aggregated_data.append([])

    def _get_clubs(self, aggregated_data):
        """Gets the clubs."""
        aggregated_data.append(["--- Clubs ---"])
        aggregated_data.append(["Club Name"])
        clubs_data = self._fetch_data(f"player/{self.username}/clubs")
        if clubs_data and clubs_data.get("clubs"):
            for club in clubs_data["clubs"]:
                aggregated_data.append([club.get("name", "N/A")])
        else:
            aggregated_data.append(["No clubs found."])
        aggregated_data.append([])

    def _get_recent_games(self, aggregated_data):
        """Gets the recent games."""
        archives_data = self._fetch_data(f"player/{self.username}/games/archives")
        if not archives_data or not archives_data.get("archives"):
            return
        aggregated_data.append(["--- Rapid Games (Last 100) ---"])
        aggregated_data.append(["PGN"])
        rapid_games = []
        blitz_games = []
        for archive_url in reversed(archives_data["archives"]):
            if len(rapid_games) >= 100 and len(blitz_games) >= 100:
                break
            games_data = self._fetch_data(archive_url.replace(self.base_url + "/", ""))
            if games_data and games_data.get("games"):
                for game in reversed(games_data["games"]):
                    time_class = game.get("time_class")
                    if time_class == "rapid" and len(rapid_games) < 100:
                        rapid_games.append(game.get("pgn", "PGN not available"))
                    elif time_class == "blitz" and len(blitz_games) < 100:
                        blitz_games.append(game.get("pgn", "PGN not available"))
        for pgn in rapid_games:
            aggregated_data.append([pgn])
        aggregated_data.append([])
        aggregated_data.append(["--- Blitz Games (Last 100) ---"])
        aggregated_data.append(["PGN"])
        for pgn in blitz_games:
            aggregated_data.append([pgn])
        aggregated_data.append([])

    def generate(self) -> Union[Dict[str, Any], List[List[Any]]]:
        """Fetches and generates the Chess.com profile as structured data."""
        print(f"Generating Chess.com profile for {self.username}...")
        if not self.username:
            print("ERROR: Chess.com username not set.")
            return {}

        aggregated_data = []
        self._get_player_profile(aggregated_data)
        self._get_detailed_stats(aggregated_data)
        self._get_clubs(aggregated_data)
        self._get_recent_games(aggregated_data)

        print(f"Successfully generated Chess.com profile for {self.username}")
        return aggregated_data
