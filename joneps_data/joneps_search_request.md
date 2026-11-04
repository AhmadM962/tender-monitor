# JONEPS – "Search List of Tender Invitation" request

Captured 2026-11-02 in the browser (network log + the live form's `FormData`), then replayed and varied from a script. No login is needed.

## 1. Bootstrap (session + CSRF)

```
GET https://www.joneps.gov.jo/ep/invt/selectListTendInvitAL.do?menuId=EP03000000&upperMenuId=EP03020000&subMenuId=EP03020100
```

* Sets the session cookie (keep a cookie jar).
* The HTML has `<input type="hidden" name="_csrf" value="…">` (Spring Security). Every POST needs it, and it is bound to the session.
* The form is `<form name="frm_list" id="frm_list" method="post">` with no `action`. The Search button
  (`#btn_search`) calls `fn_goSearchAndSaveInSession('frm_list','/ep/invt/selectListTendInvitAL.do')`, which saves the criteria in
  session storage and submits the form.
* Language is per session: `GET /um/setLocale.do?lang=en` (or `lang=ar`). It only changes the labels. Titles and entity names in the list stay as entered (mostly Arabic).

## 2. The Search request (default values)

```
POST https://www.joneps.gov.jo/ep/invt/selectListTendInvitAL.do
Content-Type: application/x-www-form-urlencoded
Cookie: <session from step 1>
```

Body sent when Search is clicked with the default values, in order (URL-decoded; `_csrf` appears twice because the form has two hidden copies):

| # | Parameter | Default value | Notes |
|---|---|---|---|
| 1 | `_csrf` | `<token>` | required |
| 2 | `searchConditions` | `_csrf=…&currentPageNo=1&offSet=0&cache=true&_csrf=…&searchStartSubmDlineDt=02%2F10%2F2026&searchEndSubmDlineDt=02%2F01%2F2027&recordCountPerPage=10` | Echo of the previous criteria, used for the "back" navigation. Not needed (the server ignores it when omitted). |
| 3 | `download_token_value_id` | (empty) | Used only by the Excel download (cookie handshake for the spinner) |
| 4 | `currentPageNo` | `1` | pagination (1-based) |
| 5 | `offSet` | `0` | the page links just change `currentPageNo` via `fn_pageview(n)`. `offSet` can stay 0 |
| 6 | `screenType` | (empty) | |
| 7 | `cache` | `true` | `true`/`false`. Either works. |
| 8 | `_csrf` | `<token>` | second copy |
| 9 | `searchTendNo` | (empty) | Tender No |
| 10 | `searchTendNm` | (empty) | Tender Name (substring, matches the Arabic name field) |
| 11 | `searchTendTypeCd1` | (empty) | Tender Type (EP0011…) |
| 12 | `searchIntrlLocalTypeCd` | (empty) | Local/International |
| 13 | `tendTypeCd2Goods` | (empty) | visible sub-type select (Goods) |
| 14 | `tendTypeCd2GSDService` | (empty) | visible sub-type select (Services) |
| 15 | `tendTypeCd2GTDService` | (empty) | visible sub-type select (Technical services) |
| 16 | `tendTypeCd2Goods` | (empty) | visible sub-type select (Medicines – same *name* as Goods) |
| 17 | `searchTendTypeCd2` | (empty) | **effective sub-type filter** |
| 18 | `searchFundType` | (empty) | Source of fund |
| 19 | `searchTendStatCd` | (empty) | Tender Status |
| 20 | `searchFiscalYear` | (empty) | Fiscal Year |
| 21 | `searchTendMthodCd` | (empty) | Tender Method |
| 22 | `searchPeNo` | (empty) | Procuring Entity org no. (e.g. 150500000) |
| 23 | `peNm` | (empty) | its display name (not needed) |
| 24 | `searchDeNo` | (empty) | **Requesting Entity** org no. |
| 25 | `deNm` | (empty) | its display name (not needed) |
| 26 | `searchStartSubmDlineDt` | `02/10/2026` | Deadline from, `dd/MM/yyyy`. Default = today − 1 month |
| 27 | `searchEndSubmDlineDt` | `02/01/2027` | Deadline to. Default = today + 2 months |
| 28 | `searchStartPublicationYmd` | (empty) | Publication date from |
| 29 | `searchEndPublicationYmd` | (empty) | Publication date to |
| 30 | `clId` | (empty) | Classification code (UNSPSC) |
| 31 | `clNmAr` | (empty) | |
| 32 | `clNmEn` | (empty) | |
| 33 | `searchTendStatusCd` | (empty) | Tender Stage (`Opened`, `Initial_Awarded`, `Final_Awarded`) |
| 34 | `recordCountPerPage` | `10` | page size |

Result with the defaults on 2026-11-02: **748 results (page 1/75)**. The response is HTML: the table rows plus a footer
`748 النتائج(الصفحة 1/75)`. Thousands use a dot (`10.864`). In English: `Results(Page x/y)`.

Minimal working body for a script (all other fields can be empty or omitted):

```
_csrf=<token>&currentPageNo=1&recordCountPerPage=1000&searchStartSubmDlineDt=01/01/2024&searchEndSubmDlineDt=31/12/2027
```

## 3. Which fields are really required

| Field | Marked `*` | Actually required? | Observed |
|---|---|---|---|
| Deadline of Submission | yes | **No error if empty**, but then the server **falls back to the default window** (today −1 month … +2 months → 748) unless some other criterion is given | Empty dates with Tender Name `حاسوب` → 230 (all years). Empty dates with Fiscal Year 2025 → 4,078 |
| Classification Name | yes | **No.** Search works without it, **and `clId` is ignored by the server** | 2026 window: 3,751 with no class, with `clId=43`, `4323`, `432115`, `43211503` (with/without names) |

Other server behaviours worth knowing:

* **`recordCountPerPage` is not capped**: 500, 1000 and 2000 all work. The whole 2024-to-now set (10,864 rows) comes back in 11 pages of 1000 (about 10–20 s each).
* **Tender Name search ignores the deadline range.** `حاسوب` returns 230 with 2026 dates, 2024–2027 dates, 2018–2027 dates or no dates. Keyword searches are effectively all-time.
* The name search matches the **Arabic** name (`software` → only 2 hits, `حاسوب` → 230).
* **Fiscal Year overrides the deadline range** (FY2025 gives 4,078 with or without the default dates).
* Publication-date-only search (no deadline) returned 0. Use the deadline range.
* `searchPeNo` and `searchDeNo` both filter and can be combined (2026: GPD 150500000 = 433, MoH 270100000 as requesting = 1,235, GPD for MoH = 115).

## 4. Row format in the response

Each tender is two `<tr>` rows inside the results table:

```html
<tr>
  <td><a onclick="fn_goDetail('2026004485','00','','EP1311','' ,'EP0061', 'EP0021', 'EP0011');">2026004485-00</a></td>
  <td><a onclick="fn_goDetail(…)">شراء مركبة صالون كهربائية</a></td>
  <td>هيئة تنظيم قطاع الطاقة والمعادن</td>   <!-- Procuring entity (name only, no code) -->
  <td>اللوازم</td>                            <!-- Tender type -->
  <td>01/11/2026</td>                         <!-- Publication date -->
  <td>15/11/2026</td>                         <!-- Deadline -->
</tr>
<tr><td colspan=6> الاستفسار الايداع مفتوح محال مبدئيا محال نهائيا </td></tr>   <!-- stage links, or e.g. "ملغي" -->
```

`fn_goDetail(tendNo, tendSeq, frameworkAgreementSeq, tendCategCd, workType, intrlLocalTypeCd, tendMthodCd, tendTypeCd1)`.
`tendCategCd`: EP1311 = goods/services, EP1312 = works (GTD), EP1313 = medicines.

## 5. Detail page and data tabs

`fn_goDetail` POSTs `frm_list` to one of:

| Condition | Page |
|---|---|
| `EP1311` and method not EP0022/EP5021, type EP0011 | `/ep/invt/GoodsDetails.do` |
| `EP1311`, other types | `/ep/invt/ServiceDetails.do` |
| `EP1312`, or method EP0022 (pre-qual) / EP5021 (EOI) | `/ep/invt/WorkDetails.do` |
| `EP1313` | `/ep/invt/MedicineDetails.do` |
| otherwise | `/ep/invt/WorkUnspscDetails.do` |

…with query `?tendNo=…&tendSeq=…&frameworkAgreementSeq=…&tendCategCd=…&workType=…&intrlLocalTypeCd=…&tendMthodCd=…&invtYn=Y&searchConditions=`.
That page is just a shell. Its tabs load via `fn_selectAllData()` →
`POST <tab url>` with `tendNo, tendSeq, frameworkAgreementSeq, tendTypeCd1, searchConditions, isFrameworkAgreementYn=N, _csrf`.
The "general information" tab, the one that holds entities and titles:

| Category | Tab URL |
|---|---|
| Goods | `/ep/invt/goods/tenderInformation.do` (also has sub-type) |
| Services | `/ep/invt/service/generalInformation.do` (+ `/ep/invt/service/tenderInformation.do`) |
| Works / pre-qual / EOI | `/ep/invt/Work/generalInformation.do` (+ `/ep/invt/Work/tenderInformation.do`) |
| Medicines | `/ep/invt/medicine/generalInformation.do` (+ `/ep/invt/medicine/tenderInformation.do`) |

These calls work directly with only the session cookie and `_csrf`. You don't need to open the shell page first.

## 6. Exports

* **Excel** (`تحميل ملف إكسل`, `#btn_download`): `POST https://www.joneps.gov.jo/joneps-reports/ep/invt/downloadDetailTendInvit.do` with the
  same `frm_list` body (+ `download_token_value_id=<ms timestamp>`). Returns `tend_report[].xlsx` with two sheets: "قائمة العطاءات" (search header block, then
  one row per tender) and "الإحصائيات". Columns: حالة العطاء, مرحلة العطاء, تاريخ نشر قرار الإحالة, تاريخ نشر نتائج التقييم, تاريخ النشر,
  آخر موعد لتقديم العروض, نوع العطاء, الجهة المشترية, أسلوب طرح العطاء, الأقسام, اسم العطاء, رقم العطاء.
  It has **no** requesting entity, sub-type or English title.
  **Don't rely on it for bulk export.** Every call returned **exactly 44 tender rows**, whatever the deadline range (2024, 2025, 2026–27),
  `recordCountPerPage=1000`, `currentPageNo=2`, `cache=true` or `searchPeNo=150500000`. The 2025 and GPD-filtered calls even returned the
  same first row. The header block echoes the requested dates, but the rows don't follow the filters. Three sample exports are in `raw/`.
  The list POST with a large `recordCountPerPage` is the reliable bulk path.
* **OCDS JSON** (`#btn_download_ocds`): `POST /ep/invt/downloadOCDSJSON.do` returns `joneps_tenders.json` with **0 bytes** (tested with and without
  a cached search, and with a single tender number). It doesn't work as of 2026-11-02.
