# JONEPS – attributing tenders to the right organisation (procuring vs requesting)

Observed 2026-11-02 on 11,199 tenders (all deadlines from 01/01/2024 onward, plus 335 older keyword hits). Every detail page was fetched.

## TL;DR for the scraper

1. **The list row only shows the procuring entity (الجهة المشترية), by name, with no code.** The organisation the tender is
   actually *for* is never on the list row.
2. **The requesting entity is on the detail "general information" tab, labelled `الجهة المستفيدة`** ("beneficiary entity"),
   formatted `[orgNo]  name`. The search form calls the same thing "Requesting Entity / الجهة الطالبة" (`searchDeNo`).
   Cross-check: tenders with GPD as procuring and `الجهة المستفيدة = [270100000]` with 2026 deadlines = **115**, exactly what
   the list returns for `searchPeNo=150500000&searchDeNo=270100000`.
3. Attribution rule: `owner = الجهة المستفيدة if present else الجهة المشترية`. Compare on the **org code** in brackets, not the name.
   Names vary, e.g. `[270100000] JMOH وزارة الصحة` vs `وزارة الصحة`.
4. **Only two procuring entities have the requesting entity recorded in a structured field:**
   * **Government Procurement Department, دائرة المشتريات الحكومية `150500000`**: 1,511 tenders, **1,233** for another entity
     (goods, services and medicines). Top clients: MoH 396, MoE 190, Customs 97, Prince Hamza Hospital 93, MPWH 40, TRC 40.
   * **Government Tenders Department, دائرة العطاءات الحكومية `210200000`**: 246 tenders, **234** for another entity (works and technical services).
     Top clients: MPWH 170, MoH 11, Ministry of Youth 9.
   * **MoDEE (`320100000`) *does* buy IT for other ministries, but JONEPS doesn't record it.** None of its 87 tenders
     (2021: 16, 2025: 24, 2026: 47) has a `الجهة المستفيدة` row. **The real client appears only in the title** (Arabic and/or English), e.g.
     * 2025004433-01 العطاء الخاص بتوسعة رخصة VEEAM **لوزارة العدل** / "Veeam License expansion for MOJ"
     * 2025002801-05 مشروع تحديث الشبكة الداخلية **لوزارة الأشغال** / "Network upgrade for The Ministry of Public Works & Housing"
     * 2026001886-04 نظام الحوكمة والمخاطر والامتثال_ **رئاسة الوزراء**
     * 2026002109-03 إعادة هندسة الإجراءات **للمؤسسة العامة للضمان الاجتماعي**
     * 2026001755-04 شراء نظام كاميرات وربط فروع **وزارة الاشغال العامة والاسكان**
     * 2021 examples: laptops for MoE / MoH, Cisco support and NDR for MoFA (4202100017-03, 4202100014-03)

     Many others are MoDEE's own (Government Service Centres, the government cloud, the government data centre).
     **For MoDEE you need a title heuristic**: match `لوزارة|لدائرة|للمؤسسة|لهيئة|لرئاسة|التابع ل|for (the )?Ministry|for MOJ|…` followed by an
     entity name, mapped to the org list. GPD/GTD don't need this; use the structured field.
5. `الجهة المستفيدة` is also filled on most **medicine** tenders, but there it equals the procuring entity (MoH buying for MoH, 1,470 cases).
   Don't treat that as "on behalf".

## Where each field appears

| Field | List row (`/ep/invt/selectListTendInvitAL.do`) | Detail tab |
|---|---|---|
| Tender no. | col 1, `NNNNNNNNNN-SS` (SS = re-tender sequence). Amended invitations append `( دعوة معدلة)` in the same cell | `رقم العطاء` |
| Title | col 2, as entered (usually Arabic) | `اسم العطاء (عربي)` and `اسم العطاء (انجلبزي)`. The EN field is often just a copy of the Arabic. A real English title exists for 3,114 / 11,199 |
| Procuring entity | col 3, **name only** | `الجهة المشترية` → `[150500000]  دائرة المشتريات الحكومية` |
| Requesting entity | **absent** | `الجهة المستفيدة` → `[130100000]  وزارة الخارجية وشؤون المغتربين` (row missing when none) |
| Contract manager | absent | `الجهة المسؤولة عن ادارة العقد` → `الجهة الطالبة` (5,943), `الجهة المشترية` (251) or empty. On GPD/GTD tenders the **requesting** entity manages the contract |
| Tender type | col 4 | `نوع العطاء` |
| Sub-type | absent | `النوع الفرعي` (goods tab only). For all types, get it from the list by filtering `searchTendTypeCd2` |
| Publication / deadline | cols 5, 6 (dd/MM/yyyy) | `تاريخ النشر` (with time), `آخر موعد لايداع العروض` |
| Status / stage | 2nd `<tr>`: a progress bar `الاستفسار › الايداع › مفتوح › محال مبدئيا › محال نهائيا`, reached steps have `<a class="current">`. Or plain text such as `ملغي` | `حالة العطاء` (e.g. فعال، ملغي، قيد التقييم الكلي) + `مرحلة العطاء` (دعوة عطاء، فتح العروض، نشر الإحالة المبدئية/النهائية) |
| Department | absent | (Excel export column `الأقسام`; for GPD/GTD also the `searchDeptNo` filter) |

