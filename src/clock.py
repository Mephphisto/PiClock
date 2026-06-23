"""Clock face renderers for the PiClock e-ink display."""
import math
import random
import time
import traceback
from datetime import datetime

from PIL import Image, ImageFont, ImageDraw, ImageFilter, ImageChops

import home_assistant
from music_cover import FUTURA_DICT, RESOLUTION


async def clock_dark_color(ha: home_assistant.HaClient) -> Image.Image:
    """Render a CMY blob clock on a white multiply-blended background."""
    time_s = datetime.now().strftime("%H:%M")
    font = ImageFont.truetype(FUTURA_DICT, 140)
    extended_y = Image.new('RGBA', RESOLUTION, (255, 255, 255, 0))
    draw = ImageDraw.Draw(extended_y)
    t = time.time() / 30 / 60
    draw.circle(
        (180 + 140 * math.sin(-t / 5), 180 + 140 * math.cos(-t / 5)),
        300, (127, 127, 0, 255)
    )
    extended_m = Image.new('RGBA', RESOLUTION, (255, 255, 255, 0))
    draw = ImageDraw.Draw(extended_m)
    draw.circle(
        (180 + 140 * math.sin(t / 7), 180 + 140 * math.cos(t / 7)),
        300, (127, 0, 127, 255)
    )
    extended_c = Image.new('RGBA', RESOLUTION, (255, 255, 255, 0))
    draw = ImageDraw.Draw(extended_c)
    draw.circle(
        (180 + 140 * math.sin(t / 11), 180 + 140 * math.cos(t / 11)),
        300, (0, 127, 127, 255)
    )
    extended = Image.new('RGBA', RESOLUTION, (255, 255, 255, 255))
    extended = ImageChops.multiply(
        extended, extended_c.filter(filter=ImageFilter.GaussianBlur(30))
    )
    extended = ImageChops.multiply(
        extended, extended_m.filter(filter=ImageFilter.GaussianBlur(30))
    )
    extended = ImageChops.multiply(
        extended, extended_y.filter(filter=ImageFilter.GaussianBlur(30))
    )
    draw = ImageDraw.Draw(extended)
    draw.text(
        (240, 240), time_s, (255, 255, 255, 255),
        font=font, anchor="ms", outline=None
    )
    await _draw_ha(draw, ha, (0, 0, 0, 255))
    return extended


async def clock_colorfull(ha: home_assistant.HaClient) -> Image.Image:
    """Render an inverted RGB blob clock."""
    font = ImageFont.truetype(FUTURA_DICT, 140)
    time_s = datetime.now().strftime("%H:%M")
    t = time.time() / 30 / 60
    extends = [
        Image.new('L', RESOLUTION, (0)),
        Image.new('L', RESOLUTION, (0)),
        Image.new('L', RESOLUTION, (0)),
    ]
    draws = [ImageDraw.Draw(ex) for ex in extends]
    draws[0].circle(
        (180 + 120 * math.sin(-t / 5), 180 + 120 * math.cos(-t / 5)), 300, (255)
    )
    draws[1].circle(
        (180 + 120 * math.sin(t / 7), 180 + 120 * math.cos(t / 7)), 300, (255)
    )
    draws[2].circle(
        (180 + 120 * math.sin(t / 11), 180 + 120 * math.cos(t / 11)), 300, (255)
    )
    for k in range(3):
        extends[k] = extends[k].filter(filter=ImageFilter.GaussianBlur(30))
    extended = ImageChops.invert(Image.merge('RGB', extends))
    draw = ImageDraw.Draw(extended)
    draw.text((240, 240), time_s, (255, 255, 255), font=font, anchor="ms", outline=None)
    await _draw_ha(draw, ha, (0, 0, 0))
    return extended


async def clock_stripy_black(ha: home_assistant.HaClient) -> Image.Image:
    """Render a black background scattered with random white stripes."""
    font = ImageFont.truetype(FUTURA_DICT, 140)
    time_s = datetime.now().strftime("%H:%M")
    extended = Image.new('L', RESOLUTION, (0))
    draw = ImageDraw.Draw(extended)
    for _ in range(700):
        draw.line(
            (random.uniform(-20, RESOLUTION[0] + 20),
             random.uniform(-20, RESOLUTION[0] + 20),
             random.uniform(-20, RESOLUTION[0] + 20),
             random.uniform(-20, RESOLUTION[0] + 20)),
            fill=(255), width=1
        )
    draw.text((240, 240), time_s, (0), font=font, anchor="ms", outline=None)
    await _draw_ha(draw, ha, (255))
    return extended


