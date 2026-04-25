import pytest
 
from events.loader import load_events
from events.models import KickOff, GameSection, Play, Pass

TEST_XML = "./data/test.xml"

def test_load_count():
    events = load_events(TEST_XML)
    assert len(events) == 10

def test_load_with_nested_subelements():
    events = load_events(TEST_XML)
    
    kickoff_event = next(e for e in events if e.event_type == "KickOff")
    assert isinstance(kickoff_event.subelement, KickOff)
    
    kickoff = kickoff_event.subelement
    assert kickoff.team_left == "DFL-CLU-000002"
    assert kickoff.team_right == "DFL-CLU-000001"
    assert kickoff.game_section == GameSection.firstHalf

    assert isinstance(kickoff.subelement, Play)
    play = kickoff.subelement
    assert play.team == "DFL-CLU-000002"
    assert play.player == "DFL-OBJ-000029"
    assert play.recipient == "DFL-OBJ-000025"
    assert play.from_open_play is False
    assert play.ball_possession_phase == 6

    assert isinstance(play.subelement, Pass)
    assert play.subelement.free_kick_layup is False

def test_load_returns_sorted_events():
    events = load_events(TEST_XML)
    times = [e.event_time for e in events]
    assert times == sorted(times)

