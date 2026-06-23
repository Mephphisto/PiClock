"""PiClock main entry point — state machine driving the e-ink display."""
import asyncio
import json
import random
import sys
import traceback
from datetime import datetime, timedelta
from enum import Enum

import gpiod
from gpiod.line import Direction, Edge, Value
from inky.inky_e673 import Inky, RESET_PIN, BUSY_PIN, DC_PIN, CS0_PIN

import clock
from display import show_image
from home_assistant import HaClient
from music_cover import create_cover_image
from wiim import Wiim


class State(Enum):
    """Display state machine states."""

    NONE = 1
    MUSIC_COVER = 2
    CLOCK = 3


async def main(args):
    """Run the main display loop."""
    with open('config.json', encoding='utf-8') as f:
        cfg = json.load(f)
    wiim = Wiim(cfg['WiM_IP'])
    display = Inky(gpio=gpiod.Chip("/dev/gpiochip4").request_lines(
        consumer="inky",
        config={
            CS0_PIN: gpiod.LineSettings(
                direction=Direction.OUTPUT, output_value=Value.ACTIVE),
            DC_PIN: gpiod.LineSettings(
                direction=Direction.OUTPUT, output_value=Value.INACTIVE),
            RESET_PIN: gpiod.LineSettings(
                direction=Direction.OUTPUT, output_value=Value.ACTIVE),
            BUSY_PIN: gpiod.LineSettings(
                direction=Direction.INPUT,
                edge_detection=Edge.RISING,
                debounce_period=timedelta(milliseconds=10)),
        }
    ))
    ha = HaClient(cfg['HA_Addr'], cfg['HA_API_Key'], cfg['HA_entities'])
    track_id = '0'
    last_state = State.NONE
    t = datetime.now().strftime("%H:%M")
    if "-c" in args:
        idx = int(args[args.index('-c') + 1]) % len(clock.CLOCKS)
        print('Using Clock ', idx)
    else:
        idx = random.randint(0, len(clock.CLOCKS) - 1)
    task = asyncio.create_task(asyncio.sleep(0.0))
    while True:
        media_info = wiim.media_info()
        playing_media = wiim.state() == 'play' and wiim.get_cover() is not None
        if playing_media:
            try:
                if media_info and (
                    track_id != media_info['trackId']
                    or last_state is not State.MUSIC_COVER
                ):
                    track_id = media_info['trackId']
                    img = create_cover_image(wiim)
                    await task
                    task = asyncio.create_task(show_image(display, img))
                    last_state = State.MUSIC_COVER
            except Exception:  # noqa: BLE001
                traceback.print_exc()
                playing_media = False
        if not playing_media:
            if t != datetime.now().strftime("%H:%M") or last_state is not State.CLOCK:
                if t.split(':')[0] != datetime.now().strftime("%H"):
                    idx = random.randint(0, len(clock.CLOCKS) - 1)
                img = await clock.CLOCKS[idx](ha)
                await task
                task = asyncio.create_task(show_image(display, img))
                last_state = State.CLOCK
        t = datetime.now().strftime("%H:%M")
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main(sys.argv))
