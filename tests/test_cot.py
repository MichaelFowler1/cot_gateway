"""Pin the two guarantees cot.py documents as the ones "most likely to be
subtly wrong": stable UIDs (one icon per track, updated in place) and correct
stale times (dead tracks drop off the map)."""
import datetime as dt
import xml.etree.ElementTree as ET

from cot_gateway import config
from cot_gateway.cot import Track, cot_uid, make_cot_event


def _track(**overrides):
    base = dict(track_id="t1", lat=37.7749, lon=-122.4194,
                class_name="drone", confidence=0.9)
    base.update(overrides)
    return Track(**base)


def _parse_cot_time(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")


def test_uid_is_stable_across_updates():
    assert cot_uid("t1") == cot_uid("t1")
    assert cot_uid("t1") != cot_uid("t2")
    assert cot_uid("t1").startswith(config.UID_PREFIX + "-")


def test_event_is_valid_cot_2_0():
    root = ET.fromstring(make_cot_event(_track()))
    assert root.tag == "event"
    assert root.get("version") == "2.0"
    assert root.get("uid") == cot_uid("t1")
    point = root.find("point")
    assert float(point.get("lat")) == 37.7749
    assert float(point.get("lon")) == -122.4194
    callsign = root.find("detail/contact").get("callsign")
    assert callsign == "t1"


def test_stale_time_honors_override():
    root = ET.fromstring(make_cot_event(_track(), stale_seconds=120))
    start = _parse_cot_time(root.get("start"))
    stale = _parse_cot_time(root.get("stale"))
    delta = (stale - start).total_seconds()
    # pytak stamps time and stale in separate calls, so allow ~2s of slack.
    assert 118 <= delta <= 122


def test_stale_defaults_exceed_fake_interval():
    # The config invariant: live tracks must never flicker stale between
    # updates, so STALE_SECONDS must comfortably exceed FAKE_INTERVAL.
    assert config.STALE_SECONDS > config.FAKE_INTERVAL
    root = ET.fromstring(make_cot_event(_track()))
    start = _parse_cot_time(root.get("start"))
    stale = _parse_cot_time(root.get("stale"))
    assert (stale - start).total_seconds() >= config.STALE_SECONDS - 2
