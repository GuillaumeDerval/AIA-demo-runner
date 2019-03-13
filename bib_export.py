import asyncio
import csv
import datetime

import aiohttp
import aiohttp_jinja2

from members import MEMBERS


class _Dial:
    def _gen_dial_link(self):
        url_start = """https://dial.uclouvain.be/DialExport/Portail?method=department&type=classic&report=true&book=true&patent=true&preprint=true&conferencePaper=true&journalArticle=true&bookChapter=true&thesis=true&workingPaper=true&sort=date&sortType=desc&format=csv&"""
        url_start += "&".join(["authorName_{}={}".format(i + 1, x) for i, x in enumerate(MEMBERS)])

        return url_start

    def _detect_type(self, dict_entry):
        type_complete = dict_entry["TYPE DE PUBLICATION"]

        type_start = type_complete.find("(")
        type_end = type_complete.find(")")

        if type_start is not None and type_end is not None:
            return type_complete[type_start+1: type_end]
        else:
            return "OTHER ({})".format(dict_entry["TYPE DE PUBLICATION"])

    def _detect_venue(self, dict_entry):
        to_check = [
            "NOM, LIEU, DATE DE LA CONFÉRENCE",
            "TITRE DE L'OUVRAGE HOTE",
            "TITRE DU PÉRIODIQUE",
            "COLLECTION"
        ]
        for x in to_check:
            if x in dict_entry and dict_entry[x] != "":
                return dict_entry[x]
        return ""

    def _sanitize_year(self, dict_entry):
        year = dict_entry["ANNÉE"].split("/")[-1]
        try:
            return int(year)
        except:
            print("Cannot parse year of publication!")
            print(dict_entry)
        return 2000 # by default...

    def _gen_entry(self, dict_entry):
        out = {"year": self._sanitize_year(dict_entry),
                 "authors": dict_entry["AUTEUR(S)"].split(" ; "),
                 "title": dict_entry["TITRE"],
                 "type": self._detect_type(dict_entry),
                 "venue": self._detect_venue(dict_entry),
                 "link": dict_entry["URL"]}
        return out

    async def _dial_update_cache(self):
        print("UPDATE")
        async with aiohttp.ClientSession() as session:
            async with session.get(self._gen_dial_link()) as resp:
                if resp.status != 200:
                    return None
                text = await resp.text()
                reader = csv.DictReader(text.split("\n"), delimiter=';')
                return [self._gen_entry(x) for x in reader]

    def __init__(self):
        self.cache = asyncio.Future()
        self.cache.set_result(None)
        self.last_update = None

    async def get(self):
        """ Use this function to get the papers. Format of each paper is:
            {
                "year": int,
                "authors": list[str],
                "title": str,
                "type": str,
                "venue": str,
                "link": str
            }
        """
        print("GET")
        if self.last_update is None or datetime.datetime.now() -self.last_update > datetime.timedelta(hours=24):
            self.last_update = datetime.datetime.now()
            self.cache = asyncio.Future()
            try:
                self.cache.set_result(await self._dial_update_cache())
            except:
                self.cache.set_result(None)
                self.last_update = None
        out = await self.cache
        print("RETURN", type(out))
        return out

DIAL = _Dial()

@aiohttp_jinja2.template('bib.jinja2')
async def bib_all(request):
    return {
        "bib": await DIAL.get()
    }
