"""Stub hardware-dependent packages before any source imports."""
import sys
from unittest.mock import MagicMock

# inky.inky_ac073tc1a._RESOLUTION_7_3_INCH drives RESOLUTION in music_cover.
# Use a small canvas so PIL filter operations run fast in tests.
_inky_ac073tc1a = MagicMock()
_inky_ac073tc1a._RESOLUTION_7_3_INCH = (200, 160)

sys.modules.setdefault('inky', MagicMock())
sys.modules['inky.inky_ac073tc1a'] = _inky_ac073tc1a
sys.modules.setdefault('inky.inky_e673', MagicMock())
sys.modules.setdefault('gpiod', MagicMock())
sys.modules.setdefault('gpiod.line', MagicMock())
sys.modules.setdefault('homeassistant_api', MagicMock())

sys.path.insert(0, 'src')
