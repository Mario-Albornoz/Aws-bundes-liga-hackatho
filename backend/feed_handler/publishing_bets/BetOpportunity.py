import uuid
from datetime import datetime, timedelta, timezone

from pydantic import BaseModel


class BetOpportunity(BaseModel):
    bet_type: str
    trigger_event_id: str
    window_seconds: int
    context: dict
    expires_at: datetime = None
    bet_id: uuid.UUID = uuid.uuid4()

    def model_post_init(self, __context) -> None:
        if self.expires_at is None:
            self.expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=self.window_seconds
            )
