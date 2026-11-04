#!/usr/bin/env python3
"""
Self-test for the Jordan Tender Monitor.
Run:  python selftest.py
No internet needed - it spins up a local mock "ministry website", runs the real
monitor against it twice, and checks every stage: scraping, baseline run,
new-tender detection, Arabic+English keyword matching, JONEPS table parsing,
and text normalization. Prints PASS/FAIL per check and exits non-zero on
failure, so you can also run it in CI.
"""

import http.server
import os
import socketserver
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

BASE = Path(__file__).resolve().parent
def _free_port():
    import socket
    with socket.socket() as so:
        so.bind(("127.0.0.1", 0))
        return so.getsockname()[1]


PORT = _free_port()  # any free port - a fixed one can be held by another process

PAGE_V1 = """<html><body>
<nav><a href="/">الرئيسية</a><a href="/c">اتصل بنا</a></nav>
<a href="/t/1">عطاء رقم 12/2026 توريد قرطاسية ومواد مكتبية للوزارة</a>
<a href="/t/2">عطاء رقم 13/2026 توريد وتركيب أجهزة حاسوب وخوادم لمركز البيانات</a>
</body></html>"""

PAGE_V2 = PAGE_V1.replace(
    "</body></html>",
    """<a href="/t/3">عطاء رقم 14/2026 توريد وتركيب أنظمة حماية Firewall وأنظمة الأمن السيبراني</a>
<a href="/t/4">عطاء رقم 15/2026 توريد أثاث مكتبي وكراسي</a>
</body></html>""",
)

# Real row structure captured from the live site (joneps_search_request.md §4)
JONEPS_SAMPLE = """<html><body><table>
<tr><th>رقم</th><th>الاسم</th><th>الجهة</th><th>النوع</th><th>النشر</th><th>الايداع</th></tr>
<tr>
  <td><a href="#" onclick="fn_goDetail('2026004485','00','','EP1311','' ,'EP0061', 'EP0021', 'EP0011');">2026004485-00</a></td>
  <td><a href="#" onclick="fn_goDetail('2026004485','00','','EP1311','' ,'EP0061', 'EP0021', 'EP0011');">شراء وتحديث نظام حماية الشبكة الخاص</a></td>
  <td>دائرة المشتريات الحكومية</td><td>اللوازم</td><td>30/09/2026</td><td>27/10/2026</td>
</tr>
<tr><td colspan="6">الاستفسار الايداع مفتوح محال مبدئيا محال نهائيا</td></tr>
<tr>
  <td><a href="#" onclick="fn_goDetail('2026004465','00','','EP1312','' ,'EP0061', 'EP0021', 'EP0012');">2026004465-00</a></td>
  <td><a href="#" onclick="fn_goDetail('2026004465','00','','EP1312','' ,'EP0061', 'EP0021', 'EP0012');">العطاء المركزي لإنشاء مركز جمرك حدود الكرامة</a></td>
  <td>دائرة العطاءات الحكومية</td><td>أشغال</td><td>01/11/2026</td><td>15/11/2026</td>
</tr>
<tr><td colspan="6">الاستفسار الايداع</td></tr>
</table></body></html>"""

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  ({detail})" if detail and not cond else ""))


def run_monitor(env):
    p = subprocess.run(
        [sys.executable, str(BASE / "monitor.py")],
        capture_output=True, text=True, env=env, cwd=BASE, timeout=120,
    )
    print("    " + " / ".join(l for l in p.stdout.splitlines() if l.startswith(("[result]", "[info]", "[email]"))))
    return p.stdout + p.stderr


