from api.components.bets.settlement_notifier import bet_settlement_notifier
from api.components.communication.ConnectionManager import (
    ConnectionManager,
    connection_manager,
)
from feed_handler.publishing_bets.BetOpportunity import BetOpportunity
from feed_handler.publishing_bets.BetOpportunityStore import bet_opportunity_store


class BetNotifier:
    def __init__(self, connection_manager: ConnectionManager) -> None:
        self._connection_manager = connection_manager

    async def notify(self, opportunity: BetOpportunity) -> None:
        bet_opportunity_store.save(opportunity)
        payload = {
            "type": "bet_opportunity",
            "opportunity": opportunity.model_dump(mode="json"),
        }
        # Deliver via chat-room sockets (users who have the chat overlay open)
        await self._connection_manager.broadcast_all(payload)
        # Deliver via bet-settlement sockets (every user on the match screen)
        await bet_settlement_notifier.notify_all_connected(payload)


bet_notifier = BetNotifier(connection_manager=connection_manager)
