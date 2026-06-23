import traceback
from io import BytesIO

import requests
from PIL import Image
from urllib3.exceptions import InsecureRequestWarning

NONE_METADATA = {'album': 'unknown', 'title': 'unknown', 'subtitle': 'unknown', 'artist': 'unknown',
                     'albumArtURI': 'un_known', 'sampleRate': 'unknown', 'bitDepth': 'unknown', 'bitRate': '0',
                     'trackId': 'unknown'}

class Wiim:
    def __init__(self, ip_port: str):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
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
        except:  # noqa E722
            traceback.print_exc()
            return None

    def state(self):
        try:
          return self._cmd('getPlayerStatus')['status']
        except: #  noqa E722
            traceback.print_exc()
            return None

    def media_info(self):
        try:
            ret = self._cmd('getMetaInfo')
            ret = ret['metaData']
            self.meta = ret
            return ret
        except:  #  noqa E722
            traceback.print_exc()
            return None

    def get_cover(self) -> str:
        try:
            img_url = self.meta['albumArtURI']
            if img_url not in ['un_known', 'unknown']:
                return img_url
            else:
                return None
        except: # noqa E722
            traceback.print_exc()
            return None

    def fetch_img(self):
        try:
            response = self.s.get(self.get_cover())
            img_url = Image.open(BytesIO(response.content))
            return img_url
        except: # noqa E722
            traceback.print_exc()
            return None
