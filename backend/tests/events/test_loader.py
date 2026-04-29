import pytest
import events.loader as loader_mod
from events.loader import iter_events
from events.models import KickOff, GameSection, Play, Pass

TEST_XML = "./data/test.xml"


def test_total_event_count():
    all_events = [e for chunk in iter_events(TEST_XML) for e in chunk]
    assert len(all_events) == 10


def test_chunk_size_respected():
    original = loader_mod.CHUNK_SIZE
    loader_mod.CHUNK_SIZE = 3
    try:
        for chunk in iter_events(TEST_XML):
            assert len(chunk) <= 3
    finally:
        loader_mod.CHUNK_SIZE = original


def test_chunk_count():
    original = loader_mod.CHUNK_SIZE
    loader_mod.CHUNK_SIZE = 3
    try:
        chunks = list(iter_events(TEST_XML))
        assert len(chunks) == 4
    finally:
        loader_mod.CHUNK_SIZE = original


def test_events_within_chunk_are_sorted():
    original = loader_mod.CHUNK_SIZE
    loader_mod.CHUNK_SIZE = 3
    try:
        for chunk in iter_events(TEST_XML):
            times = [e.event_time for e in chunk]
            assert times == sorted(times)
    finally:
        loader_mod.CHUNK_SIZE = original


def test_single_chunk_when_all_fit():
    original = loader_mod.CHUNK_SIZE
    loader_mod.CHUNK_SIZE = 100
    try:
        chunks = list(iter_events(TEST_XML))
        assert len(chunks) == 1
        assert len(chunks[0]) == 10
    finally:
        loader_mod.CHUNK_SIZE = original


def test_nested_subelements():
    all_events = [e for chunk in iter_events(TEST_XML) for e in chunk]

    kickoff_event = next(e for e in all_events if e.event_type == "KickOff")
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
