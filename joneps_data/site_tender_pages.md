# Tender list pages: Yarmouk Water, AHU, CARC

Checked 2026-11-04. Read-only, no login. The raw HTML was fetched with curl, and the pages were opened in a browser as a cross-check.

## Summary

| Site | Current-tenders URL | Rows in the raw HTML? | Pagination | Live rows on 2026-11-04 |
|---|---|---|---|---|
| Yarmouk Water | https://www.yw.com.jo/Tenders.aspx | Yes (ASP.NET GridView) | Yes: 40 rows per page, by POST postback | 40 on page 1; total unknown |
| AHU | https://www.ahu.edu.jo/TenderAr.aspx?type=1&ID=4924&Ic=0 | Yes (ASP.NET ListView) | None seen | 5 |
| CARC | https://carc.gov.jo/ar/tenders/13 | Yes (Drupal view) | None while empty; archive uses `?page=N` | 0 (list is empty) |

None of the three needs a JavaScript-rendering browser to read the first page. Only Yarmouk needs a POST to reach later pages.

---

## 1. Yarmouk Water Company

- **Current list:** https://www.yw.com.jo/Tenders.aspx (menu: "عطــــاءات قيد الإحالة"; page title "العطــــــاءات المطروحــــة")
- **Archive:** https://www.yw.com.jo/ArchTenders.aspx (only 3 columns: number, name, PDF link)

**Loading:** plain server-rendered HTML. The rows are in the raw response, in `table#ContentPlaceHolder1_GridView1`. The browser cross-check did not finish because the page was still loading, but it is not needed to read the rows.

**How a tender appears:** one table row with 11 columns:

رقم العطاء, اسم العطاء, تاريخ البدء في بيع الوثائق, تاريخ انتهاء بيع الوثيقة, تاريخ اخر موعد للاستفسار, تاريخ الموعد النهائي للرد على الاستفسار, اخر موعد للايداع, ثمن نسخة الاعلان, نسخة الاعلان, ملاحق, الاحالة الاولية

The last three columns are "عرض" links to `ImageUpload/<file>.pdf`.

| Number | Name | Sale start | Sale end | Deposit deadline | Price | Announcement PDF |
|---|---|---|---|---|---|---|
| O-T-S-2026-0174 | Consulting Services to Develop and Implement Policies, Procedures and Workflows across Yarmouk Water Company | 4/11/2026 | 25/11/2026 | 30/11/2026 | 200 | `ImageUpload/وثيقة العطاء.pdf` (URL-encoded in the HTML) |
| YWC-FARA-IV-2.3.2/2026 | Supply of maintenance water network materials | 3/11/2026 | 15/11/2026 | 16/11/2026 | 250 | `ImageUpload/Supply of maintenance water network materials-27-9-2026 قطع مواسير.pdf` (URL-encoded in the HTML) |
| C – T – W – 2026-084 | مشروع تمديد خط مياه في بلدة المكيفتة / حي الشاوي-محافظة المفرق | 3/11/2026 | 12/11/2026 | 16/11/2026 | 25 | `ImageUpload/C-T-W-2026-084.pdf` |

**Pagination: yes.**
- 40 rows per page, using `javascript:__doPostBack('ctl00$ContentPlaceHolder1$GridView1','Page$N')`.
- There is no URL parameter for the page. To get page N, POST back the page's hidden fields (`__VIEWSTATE` etc.) with `__EVENTTARGET=ctl00$ContentPlaceHolder1$GridView1` and `__EVENTARGUMENT=Page$N`. This worked for pages 2 and 11.
- The list is roughly newest-first: page 1 runs from 4/11/2026 back to about 24/9/2026, and page 2 starts at 21/9/2026 and ends at 19/7/2026. Page 11 starts in June 2025.
- The pager on page 11 links to at least page 18, so there are many pages. **The total is unknown:** the server reset the connection when I tried to walk every page with 1 second between requests, and it failed before reaching page 5. A normal GET worked again 20 seconds later, so keep requests slow.

**Parsing notes:**
- Page 1 alone covers about 6 weeks, so it should be enough for routine monitoring if checked regularly.
- The list is not only open tenders. It reaches back to 2025, so filter on the deposit deadline.
- Dates are hand-typed and inconsistent. Real examples: `4/11/2026`, `28-10-2026`, `2/112026`, `10/9/2029` (likely a typo for 2026), and `-` for an empty value.
- Tender numbers vary in format (`C – T – W – 2026-084` uses en dashes and spaces; `2026/152/O/T/S` uses slashes). Normalize them before comparing.
- Do not treat a PDF URL as a unique tender ID. Some names are generic (`وثيقة العطاء.pdf`), and `Doc1.pdf` plus the "لا يوجد ملاحق…" and "لم يتم اصدار قرار الإحالة" PDFs are shared placeholders.

---

## 2. Al-Hussein Bin Talal University (AHU)

- **Current list:** https://www.ahu.edu.jo/TenderAr.aspx?type=1&ID=4924&Ic=0 (homepage: "بوابة العطاءات" > "إعلانات العطاءات" > "لعرض جميع الإعلانات")
- **Final awards:** https://www.ahu.edu.jo/TenderAr.aspx?type=1&ID=4917&Ic=0 (20 rows)
- **Archive menu:** https://www.ahu.edu.jo/TenderAr.aspx?type=1&ID=4960&Ic=0 (links to IDs 4959 and 4954)
- **Search:** https://www.ahu.edu.jo/TenderAr.aspx?ID=0&Type=11&Keyword=

