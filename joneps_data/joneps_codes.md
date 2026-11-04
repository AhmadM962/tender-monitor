# JONEPS – search filter codes

Captured 2026-11-02 from the public form at `/ep/invt/selectListTendInvitAL.do` (the `<select>` options in the page HTML, Arabic UI and English UI via `/um/setLocale.do?lang=en`). An empty value means "All" / "no filter".

## Tender Type (نوع العطاء)

POST field: `searchTendTypeCd1`. Its `onchange` runs `selectTenderSubType()`, which only shows/hides one of four pre-rendered sub-type `<select>`s (no AJAX).

| Code | Arabic | English |
|---|---|---|
| `(empty)` | ::: الجميع | ::: All |
| `EP0011` | اللوازم | Goods |
| `EP0012` | خدمات | Services |
| `EP0014` | خدمات فنية | Technical Services |
| `EP0015` | أشغال | Works |
| `EP0016` | أدوية | Medicines |

## Sub Tender Type (نوع العطاء الفرعي) – one list per tender type

The value actually used by the server is the hidden field **`searchTendTypeCd2`** (set by `setTendTypeCode2(this.value)`). The visible selects are also posted: `tendTypeCd2Goods` (Goods), `tendTypeCd2GSDService` (Services), `tendTypeCd2GTDService` (Technical Services), and the Medicines select, which has id `tendTypeCd2Medicine` but is **also named `tendTypeCd2Goods`**. Works (`EP0015`) has no sub-type list. In a scraper, set `searchTendTypeCd1` + `searchTendTypeCd2` (+ the matching visible field) together.

### EP0011 Goods / اللوازم

| Code | Arabic | English |
|---|---|---|
| `EP0101` | الأثاث والأواني المنزلية | Furniture and household utensils |
| `EP0102` | القرطاسية والمنشورات والأختام | Stationery, publications and seals |
| `EP0103` | التوصيلات والتجهيزات والأجهزة | Connections and fittings, devices |
| `EP0104` | معدات وكاميرات وطباعة وحاسبة | Equipment and cameras, printing and calculator |
| `EP0105` | المستلزمات البيطرية والزراعية | Veterinary supplies and agricultural |
| `EP0106` | جمارك الرصاص | Lead customs |
| `EP0107` | الأجهزة والمعدات الرياضية | Devices and sports equipment |
| `EP0108` | آلات ومعدات | Machinery and equipment |
| `EP0109` | البواب | The concierge |
| `EP0110` | أجهزة الكمبيوتر ومعدات الموسيقى | Computers and music equipment |
| `EP0111` | قطع غيار / زيوت وشحوم | Parts / oils and greases |
| `EP0112` | المركبات والآليات والإطارات | Compounds, mechanisms and frames |
| `EP0113` | لوازم التطعيم | Supplies vaccination |
| `EP0114` | حقائب بلاستيكية | Plastic bags |
| `EP0115` | صوتيات | Audios |
| `EP0116` | الأجهزة البيطرية الزراعية | Agricultural veterinary devices |
| `EP0117` | أجهزة ميكانيكية | Mechanical devices |
| `EP0118` | أجهزة الكترونية | Electrical devices |
| `EP0119` | كيماويات مواد البناء والدهانات | Chemicals building materials and paints |
| `EP0120` | أحبار | Inks |
| `EP0121` | المواد الاستهلاكية والملحقات الطبية | Medical consumables and accessories |
| `EP0122` | العلاجات والأدوية | Treatments and drugs |
| `EP0123` | الملابس والمنسوجات | Clothing and Textiles |
| `EP0124` | أجهزة الكمبيوتر وملحقاتها | Computer hardware and accessories |
| `EP0125` | الإمدادات الغذائية والمواد الخام | Food supplies and raw materials |
| `EP0126` | برمجيات ومعدات حاسوب | Software and Hardware |
| `EP0127` | عقود الصيانة | Maintenance contracts |
| `EP0128` | سائل البطاريات | Batteries liquid |
| `EP0129` | أثاث طبي | Medical furniture |
| `EP0130` | اللوازم الأخرى | Other supplies |
| `EP0131` | اللوازم ومواد طب الأسنان | Supplies and dental materials |
| `EP0132` | أجهزة الاتصال | Communication devices |
| `EP0133` | معدات المكتب | Office Equipment |
| `EP0134` | المعدات الطبية والمختبرات | Medical equipment and laboratory |
| `EP0150` | تجهيزات طبية متنوعة | Various medical equipment |
| `EP0151` | مشتقات نفطية | Oil derivatives |
| `EP0152` | اجهزة كهربائية | Electrical devices |
| `EP0153` | خدمات قانونية | Legal services |

