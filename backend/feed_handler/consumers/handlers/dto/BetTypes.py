from enum import Enum


class BetTypes(str, Enum):
    SUBSTITUTION = "substitution"
    MATCH_RESULT = "match_result"
