"""Tests for the e-ink display output function."""
from unittest.mock import MagicMock

from PIL import Image

from display import show_image


class TestShowImage:
    async def test_calls_set_image_once(self):
        display = MagicMock()
        await show_image(display, Image.new('RGB', (160, 200)))
        display.set_image.assert_called_once()

    async def test_calls_show_once(self):
        display = MagicMock()
        await show_image(display, Image.new('RGB', (160, 200)))
        display.show.assert_called_once()

    async def test_calls_set_border_once(self):
        display = MagicMock()
        await show_image(display, Image.new('RGB', (160, 200)))
        display.set_border.assert_called_once()

    async def test_image_is_rotated_90_degrees(self):
        display = MagicMock()
        # 160×200 portrait → 200×160 landscape after rotate(90, expand=True)
        await show_image(display, Image.new('RGB', (160, 200)))
        passed_img = display.set_image.call_args[0][0]
        assert passed_img.size == (200, 160)

    async def test_accepts_non_rgb_input(self):
        display = MagicMock()
        # Grayscale image should be converted to RGB internally
        await show_image(display, Image.new('L', (160, 200)))
        display.show.assert_called_once()
