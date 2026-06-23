"""Tests for the album art renderer."""
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from music_cover import str_wrap, create_cover_image, RESOLUTION


class TestStrWrap:
    def test_single_word_is_unchanged(self):
        assert str_wrap('Hello') == 'Hello'

    def test_empty_string_is_unchanged(self):
        assert str_wrap('') == ''

    def test_two_words_get_a_line_break(self):
        result = str_wrap('Hello World')
        assert '\r\n' in result
        assert 'Hello' in result
        assert 'World' in result

    def test_four_words_contains_exactly_one_break(self):
        result = str_wrap('one two three four')
        assert result.count('\r\n') == 1

    def test_four_words_preserves_all_words(self):
        words = ['alpha', 'beta', 'gamma', 'delta']
        result = str_wrap(' '.join(words))
        for word in words:
            assert word in result

    def test_already_wrapped_midpoint_triggers_recursive_split(self):
        # Simulate a string where the midpoint word already carries \r\n
        text = 'word1 \r\nword2 word3'
        result = str_wrap(text)
        assert 'word1' in result
        assert 'word3' in result


class TestCreateCoverImage:
    def _mock_wiim(self, img=None, meta=None):
        wiim = MagicMock()
        wiim.fetch_img.return_value = (
            img if img is not None
            else Image.new('RGB', (300, 300), (100, 150, 200))
        )
        wiim.media_info.return_value = meta if meta is not None else {
            'title': 'Test Song',
            'album': 'Test Album',
            'artist': 'Test Artist',
            'albumArtURI': 'http://example.com/art.jpg',
        }
        return wiim

    def test_raises_runtime_error_when_fetch_img_returns_none(self):
        with pytest.raises(RuntimeError, match="fetch_img returned None"):
            create_cover_image(self._mock_wiim(img=None))

    def test_raises_runtime_error_when_media_info_returns_none(self):
        with pytest.raises(RuntimeError, match="media_info returned None"):
            create_cover_image(self._mock_wiim(meta=None))

    def test_returns_pil_image(self):
        mock_font = MagicMock()
        # Large bbox forces the font-sizing loop to exit at the first iteration
        mock_font.getbbox.return_value = (0, 0, 10000, 10000)
        with patch('music_cover.ImageFont.truetype', return_value=mock_font), \
             patch('music_cover.ImageDraw.Draw'):
            result = create_cover_image(self._mock_wiim())
        assert isinstance(result, Image.Image)

    def test_output_matches_resolution(self):
        mock_font = MagicMock()
        mock_font.getbbox.return_value = (0, 0, 10000, 10000)
        with patch('music_cover.ImageFont.truetype', return_value=mock_font), \
             patch('music_cover.ImageDraw.Draw'):
            result = create_cover_image(self._mock_wiim())
        assert result.size == (RESOLUTION[0], RESOLUTION[1])
