"""Fetch Chubu Electric Power Grid outage counts for Shizuoka and write data/teiden.json.

The source XML has no CORS header, so GitHub Actions fetches it on a schedule
(see .github/workflows/teiden.yml) and the page reads the JSON from this site.
"""

import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

BASE = "https://teiden.powergrid.chuden.co.jp/p/resource"
# Area codes -> names, taken from the site's teiden_area.js (ward names are the pre-2024 ones).
NAMES = {
    "22101_210": "静岡市葵区",
    "22102_210": "静岡市駿河区",
    "22103_220": "静岡市清水区",
    "22131_250": "浜松市中区",
    "22132_250": "浜松市東区",
    "22132_256": "浜松市東区",
    "22133_250": "浜松市西区",
    "22133_256": "浜松市西区",
    "22134_250": "浜松市南区",
    "22135_250": "浜松市北区",
    "22135_256": "浜松市北区",
    "22136_256": "浜松市浜北区",
    "22137_256": "浜松市天竜区",
    "22207_220": "富士宮市",
    "22209_231": "島田市",
    "22210_220": "富士市",
    "22211_241": "磐田市",
    "22212_230": "焼津市",
    "22213_240": "掛川市",
    "22214_230": "藤枝市",
    "22216_240": "袋井市",
    "22216_241": "袋井市",
    "22221_250": "湖西市",
    "22223_240": "御前崎市",
    "22224_240": "菊川市",
    "22226_231": "牧之原市",
    "22424_231": "榛原郡吉田町",
    "22429_231": "榛原郡川根本町",
    "22461_240": "周智郡森町",
}


def fetch(url: str) -> ET.Element:
    req = urllib.request.Request(url, headers={"User-Agent": "enshu-cam teiden (personal)"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return ET.fromstring(res.read())


def main(out: str) -> None:
    pref = fetch(f"{BASE}/disclose/xml/index.xml")
    shizuoka_total = next((a.findtext("genzai_teiden_kosu") for a in pref.iter("area") if a.findtext("address") == "静岡県"), None)
    areas = []
    for a in fetch(f"{BASE}/disclose/xml/sizuoka.xml").iter("area"):
        code = a.findtext("address") or ""
        areas.append({"code": code, "name": NAMES.get(code, code), "kosu": a.findtext("genzai_teiden_kosu")})
    jst = timezone(timedelta(hours=9))
    doc = {
        "fetchedAt": datetime.now(jst).isoformat(timespec="minutes"),
        "shizuoka": shizuoka_total,
        "areas": areas,
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
