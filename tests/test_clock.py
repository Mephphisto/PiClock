"""Tests for clock face renderers."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

import clock
from music_cover import RESOLUTION


@pytest.fixture
def ha():
    """Async mock HA client that returns a placeholder sensor string."""
    mock_ha = MagicMock()
    mock_ha.get_val = AsyncMock(return_value='20.5 °C')
    return mock_ha


@pytest.fixture
def font():
    """Mock PIL font whose getbbox always returns a small fixed value."""
    f = MagicMock()
    f.getbbox.return_value = (0, 0, 60, 20)
    return f


class TestClockFunctions:
    async def test_clock_dropshadow_returns_l_image(self, ha, font):
        with patch('clock.ImageFont.truetype', return_value=font), \
             patch('clock.ImageDraw.Draw'):
            result = await clock.clock_dropshadow(ha)
        assert isinstance(result, Image.Image)
        assert result.mode == 'L'

    async def test_clock_triangles_returns_rgb_image(self, ha, font):
        with patch('clock.ImageFont.truetype', return_value=font), \
             patch('clock.ImageDraw.Draw'):
            result = await clock.clock_triangles(ha)
        assert isinstance(result, Image.Image)
        assert result.mode == 'RGB'

    async def test_clock_dark_color_returns_rgba_image(self, ha, font):
        with patch('clock.ImageFont.truetype', return_value=font), \
             patch('clock.ImageDraw.Draw'):
            result = await clock.clock_dark_color(ha)
        assert isinstance(result, Image.Image)
        assert result.mode == 'RGBA'

    async def test_clock_colorfull_returns_rgb_image(self, ha, font):
        with patch('clock.ImageFont.truetype', return_value=font), \
             patch('clock.ImageDraw.Draw'):
            result = await clock.clock_colorfull(ha)
        assert isinstance(result, Image.Image)
        assert result.mode == 'RGB'

    async def test_clock_stripy_black_returns_l_image(self, ha, font):
        with patch('clock.ImageFont.truetype', return_value=font), \
             patch('clock.ImageDraw.Draw'):
            result = await clock.clock_stripy_black(ha)
        assert isinstance(result, Image.Image)
        assert result.mode == 'L'

    async def test_clock_stripy_white_returns_l_image(self, ha, font):
        with patch('clock.ImageFont.truetype', return_value=font), \
             patch('clock.ImageDraw.Draw'):
            result = await clock.clock_stripy_white(ha)
        assert isinstance(result, Image.Image)
        assert result.mode == 'L'

    async def test_all_clocks_return_correct_canvas_size(self, ha, font):
        with patch('clock.ImageFont.truetype', return_value=font), \
             patch('clock.ImageDraw.Draw'):
            for clock_fn in clock.CLOCKS:
                result = await clock_fn(ha)
                assert result.size == (RESOLUTION[0], RESOLUTION[1]), \
                    f"{clock_fn.__name__} returned wrong size {result.size}"


class TestDrawHa:
    async def test_does_not_raise_when_ha_is_unavailable(self, font):
        failing_ha = MagicMock()
        failing_ha.get_val = AsyncMock(side_effect=Exception("HA unreachable"))
        with patch('clock.ImageFont.truetype', return_value=font):
            # Must complete silently — exception is swallowed internally
            await clock._draw_ha(MagicMock(), failing_ha, (255,))

    async def test_draws_four_text_elements_on_success(self, ha, font):
        drw = MagicMock()
        with patch('clock.ImageFont.truetype', return_value=font):
            await clock._draw_ha(drw, ha, (0, 0, 0))
        assert drw.text.call_count == 4


class TestClocksRegistry:
    def test_registry_has_six_entries(self):
        assert len(clock.CLOCKS) == 6

    def test_all_entries_are_callable(self):
        for fn in clock.CLOCKS:
            assert callable(fn)

    def test_dropshadow_is_first_entry(self):
        assert clock.CLOCKS[0] is clock.clock_dropshadow
