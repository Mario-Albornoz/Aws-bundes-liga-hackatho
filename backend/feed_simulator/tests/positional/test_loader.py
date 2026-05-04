import pytest
from feed_simulator.positional.loader import load_positional_to_db, iter_frame_ns, get_frame
from feed_simulator.positional.models import PositionalFrame

TEST_XML = "./data/test_positional.xml"


def test_returns_correct_frame_ns():
    conn = load_positional_to_db(TEST_XML)
    assert list(iter_frame_ns(conn)) == [10001, 10002, 10003, 100001, 100002, 100003, 100004]


def test_get_frame_returns_positional_frame():
    conn = load_positional_to_db(TEST_XML)
    frame = get_frame(conn, 10001)
    assert isinstance(frame, PositionalFrame)
    assert frame.frame_n == "10001"


def test_two_persons_per_frame():
    conn = load_positional_to_db(TEST_XML)
    for n in iter_frame_ns(conn):
        frame = get_frame(conn, n)
        assert len(frame.persons) == 2


def test_ball_present_in_every_frame():
    conn = load_positional_to_db(TEST_XML)
    for n in iter_frame_ns(conn):
        frame = get_frame(conn, n)
        assert frame.ball is not None
