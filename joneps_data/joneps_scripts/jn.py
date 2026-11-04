"""Small JONEPS client: session + csrf, list search, Excel export."""
import re, time, requests
from bs4 import BeautifulSoup

BASE = "https://www.joneps.gov.jo"
LIST = BASE + "/ep/invt/selectListTendInvitAL.do"
ENTRY = LIST + "?menuId=EP03000000&upperMenuId=EP03020000&subMenuId=EP03020100"

DEFAULTS = {
    "download_token_value_id": "", "currentPageNo": "1", "offSet": "0", "screenType": "",
    "cache": "false", "searchTendNo": "", "searchTendNm": "", "searchTendTypeCd1": "",
    "searchIntrlLocalTypeCd": "", "tendTypeCd2Goods": "", "tendTypeCd2GSDService": "",
    "tendTypeCd2GTDService": "", "searchTendTypeCd2": "", "searchFundType": "",
    "searchTendStatCd": "", "searchFiscalYear": "", "searchTendMthodCd": "", "searchPeNo": "",
    "peNm": "", "searchDeNo": "", "deNm": "", "searchStartSubmDlineDt": "",
    "searchEndSubmDlineDt": "", "searchStartPublicationYmd": "", "searchEndPublicationYmd": "",
    "clId": "", "clNmAr": "", "clNmEn": "", "searchTendStatusCd": "", "recordCountPerPage": "10",
}


class Client:
    def __init__(self, lang=None):
        self.s = requests.Session()
        self.s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) tender-research"
        self.lang = lang
        self.refresh()

    def get(self, url, **kw):
        for i in range(2):
            try:
                return self.s.get(url, timeout=120, **kw)
            except requests.RequestException:
                if i: raise
                time.sleep(5)

    def post(self, url, data, **kw):
        for i in range(2):
            try:
                r = self.s.post(url, data=data, timeout=180, **kw)
                if r.status_code < 500: return r
            except requests.RequestException:
                if i: raise
            time.sleep(5)
        return r

    def refresh(self):
        url = ENTRY + (f"&lang={self.lang}" if self.lang else "")
        h = self.get(url).text
        self.csrf = re.search(r'name="_csrf"\s+value="([^"]+)"', h).group(1)
        return h

    def search(self, **over):
        d = dict(DEFAULTS); d.update(over); d["_csrf"] = self.csrf
        return self.post(LIST, d)


def total(html):
    m = re.search(r"([\d.,]+)\s*(?:النتائج|Results?)\s*\((?:الصفحة|Page)\s*(\d+)/(\d+)\)", html, re.I)
    return (int(re.sub(r"[.,]", "", m.group(1))), int(m.group(3))) if m else (None, None)


DETAIL_RE = re.compile(r"fn_goDetail\(([^)]*)\)")


def parse_rows(html):
    soup = BeautifulSoup(html, "lxml")
    out = []
    for a in soup.select('td a[onclick*="fn_goDetail"]'):
        td = a.find_parent("td")
        if td.find_previous_sibling("td") is not None:  # only first column (tender no)
            continue
        tr = td.find_parent("tr")
        tds = tr.find_all("td", recursive=False)
        args = [x.strip().strip("'") for x in DETAIL_RE.search(a["onclick"]).group(1).split(",")]
        # status row is the next <tr>
        nxt = tr.find_next_sibling("tr")
        status = " ".join(nxt.get_text(" ", strip=True).split()) if nxt else ""
        out.append({
            "tender_no": " ".join(tds[0].get_text().split()),
            "title": " ".join(tds[1].get_text(" ").split()),
            "procuring_entity": " ".join(tds[2].get_text().split()),
            "tender_type": " ".join(tds[3].get_text().split()),
            "publication_date": tds[4].get_text(strip=True),
            "deadline": tds[5].get_text(strip=True),
            "status_row": status,
            "args": args,
        })
    return out
