"""Harvest JONEPS tender invitations (read-only). Writes JSON intermediates into OUT."""
import sys, os, json, time, re, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from jn import *
import detail

OUT = sys.argv[1]
START, END = "01/01/2024", "31/12/2027"
os.makedirs(OUT, exist_ok=True)
log = open(os.path.join(OUT, "harvest.log"), "a", encoding="utf-8")
def P(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(map(str, a)); print(s, flush=True); log.write(s + "\n"); log.flush()
def save(name, obj): json.dump(obj, open(os.path.join(OUT, name), "w", encoding="utf-8"), ensure_ascii=False)
def load(name):
    p = os.path.join(OUT, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None

def total_text(html):
    t = BeautifulSoup(html, "lxml").get_text(" ")
    m = re.search(r"([\d.,]+)\s*(?:النتائج|Results?)\s*\(\s*(?:الصفحة|Page)\s*(\d+)\s*/\s*([\d.,]+)", t)
    return (int(re.sub(r"[.,]", "", m.group(1))), int(re.sub(r"[.,]", "", m.group(3)))) if m else (0, 0)

def search_all(c, per=1000, **over):
    rows, page = [], 1
    while True:
        r = c.search(recordCountPerPage=str(per), currentPageNo=str(page), **over)
        n, pages = total_text(r.text)
        got = parse_rows(r.text); rows += got
        if page >= pages or not got: break
        page += 1
    return n, rows

c = Client()

# A. main list
rows = load("list.json")
if rows is None:
    n, rows = search_all(c, searchStartSubmDlineDt=START, searchEndSubmDlineDt=END)
    P("main list", n, "reported;", len(rows), "parsed"); save("list.json", rows)

# B. sub-type map
sub = load("subtype.json")
if sub is None:
    import jn as _j
    form = c.refresh()
    soup = BeautifulSoup(form, "lxml")
    codes = []
    for sid, t1 in [("tendTypeCd2Goods", "EP0011"), ("tendTypeCd2GSDService", "EP0012"), ("tendTypeCd2GTDService", "EP0014"), ("tendTypeCd2Medicine", "EP0016")]:
        for o in soup.select(f"select#{sid} option"):
            if o.get("value"): codes.append((t1, sid, o["value"], o.get_text(strip=True)))
    sub = {}
    for t1, sid, cd, nm in codes:
        field = "tendTypeCd2Goods" if sid == "tendTypeCd2Medicine" else sid  # medicine select is named tendTypeCd2Goods
        n, rr = search_all(c, searchTendTypeCd1=t1, searchTendTypeCd2=cd, **{field: cd}, searchStartSubmDlineDt=START, searchEndSubmDlineDt=END)
        for x in rr: sub[x["tender_no"]] = f"{nm} [{cd}]"
        P("subtype", t1, cd, nm, n, len(rr))
    save("subtype.json", sub)

# C. keyword searches
TERMS = ["حاسوب", "برمجيات", "أمن", "سيبراني", "شبكات", "خوادم", "تراخيص", "صيانة", "أنظمة", "معلومات", "تحول رقمي",
         "كاميرات", "firewall", "security", "network", "software", "license", "data center"]
kw = load("keywords.json")
if kw is None:
    kw = {}
    for t in TERMS:
        n, rr = search_all(c, searchTendNm=t, searchStartSubmDlineDt=START, searchEndSubmDlineDt=END)
        kw[t] = rr; P("keyword", t, n, len(rr))
    save("keywords.json", kw)

# D. Excel export (fiscal-year-free, by deadline range, split per year to keep files small)
for y0, y1, tag in [("01/01/2024", "31/12/2024", "2024"), ("01/01/2025", "31/12/2025", "2025"), ("01/01/2026", END, "2026-27")]:
    fn = os.path.join(OUT, f"joneps_export_deadline_{tag}.xlsx")
    if os.path.exists(fn): continue
    d = dict(DEFAULTS); d.update(searchStartSubmDlineDt=y0, searchEndSubmDlineDt=y1, _csrf=c.csrf,
                                 download_token_value_id=str(int(time.time() * 1000)))
    x = c.post(BASE + "/joneps-reports/ep/invt/downloadDetailTendInvit.do", d)
    if x.content[:2] == b"PK":
        open(fn, "wb").write(x.content); P("excel", tag, len(x.content))
    else:
        P("excel FAILED", tag, x.status_code, x.content[:200])

# E. details for every unique tender
allrows = {x["tender_no"]: x for x in rows}
for t, rr in kw.items():
    for x in rr: allrows.setdefault(x["tender_no"], x)
det = load("details.json") or {}
todo = [x for k, x in allrows.items() if k not in det]
P("details todo", len(todo), "of", len(allrows))
lock = threading.Lock()
tl = threading.local()
def work(x):
    if not hasattr(tl, "c"): tl.c = Client()
    for i in range(3):
        try:
            kv, de = detail.parse(detail.fetch(tl.c, x["args"]))
            if kv: break
            tl.c.refresh()
        except Exception as e:
            kv, de = {"_error": repr(e)}, None; time.sleep(5)
    with lock:
        det[x["tender_no"]] = {"kv": kv, "de_block": de}
        if len(det) % 200 == 0:
            save("details.json", det); P("details", len(det))
with ThreadPoolExecutor(4) as ex:
    list(ex.map(work, todo))
save("details.json", det)
P("DONE", len(det))