### EP0012 Services / خدمات

| Code | Arabic | English |
|---|---|---|
| `EP0201` | خدمات التأمين | Insurance services |
| `EP0202` | النظافة والنقل الداخلي وخدمات الطعام | Cleaning and internal transport and food services |
| `EP0203` | خدمات الغسيل والبستنة والرسائل | Laundry, gardening and messaging services |
| `EP0204` | خدمات الطباعة | Printing services |
| `EP0205` | خدمات الأعلاف | Feed services |
| `EP0206` | خدمات التنظيف الداخلي والإزالة والغسيل والمطاعم | Internal cleaning, removal, laundry and catering services |
| `EP0207` | خدمات التنظيف والكونسيرج | Cleaning and concierge services |
| `EP0208` | النظافة والنقل الداخلي وخدمات الطعام | Cleaning and internal transport and food services |
| `EP0209` | خدمات النظافة والنقل الداخلي والغسيل | Cleaning and internal transportation and laundry services |
| `EP0210` | خدمات النقل الداخلي | Internal transport services |
| `EP0211` | خدمات الصيانة والتحويل الداخلي | Maintenance services and internal transfer |
| `EP0212` | خدمات الأمن والحراسة | Security and guard services |
| `EP0213` | خدمات تنظيف | Cleaning services |
| `EP0214` | خدمات التنظيف والنقل الداخلي | Internal cleaning and transport services |
| `EP0215` | خدمات صيانة | Maintenance services |
| `EP0216` | خدمات تدقيق | Auditing services |
| `EP0217` | خدمات الاسكان | Housing services |
| `EP0218` | خدمات استشارية ودراسات | consultant services and researches |
| `EP0997` | خدمات إلكترونية | Electronic Services |

### EP0014 Technical Services / خدمات فنية

| Code | Arabic | English |
|---|---|---|
| `EP1123` | تصميم | Design |
| `EP1124` | إشراف | Supervision |

### EP0016 Medicines / أدوية

| Code | Arabic | English |
|---|---|---|
| `EP0401` | أدوية الأوعية الدموية والقلب | Medications for Cardiovascular and Heart Diseases |
| `EP0402` | أدوية المضادات الحيوية | Antibiotics |
| `EP0403` | أدوية الجهاز التنفسي والأنف والأذن والحنجرة | Respiratory, Nasal, Ear, and Throat Medications |
| `EP0404` | أدوية الجهاز الهضمي | Gastrointestinal Medications |
| `EP0405` | أدوية الغدد الصماء والنسائية والتوليد والجهاز التناسلي البول | Endocrine, Gynecological, Obstetric, and Urinary Reproductive System Medications |
| `EP0406` | أدوية الجهاز العصبي والجهاز العضلي العظمي | Neurological and Musculoskeletal Medications |
| `EP0407` | أدوية العيون | Eye Medications |
| `EP0408` | أدوية المناعة والسرطان | Immunological and Cancer Medications |
| `EP0409` | أدوية الدم والمغذيات | Blood and Nutritional Medications |
| `EP0410` | الأمصال والمطاعيم ومشتقات الدم ومضادات التسمم | Serums, Vaccines, Blood Derivatives, and Antitoxins |
| `EP0411` | أدوية الجلدية | Dermatological Medications |
| `EP0412` | أدوية التخدير | Anesthetic Medications |
| `EP0413` | أدوية الإيدز | HIV/AIDS Medications |
| `EP0414` | المواد التشخيصية | Diagnostic Agents |
| `EP0415` | أدوية الإقلاع عن التدخين | Smoking Cessation Medications |
| `EP0416` | أدوية تنظيم الأسرة | Family Planning Medications |
| `EP0417` | مادة حليب الرضع والأطفال | Infant and Pediatric Formula |

## Tender Status (حالة العطاء)

POST field: `searchTendStatCd`. Note two different codes share the label "Modified Tender Invitation" (EP0190, EP0856).

