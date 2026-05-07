from api.components.communication.ConnectionManager import ConnectionManager
from api.components.communication.ConnectionManager import connection_manager
from feed_handler.publishing_bets.BetOpportunity import BetOpportunity


class BetNotifier:
    def __init__(self, connection_manager: ConnectionManager) -> None:
        self._connection_manager = connection_manager

    async def notify(self, opportunity: BetOpportunity) -> None:
        await self._connection_manager.broadcast_all(
            {
                "type": "bet_opportunity",
                "opportunity": opportunity.model_dump(mode="json"),
            }
        )


bet_notifier = BetNotifier(connection_manager=connection_manager)
