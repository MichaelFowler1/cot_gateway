"""The serialize-and-transmit half of the gateway.

TrackQueueWorker pulls Track objects off an internal asyncio.Queue
(``track_in``), turns each into CoT XML, and hands it to pytak's tx_queue.
That queue is the seam where the real detector plugs in later: anything that
can ``await track_in.put(Track(...))`` drives the map, with no changes to the
CoT/transport code below.
"""

import pytak

from .cot import make_cot_event


class TrackQueueWorker(pytak.QueueWorker):
    def __init__(self, tx_queue, config, track_in):
        super().__init__(tx_queue, config)
        self.track_in = track_in

    async def handle_data(self, data):
        """Serialize one Track to CoT and enqueue for transmission."""
        event = make_cot_event(data)
        await self.put_queue(event)

    async def run(self):
        self._logger.info("TrackQueueWorker started; awaiting tracks.")
        while True:
            track = await self.track_in.get()
            await self.handle_data(track)
