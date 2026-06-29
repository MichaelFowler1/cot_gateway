"""Offline sanity check: build a CoT event and assert it's well-formed,
without needing a TAK server. Run with `python -m cot_gateway.selfcheck`.
"""

import xml.etree.ElementTree as ET

from .cot import Track, cot_uid, make_cot_event


def _check(track: Track, expected_affil_atom: str) -> None:
    raw = make_cot_event(track)
    root = ET.fromstring(raw)  # raises if not well-formed XML

    assert root.tag == "event", root.tag
    assert root.get("uid") == cot_uid(track.track_id)
    assert root.get("type") == f"a-{expected_affil_atom}-G", root.get("type")
    for attr in ("version", "time", "start", "stale"):
        assert root.get(attr), f"missing {attr}"

    point = root.find("point")
    assert point is not None
    assert point.get("lat") == str(track.lat)
    assert point.get("lon") == str(track.lon)

    print(f"OK  {track.track_id:8} {root.get('type'):6} -> {raw.decode()}")


def main() -> None:
    # Hostile (high-confidence drone), unknown (person), and a low-confidence
    # drone that must degrade to unknown despite the hostile class mapping.
    _check(Track("t-hostile", 37.0, -122.0, "drone", 0.95), "h")
    _check(Track("t-unknown", 37.0, -122.0, "person", 0.95), "u")
    _check(Track("t-lowconf", 37.0, -122.0, "drone", 0.10), "u")
    _check(Track("t-friend", 37.0, -122.0, "friendly_vehicle", 0.95), "f")
    print("\nAll CoT self-checks passed.")


if __name__ == "__main__":
    main()