Traps:
* `اسم المستفيد` on the goods tab is the **beneficiary of the bid bond** (a person or office title), not the requesting entity.
* There is an HTML block `<!-- Demanding Entity Start --> … <!-- Demanding Entity End -->` on the services/works tabs. It was **empty in all 11,199 tenders**.
  The data is in the `الجهة المستفيدة` row instead.
* `عنوان الجهة المشترية` is always `[]`.

## The 5 tenders inspected (list row vs detail)

The first three were opened in the browser. The other two came from the same tab endpoints.

| Tender | List row shows | Detail `الجهة المشترية` | Detail `الجهة المستفيدة` | Notes |
|---|---|---|---|---|
| **2026003513-00** تجديد عقد صيانة نظام الاتصالات والشبكات لوزارة الخارجية | دائرة المشتريات الحكومية · اللوازم · 08/09/2026 · 29/09/2026 | `[150500000] دائرة المشتريات الحكومية` | `[130100000] وزارة الخارجية وشؤون المغتربين` | sub-type عقود الصيانة. IT maintenance for MoFA bought by GPD |
| **2026003971-00** شراء وتحديث نظام حماية الشبكة الخاص | دائرة المشتريات الحكومية · اللوازم · 30/09/2026 · 27/10/2026 | `[150500000] دائرة المشتريات الحكومية` | `[814300000] هيئة الاوراق المالية` | Network security for the Securities Commission. The title doesn't name the client at all, so you only learn it from the detail page. Status قيد التقييم الكلي / فتح العروض |
| **2026004465-00** العطاء المركزي رقم (109/2026) … مركز جمرك حدود الكرامة | دائرة العطاءات الحكومية · أشغال · 01/11/2026 · … | `[210200000] دائرة العطاءات الحكومية` | `[210100000] وزارة الأشغال العامة والاسكان` | Works page (`WorkDetails.do`). General info loads inline. GTD "central tender" (العطاء المركزي) naming |
| **2026004246-01** تجهيز البنية التحتية لأنظمة الشبكات، والألياف الضوئية | دائرة المشتريات الحكومية · اللوازم | `[150500000] دائرة المشتريات الحكومية` | `[160200000] وزارة الصناعة والتجارة والتموين / دائرة مراقبة الشركات` | sub-type برمجيات ومعدات حاسوب |
| **2026004492-00** Ponatinib 15 mg Tablet (control case) | وزارة الصحة · أدوية | `[270100000] وزارة الصحة` | `[270100000] JMOH وزارة الصحة` | Same code: **not** on-behalf. Name spelled differently |

Plus MoDEE cases 2026004162-01, 2026004068-03, 2026004419-00 and 2026004395-00: `الجهة المشترية = [320100000] وزارة الاقتصاد الرقمي والريادة`, no `الجهة المستفيدة` row,
and real English titles. MoDEE's on-behalf tenders such as 2025004433-01 (MoJ) look exactly the same structurally. Only the title tells them apart (see TL;DR 4).

## How to fetch the detail cheaply

You don't need to render the detail page. After `GET` of the list page (cookie + `_csrf`):

```
POST https://www.joneps.gov.jo<tab>
tendNo=2026003971&tendSeq=00&frameworkAgreementSeq=&tendTypeCd1=EP0011&searchConditions=&isFrameworkAgreementYn=N&_csrf=<token>
```

`<tab>` is chosen from the `fn_goDetail(...)` arguments on the list row (`tendCategCd`, `tendMthodCd`, `tendTypeCd1`):

| Condition | Tab with entities and titles |
|---|---|
| EP1313 (medicines) | `/ep/invt/medicine/generalInformation.do` |
| EP1312 (works / GTD), or method EP0022 / EP5021 | `/ep/invt/Work/generalInformation.do` |
| EP1311 and type EP0011 (goods) | `/ep/invt/goods/tenderInformation.do` |
| EP1311, other types (services) | `/ep/invt/service/generalInformation.do` |

Parse every `<th>` → next `<td>`. Strip the leading paragraph numbers (`1.1`) and `*`, and split `[code]  name`.
11,199 tabs took about 10.5 minutes with 4 parallel connections and 0 errors.

## Alternative without detail pages

`searchDeNo` filters by requesting entity on the list, so you can attribute a GPD/GTD tender by running the list once per requesting org
(`searchPeNo=150500000&searchDeNo=<org>`). This needs the org list (`joneps_codes.md`, 143 top-level orgs, plus sub-units such as hospitals,
e.g. `270100003` Prince Hamza Hospital, which are only reachable via `/um/org/selectOrgMidCdList.do`). Fetching detail pages is simpler and complete.