| Code | Arabic | English |
|---|---|---|
| `(empty)` | ::: الجميع | ::: All |
| `EP0859` | ارجاع حالة العطاء | Return tender status |
| `EP0035` | اعادة طرح العطاء | Re-Tendered |
| `EP0854` | تجميد | Freeze |
| `EP0560` | تم نشر نتائج الفتح الفني | Technical opening have been published |
| `EP0561` | تم نشر نتائج الفتح المالي | Financial  opening have been published |
| `EP0190` | دعوة معدلة | Modified Tender Invitation |
| `EP0856` | دعوة معدلة | Modified Tender Invitation |
| `EP0032` | معدل | Amended |
| `EP0034` | ملغي | Canceled |

## Tender Method (أسلوب طرح العطاء)

POST field: `searchTendMthodCd`

| Code | Arabic | English |
|---|---|---|
| `(empty)` | ::: اختيار | ::: select |
| `EP0022` | التأهيل المسبق | Open Competitive Tendering with Pre-Qualification |
| `EP5021` | التعبير عن الأهتمام | Open Competitive Tendering with Expression of Interest |
| `EP0027` | الشراء من مصدرواحد (التلزيم) | Single Source Tendering (Direct bidding) |
| `EP0021` | المناقصة العامة | Open Competitive Biddings/One-Envelope |
| `EP0025` | المناقصة المحدودة (الأستدراج) | Limited Biddings/One-Envelope |
| `EP0026` | المناقصة المحدودة مغلفين (الأستدراج) | Limited Biddings/Two-Envelopes(Technical + Financial) |
| `EP0023` | تأهيل مسبق (مغلفين) | Open Competitive Tendering with Pre-Qualification + Two-Stages |
| `EP1122` | شراء خدمات الأستشاريين الأفراد | Individual Consultant Services |
| `EP0024` | مناقصة عامة مغلفين | Open Competitive Biddings/Two-Envelopes (Technical + Financial) |

## Tender Stage (مرحلة العطاء)

POST field: `searchTendStatusCd`. Text codes, not EPxxxx.

| Code | Arabic | English |
|---|---|---|
| `(empty)` | ::: اختيار | ::: select |
| `Opened` | مفتوح | Opened |
| `Initial_Awarded` | محال مبدئيا | Initial Awarded |
| `Final_Awarded` | محال نهائيا | Final Awarding |

## Local / International (محلي/دولي)

POST field: `searchIntrlLocalTypeCd`

| Code | Arabic | English |
|---|---|---|
| `(empty)` | ::: الجميع | ::: All |
| `EP0061` | محلي | Local |
| `EP0062` | دولي | International |

## Fiscal Year (السنة المالية)

POST field: `searchFiscalYear`. **When a fiscal year is set the server ignores the deadline date range** (FY2025 → 4,078 results with or without dates).

| Code | Arabic | English |
|---|---|---|
| `(empty)` | ::: اختيار | ::: select |
| `2018` | 2018 | 2018 |
| `2019` | 2019 | 2019 |
| `2020` | 2020 | 2020 |
| `2021` | 2021 | 2021 |
| `2022` | 2022 | 2022 |
| `2023` | 2023 | 2023 |
| `2024` | 2024 | 2024 |
| `2025` | 2025 | 2025 |
| `2026` | 2026 | 2026 |

## Source of Fund (مصدر التمويل) – bonus

POST field: `searchFundType`

| Code | Arabic | English |
|---|---|---|
| `(empty)` | ::: اختيار | ::: select |
| `EP1076` | خزينة | Treasury |
| `EP1061` | وطني | National |
| `EP1062` | MCC | MCC |
| `EP1063` | KFW | KFW |
| `EP1064` | AFD | AFD |
| `EP1065` | USAID | USAID |
| `EP1066` | EBRD | EBRD |
| `EP1067` | EU | EU |
| `EP1068` | AECID | AECID |
| `EP1069` | EDCF | EDCF |
| `EP1070` | UNEP | UNEP |
| `EP1071` | UAE/ABUDHABI | UAE/ABUDHABI |
| `EP1072` | EIA | EIA |
| `EP1073` | KOICA | KOICA |
| `EP1074` | JICA | JICA |
| `EP1075` | World Bank | World Bank |
| `EP1078` | شراء على حساب | Purchase on account |
| `EP1077` | اخرى | Others |
| `EP1079` | منظمة العمل الدولية | International Labour Organization |

## Results per page

POST field: `recordCountPerPage`. The UI offers 5–20, but **the server accepts any value** (500, 1000 and 2000 were all honoured).

| Code | Arabic | English |
|---|---|---|
| `5` | 5 نتائج | 5 Results |
| `10` | 10 نتائج | 10 Results |
| `15` | 15 نتائج | 15 Results |
| `20` | 20 نتائج | 20 Results |

