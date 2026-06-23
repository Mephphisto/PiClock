"""Tests for the WiiM HTTP API client."""
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from wiim import Wiim, NONE_METADATA


@pytest.fixture
def wiim():
    return Wiim('192.168.1.100')


class TestWiimInit:
    def test_ssl_verification_disabled(self, wiim):
        assert wiim.s.verify is False

    def test_meta_initialised_to_none_metadata(self, wiim):
        assert wiim.meta == NONE_METADATA


class TestCmd:
    def test_returns_parsed_json(self, wiim):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {'status': 'play'}
        with patch.object(wiim.s, 'get', return_value=mock_resp):
            assert wiim._cmd('getPlayerStatus') == {'status': 'play'}

    def test_sets_encoding_to_utf8(self, wiim):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        with patch.object(wiim.s, 'get', return_value=mock_resp):
            wiim._cmd('test')
        assert mock_resp.encoding == 'UTF-8'

    def test_builds_correct_url(self, wiim):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        with patch.object(wiim.s, 'get', return_value=mock_resp) as mock_get:
            wiim._cmd('myCommand')
        mock_get.assert_called_once_with(
            'https://192.168.1.100/httpapi.asp?command=myCommand'
        )

    def test_returns_none_on_connection_error(self, wiim):
        with patch.object(wiim.s, 'get', side_effect=ConnectionError):
            assert wiim._cmd('anything') is None


class TestState:
    def test_returns_status_string(self, wiim):
        with patch.object(wiim, '_cmd', return_value={'status': 'play'}):
            assert wiim.state() == 'play'

    def test_returns_none_when_cmd_returns_none(self, wiim):
        with patch.object(wiim, '_cmd', return_value=None):
            assert wiim.state() is None

    def test_returns_none_when_status_key_missing(self, wiim):
        with patch.object(wiim, '_cmd', return_value={}):
            assert wiim.state() is None


class TestMediaInfo:
    def test_returns_metadata_dict(self, wiim):
        payload = {'metaData': {'title': 'Song', 'artist': 'Band'}}
        with patch.object(wiim, '_cmd', return_value=payload):
            assert wiim.media_info() == {'title': 'Song', 'artist': 'Band'}

    def test_caches_result_to_meta(self, wiim):
        meta = {'title': 'Song', 'albumArtURI': 'http://example.com/art.jpg'}
        with patch.object(wiim, '_cmd', return_value={'metaData': meta}):
            wiim.media_info()
        assert wiim.meta == meta

    def test_returns_none_when_cmd_returns_none(self, wiim):
        with patch.object(wiim, '_cmd', return_value=None):
            assert wiim.media_info() is None

    def test_returns_none_when_metadata_key_missing(self, wiim):
        with patch.object(wiim, '_cmd', return_value={'other': 'data'}):
            assert wiim.media_info() is None


class TestGetCover:
    def test_returns_valid_url(self, wiim):
        wiim.meta = {'albumArtURI': 'http://example.com/art.jpg'}
        assert wiim.get_cover() == 'http://example.com/art.jpg'

    def test_returns_none_for_un_known_sentinel(self, wiim):
        wiim.meta = {'albumArtURI': 'un_known'}
        assert wiim.get_cover() is None

    def test_returns_none_for_unknown_sentinel(self, wiim):
        wiim.meta = {'albumArtURI': 'unknown'}
        assert wiim.get_cover() is None

    def test_returns_none_when_key_missing(self, wiim):
        wiim.meta = {}
        assert wiim.get_cover() is None

    def test_initial_state_has_no_cover(self, wiim):
        assert wiim.get_cover() is None


class TestFetchImg:
    def _png_bytes(self):
        buf = BytesIO()
        Image.new('RGB', (50, 50), (100, 150, 200)).save(buf, format='PNG')
        buf.seek(0)
        return buf.read()

    def test_returns_pil_image(self, wiim):
        wiim.meta = {'albumArtURI': 'http://example.com/art.jpg'}
        mock_resp = MagicMock()
        mock_resp.content = self._png_bytes()
        with patch.object(wiim.s, 'get', return_value=mock_resp):
            result = wiim.fetch_img()
        assert isinstance(result, Image.Image)

    def test_returns_none_on_request_error(self, wiim):
        wiim.meta = {'albumArtURI': 'http://example.com/art.jpg'}
        with patch.object(wiim.s, 'get', side_effect=ConnectionError):
            assert wiim.fetch_img() is None
