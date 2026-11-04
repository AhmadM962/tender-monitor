#!/usr/bin/env python3
"""
Seniors IT - Jordan Government Tender Monitor
=============================================
Scrapes the tender pages of ~46 Jordanian government organizations plus the
central portals (JONEPS, GTD, MoDEE), detects NEW tender announcements since
the last run, flags the ones matching Seniors IT's portfolio (cybersecurity,
infrastructure, networking, data protection, backup, etc. in English and
Arabic), and sends an email digest.

Run it twice a day via GitHub Actions, cron, or Windows Task Scheduler.

Usage:
    python monitor.py                 # normal run (scrape -> diff -> email)
    python monitor.py --dry-run      # scrape + diff, print to console, no email
    python monitor.py --test-email   # send a test email and exit

Environment variables (secrets - never commit these):
    SMTP_HOST   e.g. smtp.gmail.com
    SMTP_PORT   e.g. 465 (SSL) or 587 (STARTTLS)
    SMTP_USER   sender account, e.g. alerts.seniorsit@gmail.com
    SMTP_PASS   password / app password
    EMAIL_TO    comma-separated recipients, e.g. ahmad@seniorsit.me
"""

import argparse
import hashlib
import html
import json
import os
import re
import smtplib
import ssl
import sys
import time
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
import urllib3
import yaml
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Windows: piped output (Task Scheduler, subprocess) defaults to a legacy
# codepage, and printing an Arabic tender title would crash the run before
# the state file is saved -> duplicate alerts. Force UTF-8, never crash.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

BASE_DIR = Path(__file__).resolve().parent
# TM_* env vars let the self-test (and you) point at alternate files
STATE_FILE = Path(os.environ.get("TM_STATE_FILE", BASE_DIR / "state" / "seen.json"))
SOURCES_FILE = Path(os.environ.get("TM_SOURCES_FILE", BASE_DIR / "sources.yaml"))
CONFIG_FILE = Path(os.environ.get("TM_CONFIG_FILE", BASE_DIR / "config.yaml"))

AMMAN_TZ = timezone(timedelta(hours=3))  # Jordan is permanently UTC+3

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
}
TIMEOUT = (15, 45)  # (connect, read) seconds - a blocked host fails in 15s, not 45
STATE_RETENTION_DAYS = 400  # forget a fingerprint after this long unseen

# Link texts that are site navigation, not tenders (normalized form)
NAV_NOISE = {
    "الرئيسية", "الصفحة الرئيسية", "اتصل بنا", "تواصل معنا", "عن الوزارة",
    "عن الدائرة", "خريطة الموقع", "الاخبار", "الأخبار", "english", "عربي",
    "تسجيل الدخول", "دخول", "تسجيل", "الاسئلة الشائعة", "الأسئلة الشائعة",
    "سياسة الخصوصية", "شروط الاستخدام", "home", "contact us", "about",
    "login", "register", "sitemap", "faq", "news", "more", "المزيد",
    "اقرا المزيد", "اقرأ المزيد", "read more", "التفاصيل", "details",
}

# ----------------------------------------------------------------------------
# Text normalization (Arabic-aware)
# ----------------------------------------------------------------------------

_AR_DIACRITICS = re.compile(r"[ً-ْٰـ]")  # harakat + tatweel


def normalize(text: str) -> str:
    """Lowercase, strip Arabic diacritics, unify alef/yaa variants, squeeze spaces."""
    if not text:
        return ""
    t = text.lower()
    t = _AR_DIACRITICS.sub("", t)
    t = (
        t.replace("أ", "ا")  # أ -> ا
        .replace("إ", "ا")  # إ -> ا
        .replace("آ", "ا")  # آ -> ا
        .replace("ى", "ي")  # ى -> ي
        .replace("ة", "ه")  # ة -> ه
    )
    t = re.sub(r"\s+", " ", t).strip()
    return t


# ----------------------------------------------------------------------------
# Config / state
# ----------------------------------------------------------------------------

def load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)


# ----------------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------------

def fetch(url: str) -> str:
    """GET a page with retries; falls back to verify=False (many .gov.jo sites
    have broken TLS chains)."""
    last_err = None
    for attempt, verify in [(1, True), (2, True), (3, False)]:
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=verify)
            r.raise_for_status()
            if not r.encoding or r.encoding.lower() == "iso-8859-1":
                r.encoding = r.apparent_encoding or "utf-8"
            return r.text
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(3 * attempt)
    raise RuntimeError(f"fetch failed: {last_err}")


