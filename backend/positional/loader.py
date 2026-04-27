from lxml import etree
from dataclasses import dataclass
from typing import Optional
from positional.models import PositionalFrame, PersonFrame, BallFrame
from collections import defaultdict
from datetime import datetime

@dataclass
class _RawFrame:
    timestamp: str
    x: float; y: float
    speed: float; distance: float; acceleration: float
    team_id: str

    # Ball-only
    z: Optional[float] = None
    status: Optional[str] = None
    possession: Optional[str] = None

# frame_n -> person_id -> raw frame
_FrameIndex = dict[str, dict[str, _RawFrame]]

# frame_n -> game_section
_SectionIndex = dict[str, str]

def _to_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def _scatter_frameset(
    frameset_el: etree._Element,
    index: _FrameIndex,
    sections: _SectionIndex,
) -> str:
    """
    Read one <FrameSet> and scatter its <Frame> children into index.
 
    Returns match_id from the FrameSet attributes.
    """
    match_id = frameset_el.get("MatchId")
    game_section = frameset_el.get("GameSection")
    team_id = frameset_el.get("TeamId")
    person_id = frameset_el.get("PersonId")
 
 
    for frame_el in frameset_el:
        if frame_el.tag != "Frame":
            continue
 
        n = frame_el.get("N")
        sections[n] = game_section
        timestamp = frame_el.get("T")
        x =  _to_float(frame_el.get("X"))
        y = _to_float(frame_el.get("Y"))
        z = _to_float(frame_el.get("Z"))
        speed = _to_float(frame_el.get("S"))
        distance = _to_float(frame_el.get("D"))
        acceleration = _to_float(frame_el.get("A"))
        status = frame_el.get("BallStatus")
        possession = frame_el.get("BallPossession")
        frame = _RawFrame(
            timestamp=timestamp,
            x=x, y=y, z=z,
            speed=speed, distance=distance,
            acceleration=acceleration, status=status,
            possession=possession, team_id=team_id
        )
 
        index[n][person_id] = frame
 
    return match_id

def _assemble(
    index: _FrameIndex,
    sections: _SectionIndex,
    match_id: str,
) -> list[PositionalFrame]:
    """
    Combine per-entity raw entries into PositionalFrame instances.
    """
    frames: list[PositionalFrame] = []
 
    for n in index.keys():
        entities = index[n]
 
        players: list[PersonFrame] = []
        ball: Optional[BallFrame] = None
        timestamp = None
 
        for person_id, entry in entities.items():
            # Use the first valid timestamp we encounter for this frame N
            if timestamp is None and entry.timestamp:
                try:
                    timestamp = datetime.fromisoformat(entry.timestamp)
                except ValueError:
                    continue

            if entry.team_id == "BALL":
                ball = BallFrame(
                    x=entry.x,
                    y=entry.y,
                    z=entry.z,
                    speed=entry.speed,
                    distance=entry.distance,
                    acceleration=entry.acceleration,
                    status=entry.status,
                    possession=entry.possession,
                )
            else:
                players.append(
                    PersonFrame(
                        person_id=person_id,
                        team_id=entry.team_id,
                        x=entry.x,
                        y=entry.y,
                        speed=entry.speed,
                        distance=entry.distance,
                        acceleration=entry.acceleration,
                    )
                )

        frames.append(
            PositionalFrame(
                frame_n=n,
                timestamp=timestamp,
                game_section=sections[n],
                match_id=match_id,
                players=players,
                ball=ball,
            )
        )
 
    return frames

def load_positional(path: str = "./data/Positions_Bayern_Hamburg.xml") -> list[PositionalFrame]:
    tree = etree.parse(path)
    root = tree.getroot()
    index: _FrameIndex = defaultdict(dict)
    sections: _SectionIndex = {}

    for el in root.iter("FrameSet"):
        match_id = _scatter_frameset(el, index, sections)
        el.clear()
    

    return _assemble(index, sections=sections, match_id=match_id)