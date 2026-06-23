"""WiiM HTTP API client with cover art fetching."""
import traceback
from io import BytesIO

import requests
import urllib3
from PIL import Image

NONE_METADATA = {
    'album': 'unknown', 'title': 'unknown', 'subtitle': 'unknown',
    'artist': 'unknown', 'albumArtURI': 'un_known', 'sampleRate': 'unknown',
    'bitDepth': 'unknown', 'bitRate': '0', 'trackId': 'unknown',
}


class Wiim:
    """Client for the WiiM HTTP API."""

    def __init__(self, ip_port: str):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.ip = ip_port
        self.s = requests.session()
        self.s.verify = False
        self.meta = NONE_METADATA

    def _cmd(self, cmd: str):
        try:
            cmd = f"https://{self.ip}/httpapi.asp?command={cmd}"
            ret = self.s.get(cmd)
            ret.encoding = 'UTF-8'
            return ret.json()
        except (requests.exceptions.RequestException, ValueError):
            traceback.print_exc()
            return None

    def state(self):
        """Return the current playback state string."""
        try:
            return self._cmd('getPlayerStatus')['status']
        except (requests.exceptions.RequestException, ValueError, RuntimeError):
            traceback.print_exc()
            return None

    def media_info(self):
        """Return the current track metadata dict."""
        try:
            ret = self._cmd('getMetaInfo')
            ret = ret['metaData']
            self.meta = ret
            return ret
        except (requests.exceptions.RequestException, ValueError, RuntimeError):
            traceback.print_exc()
            return None

    def get_cover(self) -> str:
        """Return the album art URL, or None if unavailable."""
        try:
            img_url = self.meta['albumArtURI']
            if img_url not in ['un_known', 'unknown']:
                return img_url
            return None
        except (requests.exceptions.RequestException, ValueError, RuntimeError):
            traceback.print_exc()
            return None

    def fetch_img(self):
        """Fetch and return the album art as a PIL Image."""
        try:
            response = self.s.get(self.get_cover())
            return Image.open(BytesIO(response.content))
        except (requests.exceptions.RequestException, ValueError, RuntimeError):
            traceback.print_exc()
            return None


