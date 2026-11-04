#!/usr/bin/env python3
"""
Keyword calibration tool - answers "would our keywords have caught the real
historical tenders?"

Feed it a CSV of past tender titles (e.g. harvested from JONEPS / org archive
pages). Two modes:

1) Unlabeled - just a 'title' column (other columns ignored):
       python keyword_check.py harvest.csv
   Prints every title with the keywords it matched (or NO MATCH), so you can
   eyeball what the current config.yaml catches.

2) Labeled - add a 'relevant' column (1 = Seniors IT should have seen this,
   0 = not our business):
       python keyword_check.py harvest.csv
   Additionally reports RECALL (the number that matters: of all relevant
   tenders, how many we caught), lists every MISSED relevant tender so you can
   add the missing vocabulary to config.yaml, and lists false positives.

CSV encoding: UTF-8 (Excel: save as "CSV UTF-8"). Delimiter , or ; auto-detected.
Re-run after every config.yaml edit until recall is 100% on the harvest.
"""

import csv
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
import monitor as m  # noqa: E402


def read_rows(path):
    raw = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    delim = ";" if raw.splitlines()[0].count(";") > raw.splitlines()[0].count(",") else ","
    rows = list(csv.DictReader(raw.splitlines(), delimiter=delim))
    if not rows:
        sys.exit("CSV is empty")
    # find the title column case-insensitively (title / Tender Name / name ...)
    cols = {c.lower().strip(): c for c in rows[0].keys()}
    title_col = next((cols[c] for c in ("title", "tender name", "tender_name", "name", "اسم العطاء") if c in cols), None)
    if not title_col:
        sys.exit(f"No title column found. Columns: {list(rows[0].keys())}")
    rel_col = next((cols[c] for c in ("relevant", "match", "ours") if c in cols), None)
    return rows, title_col, rel_col


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    rows, title_col, rel_col = read_rows(sys.argv[1])
    cfg = m.load_yaml(BASE / "config.yaml")
    match = m.build_matcher(cfg)

    matched, unmatched = [], []
    for r in rows:
        title = (r.get(title_col) or "").strip()
        if not title:
            continue
        hits = match(title)
        rec = {"title": title, "hits": hits or [],
               "relevant": str(r.get(rel_col, "")).strip() in ("1", "true", "yes", "y") if rel_col else None}
        (matched if hits else unmatched).append(rec)

    print(f"\n{len(matched) + len(unmatched)} titles | matched: {len(matched)} | not matched: {len(unmatched)}\n")
    print("--- MATCHED " + "-" * 55)
    for r in matched:
        print(f"  [{', '.join(r['hits'][:4])}]  {r['title'][:110]}")
    print("\n--- NOT MATCHED " + "-" * 51)
    for r in unmatched:
        print(f"  {r['title'][:118]}")

    if rel_col:
        rel = [r for r in matched + unmatched if r["relevant"]]
        caught = [r for r in rel if r["hits"]]
        missed = [r for r in rel if not r["hits"]]
        fp = [r for r in matched if r["relevant"] is False]
        print("\n" + "=" * 68)
        print(f"RECALL:    {len(caught)}/{len(rel)} relevant tenders caught"
              + (f"  ({100*len(caught)/len(rel):.0f}%)" if rel else ""))
        print(f"PRECISION: {len(matched)-len(fp)}/{len(matched)} of matches were truly relevant" if matched else "")
        if missed:
            print(f"\n❌ MISSED relevant tenders ({len(missed)}) - add their vocabulary to config.yaml:")
            for r in missed:
                print(f"   - {r['title'][:118]}")
        else:
            print("\n✅ No relevant tender missed - keywords are safe on this dataset.")
        if fp:
            print(f"\n⚠ False positives ({len(fp)}) - fine to ignore (they're only highlighted, not exclusive):")
            for r in fp[:15]:
                print(f"   - [{', '.join(r['hits'][:3])}] {r['title'][:100]}")


if __name__ == "__main__":
    main()
