"""CoT event construction. The two things most likely to be subtly wrong —
a *stable* UID per track (so one icon updates in place instead of leaving a
trail of duplicates) and a correct *stale* time (so dead tracks drop off the
map) — both live here, in one place.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass

import pytak

from . import config
from .affiliation import cot_type_for

# Per the CoT schema, these sentinels mean "value unknown" for point error /
# height fields. We don't have altitude or error estimates in v1.
_UNKNOWN = "9999999.0"


@dataclass
class Track:
    """A single object track from the CV pipeline.

    Mirrors the (track_id, lat, lon, class_name, confidence) tuple the
    detector produces, as a typed object.
    """

    track_id: str
    lat: float
    lon: float
    class_name: str
    confidence: float


def cot_uid(track_id) -> str:
    """Stable CoT UID for a track. Same track_id -> same UID across updates,
    so ATAK moves the existing icon rather than spawning a new one."""
    return f"{config.UID_PREFIX}-{track_id}"


def make_cot_event(track: Track, stale_seconds: int = None) -> bytes:
    """Serialize a Track to CoT XML bytes ready for the tx_queue."""
    if stale_seconds is None:
        stale_seconds = config.STALE_SECONDS

    root = ET.Element("event")
    root.set("version", "2.0")
    root.set("type", cot_type_for(track.class_name, track.confidence))
    root.set("uid", cot_uid(track.track_id))
    root.set("how", "m-g")  # GPS-derived; closest fit for a sensor-fixed track
    root.set("time", pytak.cot_time())
    root.set("start", pytak.cot_time())
    root.set("stale", pytak.cot_time(stale_seconds))

    point = ET.SubElement(root, "point")
    point.set("lat", str(track.lat))
    point.set("lon", str(track.lon))
    point.set("hae", _UNKNOWN)  # height above ellipsoid: unknown in v1
    point.set("ce", _UNKNOWN)   # circular error: unknown
    point.set("le", _UNKNOWN)   # linear error: unknown

    detail = ET.SubElement(root, "detail")
    ET.SubElement(detail, "contact").set("callsign", str(track.track_id))
    remarks = ET.SubElement(detail, "remarks")
    remarks.text = f"class={track.class_name} conf={track.confidence:.2f}"

    return ET.tostring(root)