## Classification Name (اسم التصنيف) – UNSPSC

* The form field is `clId` (+ hidden `clNmAr`, visible `clNmEn`), filled by the **Find** popup
  `GET https://www.joneps.gov.jo/ca/cs/selectListPageClComdtFind.do` ("Search by commodity, 4th level of UNSPSC").
* The popup posts its own form `frm_clSearch` back to `/ca/cs/selectListPageClComdtFind.do`:
  * **Browse the tree**: `root=root&rclId=<parent code>&rclLvl=<parent level>&clId=<parent code>&useYn=Y&currentPageNo=N&offSet=…&_csrf=…`
    (`fn_PathSearch(clId, lvl)`). Level 1 = segment (2 digits, 57 segments), 2 = family (4), 3 = class (6), 4 = commodity (8).
    10 rows per page; the page footer shows `N النتائج(الصفحة x / y)`.
  * **Free-text search**: `root=all&clNmEn=<text>` (English names; e.g. `software` → families, classes and commodities containing it).
  * Picking a commodity calls `setForm(idx, clId, clNmEn, clNmAr)` → `opener.callBackCommodity({clId, clNmEn, clNmAr})`.
  * A JSON variant also exists: `GET /ca/cs/selectClComdtFind.do?<same params>` → `{result: ["clId|nameEn|nameAr", …]}`.
* **Important:** on the public tender list, **`clId` has no effect on the results.** In the 2026 deadline window,
  no classification, `clId=43`, `4323`, `432115` and `43211503` (with or without names) all returned 3,751. The `*` on the label is not enforced either.
  You can't filter IT tenders by classification on this screen. Use sub-type, keywords or entity instead.

### IT-related UNSPSC codes (families → classes)


**4319 Communications Devices and Accessories**

- `431915` Personal communication devices
- `431916` Personal communications device accessories or parts

**4320 Components for information technology or broadcasting or telecommunications**

- `432014` System Cards
- `432015` System boards processors interfaces or modules
- `432016` Chassis components
- `432018` Media storage devices
- `432019` Media storage device accessories
- `432020` Removable storage media
- `432021` Removable storage media accessories
- `432022` Sub assemblies for electronic devices

**4321 Computer Equipment and Accessories**

- `432115` Computers
- `432116` Computer accessories
- `432117` Computer data input devices
- `432118` Computer data input device accessories
- `432119` Computer displays
- `432120` Computer display accessories
- `432121` Computer printers
- `432122` Computer data storage management systems

**4322 Data Voice or Multimedia Network Equipment or Platforms and Accessories**

- `432215` Call management systems or accessories
- `432216` Digital subscriber loop DSL access equipment and components and accessories
- `432217` Fixed network equipment and components
- `432218` Optical network devices
- `432225` Network security equipment
- `432226` Network service equipment
- `432227` Telegraph equipment
- `432228` Telephony equipment
- `432229` Telephony equipment accessories
- `432230` Teletype equipment
- `432231` Digital mobile network infrastructure equipment and components
- `432232` Mobile messaging platforms
- `432233` Datacom and network connectivity installation devices and equipment

**4323 Software**

- `432315` Business function specific software
- `432316` Finance accounting and enterprise resource planning ERP software
- `432320` Computer game or entertainment software
- `432321` Content authoring and editing software
- `432322` Content management software
- `432323` Data management and query software
- `432324` Development software
- `432325` Educational or reference software
- `432326` Industry specific software
- `432327` Network applications software
- `432328` Network management software
- `432329` Networking software
- `432330` Operating environment software
- `432332` Security and protection software
- `432334` Utility and device driver software
- `432335` Information exchange software
- `432336` Electrical Equipment software
- `432337` System management software

**8110 Professional engineering services**

- `811015` Civil engineering
- `811016` Mechanical engineering
- `811017` Electrical and electronic engineering
- `811018` Chemical engineering
- `811019` Oil and gas engineering
- `811020` Mining engineering
- `811021` Ocean engineering
- `811022` Transportation engineering
- `811023` Aeronautical engineering
- `811024` Electrical power transmission engineering
- `811025` Permitting services
- `811026` Sampling services
- `811027` Instrumented control systems design and engineering services
- `811028` Minefield and demining services

**8111 Computer services**

