import sqlite3
import os
from lxml import etree
from typing import Iterator
from positional.models import PositionalFrame, PersonFrame, BallFrame
from datetime import datetime


def _to_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _create_tables(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE person_frames (
            frame_n      INTEGER,
            game_section TEXT,
            match_id     TEXT,
            timestamp    TEXT,
            person_id    TEXT,
            team_id      TEXT,
            x            REAL,
            y            REAL,
            speed        REAL,
            distance     REAL,
            acceleration REAL
        )
    """)
    conn.execute("""
        CREATE TABLE ball_frames (
            frame_n      INTEGER,
            game_section TEXT,
            match_id     TEXT,
            timestamp    TEXT,
            x            REAL,
            y            REAL,
            z            REAL,
            speed        REAL,
            distance     REAL,
            acceleration REAL,
            status       TEXT,
            possession   TEXT
        )
    """)
    conn.execute("CREATE INDEX idx_person_frame_n ON person_frames (frame_n)")
    conn.execute("CREATE INDEX idx_ball_frame_n ON ball_frames (frame_n)")
    conn.commit()


def _ingest(conn: sqlite3.Connection, path: str) -> None:
    for _, el in etree.iterparse(path, events=("end",), tag="FrameSet"):
        game_section = el.get("GameSection")
        match_id = el.get("MatchId")
        team_id = el.get("TeamId")
        person_id = el.get("PersonId")

        for frame_el in el:
            if frame_el.tag != "Frame":
                continue

            n = int(frame_el.get("N"))
            timestamp = frame_el.get("T")
            x = _to_float(frame_el.get("X"))
            y = _to_float(frame_el.get("Y"))
            speed = _to_float(frame_el.get("S"))
            distance = _to_float(frame_el.get("D"))
            acceleration = _to_float(frame_el.get("A"))

            if team_id == "BALL":
                conn.execute(
                    "INSERT INTO ball_frames VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        n,
                        game_section,
                        match_id,
                        timestamp,
                        x,
                        y,
                        _to_float(frame_el.get("Z")),
                        speed,
                        distance,
                        acceleration,
                        frame_el.get("BallStatus"),
                        frame_el.get("BallPossession"),
                    ),
                )
            else:
                conn.execute(
                    "INSERT INTO person_frames VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        n,
                        game_section,
                        match_id,
                        timestamp,
                        person_id,
                        team_id,
                        x,
                        y,
                        speed,
                        distance,
                        acceleration,
                    ),
                )

        el.clear()

    conn.commit()


def load_positional_to_db(
    path: str = "./data/Positions_Bayern_Hamburg.xml",
) -> sqlite3.Connection:
    db_path = path.rsplit(".", 1)[0] + ".db"
    already_exists = os.path.exists(db_path)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    if not already_exists:
        _create_tables(conn)
        _ingest(conn, path)
    return conn


def iter_frame_ns(conn: sqlite3.Connection) -> Iterator[int]:
    # frame_n is globally unique across game sections.
    cur = conn.execute("SELECT DISTINCT frame_n FROM person_frames ORDER BY frame_n")
    for (frame_n,) in cur:
        yield frame_n


def get_frame(conn: sqlite3.Connection, frame_n: int) -> PositionalFrame:
    rows = conn.execute(
        """SELECT person_id, team_id, x, y, speed, distance, acceleration,
                  game_section, match_id, timestamp
           FROM person_frames WHERE frame_n = ?""",
        (frame_n,),
    ).fetchall()

    persons = [
        PersonFrame(
            person_id=r[0],
            team_id=r[1],
            x=r[2],
            y=r[3],
            speed=r[4],
            distance=r[5],
            acceleration=r[6],
        )
        for r in rows
    ]

    ball = conn.execute(
        """SELECT x, y, z, speed, distance, acceleration, status, possession
           FROM ball_frames WHERE frame_n = ?""",
        (frame_n,),
    ).fetchone()

    return PositionalFrame(
        frame_n=str(frame_n),
        timestamp=datetime.fromisoformat(rows[0][9]),
        game_section=rows[0][7],
        match_id=rows[0][8],
        persons=persons,
        ball=BallFrame(
            x=ball[0],
            y=ball[1],
            z=ball[2],
            speed=ball[3],
            distance=ball[4],
            acceleration=ball[5],
            status=ball[6],
            possession=ball[7],
        ),
    )
