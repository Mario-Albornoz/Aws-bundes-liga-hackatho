from typing import Callable, Optional

from feed_handler.consumers.handlers.dto.BetTypes import BetTypes
from feed_handler.publishing_bets.BetOpportunity import BetOpportunity
from feed_simulator.events.models import MatchEvent, Substitution

RuleFunc = Callable[[MatchEvent], BetOpportunity]


class BetRuleEngine:
    def __init__(self):
        self._rules: dict[str, RuleFunc] = {
            "Substitution": self._rule_substitution,
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
            context={
                "player_on": sub.player_in,
                "team": sub.team,
            },
        )


bet_rule_engine = BetRuleEngine()
