import math

from WiiM import Wiim
from PIL import Image, ImageFont, ImageDraw, ImageOps
from inky.inky_ac073tc1a import _RESOLUTION_7_3_INCH

FUTURA_DICT = "Futura.ttc"
RESOLUTION = [_RESOLUTION_7_3_INCH[1], _RESOLUTION_7_3_INCH[0]]

def str_wrap(text: str):
    ann = text.split(' ')
    if len(ann) > 1:
        idx = math.floor(len(ann)/2)
        if ann[idx][:2] == '\r\n':
            return str_wrap(' '.join(ann[:idx])) + ' ' + str_wrap(' '.join(ann[idx:]))
        ann[idx] = '\r\n' + ann[idx]
    return ' '.join(ann)

def create_Cover_Image(dev: Wiim) -> Image.Image:
    raw = dev.fetch_img()
    if raw is None:
        raise RuntimeError("fetch_img returned None")
    img = raw.convert('RGB')
    img = img.resize((RESOLUTION[0], RESOLUTION[0]), Image.Resampling.LANCZOS)
    meta_data = dev.media_info()
    if meta_data is None:
        raise RuntimeError("media_info returned None")
    annotation1, annotation2 = f"{meta_data['title']}", f"{meta_data['album']} - {meta_data['artist']}"
    extended = ImageOps.expand(img, border=(0, 0, 0, RESOLUTION[1] - RESOLUTION[0]))
    w, h = extended.size
    font_size = 100
    font1 = ImageFont.truetype(FUTURA_DICT, font_size)
    _, _, tw, th = font1.getbbox(annotation1)
    for k in range(1, 999999, 10):
        font_size = k
        font1 = ImageFont.truetype(FUTURA_DICT, font_size)
        _, _, tw, th = font1.getbbox(annotation1)
        if 2 * th > h - RESOLUTION[0] or 10 * (tw + 40) > 8 * w:
            # print(tw, w, th,  h - res[0])
            font_size = k - 1
            font1 = ImageFont.truetype(FUTURA_DICT, font_size)
            break
    font2 = ImageFont.truetype(FUTURA_DICT, 16)
    line_2_does_not_fit = True
    for _ in range(10):
        if line_2_does_not_fit:
            for k in range(int(max(2 * font_size / 3, 16)), 15, -1):
                font2 = ImageFont.truetype(FUTURA_DICT, k)
                sizes = [a for a in zip(*[font2.getbbox(line) for line in annotation2.split('\r\n')])]
                # print(sizes)
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
    # Get drawing context and annotate
    draw = ImageDraw.Draw(extended)
    draw.text((20, RESOLUTION[0]), annotation1, (255, 255, 255), font=font1)
    draw.multiline_text((20, RESOLUTION[0] + th + 10), annotation2, (255, 255, 255), font=font2)
    return extended