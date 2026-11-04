# Jordan Tender Monitor — Seniors IT

Watches the tender pages of your 46 account organizations **plus the central
portals (JONEPS, GTD, MoDEE)** twice a day, detects newly posted tenders, flags
the ones relevant to the Seniors IT portfolio (cybersecurity, infrastructure,
network, endpoint, DLP, backup, cloud — in **English and Arabic**), and emails
you a digest.

```
tender-monitor/
├── monitor.py              # the monitor (scrape → diff → match → email)
├── sources.yaml            # the 46 orgs + JONEPS/GTD/MoDEE, with status notes
├── config.yaml             # keywords (EN + AR, two-tier) and notification behaviour
├── selftest.py             # offline automated test suite (38 checks)
├── keyword_check.py        # keyword recall check against real past tenders
├── requirements.txt
├── state/seen.json         # what's already been seen (committed back by the Action)
├── joneps_data/            # JONEPS research: 11,199-tender harvest, request/codes/notes,
│                           #   per-site tender-page findings, harvester scripts
└── .github/workflows/tender-monitor.yml   # twice-daily schedule (GitHub Actions)
```

---

## How it works

1. Fetches every `enabled: true` source in `sources.yaml`.
2. Extracts the tender announcements on each page with one of three parsers:
   - `joneps` — one POST pulls the whole active JONEPS window (~825 tenders);
     each tender is identified by tender no + sequence, so deadline
     extensions don't re-alert.
   - `table` — sites that list tenders as table rows (Yarmouk Water, AHU);
     identified by tender no + name.
   - `generic` — link lists (the shared `.gov.jo` platform, WordPress sites,
     universities); an optional `css:` selector limits it to the tender rows.
3. Compares against `state/seen.json` → anything not seen before is **new**.
4. New tender **titles** (never the entity name) are matched against
   `config.yaml` in two tiers: strong IT/security terms always star; generic
   words (نظام, system, شبكة…) star only when the title isn't about fire,
   HVAC, medical, roads, water, etc. Arabic is normalized first (diacritics
   stripped, أ/إ/آ→ا, ى→ي, ة→ه).
5. Sends one HTML email: ⭐ matched tenders first, then other new tenders in
   your accounts, then any sources that failed (so you know to check them by
   hand).

**The first run is a silent baseline** — it records everything currently
posted without emailing, so you don't get 500 old tenders. Alerts start from
run #2.

---

## Option A (recommended): run it free on GitHub Actions

No server needed, runs even when your PC is off.

1. Push this folder to a GitHub repo. Public works: the email settings below
   are encrypted Secrets and never appear in the code, and the monitor never
   prints recipient addresses in the (public) Action logs.
2. In the repo: **Settings → Secrets and variables → Actions → New repository
   secret**, add these five:

   | Secret | Value (Gmail example) |
   |---|---|
   | `SMTP_HOST` | `smtp.gmail.com` |
   | `SMTP_PORT` | `465` |
   | `SMTP_USER` | the Gmail address that will send alerts |
   | `SMTP_PASS` | a Gmail **App Password** (see below) |
   | `EMAIL_TO`  | where alerts go, e.g. `you@seniorsit.me` (comma-separate for several) |

3. Go to the **Actions** tab → "Jordan Tender Monitor" → **Run workflow** once
   manually (this is the silent baseline run).
4. Done. It now runs at **08:00 and 14:30 Amman time** daily. Edit the two
   `cron:` lines in `.github/workflows/tender-monitor.yml` to change times
   (cron is in UTC; Amman = UTC+3, so 05:00 UTC = 08:00 Amman).