async def clock_stripy_white(ha: home_assistant.HaClient) -> Image.Image:
    """Render a white background scattered with random black stripes."""
    font = ImageFont.truetype(FUTURA_DICT, 140)
    time_s = datetime.now().strftime("%H:%M")
    extended = Image.new('L', RESOLUTION, (255))
    draw = ImageDraw.Draw(extended)
    for _ in range(700):
        draw.line(
            (random.uniform(-20, RESOLUTION[0] + 20),
             random.uniform(-20, RESOLUTION[0] + 20),
             random.uniform(-20, RESOLUTION[0] + 20),
             random.uniform(-20, RESOLUTION[0] + 20)),
            fill=(0), width=1
        )
    draw.text((240, 240), time_s, (255), font=font, anchor="ms", outline=None)
    await _draw_ha(draw, ha, (0))
    return extended


async def clock_dropshadow(ha: home_assistant.HaClient) -> Image.Image:
    """Render a drop-shadow clock on a black background."""
    font = ImageFont.truetype(FUTURA_DICT, 140)
    time_s = datetime.now().strftime("%H:%M")
    extended = Image.new('L', RESOLUTION, (0))
    draw = ImageDraw.Draw(extended)
    draw.text((240, 240), time_s, (255), font=font, anchor="ms", outline=None)
    extended = extended.filter(filter=ImageFilter.GaussianBlur(30))
    draw = ImageDraw.Draw(extended)
    draw.text((240, 240), time_s, (0), font=font, anchor="ms", outline=None)
    await _draw_ha(draw, ha, (255))
    return extended


async def clock_triangles(ha: home_assistant.HaClient) -> Image.Image:
    """Render overlapping rotating polygons composited into an RGB clock."""
    font = ImageFont.truetype(FUTURA_DICT, 140)
    time_s = datetime.now().strftime("%H:%M")
    t = time.time() / 60 ** 2
    center = (RESOLUTION[0] / 2, RESOLUTION[0] / 2)
    radius = RESOLUTION[0] / 2
    red = Image.new('L', RESOLUTION, (0))
    green = Image.new('L', RESOLUTION, (0))
    blue = Image.new('L', RESOLUTION, (0))
    draw = ImageDraw.Draw(blue)
    draw.regular_polygon(
        (center, radius), 3,
        rotation=-t / 7 % 360, fill=(255), outline=None, width=1
    )
    draw = ImageDraw.Draw(green)
    draw.regular_polygon(
        (center, radius), 5,
        rotation=t / 11 % 360, fill=(255), outline=None, width=1
    )
    draw = ImageDraw.Draw(red)
    draw.regular_polygon(
        (center, radius), 4,
        rotation=t / 5 % 360, fill=(255), outline=None, width=1
    )
    channels = [
        red.filter(filter=ImageFilter.GaussianBlur(30)),
        green.filter(filter=ImageFilter.GaussianBlur(30)),
        blue.filter(filter=ImageFilter.GaussianBlur(30)),
    ]
    extended = ImageChops.invert(Image.merge('RGB', channels))
    draw = ImageDraw.Draw(extended)
    draw.text((240, 240), time_s, (255, 255, 255), font=font, anchor="ms", outline=None)
    await _draw_ha(draw, ha, (0, 0, 0))
    return extended


async def _draw_ha(drw: ImageDraw.Draw, ha: home_assistant.HaClient, color):
    """Draw Home Assistant sensor values in the corners of the image."""
    try:
        font = ImageFont.truetype(FUTURA_DICT, 35)
        temp = await ha.get_val('temp')
        baro = await ha.get_val('baro')
        humid = await ha.get_val('humid')
        percip = await ha.get_val('baro_change')
        drw.text((20, RESOLUTION[1] - 80), temp, color, font=font, anchor="lm")
        drw.text((20, RESOLUTION[1] - 30), humid, color, font=font, anchor="lm")
        drw.text(
            (RESOLUTION[0] - 260, RESOLUTION[1] - 80), baro,
            color, font=font, anchor="lm"
        )
        drw.text(
            (RESOLUTION[0] - 260, RESOLUTION[1] - 30), percip,
            color, font=font, anchor="lm"
        )
    except (OSError, IOError):
        traceback.print_exc()


CLOCKS = [
    clock_dropshadow,
    clock_triangles,
    clock_dark_color,
    clock_colorfull,
    clock_stripy_black,
    clock_stripy_white,
]
