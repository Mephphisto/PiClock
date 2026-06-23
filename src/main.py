import asyncio
import random
import traceback
from datetime import datetime
from Display import show_image
from Home_Assistant import HA_Client
from MusicCover import create_Cover_Image
from WiiM  import  Wiim
import json
#from inky.inky_ac073tc1a import Inky
from inky.inky_e673 import Inky, RESET_PIN,  BUSY_PIN,  DC_PIN, CS0_PIN
import Clock
import gpiod
from gpiod.line import Direction, Edge, Value

from datetime import timedelta
from enum import Enum
import sys
class State(Enum):
    NONE = 1
    MusicCover = 2
    Clock = 3


async def main(args):
    #print(f'Using {gpiodevice.find_chip_by_platform()} for accessing GPIOs')
    with open('config.json') as f:
        cfg = json.load(f)
    wiim = Wiim(cfg['WiM_IP'])
    display = Inky(gpio=gpiod.Chip("/dev/gpiochip4").request_lines(consumer="inky", config={
                        CS0_PIN: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.ACTIVE),
                        DC_PIN: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE),
                        RESET_PIN: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.ACTIVE),
                        BUSY_PIN: gpiod.LineSettings(direction=Direction.INPUT, edge_detection=Edge.RISING, debounce_period=timedelta(milliseconds=10))
                    }))
    ha = HA_Client(cfg['HA_Addr'], cfg['HA_API_Key'], cfg['HA_entities'])
    track_id = '0'
    last_state = State.NONE
    t = datetime.now().strftime("%H:%M")
    if "-c" in args:
        idx = int(args[args.index('-c')+1]) % len(Clock.CLOCKS)
        print('Using Clock ', idx)
    else:
        idx = random.randint(0, len(Clock.CLOCKS) - 1)
    task = asyncio.create_task(asyncio.sleep(0.0))
    while True:
        media_info = wiim.media_info()
        playing_media = wiim.state() == 'play' and wiim.get_cover() is not None
        if playing_media:
            try:
                if media_info and (track_id != media_info['trackId'] or last_state is not State.MusicCover):
                    track_id = media_info['trackId']
                    img = create_Cover_Image(wiim)
                    await task
                    task = asyncio.create_task(show_image(display, img))
                    last_state = State.MusicCover
            except:  # noqa E722
                traceback.print_exc()
                playing_media = False
        if not playing_media:
            if t != datetime.now().strftime("%H:%M") or last_state is not State.Clock:
                if t.split(':')[0] != datetime.now().strftime("%H"):
                    idx = random.randint(0, len(Clock.CLOCKS) - 1)
                img = await Clock.CLOCKS[idx](ha)
                await task
                task = asyncio.create_task(show_image(display, img))
                last_state = State.Clock
                
        t = datetime.now().strftime("%H:%M")
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main(sys.argv))