# ----------------------------------------------------------------------------
# Parsers -> list of items {title, url}
# ----------------------------------------------------------------------------

def parse_generic(html_text: str, base_url: str, min_title_len: int, src: dict = None) -> list:
    """Generic extractor: collect meaningful links from a tenders listing page.

    Works for the shared Jordanian gov platform (/AR/Modules/Tenders), the
    WordPress-style sites (moe.gov.jo, dos.gov.jo), and most university pages.
    Optional per-source `css:` limits extraction to matching elements
    (e.g. CARC's "div.views-row"), so site menus and news can't leak in.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    css = (src or {}).get("css")
    if css:
        scope = BeautifulSoup("".join(str(el) for el in soup.select(css)), "html.parser")
    else:
        scope = soup
        for tag in scope(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

    items, seen_local = [], set()
    for a in scope.find_all("a", href=True):
        title = " ".join(a.get_text(" ", strip=True).split())
        href = a["href"].strip()
        if not title or len(title) < min_title_len:
            continue
        if href.startswith(("javascript:", "#", "mailto:", "tel:")):
            continue
        norm_title = normalize(title)
        if norm_title in NAV_NOISE:
            continue
        url = urljoin(base_url, href)
        key = (norm_title, url)
        if key in seen_local:
            continue
        seen_local.add(key)
        items.append({"title": title, "url": url})

    # Also catch tenders rendered as plain list rows with a PDF/doc attachment
    return items


def _norm_tender_no(s: str) -> str:
    """'C – T – W – 2026-084' and 'C-T-W-2026-084' -> 'ctw2026084'."""
    return re.sub(r"[\s\-–—_/\\.]+", "", normalize(s))


def parse_table(html_text: str, base_url: str, min_title_len: int, src: dict = None) -> list:
    """Tender lists published as table rows (Yarmouk Water, AHU), where the
    tender name is plain text and attachment links are not unique.

    Per-source settings:
      css:      selector for the rows (default: all <tr>)
      columns:  {no: idx, name: idx, <label>: idx, ...} - zero-based <td>
                indexes. Identity = normalized tender no + name (numbers are
                reused across rounds, names alone can repeat). Extra labelled
                columns (deadline, posted...) are shown in the alert only.
    """
    src = src or {}
    cols = src.get("columns", {"no": 0, "name": 1})
    soup = BeautifulSoup(html_text, "html.parser")
    rows = soup.select(src["css"]) if src.get("css") else soup.find_all("tr")
    items, seen = [], set()
    for tr in rows:
        tds = tr.find_all("td", recursive=False) or tr.find_all("td")
        if len(tds) <= max(cols.values()):
            continue  # header, pager or layout row
        cell = lambda i: " ".join(tds[i].get_text(" ", strip=True).split())
        name = cell(cols["name"])
        no = cell(cols["no"]) if "no" in cols else ""
        if len(name) < min_title_len:
            continue
        key = f"{_norm_tender_no(no)}|{normalize(name)}"
        if key in seen:
            continue
        seen.add(key)
        extras = [f"{lbl} {cell(i)}" for lbl, i in cols.items()
                  if lbl not in ("no", "name") and cell(i) and cell(i) != "-"]
        items.append({
            "title": " — ".join(x for x in [f"[{no}] {name}" if no else name, *extras] if x),
            "match_text": name,
            "key": key,
            "url": base_url,  # PDF links are shared placeholders; the list page is the stable link
        })
    return items


def _joneps_detail_url(base_url: str, args: list) -> str:
    """Browser link to a tender, mirroring JONEPS's own fn_goDetail(tendNo,
    tendSeq, frameworkAgreementSeq, tendCategCd, workType, intrlLocalTypeCd,
    tendMthodCd, tendTypeCd1): the page depends on the tender category
    (EP1311 goods/services, EP1312 works, EP1313 medicines) and method
    (EP0022 pre-qualification / EP5021 EOI open the works page).
    Verified in a browser 2026-11-04 (opens the tender's tabbed page)."""
    a = [x.strip() for x in args] + [""] * 8
    tend_no, tend_seq, fa_seq, categ, work_type, local_cd, method, type1 = a[:8]
    if categ == "EP1313":
        page = "MedicineDetails.do"
    elif categ == "EP1312" or method in ("EP0022", "EP5021"):
        page = "WorkDetails.do"
    elif categ == "EP1311":
        page = "GoodsDetails.do" if type1 == "EP0011" else "ServiceDetails.do"
    else:
        page = "WorkUnspscDetails.do"
    q = (f"tendNo={tend_no}&tendSeq={tend_seq or '00'}&frameworkAgreementSeq={fa_seq}"
         f"&tendCategCd={categ}&workType={work_type}&intrlLocalTypeCd={local_cd}"
         f"&tendMthodCd={method}&invtYn=Y&searchConditions=")
    return urljoin(base_url, f"/ep/invt/{page}?{q}")


def parse_joneps(html_text: str, base_url: str, min_title_len: int, src: dict = None) -> list:
    """Parser for the JONEPS tender list (selectListTendInvitAL.do).

    Row format (captured from the live site): each tender is a <tr> with 6
    <td>s — tender no (link with onclick fn_goDetail('tendNo','tendSeq',...)),
    title, procuring entity, type, publication date, deadline — followed by a
    colspan stage-bar row, which is skipped."""
    soup = BeautifulSoup(html_text, "html.parser")
    items, seen = [], set()

    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 6:
            continue
        onclick = ""
        for a in tr.find_all("a"):
            oc = a.get("onclick") or ""
            if "fn_goDetail" in oc:
                onclick = oc
                break
        if not onclick:
            continue
        args = re.findall(r"'([^']*)'", onclick)
        tend_no = args[0] if args else ""
        tend_seq = (args[1] if len(args) > 1 else "00") or "00"
        title = tds[1].get_text(" ", strip=True)
        entity = tds[2].get_text(" ", strip=True)
        ttype = tds[3].get_text(" ", strip=True)
        deadline = tds[5].get_text(" ", strip=True)
        if not tend_no or not title or (tend_no, tend_seq) in seen:
            continue
        seen.add((tend_no, tend_seq))
        items.append(
            {
                "title": f"{title} — {entity} — {ttype} — deadline {deadline} — No. {tend_no}-{tend_seq}",
                "match_text": title,  # keywords look at the tender name only, never the entity name
                "type": ttype,
                "key": f"{tend_no}-{tend_seq}",
                "url": _joneps_detail_url(base_url, args),
            }
        )

    if not items:  # fallback: any tendNo occurrences in scripts/links
        for m in re.finditer(r"tendNo=([0-9]{6,})", html_text):
            items.append(
                {
                    "title": f"JONEPS tender {m.group(1)}",
                    "url": base_url,  # no fn_goDetail args available - link the list
                }
            )
    if not items:
        items = parse_generic(html_text, base_url, min_title_len)
    return items


def fetch_joneps_bulk(list_url: str, min_title_len: int) -> list:
    """Pull the WHOLE active JONEPS window in one request.

    Flow (documented in joneps_data/joneps_search_request.md): GET the list
    page to obtain the session cookie and the Spring `_csrf` token, then POST
    the search with recordCountPerPage=2000 and an explicit deadline window
    (today-35d .. today+95d, dd/MM/yyyy) — wider than the server default, so
    nothing near the edges is missed. ~750 active tenders come back in one
    page instead of 75 pages of 10."""
    s = requests.Session()
    s.headers.update(HEADERS)

    def req(method, u, **kw):
        last = None
        for attempt, verify in [(1, True), (2, True), (3, False)]:
            try:
                r = s.request(method, u, timeout=(15, 90), verify=verify, **kw)
                r.raise_for_status()
                return r
            except Exception as e:  # noqa: BLE001
                last = e
                time.sleep(3 * attempt)
        raise RuntimeError(f"joneps request failed: {last}")

    r = req("GET", list_url)
    m = re.search(r'name="_csrf"[^>]*value="([^"]+)"', r.text)
    if not m:
        m = re.search(r'value="([^"]+)"[^>]*name="_csrf"', r.text)
    if not m:
        raise RuntimeError("csrf token not found on JONEPS list page")

    now = datetime.now(AMMAN_TZ)
    post_url = list_url.split("?")[0]
    data = {
        "_csrf": m.group(1),
        "currentPageNo": "1",
        "offSet": "0",
        "recordCountPerPage": "2000",
        "searchStartSubmDlineDt": (now - timedelta(days=35)).strftime("%d/%m/%Y"),
        "searchEndSubmDlineDt": (now + timedelta(days=95)).strftime("%d/%m/%Y"),
    }
    r2 = req("POST", post_url, data=data)
    items = parse_joneps(r2.text, post_url, min_title_len)
    if len(items) < 20:  # a healthy window has hundreds of tenders
        raise RuntimeError(f"bulk POST parsed only {len(items)} rows - treating as failure")
    return items


PARSERS = {"generic": parse_generic, "joneps": parse_joneps, "table": parse_table}


# ----------------------------------------------------------------------------
# Matching
# ----------------------------------------------------------------------------

_SHORT_ASCII = re.compile(r"[a-z0-9+./-]+\Z")


def _compile_terms(terms):
    """Short English terms (<=5 chars: EDR, NAS, RAM...) match on word
    boundaries only; everything else is a normalized substring."""
    subs, regs = [], []
    for k in terms or []:
        n = normalize(str(k))
        if not n:
            continue
        if _SHORT_ASCII.match(n) and len(n) <= 5:
            regs.append((str(k), re.compile(r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])")))
        else:
            subs.append((str(k), n))

    def find(t):
        return [k for k, n in subs if n in t] + [k for k, rx in regs if rx.search(t)]

    return find


def build_matcher(cfg: dict):
    """Two-tier matching, calibrated on 11,199 real JONEPS tenders:

    - keywords.include (STRONG): unambiguous IT/security terms -> always star.
    - keywords.weak: generic words (نظام, system, digital, شبكة...) -> star
      only if the title has NO keywords.weak_veto term (fire, HVAC, medical,
      roads, water...). A veto can never cancel a STRONG hit, so recall on
      real IT tenders is protected.
    - keywords.skip_types: tender types never starred (e.g. أدوية medicines).
    - keywords.exclude: hard veto for everything (keep empty unless sure).
    Nothing here hides a tender - unstarred tenders are still emailed."""
    kw = cfg.get("keywords", {}) or {}
    strong = _compile_terms(kw.get("include"))
    weak = _compile_terms(kw.get("weak"))
    veto = _compile_terms(kw.get("weak_veto"))
    exclude = _compile_terms(kw.get("exclude"))
    skip_types = {normalize(x) for x in kw.get("skip_types", []) or []}

    def match(title: str, ttype: str = ""):
        t = normalize(title)
        if ttype and normalize(ttype) in skip_types:
            return None
        hits = strong(t)
        if not hits:
            w = weak(t)
            if w and not veto(t):
                hits = w
        if not hits or exclude(t):
            return None
        return hits

    return match


def fingerprint(source_id: str, item: dict) -> str:
    """Identity of a tender. Parsers that know a stable ID (JONEPS tender
    no + re-tender sequence) set item['key'], so a deadline extension or an
    amended title does NOT re-alert. Otherwise: normalized title + URL."""
    if item.get("key"):
        raw = f"{source_id}|key|{item['key']}"
    else:
        url = re.sub(r";jsessionid=[^?&#]+", "", item["url"])
        raw = f"{source_id}|{normalize(item['title'])}|{url}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


# ----------------------------------------------------------------------------
# Email
# ----------------------------------------------------------------------------

def send_email(subject: str, html_body: str):
    host = os.environ.get("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", "465"))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    to = [x.strip() for x in os.environ.get("EMAIL_TO", "").split(",") if x.strip()]

    if not all([host, user, password, to]):
        print("[email] SMTP_HOST/SMTP_USER/SMTP_PASS/EMAIL_TO not set -> skipping email")
        print(f"[email] would have sent: {subject}")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = ", ".join(to)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context()) as s:
            s.login(user, password)
            s.sendmail(user, to, msg.as_string())
    else:
        with smtplib.SMTP(host, port) as s:
            s.starttls(context=ssl.create_default_context())
            s.login(user, password)
            s.sendmail(user, to, msg.as_string())
    print(f"[email] sent to {len(to)} recipient(s): {subject}")  # never log addresses (public Action logs)
    return True