- `811115` Software or hardware engineering
- `811116` Computer programmers
- `811117` Management information systems MIS
- `811118` System and system component administration services
- `811119` Information retrieval systems
- `811120` Data services
- `811121` Internet services
- `811122` Software maintenance and support
- `811123` Computer hardware maintenance and support
- `811124` Computer hardware rental or leasing services
- `811125` Computer software licensing rental or leasing service
- `811126` Computer hardware offsite or depot maintenance, repair and support

**8112 Economics**

- `811215` Economic analysis
- `811216` Monetary systems and issues

**8113 Statistics**

- `811315` Methodology and analysis

**8114 Manufacturing technologies**

- `811415` Quality control
- `811416` Supply chain management
- `811417` Production planning and control
- `811418` Facilities management
- `811419` Manufacturing technology research and development services

**8115 Earth science services**

- `811515` Meteorology
- `811516` Cartography
- `811517` Geology
- `811518` Oceanography and hydrology
- `811519` Geophysics

**8116 Information Technology Service Delivery**

- `811615` Access management services
- `811616` Electronic mail and messaging services
- `811617` Telecommunication Services
- `811618` Data voice or multimedia network equipment or platform rental or leasing services

**8117 Biological science services**

- `811715` Marine biology services
- `811716` Ecological science services
- `811717` Botanical science services
- `811718` Agricultural science services
- `811719` Aerobiological science services

**4617 Security surveillance and detection**

- `461715` Locks and security hardware and accessories
- `461716` Surveillance and detection equipment
- `461717` Vehicle access control

**4619 Fire protection**

- `461915` Fire prevention
- `461916` Fire fighting equipment

**8311 Telecommunications media services**

- `831115` Local and long distance telephone communications
- `831116` Mobile communications services
- `831117` Facsimile and telegraph services
- `831118` Television services
- `831119` Radio services
- `831122` Enhanced telecommunications services
- `831123` Fiber telecommunications services
- `831124` Switched dial up and leased dedicated line circuit telecommunications services
- `831125` Backbone capacities
- `831126` Customer access

**8312 Information services**

- `831215` Libraries
- `831216` Information centers
- `831217` Mass communication services

**7210 Building construction and support and maintenance and repair services**

- `721015` Building maintenance and repair services
- `721016` Roofing and siding and sheet metal work
- `721017` Concrete work
- `721021` Pest control
- `721029` Facility maintenance and repair services
- `721031` Conveyance systems installation and repair
- `721033` Infrastructure maintenance and repair services

**7212 Nonresidential building construction services**

- `721210` New industrial building and warehouse construction services
- `721211` Commercial and office building construction services
- `721212` Agricultural building construction services
- `721213` Automotive garage and service station construction services
- `721214` Specialized public building construction services
- `721215` Industrial plant construction services

**7214 Heavy construction services**

- `721410` Highway and road construction services
- `721411` Infrastructure building and surfacing and paving services
- `721412` Marine construction services
- `721414` Detention facility construction and repair services
- `721415` Land preparation services
- `721416` Mass transit system construction services
- `721417` Construction machinery and equipment rental or leasing services

**7215 Specialized trade construction and maintenance services**

- `721510` Boiler and furnace construction and maintenance services
- `721511` Plumbing construction services
- `721512` Heating and cooling and air conditioning HVAC construction and maintenance services
- `721513` Painting and paper hanging services
- `721514` Wall covering construction services
- `721515` Electrical system services
- `721516` Specialized communication system services
- `721517` Safety and security system installation services
- `721518` Machine installation and maintenance and repair services
- `721519` Masonry and stonework services
- `721520` Plastering and drywall services
- `721521` Acoustical and insulation services
- `721522` Terrazzo tile and marble and mosaic services
- `721523` Carpentry services
- `721524` Window and door installation and erection services
- `721525` Floor laying services
- `721526` Roofing and siding and sheet metal services
- `721527` Concrete installation and repair services
- `721528` Water well drilling services
- `721529` Structural steel erection services
- `721530` Glass and glazing services
- `721531` Athletic and recreational facility construction services
- `721532` Coating and caulking and weather water and fireproofing services
- `721533` Service station equipment installation and maintenance services
- `721534` Rigging and scaffolding services
- `721535` Structural exterior cleaning services
- `721536` Interior finishing and furnishing and remodeling services
- `721537` Parking facility construction and equipment installation and maintenance and repair services
- `721539` Building site preparation services
- `721540` Specialty building and trades services
- `721541` Distribution and conditioning system equipment maintenance and repair services
- `721542` Instrumentation installation maintenance and repair services
- `721543` Motive and electrical power generation equipment maintenance and repair services
- `721544` Pipefitting fabrication and maintenance services
- `721545` Heavy equipment installation and maintenance services
- `721546` Animal habitat and enclosure construction and maintenance services

