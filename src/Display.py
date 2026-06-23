import PIL
import inky
from inky.inky_ac073tc1a import Inky
from PIL import ImageFilter
from PIL.ImageEnhance import Color, Contrast, Sharpness
GAMMA = 1.3
SATURATION = 1.4
CONTRAST = 1.2
SHARPNESS = 1.2
async def show_image(display: Inky, img: PIL.Image.Image):
        LUT = ImageFilter.Color3DLUT.generate((11,11,11), lambda r, g, b: (r**GAMMA, g**GAMMA, b**GAMMA))
        img_out = Sharpness(Contrast(Color(img.convert('RGB').filter(LUT)).enhance(SATURATION)).enhance(CONTRAST)).enhance(SHARPNESS)
        display.set_image(img_out.rotate(90, expand=True), saturation=0.0)
        display.set_border(inky.RED)
        display.show()