from lxml import etree
from events.models import EVENTS_REGISTRY, SUBELEMENTS_REGISTRY, MatchEvent
from datetime import datetime


def _parse_element(element: etree._Element, regisrty: dict) -> tuple[str, object]:
    """Recursively parse an element and its children."""
    event_type = element.tag
    attribs = dict(element.attrib)
    model_cls = regisrty.get(event_type)

    # Handle nested child
    children = list(element)
    if children:
        child_el = children[0]
        child_event_type = child_el.tag
        child_registry = (
            SUBELEMENTS_REGISTRY
            if child_event_type in SUBELEMENTS_REGISTRY
            else EVENTS_REGISTRY
        )
        attribs["subelement"] = _parse_element(child_el, child_registry)

    return model_cls(**attribs)


def load_events(path: str = "./data/Events_Anonym.xml") -> list[MatchEvent]:
    tree = etree.parse(path)
    root = tree.getroot()

    events: list[MatchEvent] = []

    for el in root.iter("Event"):
        event_id = el.get("EventId")
        match_id = el.get("MatchId")
        raw_time = el.get("EventTime")

        try:
            event_time = datetime.fromisoformat(raw_time)
        except ValueError:
            continue

        children = list(el)
        if not children:
            continue

        event_type = children[0].tag
        subelement = _parse_element(children[0], EVENTS_REGISTRY)

        events.append(
            MatchEvent(
                event_id=event_id,
                match_id=match_id,
                event_time=event_time,
                event_type=event_type,
                subelement=subelement,
            )
        )

    events.sort(key=lambda e: e.event_time)
    return events
