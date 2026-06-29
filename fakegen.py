"""Fake track generator (v1 only).

Advances a handful of tracks along a straight line and pushes them into the
shared ``track_in`` queue on a fixed interval. Re-emitting every tick keeps
each track's ``stale`` time fresh, so icons stay alive and visibly move; stop
the generator and the tracks go stale and drop — which doubles as a live demo
of the stale behavior. Swap this out for the real detector later.
"""

import asyncio

import pytak

from . import config
from .cot import Track

# Give the line of tracks a spread of affiliations so the demo shows
# friendly/hostile/unknown coloring at once. These class names line up with
# the seeds in affiliation.CLASS_AFFILIATION.
_DEMO_CLASSES = ["friendly_vehicle", "drone", "person"]


class FakeTrackWorker(pytak.QueueWorker):
    def __init__(self, tx_queue, config_, track_in):
        super().__init__(tx_queue, config_)
        self.track_in = track_in

    async def run(self):
        n = config.FAKE_TRACK_COUNT
        # Each track starts at a fixed lateral offset and walks the same vector.
        lats = [config.FAKE_START_LAT for _ in range(n)]
        lons = [
            config.FAKE_START_LON + i * config.FAKE_TRACK_SPACING_LON
            for i in range(n)
        ]
        self._logger.info("FakeTrackWorker started; emitting %d tracks.", n)

        while True:
            for i in range(n):
                lats[i] += config.FAKE_STEP_LAT
                lons[i] += config.FAKE_STEP_LON
                class_name = _DEMO_CLASSES[i % len(_DEMO_CLASSES)]
                track = Track(
                    track_id=f"fake-{i}",
                    lat=lats[i],
                    lon=lons[i],
                    class_name=class_name,
                    confidence=0.9,
                )
                await self.track_in.put(track)
            await asyncio.sleep(config.FAKE_INTERVAL)
