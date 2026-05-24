"""
In-memory store for active BetOpportunity objects.

Used so that late-connecting clients can receive the current open
opportunity immediately upon joining a chat room, without waiting
for the next feed event to re-broadcast it.
"""

from datetime import datetime, timezone

from feed_handler.publishing_bets.BetOpportunity import BetOpportunity


class BetOpportunityStore:
    def __init__(self) -> None:
        # Keyed by bet_type so there is at most one active opportunity per type
        self._store: dict[str, BetOpportunity] = {}

    def save(self, opportunity: BetOpportunity) -> None:
        self._store[opportunity.bet_type] = opportunity

    def get_active(self) -> list[BetOpportunity]:
        now = datetime.now(timezone.utc)
        return [o for o in self._store.values() if o.expires_at > now]

    def clear(self, bet_type: str) -> None:
        self._store.pop(bet_type, None)


bet_opportunity_store = BetOpportunityStore()
