"""Tuning constants for the gateway. Most are env-overridable so the same
build runs against a local FreeTAKServer or a different TAK endpoint."""

import os


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    return float(raw) if raw is not None else default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    return int(raw) if raw is not None else default


# --- Transport -------------------------------------------------------------
# FreeTAKServer's default plaintext CoT input is TCP 8087 on localhost.
COT_URL = os.getenv("COT_URL", "tcp://127.0.0.1:8087")

# --- CoT semantics ---------------------------------------------------------
# How long after its last update a track stays on the map before ATAK greys
# it out / drops it. Must comfortably exceed FAKE_INTERVAL so live tracks
# never flicker stale between updates.
STALE_SECONDS = _env_int("STALE_SECONDS", 60)

# Namespace for our CoT UIDs so they don't collide with other feeds on the
# same TAK server. Final UID is f"{UID_PREFIX}-{track_id}".
UID_PREFIX = os.getenv("UID_PREFIX", "cvgw")

# Below this confidence, affiliation is forced to unknown (a-u-*) regardless
# of the class->affiliation mapping.
CONFIDENCE_FLOOR = _env_float("CONFIDENCE_FLOOR", 0.40)

# --- FreeTAKServer compatibility -------------------------------------------
# pytak's TX worker sleeps a random 0..DEFAULT_SLEEP(=5)s after each event when
# FTS_COMPAT is truthy, so a burst of tracks doesn't overwhelm FreeTAKServer.
# Default on ("1") for the live FTS test.
# NOTE: pytak evaluates this as bool(config.get("FTS_COMPAT")), and bool("0")
# is True in Python — so "0" does NOT disable it. To disable, set it empty:
#   $env:FTS_COMPAT=""   (e.g. for a fast log:// dry-run)
FTS_COMPAT = os.getenv("FTS_COMPAT", "1")

# --- Fake track generator (v1 only) ----------------------------------------
FAKE_TRACK_COUNT = _env_int("FAKE_TRACK_COUNT", 3)
FAKE_INTERVAL = _env_float("FAKE_INTERVAL", 2.0)  # seconds between updates
# Start point for the line of fake tracks (lat, lon). Default near (0, 0) is
# fine for a demo; override to put them over your AO.
FAKE_START_LAT = _env_float("FAKE_START_LAT", 37.7749)   # San Francisco-ish
FAKE_START_LON = _env_float("FAKE_START_LON", -122.4194)
# Per-tick movement, in degrees. ~0.0001 deg latitude is ~11 m.
FAKE_STEP_LAT = _env_float("FAKE_STEP_LAT", 0.0002)
FAKE_STEP_LON = _env_float("FAKE_STEP_LON", 0.0002)
# Lateral spacing between the parallel tracks so they don't overlap.
FAKE_TRACK_SPACING_LON = _env_float("FAKE_TRACK_SPACING_LON", 0.0005)