def esc(s: str) -> str:
    return html.escape(s or "")


def render_email(matched, unmatched, errors, cfg) -> str:
    now = datetime.now(AMMAN_TZ).strftime("%Y-%m-%d %H:%M")
    css_card = (
        "margin:8px 0;padding:10px 14px;border:1px solid #e0e0e0;"
        "border-radius:8px;background:#fafafa"
    )
    out = [
        "<div style='font-family:Segoe UI,Arial,sans-serif;max-width:760px'>",
        f"<h2 style='color:#0b5394'>Jordan Tender Monitor &mdash; {now} (Amman)</h2>",
    ]

    if matched:
        out.append(
            f"<h3 style='color:#1a7f37'>&#11088; {len(matched)} new tender(s) matching "
            "the Seniors IT portfolio</h3>"
        )
        for it in matched:
            kw = ", ".join(it["hits"][:6])
            out.append(
                f"<div style='{css_card};border-left:5px solid #1a7f37'>"
                f"<b>{esc(it['source'])}</b><br>"
                f"<a href='{esc(it['url'])}'>{esc(it['title'])}</a><br>"
                f"<small style='color:#666'>matched: {esc(kw)}</small></div>"
            )
    else:
        out.append("<p>No new tenders matched your keywords this run.</p>")

    if unmatched and cfg.get("notify", {}).get("show_unmatched", True):
        out.append(
            f"<h3 style='color:#555'>Other new tenders in your accounts ({len(unmatched)})</h3>"
        )
        for it in unmatched[:60]:
            out.append(
                f"<div style='{css_card}'>"
                f"<b>{esc(it['source'])}</b><br>"
                f"<a href='{esc(it['url'])}'>{esc(it['title'])}</a></div>"
            )
        if len(unmatched) > 60:
            out.append(f"<p>&hellip;and {len(unmatched) - 60} more.</p>")

    if errors:
        out.append(f"<h3 style='color:#b30000'>Sources that failed this run ({len(errors)})</h3><ul>")
        for src, err in errors:
            out.append(f"<li><b>{esc(src)}</b>: {esc(str(err)[:160])}</li>")
        out.append("</ul>")

    out.append(
        "<p style='color:#999;font-size:12px'>Automated digest &mdash; Seniors IT tender monitor. "
        "Tune keywords in config.yaml, sources in sources.yaml.</p></div>"
    )
    return "".join(out)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def run(dry_run: bool = False, only_cloud_blocked: bool = False):
    cfg = load_yaml(CONFIG_FILE) or {}
    sources = load_yaml(SOURCES_FILE)["sources"]
    min_title_len = int(cfg.get("min_title_length", 12))
    match = build_matcher(cfg)
    state = load_state()
    first_run_global = not STATE_FILE.exists()
    today = datetime.now(AMMAN_TZ).strftime("%Y-%m-%d")
    # Drop state of sources that no longer exist in sources.yaml (renamed or
    # removed). If one comes back, its first run is a silent baseline again.
    known = {x["id"] for x in sources}
    state = {k: v for k, v in state.items() if k in known}

    matched, unmatched, errors = [], [], []
    attempted = 0

    in_cloud = os.environ.get("GITHUB_ACTIONS") == "true"
    for src in sources:
        if not src.get("enabled", True):
            continue
        # `cloud_blocked: true` = the site refuses GitHub's (non-Jordanian)
        # servers. The cloud skips it; a machine in Jordan covers it with
        # `python monitor.py --only-cloud-blocked`.
        if in_cloud and src.get("cloud_blocked"):
            print(f"[skip] {src['name']} - blocked from cloud, covered by the local run")
            continue
        if only_cloud_blocked and not src.get("cloud_blocked"):
            continue
        # Fail fast if the network can't reach Jordan at all (e.g. a cloud
        # runner outside Jordan being geo-blocked): don't spend an hour
        # timing out on every site, and don't touch the state.
        if attempted >= 4 and len(errors) == attempted:
            print("\n[FATAL] The first 4 sources ALL failed to connect - this machine "
                  "probably cannot reach Jordanian government sites (geo-blocking or "
                  "network outage). Aborting without changing state.")
            for n_, e_ in errors:
                print(f"  - {n_}: {str(e_)[:160]}")
            return 2
        attempted += 1
        sid, name, url = src["id"], src["name"], src["url"]
        parser = PARSERS.get(src.get("parser", "generic"), parse_generic)
        print(f"[scan] {name} -> {url}")

        items = None
        if src.get("parser") == "joneps":
            # Preferred path: one POST pulls the whole active window (~750)
            try:
                items = fetch_joneps_bulk(url, min_title_len)
                print(f"  (bulk POST: full window, {len(items)} tenders)")
            except Exception as e:  # noqa: BLE001
                print(f"  bulk POST failed ({str(e)[:90]}) -> falling back to paged GET")
                items = None

        if items is None:
            # Generic path: GET the page(s); sources with `pages: N` are
            # paginated lists fetched page by page
            urls = [url]
            for i in range(2, int(src.get("pages", 1)) + 1):
                sep = "&" if "?" in url else "?"
                urls.append(f"{url}{sep}pageIndex={i}")

            items, fetch_err = [], None
            for u in urls:
                try:
                    page = fetch(u)
                except Exception as e:  # noqa: BLE001
                    fetch_err = e
                    break
                items.extend(parser(page, u, min_title_len, src))
            if fetch_err and not items:
                errors.append((name, fetch_err))
                print(f"  !! {fetch_err}")
                continue
            if fetch_err:
                print(f"  !(partial) later page failed: {str(fetch_err)[:100]}")
        # Per-source filter for pages that are not pure tender lists
        # (e.g. a homepage): keep only links that look like tenders.
        req = [normalize(x) for x in src.get("require_terms", []) or []]
        if req:
            before = len(items)
            items = [it for it in items
                     if any(r in normalize(it["title"] + " " + it["url"]) for r in req)]
            print(f"  require_terms: kept {len(items)}/{before} tender-like links")

        prev = state.get(sid, {})
        if isinstance(prev, list):  # migrate old list format
            prev = {fp: today for fp in prev}
        first_run_source = sid not in state
        new_items = []
        for it in items:
            fp = fingerprint(sid, it)
            if fp not in prev:
                new_items.append(it)
            prev[fp] = today  # refresh last-seen date for everything still listed
        # forget fingerprints not seen for STATE_RETENTION_DAYS (tender long gone)
        cutoff = (datetime.now(AMMAN_TZ) - timedelta(days=STATE_RETENTION_DAYS)).strftime("%Y-%m-%d")
        state[sid] = {fp: d for fp, d in prev.items() if d >= cutoff}
        print(f"  {len(items)} items on page, {len(new_items)} new")

        if first_run_source and not cfg.get("alert_on_first_run", False):
            # Baseline run for this source: record everything, alert nothing.
            continue

        for it in new_items:
            hits = match(it.get("match_text") or it["title"], it.get("type", ""))
            record = {"source": name, "title": it["title"], "url": it["url"], "hits": hits or []}
            (matched if hits else unmatched).append(record)

        time.sleep(float(cfg.get("delay_between_sources_sec", 2)))

    # ---- report ----
    print(f"\n[result] matched={len(matched)} other_new={len(unmatched)} errors={len(errors)}")
    for it in matched:
        print(f"  * [{it['source']}] {it['title'][:110]} -> {it['url']}")
    if unmatched:
        print(f"\n[other new tenders - not keyword-matched] ({len(unmatched)}):")
        for it in unmatched[:80]:
            print(f"  - [{it['source']}] {it['title'][:110]}")
        if len(unmatched) > 80:
            print(f"  ... and {len(unmatched) - 80} more")

    should_send = bool(matched) or (
        unmatched and cfg.get("notify", {}).get("send_when_unmatched_only", True)
    ) or (errors and cfg.get("notify", {}).get("send_error_reports", False))

    if first_run_global:
        print("[info] First run: baseline recorded, no alerts. Next runs will alert on new tenders.")
        should_send = False

    if should_send and not dry_run:
        n = len(matched)
        subject = (
            f"\U0001F514 {n} new Seniors IT-relevant tender(s) - Jordan tender monitor"
            if n
            else f"Jordan tender monitor: {len(unmatched)} new tender(s), none matched keywords"
        )
        sent = send_email(subject, render_email(matched, unmatched, errors, cfg))
        if not sent and os.environ.get("TM_SAVE_WITHOUT_EMAIL") != "1":
            # Email isn't configured: do NOT mark these tenders as seen, or
            # they'd be lost. They'll be re-reported once email works.
            print("[state] NOT saved - alerts were due but no email was sent; "
                  "they will be reported again on the next run")
            return 0
    elif dry_run:
        print("[dry-run] email skipped")

    if not dry_run:
        save_state(state)
        print(f"[state] saved -> {STATE_FILE}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="no email, no state save")
    ap.add_argument("--test-email", action="store_true", help="send a test email and exit")
    ap.add_argument("--only-cloud-blocked", action="store_true",
                    help="scan only sources marked cloud_blocked (run this on a PC in Jordan)")
    args = ap.parse_args()

    if args.test_email:
        ok = send_email(
            "Tender monitor: test email",
            "<p>Your Jordan tender monitor email settings work. &#9989;</p>",
        )
        sys.exit(0 if ok else 1)

    sys.exit(run(dry_run=args.dry_run, only_cloud_blocked=args.only_cloud_blocked))


if __name__ == "__main__":
    main()