**Loading:** plain server-rendered HTML. The rows are in the raw response, inside `#ContentPlaceHolder1_Panel4924`, as `tr.style-table2`. The browser showed the same 5 rows with no XHR or fetch requests. The page source contains `$.ajax` calls, but their endpoint names (such as `InsertPersonAuthorities`) look unrelated to the tender list.

**How a tender appears:** one table row with 10 columns:

رقم العطاء, عنوان العطاء, تاريخ الطرح, تاريخ تقديم العروض, تاريخ انتهاء بيع النسخ, موعد فتح العروض عند اكتمالها, ثمن النسخة, ملفات مرفقة, اسلوب الشراء, اسم اللجنة

Attachment links look like `/Admin_Site/Articles/Images/<a>/<id>/Gal/<file>`.

| Number | Title | Posted | "Offers" date | "Sale end" date | Opening | Price | Method | Attachment |
|---|---|---|---|---|---|---|---|---|
| 9/2026 | صيانة المرافق الصحية في الجامعة | 2026/10/27 | 2026-11-01 | 2026-11-22 | 22/11/2026, 12:00 | 25 دينار | إستدراج عروض | `/Admin_Site/Articles/Images/-1/51921/Gal/main_b_ UNIVERSITY-2.pdf` |
| 8/2026 | صيانة وتبديل العازل المطري لعدد من مباني الجامعة | 2026/10/20 | 2026-10-25 | 2026-11-08 | 8/11/2026, 12:00 | 50 دينار | إستدراج عروض | `/Admin_Site/Articles/Images/4924/50911/Gal/3zeel.pdf` |
| 9/2025 | تأجير اكشاك فارغة على بوابة الطلبة | 2026/4/28 | 2026-04-28 | 2026-12-31 | لحين اكتمال العروض المناسبة | 25 دينار | عطاء - مناقصة عامة | `/Admin_Site/Articles/Images/-1/48628/Gal/akshak_New1.pdf` |

**Pagination: none seen.** All 5 rows are on one page, with no pager markup. The list is ordered newest-first by posted date. A pager could still appear if the list grows.

**Parsing notes:**
- The labelled dates look misleading. "تاريخ انتهاء بيع النسخ" matches the opening date in the rows above, and "تاريخ تقديم العروض" falls before it, so it may be a start date. Confirm against a tender PDF before relying on either as the deadline.
- Date formats differ by column (`2026/10/27`, `2026-11-22`), and the opening column is free text.
- Attachments are not always PDFs (`insu5.jpeg`), and file names can contain spaces, so URL-encode them.
- Numbers get reused across rounds and titles change (`9/2025` also appears in the awards list with "/ للمرة الثالثة"), so compare the number and title together.
- The awards list (ID 4917) includes tenders that are still open, with empty award fields, so a row there does not mean the tender was awarded.
- The homepage has an initial-awards tab ("الإحالات المبدئية"), which currently reads "لا يوجد إحالات مبدئية حالياً". No dedicated list URL for it appears in the homepage links.

---

## 3. CARC (Civil Aviation Regulatory Commission)

- **Current list:** https://carc.gov.jo/ar/tenders/13 ("العطاءات الحالية")
- **Archive:** https://carc.gov.jo/ar/tenders/12 ("العطاءات المؤرشفة")
- **Landing page:** https://carc.gov.jo/ar/tenders only links to those two lists and has no tenders itself.

**Loading:** plain server-rendered Drupal HTML. The archive rows are in the raw response, and the browser made no separate data request for the empty current list. Drupal's `ajax.js` loads on the page, but it was not used to fetch rows.

**The current list is empty today.** The raw HTML and the browser both show only the title search box, with no rows. **The examples below therefore come from the archive.** I am assuming the current list uses the same row format, but that could not be checked until a tender is listed there.

**How a tender appears:** a `div.views-row` containing a title link to `/ar/node/<id>`, two `<time datetime="...">` elements (start and end), and a "إقرأ المزيد" link.

| Title | Start | End | Link |
|---|---|---|---|
| عقد صيانة الاعمال الكهربائية والتكييف والهوائيات في المطارات والمحطات الخارجية ومباني الهيئة | 2026-10-25 | 2026-11-04 | https://carc.gov.jo/ar/node/1691 |
| توريد قطع غيار نظام الاتصال الصوتي في مطار الملكة علياء الدولي | 2026-07-03 | 2026-07-08 | https://carc.gov.jo/ar/node/1641 |
| بيع مواد غير صالحة في مستودعات مطار الملكة علياء الدولي | 2025-12-28 | 2026-01-20 | https://carc.gov.jo/ar/node/1547 |

The tender number and price appear only on the detail page. For node 1691 these are "رقم العطاء: 8/3/40/2026" and "ثمن النسخة: 50". That page also has a "الملف" field, but I did not determine its link format.

**Pagination:**
- Current list: no pager while empty. It may use `?page=N` once it has enough rows, like the archive.
- Archive: 10 rows per page with a GET parameter (`?page=1`, `?page=2`; numbering starts at 0). It has at least 3 pages.

**Parsing notes:**
- The first archive row ended on the day of this check (2026-11-04) and had already moved to the archive. Tenders may be archived on their closing date, so a tender could be missed if checks are too far apart.
- Use the node ID as the unique key. The dates are clean ISO values in the `datetime` attribute.
- An empty current list is normal for this site, so it should not be treated as a scraper failure. Checking that the search box is present would confirm the page loaded correctly.
