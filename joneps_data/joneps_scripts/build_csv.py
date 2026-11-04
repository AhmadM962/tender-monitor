"""Merge list + subtype + keyword + details + Excel status into harvest.csv (UTF-8, no BOM)."""
import sys, os, json, csv, re, glob
import openpyxl

OUT, DEST = sys.argv[1], sys.argv[2]
L = lambda n: json.load(open(os.path.join(OUT, n), encoding="utf-8"))
rows, sub, kw, det = L("list.json"), L("subtype.json"), L("keywords.json"), L("details.json")

# Excel: status + stage per tender_no
xl = {}
for fn in sorted(glob.glob(os.path.join(OUT, "joneps_export_deadline_*.xlsx"))):
    ws = openpyxl.load_workbook(fn, read_only=True).worksheets[0]
    hdr = None
    for r in ws.iter_rows(values_only=True):
        if hdr is None:
            if r and "رقم العطاء" in r and "حالة العطاء" in r: hdr = {v: i for i, v in enumerate(r) if v}
            continue
        no = (r[hdr["رقم العطاء"]] or "").strip()
        if no: xl[no] = {"status": (r[hdr["حالة العطاء"]] or "").strip(), "stage": (r[hdr["مرحلة العطاء"]] or "").strip(),
                         "method": (r[hdr["أسلوب طرح العطاء"]] or "").strip(), "dept": (r[hdr["الأقسام"]] or "").strip()}

def clean(s): return " ".join((s or "").split())
def strip_code(s):
    m = re.match(r"\[(\d*)\]\s*(.*)", s or "")
    return (m.group(2).strip(), m.group(1)) if m else ((s or "").strip(), "")

allrows, kwhits = {}, {}
for x in rows: allrows[x["tender_no"]] = x
for t, rr in kw.items():
    for x in rr:
        allrows.setdefault(x["tender_no"], x); kwhits.setdefault(x["tender_no"], []).append(t)
# the tender-no cell may carry an amendment marker, e.g. "2026002223-00 ( دعوة معدلة)"
def norm_no(raw):
    m = re.match(r"\s*(\d+-\d+)\s*(.*)", raw)
    return (m.group(1), clean(m.group(2)).strip("() ")) if m else (raw, "")

COLS = ["tender_no", "title", "title_en", "tender_type", "sub_tender_type", "procuring_entity", "requesting_entity",
        "publication_date", "deadline", "status", "relevant"]
out, stats = [], {"title_en": 0, "requesting": 0, "differs": 0, "detail_missing": 0, "status_from_list": 0}
for no, x in allrows.items():
    d = det.get(no, {}); kv = d.get("kv") or {}
    if not kv or "_error" in kv: stats["detail_missing"] += 1
    title = clean(kv.get("اسم العطاء (عربي)")) or clean(x["title"])
    en = clean(kv.get("اسم العطاء (انجلبزي)"))
    if en == title: en = ""          # portal copies the Arabic name into the EN field when none is given
    if en: stats["title_en"] += 1
    pe_name, pe_code = strip_code(clean(kv.get("الجهة المشترية")))
    pe = clean(x["procuring_entity"]) or pe_name
    if pe_code: pe = f"{pe} [{pe_code}]"
    de_raw = clean(kv.get("الجهة المستفيدة")) or clean(d.get("de_block") or "")
    de_name, de_code = strip_code(de_raw)
    if de_code and not de_name: de_name = ""      # medicine pages sometimes show only the code
    de = f"{de_name} [{de_code}]".strip() if de_code else de_name
    if de: stats["requesting"] += 1
    if de_code and pe_code and de_code != pe_code: stats["differs"] += 1
    st = xl.get(no)
    dst = [clean(kv.get("حالة العطاء")), clean(kv.get("مرحلة العطاء"))]
    if any(dst): status = " / ".join(v for v in dst if v)
    elif st: status = " / ".join(v for v in (st["status"], st["stage"]) if v)
    else:
        sr = clean(x.get("status_row"))
        status = "" if sr.startswith("الاستفسار") else sr; stats["status_from_list"] += 1
    clean_no, marker = norm_no(no)
    if marker: status = f"{status} ({marker})" if status else marker
    out.append({"tender_no": clean_no, "title": title, "title_en": en, "tender_type": clean(x["tender_type"]),
                "sub_tender_type": sub.get(no, "") or clean(kv.get("النوع الفرعي")), "procuring_entity": pe,
                "requesting_entity": de, "publication_date": x["publication_date"], "deadline": x["deadline"],
                "status": status, "relevant": ""})
out.sort(key=lambda r: r["tender_no"], reverse=True)
with open(DEST, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, COLS); w.writeheader(); w.writerows(out)
json.dump({no: v for no, v in kwhits.items()}, open(os.path.join(OUT, "keyword_hits.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(len(out), "rows;", "excel status for", len(xl), stats)
