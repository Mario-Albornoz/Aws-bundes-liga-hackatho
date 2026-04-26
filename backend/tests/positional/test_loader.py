import pytest
from positional.loader import load_positional
from positional.models import PositionalFrame


TEST_XML = "./data/test_positional.xml"

def test_returns_list_of_positional_frames():
    frames = load_positional(TEST_XML)
    assert isinstance(frames, list)
    assert all(isinstance(f, PositionalFrame) for f in frames)
    assert len(frames) == 3
 
def test_frame_n_values():
    frames = load_positional(TEST_XML)
    assert [f.frame_n for f in frames] == ["10001", "10002", "10003"]

def test_two_players_per_frame():
    frames = load_positional(TEST_XML)
    for frame in frames:
        assert len(frame.players) == 2
 
def test_ball_present_in_every_frame():
    frames = load_positional(TEST_XML)
    for frame in frames:
        assert frame.ball is not None