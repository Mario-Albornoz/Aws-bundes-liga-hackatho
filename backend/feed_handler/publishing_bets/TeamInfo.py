"""
Display-name mapping for the anonymised club IDs used in the demo dataset.
Used when building BetOpportunity context so the frontend can show human-
readable names without needing a separate API call.
"""

import os

_MATCH_ID: str = os.getenv("MATCH_ID", "DFL-MAT-111111")

# Anonymised → display name (Bundesliga demo dataset)
TEAM_DISPLAY_NAMES: dict[str, str] = {
    "DFL-CLU-000001": "Hamburg",
    "DFL-CLU-000002": "Bayern",
}


def get_team_name(team_id: str) -> str:
    """Return a human-readable club name, falling back to the ID suffix."""
    return TEAM_DISPLAY_NAMES.get(team_id, team_id.split("-")[-1])


def match_result_context(team_left: str, team_right: str) -> dict:
    """Build the standard match-result opportunity context dict."""
    return {
        "team_left": team_left,
        "team_right": team_right,
        "team_left_name": get_team_name(team_left),
        "team_right_name": get_team_name(team_right),
    }
