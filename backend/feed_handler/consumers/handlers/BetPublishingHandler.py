from feed_handler.consumers.handlers.AbstractHandler import AbstractHandler
from feed_handler.publishing_bets.BetRuleEngine import bet_rule_engine
from feed_handler.publishing_bets.BetNotifier import bet_notifier
from feed_simulator.events.models import MatchEvent


class BetPublishingHandler(AbstractHandler[MatchEvent]):
    async def complete(self) -> None:
        return None

    async def handle(self, event: MatchEvent):
        opportunity = bet_rule_engine.evaluate(event)
        if opportunity:
            await bet_notifier.notify(opportunity)
