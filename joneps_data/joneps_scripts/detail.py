import re
from bs4 import BeautifulSoup
from jn import BASE

def gi_path(a):
    no, seq, fa, categ, work, il, mth, t1 = a
    if categ == 'EP1313': return "/ep/invt/medicine/generalInformation.do"
    if categ == 'EP1312' or mth in ('EP0022', 'EP5021'): return "/ep/invt/Work/generalInformation.do"
    if categ == 'EP1311' and t1 == 'EP0011': return "/ep/invt/goods/tenderInformation.do"
    if categ == 'EP1311': return "/ep/invt/service/generalInformation.do"
    return "/ep/invt/Work/generalInformation.do"

def fetch(c, a):
    r = c.post(BASE + gi_path(a), {"tendNo": a[0], "tendSeq": a[1], "frameworkAgreementSeq": a[2], "tendTypeCd1": a[7],
                                    "searchConditions": "", "isFrameworkAgreementYn": "N", "_csrf": c.csrf})
    return r.text

def parse(html):
    soup = BeautifulSoup(html, "lxml")
    kv = {}
    for th in soup.find_all("th"):
        td = th.find_next_sibling("td")
        if td is None: continue
        k = " ".join(th.get_text(" ").split()).lstrip("*0123456789. ").strip()
        v = td.find("textarea").get_text() if td.find("textarea") else td.get_text(" ")
        v = " ".join(v.replace("\xa0", " ").split())
        kv.setdefault(k, v)
    # demanding-entity block (between HTML comments)
    m = re.search(r"<!-- Demanding Entity Start -->(.*?)<!-- Demanding Entity End -->", html, re.S)
    de_block = " ".join(BeautifulSoup(m.group(1), "lxml").get_text(" ").split()) if m else None
    return kv, de_block