def main():
    tmp = Path(tempfile.mkdtemp(prefix="tm_selftest_"))
    www = tmp / "www"
    www.mkdir()
    (www / "index.html").write_text(PAGE_V1, encoding="utf-8")

    src_file = tmp / "sources.yaml"
    src_file.write_text(
        "sources:\n"
        "  - id: mock\n"
        "    name: \"Mock Ministry\"\n"
        f"    url: \"http://127.0.0.1:{PORT}/index.html\"\n"
        "    parser: generic\n"
        "    enabled: true\n",
        encoding="utf-8",
    )

    env = dict(os.environ)
    env.update({
        "TM_SOURCES_FILE": str(src_file),
        "TM_STATE_FILE": str(tmp / "state" / "seen.json"),
        "NO_PROXY": "127.0.0.1,localhost", "no_proxy": "127.0.0.1,localhost",
        "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1",  # Windows piped-output safety
        "TM_SAVE_WITHOUT_EMAIL": "1",  # the test has no SMTP; still persist state between runs
    })
    # make sure no real email goes out during the test
    for k in ("SMTP_HOST", "SMTP_USER", "SMTP_PASS", "EMAIL_TO"):
        env.pop(k, None)

    handler = type("H", (http.server.SimpleHTTPRequestHandler,), {
        "directory": str(www), "log_message": lambda *a, **k: None,
    })
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), lambda *a, **k: handler(*a, directory=str(www), **k))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    print("\n== 1. Scrape + baseline run ==")
    out1 = run_monitor(env)
    check("mock site scraped (2 items found)", "2 items on page" in out1, out1[-300:])
    check("first run is a silent baseline", "First run: baseline recorded" in out1)

    print("\n== 2. New-tender detection + keyword matching ==")
    (www / "index.html").write_text(PAGE_V2, encoding="utf-8")
    out2 = run_monitor(env)
    check("2 new tenders detected", "2 new" in out2)
    check("cyber tender MATCHED (Firewall / الأمن السيبراني)", "matched=1" in out2 and "Firewall" in out2)
    check("furniture tender NOT matched but still reported", "other_new=1" in out2)
    check("alert email would be sent", "would have sent" in out2 or "sent to" in out2)

    print("\n== 3. Run again with no changes ==")
    out3 = run_monitor(env)
    check("no duplicate alerts on unchanged page", "matched=0 other_new=0" in out3)

    print("\n== 4. JONEPS parser ==")
    sys.path.insert(0, str(BASE))
    import monitor as m  # noqa: E402
    items = m.parse_joneps(JONEPS_SAMPLE, "https://www.joneps.gov.jo/ep/invt/x.do", 12)
    check("JONEPS rows parsed (stage-bar rows skipped)", len(items) == 2, f"got {len(items)}")
    check("JONEPS goods tender links to GoodsDetails.do with all fn_goDetail args",
          any("/ep/invt/GoodsDetails.do?tendNo=2026004485&tendSeq=00" in i["url"] and "tendMthodCd=EP0021" in i["url"]
              and "invtYn=Y" in i["url"] for i in items))
    check("JONEPS works tender (EP1312) links to WorkDetails.do",
          any("/ep/invt/WorkDetails.do?tendNo=2026004465" in i["url"] for i in items))
    check("JONEPS item carries title + entity + type + deadline",
          any("نظام حماية الشبكة" in i["title"] and "دائرة المشتريات الحكومية" in i["title"]
              and "27/10/2026" in i["title"] for i in items))

    print("\n== 5. Arabic normalization / matcher ==")
    cfg = m.load_yaml(BASE / "config.yaml")
    match = m.build_matcher(cfg)
    check("diacritics + alef variants ('الأَمْن السِّيبْراني')", bool(match("عطاء الأَمْن السِّيبْراني للوزارة")))
    check("English vendor name (Fortinet)", bool(match("Supply of Fortinet NGFW licenses")))
    check("plain furniture title does not match", not match("توريد أثاث مكتبي وكراسي للمديرية"))
    check("bare Arabic نظام matches (calibration finding)", bool(match("نظام رصد وتحليل المحتوى الاعلامي")))
    check("acronym needs word boundary: 'nasal spray' no NAS hit", not match("Supply of nasal spray drops"))
    check("acronym as word matches: 'NAS storage'", bool(match("توسعة NAS للمستشفى")))
    check("drug 'Paracetamol Tablet' does not match", not match("Paracetamol 500mg Tablet"))
    check("Arabic تابلت still matches", bool(match("شراء أجهزة تابلت لمدارس الوزارة")))

    print("\n== 6. Fixes from the 2026-11-04 live dry-run ==")
    check("strong hit stars (تحديث اجهزة حماية نوع Fortinet)", bool(match("تحديث اجهزة حماية نوع Fortinet")))
    check("fire-alarm 'نظام' is vetoed", not match("ادامة نظام انذار الحريق واطفاء الحريق"))
    check("HVAC 'نظام' is vetoed", not match("ادامة نظام التكييف لدى مبنى المعهد القضائي"))
    check("'CT Scanner' medical device not starred", not match("تقديم جهاز Spiral Multi Slice CT Scanner مقابل عقد صيانة"))
    check("veto never cancels a strong hit (خوادم + حريق)", bool(match("نظام اطفاء حريق لغرفة الخوادم")))
    check("طبي-inside-تطبيق trap: pen-test of web apps stars",
          bool(match("شراء خدمات استشارية متخصصة باختبار الاختراق لتطبيقات الويب")))
    check("mobile app tender stars", bool(match("إعادة تطوير تطبيق الهاتف المحمول الخاص بوزارة العدل")))
    check("medicine-type tender never starred", not match("Software-guided insulin pump", "أدوية"))
    jn = m.parse_joneps(JONEPS_SAMPLE.replace("شراء وتحديث نظام حماية الشبكة الخاص",
                                              "تدريب الكوادر على اللياقة"), "https://www.joneps.gov.jo/x.do", 12)
    check("JONEPS: keywords ignore the entity column",
          not match(jn[0].get("match_text", jn[0]["title"]), jn[0].get("type", "")) if jn else False)
    a = m.parse_joneps(JONEPS_SAMPLE, "https://www.joneps.gov.jo/x.do", 12)[0]
    b = m.parse_joneps(JONEPS_SAMPLE.replace("27/10/2026", "10/11/2026"), "https://www.joneps.gov.jo/x.do", 12)[0]
    check("JONEPS: deadline extension does NOT re-alert (same fingerprint)",
          m.fingerprint("joneps_v2", a) == m.fingerprint("joneps_v2", b))
    nav = [{"title": "مجلس منظمة الطيران المدني يقر قرارا جديدا", "url": "https://x.jo/node/1"},
           {"title": "إعلان طرح عطاء توريد أجهزة شبكات", "url": "https://x.jo/node/2"}]
    req = [m.normalize(x) for x in ["عطاء", "tender"]]
    kept = [i for i in nav if any(r in m.normalize(i["title"] + " " + i["url"]) for r in req)]
    check("require_terms keeps tender links, drops homepage news", len(kept) == 1 and "عطاء" in kept[0]["title"])

    print("\n== 7. Site-specific tender pages (structures captured 2026-11-04) ==")
    YW = """<table id="ContentPlaceHolder1_GridView1">
<tr><th>رقم العطاء</th><th>اسم العطاء</th><th>a</th><th>b</th><th>c</th><th>d</th><th>اخر موعد للايداع</th><th>e</th><th>f</th><th>g</th><th>h</th></tr>
<tr><td>O-T-S-2026-0174</td><td>Consulting Services to Develop and Implement Policies, Procedures and Workflows across Yarmouk Water Company</td>
<td>4/11/2026</td><td>25/11/2026</td><td>-</td><td>-</td><td>30/11/2026</td><td>200</td><td><a href="ImageUpload/Doc1.pdf">عرض</a></td><td><a href="ImageUpload/Doc1.pdf">عرض</a></td><td>-</td></tr>
<tr><td>C – T – W – 2026-084</td><td>مشروع تمديد خط مياه في بلدة المكيفتة / حي الشاوي-محافظة المفرق</td>
<td>3/11/2026</td><td>12/11/2026</td><td>-</td><td>-</td><td>16/11/2026</td><td>25</td><td><a href="ImageUpload/C-T-W-2026-084.pdf">عرض</a></td><td>-</td><td>-</td></tr>
<tr><td colspan="11"><table><tr><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td><td>8</td><td>9</td><td>10</td><td>...</td></tr></table></td></tr>
</table>"""
    yw_src = {"css": "table#ContentPlaceHolder1_GridView1 tr", "columns": {"no": 0, "name": 1, "deadline": 6}}
    yw = m.parse_table(YW, "https://www.yw.com.jo/Tenders.aspx", 12, yw_src)
    check("Yarmouk Water: 2 tenders parsed, header + nested pager ignored", len(yw) == 2, f"got {len(yw)}")
    check("Yarmouk Water: deadline column shown in alert", any("deadline 30/11/2026" in i["title"] for i in yw))
    yw2 = m.parse_table(YW.replace("C – T – W – 2026-084", "C-T-W-2026-084").replace("16/11/2026", "20/11/2026"),
                        "https://www.yw.com.jo/Tenders.aspx", 12, yw_src)
    check("Yarmouk Water: dash/space variants + edited date -> same identity",
          {m.fingerprint("yw_tenders", i) for i in yw} == {m.fingerprint("yw_tenders", i) for i in yw2})
    check("Yarmouk Water: consulting tender not starred (policies/workflows, not IT)",
          not match(yw[0]["match_text"]))

    AHU = """<div id="ContentPlaceHolder1_Panel4924"><table>
<tr><th>رقم العطاء</th><th>عنوان العطاء</th><th>تاريخ الطرح</th><th>x</th><th>y</th><th>موعد فتح العروض</th><th>z</th><th>w</th><th>v</th><th>u</th></tr>
<tr class="style-table2"><td>9/2026</td><td>صيانة المرافق الصحية في الجامعة</td><td>2026/10/27</td><td>2026-11-01</td><td>2026-11-22</td><td>22/11/2026, 12:00</td><td>25 دينار</td><td><a href="/Admin_Site/x.pdf">ملف</a></td><td>إستدراج عروض</td><td>لجنة العطاءات</td></tr>
<tr class="style-table2"><td>10/2026</td><td>توريد وتركيب جدار ناري وأجهزة شبكات لمبنى الحاسوب</td><td>2026/11/04</td><td>2026-11-05</td><td>2026-11-20</td><td>20/11/2026, 12:00</td><td>50 دينار</td><td></td><td>إستدراج عروض</td><td>لجنة العطاءات</td></tr>
</table></div>"""
    ahu_src = {"css": "#ContentPlaceHolder1_Panel4924 tr", "columns": {"no": 0, "name": 1, "posted": 2, "opening": 5}}
    ahu = m.parse_table(AHU, "https://www.ahu.edu.jo/TenderAr.aspx?type=1&ID=4924&Ic=0", 12, ahu_src)
    check("AHU: 2 tenders parsed", len(ahu) == 2, f"got {len(ahu)}")
    check("AHU: firewall tender starred, sanitation not",
          bool(match(ahu[1]["match_text"])) and not match(ahu[0]["match_text"]))
    ahu_round2 = m.parse_table(AHU.replace("صيانة المرافق الصحية في الجامعة", "صيانة المرافق الصحية في الجامعة / للمرة الثانية"),
                               "https://www.ahu.edu.jo/x", 12, ahu_src)
    check("AHU: reused number with new round title -> NEW identity",
          m.fingerprint("ahu_tenders", ahu[0]) != m.fingerprint("ahu_tenders", ahu_round2[0]))

    CARC = """<nav><a href="/ar/node/1">الأخبار والتصريحات الصحفية الرسمية</a></nav>
<div class="news"><a href="/ar/node/1624">مجلس منظمة الطيران المدني الدولي يقر قرارا</a></div>
<div class="view-content"><div class="views-row"><a href="/ar/node/1691">عقد صيانة الاعمال الكهربائية والتكييف والهوائيات في المطارات</a>
<time datetime="2026-10-25">25</time><time datetime="2026-11-04">4</time><a href="/ar/node/1691">إقرأ المزيد</a></div></div>"""
    carc = m.parse_generic(CARC, "https://carc.gov.jo/ar/tenders/13", 12, {"css": "div.views-row"})
    check("CARC: only the tender row kept (news + menu + 'read more' dropped)",
          len(carc) == 1 and carc[0]["url"].endswith("/ar/node/1691"), f"got {[i['title'] for i in carc]}")
    check("CARC: empty current list parses to 0 items (not an error)",
          m.parse_generic("<div class='view-content'></div>", "https://carc.gov.jo/ar/tenders/13", 12,
                          {"css": "div.views-row"}) == [])

    httpd.shutdown()
    failed = [n for n, ok in results if not ok]
    print(f"\n{'='*50}\n{'ALL ' + str(len(results)) + ' CHECKS PASSED ✅' if not failed else 'FAILED: ' + ', '.join(failed) + ' ❌'}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
