import asyncio
from enum import Enum

import aiohttp


class Region(Enum):
    EU = 0
    US = 1
    KR = 2
    TW = 3


class EndPoint(Enum):
    API_BASE = "https://{region}.api.battle.net"
    WOW = API_BASE + '/wow'
    WOW_REALM = WOW + '/realm/status'


class BlizzardAPI:
    def __init__(self, key, loop=None, sess=None):
        self.key = key
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6',
        }
        self.loop = loop or asyncio.get_event_loop()
        self.sess = sess or aiohttp.ClientSession(loop=self.loop, headers=headers)

    async def realm_status(self, region: Region = None):
        regions = Region if region is None else [region]
        statuses = {}
        for r in regions:
            statuses[r] = (await self._do_req(EndPoint.WOW_REALM, r))['realms']
        return statuses

    async def _do_req(self, endpoint: EndPoint, region: Region):
        url = endpoint.value.format(region=region.name.lower())
        params = {'locale': 'en_GB', 'apikey': self.key}
        async with self.sess.get(url, params=params) as req:
            print(req.url)
            print(req.status)
            return await req.json()