Most relevant for IT monitoring: 4321 (computers), 4322 (network incl. **432225 Network security equipment**), 4323 (software),
4320 (storage/components), 8111 (computer services incl. 811122 software maintenance, 811123 hardware maintenance),
8116 (IT service delivery), 8311/8312 (telecom & information services), 4617 (security surveillance – CCTV), 7215 (specialised trade incl. cabling).

### IT-related **sub tender types** (these *do* filter)

`EP0104` معدات وكاميرات وطباعة وحاسبة, `EP0110` أجهزة الكمبيوتر ومعدات الموسيقى, `EP0118` أجهزة الكترونية, `EP0120` أحبار,
`EP0124` أجهزة الكمبيوتر وملحقاتها, `EP0126` برمجيات ومعدات حاسوب, `EP0127` عقود الصيانة, `EP0132` أجهزة الاتصال,
`EP0133` معدات المكتب, `EP0215` خدمات صيانة, `EP0211` خدمات الصيانة والتحويل الداخلي, `EP0997` خدمات إلكترونية, `EP0218` خدمات استشارية ودراسات.

## Department (الأقسام) – only for GPD and GTD

When `searchPeNo` is 150500000 (GPD) or 210200000 (GTD), `fn_getDepartement()` calls
`POST /ep/invt/select-organization-departements.do organizationNo=<peNo>&departmentType=<EP1331 goods | EP1334 medicines | EP1333 works | empty>&departmentNo=&_csrf=…`,
which returns `<option>`s for the extra **`searchDeptNo`** select:

| Org | searchDeptNo | Department |
|---|---|---|
| GPD 150500000 | `1505000000001` | قسم التجهيزات الالكترونية (Electronic equipment – **main IT desk**) |
| GPD 150500000 | `1505000000012` | قسم المستهلكات الطبية |
| GPD 150500000 | `1505000000013` | قسم الاجهزة والتجهيزات الطبية |
| GPD 150500000 | `1505000000021` | قسم التجهيزات المكتبية و العقود (Office equipment & contracts – maintenance contracts) |
| GPD 150500000 | `1505000000022` | قسم التجهيزات الميكانيكية |
| GPD 150500000 | `3030000000001` | قسم الأدوية (medicines, departmentType EP1334) |
| GTD 210200000 | `2102020000001` | قسم الأبنية |
| GTD 210200000 | `2102020000002` | قسم المياه والري والصرف الصحي والسدود |
| GTD 210200000 | `2102020000003` | قسم الطرق والنقل والتعدين |
| GTD 210200000 | `2102020000004` | قسم الكهروميكانيكية والاتصالات (Electro-mechanical & **telecom**) |
| GTD 210200000 | `2102000000016` | مديرية الشؤؤون المالية والادارية وتطوير الاداء |
| GTD 210200000 | `2102000000017` | وحدة العلاقات الدوليه |
| GTD 210200000 | `2102000000021` | مديرية المناقصات |
| GTD 210200000 | `2102000000024` | قسم اللوازم والخدمات |
| GTD 210200000 | `2102000000025` | قسم اللوازم |

The Excel export's "الأقسام" column holds the department name for every tender, not only GPD/GTD ones.

## Organisation codes (Procuring `searchPeNo` / Requesting `searchDeNo`)

From the organisation popup `GET /um/popup/org/UMDEMDeInfoPW.do` (top-level `orgLno` list; mid-level via `POST /um/org/selectOrgMidCdList.do orgLno=…`).
Both `searchPeNo` and `searchDeNo` **do** filter the list (2026: MoH as requesting entity = 1,235; GPD as procuring = 433; GPD for MoH = 115).