**Gmail App Password:** Google account → Security → turn on 2-Step
Verification → Security → App passwords → create one for "Mail". Use that
16-character password as `SMTP_PASS` (your normal password won't work).
If Seniors IT uses Microsoft 365 instead: `SMTP_HOST=smtp.office365.com`,
`SMTP_PORT=587`.

---

## Option B: run it on your own Windows PC

```powershell
cd tender-monitor
pip install -r requirements.txt

# set email settings once (System → Advanced → Environment Variables, or per-session):
$env:SMTP_HOST="smtp.gmail.com"; $env:SMTP_PORT="465"
$env:SMTP_USER="you@gmail.com";  $env:SMTP_PASS="your-app-password"
$env:EMAIL_TO="you@seniorsit.me"

python monitor.py --test-email   # verify email works
python monitor.py                # first run = silent baseline
```

Then schedule it twice a day with **Task Scheduler**: Create Basic Task →
Daily → repeat the task with a second trigger (e.g. 08:00 and 14:30) →
Action: Start a program → Program: `python`, Arguments:
`C:\path\to\tender-monitor\monitor.py`, Start in: `C:\path\to\tender-monitor`.

(Linux/Kali: `crontab -e` → `0 8,14 * * * cd /path/tender-monitor && python3 monitor.py >> monitor.log 2>&1`)

---

## Useful commands

```bash
python monitor.py --dry-run      # scrape + show what would be alerted, no email, no state change
python monitor.py --test-email   # just test SMTP settings
python selftest.py               # full automated test - no internet needed (see Testing)
python keyword_check.py joneps_data/harvest.csv   # keyword recall against 11,199 real past tenders
```

---

## Testing — 3 levels

1. **`python selftest.py`** — fully automated, no internet, no email. Spins up a
   fake ministry website locally and runs the real monitor against it twice,
   checking 38 behaviours: scraping, silent baseline, new-tender detection,
   Arabic+English keyword matching (including diacritics/alef normalization),
   no-duplicate-alerts, JONEPS/Yarmouk Water/AHU/CARC page formats, and the
   keyword traps found in live runs. Run it after any code change.
2. **`python monitor.py --test-email`** — confirms your SMTP secrets work.
3. **Live test** — run `python monitor.py` once (baseline), then run it again
   the next day: you should get a digest of whatever was posted in between.
   `--dry-run` lets you preview without sending email or saving state.

## "Are we missing tenders?" — the safety design + calibration

**Keywords can never hide a tender.** Every new item found on any source goes
into the email; keywords only decide which ones are ⭐-highlighted on top.
Worst case for a bad keyword list is a relevant tender sitting in the
"other new tenders" section instead of the starred one. Keep
`show_unmatched: true` and `send_when_unmatched_only: true` (the defaults) and
nothing is ever dropped.

To make the highlighting trustworthy, calibrate against **real past tenders**:

1. Harvest historical tender titles from JONEPS (and org archive pages) into a
   CSV with a `title` column — ideally also a `relevant` column (1 = we should
   have seen it, 0 = not our business). Use the Claude-in-Chrome harvest
   prompt for this, or JONEPS's own Excel export button on the search results.
2. Run `python keyword_check.py harvest.csv`. It reports **recall** (of all
   relevant tenders, how many the keywords caught) and lists every missed one.
3. Add the missing vocabulary to `config.yaml` → re-run → repeat until recall
   is 100% on the harvest.

## JONEPS specifics (it's the tricky source — handle with care)

- **We don't rely on JONEPS's filter form.** The search form has many
  parameters (type, sub-type, classification, entities…) and filtering
  server-side risks excluding something. The monitor instead takes **every row**
  of the default public list (deadlines ≈ 1 month back → 2 months ahead) and
  diffs it — filtering/highlighting happens on our side where nothing is lost.
- **MoDEE procures on behalf of other entities.** JONEPS rows carry both the
  procuring and the requesting entity, and the monitor fingerprints the whole
  row text — so a tender procured by MoDEE for one of your accounts still
  appears, with both names visible in the alert.
- Once you've harvested the sub-type/classification codes used by past IT
  tenders (via the browser session), you *can* add pre-filtered JONEPS queries
  as extra sources — but keep the unfiltered list enabled as the safety net.

---

## Tuning

- **Keywords** — edit `config.yaml`. Matching is substring-based on the tender
  title; keep Arabic keywords broad (titles are short). `exclude:` drops
  titles even when an include keyword hits — keep it minimal.
- **Sources** — edit `sources.yaml`. Each entry has a human `status:` note:
  - `verified` — confirmed working URL.
  - `guessed standard path` — most `.gov.jo` sites use `/AR/Modules/Tenders`;
    these are enabled, and if one 404s it will show in the email's
    "failed sources" list → open the site, find the real tenders URL, paste it in.
  - `enabled: false` — no tender page found yet (GAM, ASE, Petra, IEC, RJGC,
    JUNet, Ajloun NU, Crown Prince Foundation, Silos, RMS…). Verify by hand
    once, update the URL, flip to `true`.
- **MFA, JSC, GPD** have no own tender pages — their tenders flow through
  **JONEPS and MoDEE**, which are already monitored.

## JONEPS notes

- The public list (`دعوات العطاءات`) needs no login and defaults to tenders
  with deadlines from 1 month back to 2 months ahead — exactly the window you
  want. It can be slow; the script retries 3× automatically.
- A JONEPS alert links to the tender detail page (`tendNo=…`). Buying the
  tender documents and bidding require Seniors IT's registered supplier
  account (GPD registration is free; login via email or Sanad).
- Entities not yet fully on their own websites (GAM, JSC, MFA…) increasingly
  publish there, so JONEPS is your safety net — Jordan targets full JONEPS
  deployment by 2027.

## Limitations to know about

- Detection is based on each page's **listing titles**. If a site publishes a
  tender only as a PDF with a generic title ("إعلان عطاء"), you'll still get
  alerted that something new appeared — but keyword matching may not fire, so
  keep `show_unmatched: true`.
- A few sites may be JavaScript-rendered or behind a WAF that blocks bots; the
  email's "failed sources" section tells you which ones to check manually.
- Jordanian gov sites get migrated periodically — expect to refresh a URL in
  `sources.yaml` occasionally.
