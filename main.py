"""Entry point: wire pytak's CLITool to our workers and run the event loop."""

import asyncio
from configparser import ConfigParser

import pytak

from . import config
from .fakegen import FakeTrackWorker
from .worker import TrackQueueWorker


async def main():
    cfg = ConfigParser()
    section_values = {"COT_URL": config.COT_URL}
    # Only set FTS_COMPAT when enabled — pytak treats any non-empty string
    # (even "0") as truthy, so we omit the key entirely to disable it.
    if config.FTS_COMPAT:
        section_values["FTS_COMPAT"] = config.FTS_COMPAT
    cfg["cot_gateway"] = section_values
    section = cfg["cot_gateway"]

    clitool = pytak.CLITool(section)
    await clitool.setup()

    # Shared seam between track production (fake now, real detector later) and
    # serialization/transport.
    track_in = asyncio.Queue()

    clitool.add_tasks(
        {
            TrackQueueWorker(clitool.tx_queue, section, track_in),
            FakeTrackWorker(clitool.tx_queue, section, track_in),
        }
    )

    await clitool.run()


if __name__ == "__main__":
    asyncio.run(main())
