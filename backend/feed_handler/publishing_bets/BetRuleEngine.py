from typing import Callable, Optional

from feed_handler.consumers.handlers.dto.BetTypes import BetTypes
from feed_handler.publishing_bets.BetOpportunity import BetOpportunity
from feed_handler.publishing_bets.TeamInfo import match_result_context
from feed_simulator.events.models import GameSection, KickOff, MatchEvent, Substitution

RuleFunc = Callable[[MatchEvent], BetOpportunity]


class BetRuleEngine:
    def __init__(self):
        self._rules: dict[str, RuleFunc] = {
            "Substitution": self._rule_substitution,
            "KickOff": self._rule_match_result,
        }

    def evaluate(self, event: MatchEvent) -> Optional[BetOpportunity]:
        rule = self._rules.get(event.event_type)
        if rule is None:
            return None
        return rule(event)

    def _rule_substitution(self, event: MatchEvent) -> Optional[BetOpportunity]:
        sub = Substitution.model_validate(event.subelement)
        return BetOpportunity(
            bet_type=BetTypes.SUBSTITUTION.value,
            trigger_event_id=event.event_id,
            window_seconds=120,
            match_id=event.match_id,
            context={
                "player_on": sub.player_in,
                "team": sub.team,
            },
        )

    def _rule_match_result(self, event: MatchEvent) -> Optional[BetOpportunity]:
        kickoff = KickOff.model_validate(event.subelement)
        # Only publish an opportunity on the opening kick-off of the match
        if kickoff.game_section != GameSection.firstHalf:
            return None
        return BetOpportunity(
            bet_type=BetTypes.MATCH_RESULT.value,
            trigger_event_id=event.event_id,
            window_seconds=5400,  # 90 minutes
            match_id=event.match_id,
            context=match_result_context(kickoff.team_left, kickoff.team_right),
        )


bet_rule_engine = BetRuleEngine()
