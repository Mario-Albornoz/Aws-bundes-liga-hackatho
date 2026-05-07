from pydantic import BaseModel
from datetime import datetime, timezone, timedelta


class BetOpportunity(BaseModel):
    bet_type: str
    trigger_event_id: str
    window_seconds: int
    context: dict
    expires_at: datetime = None

    def model_post_init(self, __context) -> None:
        if self.expires_at is None:
            self.expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=self.window_seconds
            )
