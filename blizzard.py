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
    WOW_CHAR = WOW + '/character/{realm}/{name}'
    WOW_CHARS = WOW + '/user/characters?access_token={token}'


WOW_RACES = {
    1: {'side': 'alliance', 'name': 'Human'}, 2: {'side': 'horde', 'name': 'Orc'},
    3: {'side': 'alliance', 'name': 'Dwarf'}, 4: {'side': 'alliance', 'name': 'Night Elf'},
    5: {'side': 'horde', 'name': 'Undead'}, 6: {'side': 'horde', 'name': 'Tauren'},
    7: {'side': 'alliance', 'name': 'Gnome'}, 8: {'side': 'horde', 'name': 'Troll'},
    9: {'side': 'horde', 'name': 'Goblin'}, 10: {'side': 'horde', 'name': 'Blood Elf'},
    11: {'side': 'alliance', 'name': 'Draenei'}, 22: {'side': 'alliance', 'name': 'Worgen'},
    24: {'side': 'neutral', 'name': 'Pandaren'}, 25: {'side': 'alliance', 'name': 'Pandaren'},
    26: {'side': 'horde', 'name': 'Pandaren'}}

WOW_CLASSES = {
    1: {'powerType': 'rage', 'name': 'Warrior'}, 2: {'powerType': 'mana', 'name': 'Paladin'},
    3: {'powerType': 'focus', 'name': 'Hunter'}, 4: {'powerType': 'energy', 'name': 'Rogue'},
    5: {'powerType': 'mana', 'name': 'Priest'}, 6: {'powerType': 'runic-power', 'name': 'Death Knight'},
    7: {'powerType': 'mana', 'name': 'Shaman'}, 8: {'powerType': 'mana', 'name': 'Mage'},
    9: {'powerType': 'mana', 'name': 'Warlock'}, 10: {'powerType': 'energy', 'name': 'Monk'},
    11: {'powerType': 'mana', 'name': 'Druid'}, 12: {'powerType': 'fury', 'name': 'Demon Hunter'}}


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
            statuses[r] = (await self._do_req(EndPoint.WOW_REALM, {'region': r}))['realms']
        return statuses

    async def character(self, name: str, realm: str, region: Region = None):
        regions = Region if region is None else [region]
        chars = {}
        for r in regions:
            char = await self._do_req(EndPoint.WOW_CHAR, {'name': name, 'realm': realm, 'region': r.name.lower()})
            if char.get('status') != 'nok':
                chars[r] = char
        return chars

    async def characters(self, token: str, region: Region):
        chars = await self._do_req(EndPoint.WOW_CHARS, {'token': token, 'region': region.name.lower()})
        return chars['characters']

    async def _do_req(self, endpoint: EndPoint, url_params: dict):
        url = endpoint.value.format(**url_params)
        params = {'locale': 'en_GB', 'apikey': self.key}
        async with self.sess.get(url, params=params) as req:
            print(req.url)
            print(req.status)
            return await req.json()
