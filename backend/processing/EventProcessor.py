from feed_simulator.events.models import MatchEvent


class EventHandler:
    def __init__(self) -> None:
        self.active_bets: dict = {}
        pass

    def register_bet(self, bet_id: str) -> None:

        pass

    async def process_event(self, event: MatchEvent):

        bet = self.active_bets.get(event)

    # take event -> handle it storage quick access
    # if event affects bets -> query storage and update the state of the bet
