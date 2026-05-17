from fastapi import FastAPI
from starlette.testclient import TestClient

from api.components.bets.router import router as bets_router


def test_create_bet_endpoint():
    app = FastAPI()
    app.include_router(bets_router)
    body = {
        "bet_info": {
            "bet_id": "api-test-1",
            "bet_type": "substitution",
            "duration": 90,
            "match_id": 1,
            "bet_specs": {"player_id": "p1", "trigger_event_type": "Substitution"},
        },
        "bet_subscription": {
            "participant": {"user_id": 1, "bet_amount": 5, "position": True},
        },
    }
    with TestClient(app) as client:
        r = client.post("/bets/create", json=body)
        assert r.status_code == 200
        data = r.json()
        assert data["bet_info"]["bet_id"] == "api-test-1"
        assert data["bet_status"] == "PENDING"
        assert len(data["participants"]) == 1
