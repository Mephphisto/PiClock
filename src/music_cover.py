"""Album art renderer for the PiClock e-ink display."""
import math
from typing import Any

from PIL import Image, ImageFont, ImageDraw, ImageOps
from inky.inky_ac073tc1a import _RESOLUTION_7_3_INCH

from wiim import Wiim

FUTURA_DICT = "Futura.ttc"
RESOLUTION = [_RESOLUTION_7_3_INCH[1], _RESOLUTION_7_3_INCH[0]]


def str_wrap(text: str) -> str:
    """Insert a line break at the midpoint of a multi-word string."""
    ann = text.split(' ')
    if len(ann) > 1:
        idx = math.floor(len(ann) / 2)
        if ann[idx][:2] == '\r\n':
            return str_wrap(' '.join(ann[:idx])) + ' ' + str_wrap(' '.join(ann[idx:]))
        ann[idx] = '\r\n' + ann[idx]
    return ' '.join(ann)


def create_cover_image(raw:Any, meta_data:str = '') -> Image.Image:  # pylint: disable=too-many-locals
    """Render album art with title and artist annotation for the display."""
    if raw is None:
        raise RuntimeError("fetch_img returned None")
    img = raw.convert('RGB')
    img = img.resize((RESOLUTION[0], RESOLUTION[0]), Image.Resampling.LANCZOS)
    if meta_data is None:
        raise RuntimeError("media_info returned None")
    annotation1 = f"{meta_data['title']}"
    annotation2 = f"{meta_data['album']} - {meta_data['artist']}"
    extended = ImageOps.expand(img, border=(0, 0, 0, RESOLUTION[1] - RESOLUTION[0]))
    w, h = extended.size
    font_size = 100
    font1 = ImageFont.truetype(FUTURA_DICT, font_size)
    for k in range(1, 999999, 10):
        font_size = k
        font1 = ImageFont.truetype(FUTURA_DICT, font_size)
        _, _, tw, th = font1.getbbox(annotation1)
        if 2 * th > h - RESOLUTION[0] or 10 * (tw + 40) > 8 * w:
            font_size = k - 1
            font1 = ImageFont.truetype(FUTURA_DICT, font_size)
            break
    font2 = ImageFont.truetype(FUTURA_DICT, 16)
    line_2_does_not_fit = True
    for _ in range(10):
        if line_2_does_not_fit:
            for k in range(int(max(2 * font_size / 3, 16)), 15, -1):
                font2 = ImageFont.truetype(FUTURA_DICT, k)
                sizes = list(zip(*[font2.getbbox(line) for line in annotation2.split('\r\n')]))
                th = sum(sizes[3])
                tw = max(sizes[2])
                if 2 * th < h - RESOLUTION[0] and tw + 40 < w:
                    font_size = k
                    font2 = ImageFont.truetype(FUTURA_DICT, k)
                    line_2_does_not_fit = False
                    break
            else:
                annotation2 = str_wrap(annotation2)
    _, _, tw, th = font1.getbbox(annotation1)
    draw = ImageDraw.Draw(extended)
    draw.text((20, RESOLUTION[0]), annotation1, (255, 255, 255), font=font1)
    draw.multiline_text(
        (20, RESOLUTION[0] + th + 10), annotation2, (255, 255, 255), font=font2
    )
    return extended