| orgNo | Name |
|---|---|
| `010100000` | الديوان الملكي الهاشمي |
| `020100000` | مجلس الأمة |
| `030100000` | رئاسة الوزراء |
| `030200000` | رئاسة الوزراء / ديوان التشريع والرأي |
| `030300000` | رئاسة الوزراء/دائرة الشراء الموحد(المقر الرئيسي) |
| `030400000` | رئاسة الوزراء / وكالة الأنباء الأردنية |
| `040100000` | ديوان المحاسبة |
| `050100000` | وزارة تطوير القطاع العام |
| `060100000` | هيئة الخدمة والادارة العامة |
| `070100000` | وزارة التنمية السياسية(المقر الرئيسي) |
| `070200000` | وزارة الشؤون السياسية والبرلمانية |
| `080100000` | وزارة الدفاع (المقر الرئيسي) |
| `080200000` | الخدمات الطبية الملكية(المقر الرئيسي) |
| `090100000` | المركز الجغرافي الملكي الأردني |
| `100100000` | وزارة الداخلية |
| `100200000` | وزارة الداخلية / دائرة الأحوال المدنية والجوازات |
| `100300000` | وزارة الداخلية / الأمن العام |
| `100400000` | وزارة الداخلية / الدفاع المدني(المقر الرئيسي) |
| `100500000` | وزارة الداخلية / المديرية العامة للدرك (المقر الرئيسي) |
| `110100000` | وزارة العدل |
| `111000000` | المجلس القضائي |
| `120100000` | دائرة قاضي القضاة |
| `130100000` | وزارة الخارجية وشؤون المغتربين |
| `130200000` | دائرة الشؤون الفلسطينية |
| `150100000` | وزارة المالية |
| `150200000` | وزارة المالية / دائرة الموازنة العامة |
| `150300000` | وزارة المالية / الجمارك الاردنية |
| `150400000` | وزارة المالية / دائرة الأراضي والمساحة |
| `150500000` | وزارة المالية/ دائرة المشتريات الحكومية |
| `150600000` | وزارة المالية / دائرة ضريبة الدخل والمبيعات |
| `150700000` | وزارة المالية / دائرة المشتريات الحكومية |
| `160100000` | وزارة الصناعة والتجارة والتموين |
| `160200000` | وزارة الصناعة والتجارة والتموين / دائرة مراقبة الشركات |
| `160300000` | هيئة الاستثمار |
| `160400000` | مؤسسة المواصفات والمقاييس |
| `160500000` | المؤسسة الاردنية لتطوير المشاريع الاقتصادية |
| `160600000` | وزارة الاستثمار |
| `170100000` | وزارة التخطيط والتعاون الدولي/ المجلس القومي للتخطيط |
| `170200000` | وزارة التخطيط والتعاون الدولي/ دائرة الاحصاءات العامة |
| `180100000` | وزارة السياحة والآثار |
| `180200000` | وزارة السياحة والآثار/ دائرة الآثار العامة |
| `180300000` | متحف الأردن |
| `190100000` | وزارة الإدارة المحلية |
| `200100000` | وزارة الطاقة والثروة المعدنية |
| `200200000` | وزارة الطاقة والثروة المعدنية / سلطة المصادر الطبيعية( المقر الرئيسي) |
| `200300000` | هيئة الطاقة الذرية الأردنية |
| `200400000` | هيئة تنظيم قطاع الطاقة والمعادن |
| `210100000` | وزارة الأشغال العامة والاسكان |
| `210200000` | دائرة العطاءات الحكومية |
| `210300000` | وزارة الأشغال العامة والاسكان/دائرة الأبنية الحكومية (المقر الرئيسي) |
| `220100000` | وزارة الزراعة |
| `220200000` | المؤسسة التعاونية الأردنية |
| `230100000` | وزارة المياه والري |
| `230200000` | وزارة المياه والري / سلطة وادي الأردن |
| `240100000` | وزارة البيئة |
| `250100000` | وزارة التربية والتعليم |
| `250200000` | مجمع اللغة العربية الأردني |
| `260100000` | وزارة التعليم العالي و البحث العلمي |
| `260200000` | هيئة إعتماد مؤسسات التعليم العالي وضمان جودتها |
| `269300000` | مجلس الخدمات المشتركة لمحافظة مادبا |
| `270100000` | وزارة الصحة |
| `270200000` | المجلس الصحي العالي |
| `270300000` | المجلس الطبي الأردني |
| `270400000` | المؤسسة العامة للغذاء والدواء |
| `270500000` | مستشفى الأمير حمزة |
| `280100000` | وزارة التنمية الاجتماعية |
| `280200000` | صندوق المعونة الوطنية |
| `280300000` | المجلس الاعلى لحقوق الاشخاص ذوي الاعاقة |
| `290100000` | وزارة العمل |
| `290200000` | مؤسسة التدريب المهني |
| `290300000` | صندوق التشغيل والتدريب والتعليم المهني والتقني |
| `290400000` | هيئة تنمية وتطوير المهارات المهنية والتقنية |
| `300100000` | وزارة الثقافة |
| `300200000` | وزارة الثقافة/دائرة المطبوعات والنشر(المقر الرئيسي) |
| `300300000` | وزارة الثقافة / دائرة المكتبة الوطنية |
| `300400000` | وزارة الثقافة /المركز الأردني للاعلام (المقر الرئيسي) |
| `303000000` | Joint Procurement Department |
| `305000000` | وزارة الشباب |
| `310100000` | وزارة النقل |
| `310200000` | وزارة النقل/ سلطة الطيران المدني (المقر الرئيسي) |
| `310300000` | وزارة النقل / دائرة الأرصاد الجوية |
| `310400000` | هيئة تنظيم النقل البري |
| `310500000` | هيئة تنظيم الطيران المدني |
| `310600000` | الهيئة البحرية الأردنية |
| `312000000` | بنك تنمية المدن والقرى |
| `320100000` | وزارة الاقتصاد الرقمي والرياده |
| `320200000` | مركز تكنولوجيا المعلومات الوطني |
| `320300000` | هيئة تنظيم قطاع الاتصالات |
| `321000000` | المركز الوطني للأمن السيبراني |
| `330100000` | ديوان المظالم (المقر الرئيسي) |
| `330200000` | وزارة الأوقاف والشؤون والمقدسات الاسلامية |
| `340100000` | وزارة الشؤون البرلمانية |
| `340200000` | دائرة الافتاء العام |
| `350100000` | هيئة الاعلام |
| `350500000` | وزارة الاتصال الحكومي |
| `360100000` | هيئة النزاهة ومكافحة الفساد |
| `370100000` | المجلس الإقتصادي والإجتماعي |
| `380100000` | معهد الإدارة العامة |
| `390100000` | هيئة الاوراق المالية |
| `542000000` | المجلس الأعلى للعلوم و التكنولوجيا |
| `603000000` | وحدة مكافحة غسل الأموال وتمويل الإرهاب |
| `606700000` | دائرة تنمية اموال الاوقاف |
| `631800000` | مجلس الخدمات المشتركة للواء ذيبان |
| `810200000` | سلطة المياه |
| `810500000` | المؤسسة العامة للاسكان والتطوير الحضري |
| `810900000` | المؤسسة الإستهلاكية المدنية |
| `811000000` | مؤسسة التدريب المهني |
| `811300000` | صندوق التأمين الصحي المدني |
| `811400000` | مؤسسة الخط الحديدي الحجازي الاردني |
| `811500000` | صندوق توفير البريد |
| `811700000` | معهد الإدارة العامة |
| `812000000` | صندوق المعونة الوطنية |
| `812100000` | هيئة الإستثمار |
| `812200000` | صندوق التنمية والتشغيل |
| `812400000` | مؤسسة المواصفات والمقاييس |
| `812700000` | مؤسسة الإذاعة والتلفزيون |
| `812800000` | المؤسسة التعاونية الاردنية |
| `812900000` | سلطة اقليم البترا التنموي السياحي |
| `813100000` | هيئة تنظيم النقل البري |
| `813300000` | هيئة الطاقة الذرية الاردنية |
| `814100000` | المؤسسة العامة للغذاء والدواء |
| `814300000` | هيئة الاوراق المالية |
| `814400000` | سلطة منطقة العقبة الاقتصادية الخاصة |
| `814600000` | المؤسسة الاردنية لتطوير المشاريع الاقتصادية |
| `815000000` | هيئة  النزاهة ومكافحة الفساد |
| `815100000` | هيئة تنظيم الطيران المدني |
| `815300000` | دائرة الافتاء العام |
| `815400000` | شركة البريد الاردني |
| `815500000` | شركة الكهرباء الوطنية |
| `815600000` | الشركة العامة الاردنية للصوامع و التموين |
| `815700000` | بورصة عمان |
| `815900000` | البنك المركزي الأردني |
| `816000000` | شركة تطوير العقبة |
| `816100000` | شركة مياه الاردن ( مياهنا ) |
| `816500000` | متحف الأردن |
| `816900000` | شركة المطارات الاردنية |
| `817200000` | شركة مياة اليرموك |
| `817300000` | المحكمة الدستورية |
| `817800000` | المجلس الطبي الاردني |
| `900200000` | المؤسسة العامة للضمان الإجتماعي |
| `901000000` | صندوق تسليف النفقة |
| `999900000` | المركز الوطني للعناية بصحة المراه |
