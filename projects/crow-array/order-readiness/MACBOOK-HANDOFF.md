# MacBook handoff — JLC availability and order preparation

**Superseded next action, 2026-10-30:** the 35-identity pass below is complete.
Use [MACBOOK-PRICING-HANDOFF.md](MACBOOK-PRICING-HANDOFF.md) on branch
`codex/crow-jlc-source-review-20261030` for the seven-shortage price/lead-time
check. Do not repeat this historical task or assume the new files are on main.

Start here after pulling remote main. This is a browser/sourcing continuation,
not a board redesign or permission to order. Use only local `vnext/` instructions.
The published files suffice for this stock-check task; they are not the complete
original engineering archive or an approved turnkey upload packet.

## Exact job and decisions

- Five carrier boards and ten microphone pods, NOT five eight-pod arrays.
- JLC requested: 915 SMT placements plus 50 Amphenol RJHSE-5080 jacks,
  five Same Sky PJ-102AH power jacks and five RECOM R-78E5.0-0.5 modules.
- User installs ten CMA-4544PF-W microphones, ten CPE-203 buzzers and five
  original SC0915 Picos. Existing protected acoustic hand-solder and Pico
  D1-only preparation/inspection instructions remain binding.
- User-installed parts stay outside JLC placement/paste scope; keep applicable
  holes open for later assembly. Do not assume JLC ships loose parts.
- User accepted the discussed prototype Pico-fit risk and asked us to move on.
  Do not reopen Pico-relief research without new contrary evidence. This does
  not assert measured fit or waive unrelated connector requirements.
- No substitutions, purchases, supplier messages or manufacturing submissions
  are authorized by this handoff. The browser task is read-only stock checking;
  obtain explicit authority before uploading files or creating/submitting orders.

## Read these inputs

1. `vnext/skills/pcb-design/SKILL.md` and its sourcing/part-recheck instructions.
2. `projects/crow-array/order-readiness/STATUS.md` for the current journal and limits.
3. `projects/crow-array/order-readiness/ASSEMBLY-MAPPING-20261026.md`.
4. `projects/crow-array/order-readiness/procurement-map-20261026-v3.csv`:
   all 38 exact identities, installed quantities, board references, observed
   supplier codes/URLs and proposed routes. This is NOT a JLC upload BOM.
5. `projects/crow-array/releases/crow-prototype-v3-first-run-5c10p-public-v1/README.md`
   for the native boards, PDFs, Gerbers, original BOM/CPL and explicit exclusions.

Paths are repository-relative. No server filesystem or credentials are needed
to read these files or run the portable checks below. Native regeneration needs
the documented KiCad toolchain; do not run it just to check inventory.

## Browser-first next action

Use the Mac's available browser tools; user handles sign-in and any MFA. Verify
the tools actually work before claiming browser access. Use exact JLC C-codes
and full manufacturer MPNs from the worksheet. Check 35 JLC-requested identities
(32 SMT plus three connector/regulator identities); the other three identities
are user-installed. Quantities in the worksheet are installed need, not invented
feeder losses or spares.

Record exact identity, package, visible available quantity or in-stock wording,
stock pool, lead time, PCBA eligibility and source URL/date. Distinguish JLC-ready
stock, global sourcing, LCSC inventory, insufficient stock and failed lookups.
Do not equate a missing match or an HTTP error with zero stock. Do not sum
overseas/presale/assembly pools. Do not change a suffix or maker silently.

Use JLC's normal catalog/BOM-matching workflow first. An email/support inquiry
is NOT a prerequisite: `jlc-inquiry-draft.md` is an unsent contingency for exact
exceptions the workflow cannot resolve. Both released factory BOMs are empty;
the existing consigned exports and worksheet must not be presented as accepted
turnkey files. If a BOM upload is needed, prepare/review a new draft outside the
immutable release and obtain upload authority; user can perform the upload if
the available browser cannot.

Known questions to resolve, not automatic substitute requests:

- Exact JLC matches for CTS CB3LV-3I-12M288000, Panasonic ERJ-3EKF68R0V,
  TDK C2012X7R1V225K125AE and TI PCM1864DBT.
- Earlier checked pools: Littelfuse 1206L010/30WR had 13 versus 50 needed;
  Murata GRM21BR71A105KA01L was JLC out-of-stock; TDK C3216X7R1V106K160AC
  and RECOM R-78E5.0-0.5 had zero at LCSC. Independent supplier leads exist.
- PJ-102AH is listed under CUI at LCSC; reconcile maker identity with the
  released Same Sky part rather than automatically accepting a brand alias.
- Public JLC pages list RJHSE-5080 (C599441) and the exact RECOM module
  (C5199916) as wave-soldering assembly parts. This supports catalog/service
  eligibility, not current stock or compatibility with our released process.
- A later public-page check in the server conversation encountered HTTP 429
  for SMBJ15A. That is an access failure, not a new shortage. That check was
  not saved as a new observation artifact; retained JSON timestamps govern.

Stop after one complete matching pass and report a compact exception table
and the orchestrator's top two recommended paths. Preserve evidence in a new
dated result beside this file, update STATUS/journal, and do not spin on repeated
lookups. Supplier support is for concrete remaining exceptions. Payment and
final ordering require separate user approval.

## Portable validation

From repository root, using Python 3.11 or newer (no network needed):

```sh
python3 -B projects/crow-array/publication.py verify
python3 -B -m unittest discover -s projects/crow-array -p test_publication.py
python3 -B -m unittest discover -s projects/crow-array/order-readiness -p 'test_*.py'
```

Expected: publication preservation PASS for 256 payload files, 15 publication
tests and 14 sourcing/mapping tests. `DO-NOT-ORDER` is expected until actual
order prerequisites close; never edit historical receipts to make it disappear.

## Suggested local task prompt

> Read projects/crow-array/order-readiness/MACBOOK-HANDOFF.md and follow vNext.
> Use my Mac browser to check exact JLC part matching and usable availability
> for five Crow carriers and ten pods. Preserve the selected JLC/user assembly
> split. Make one complete pass and report exceptions with your top two next
> recommendations. Do not substitute, upload files, contact suppliers, create
> orders or purchase anything. Ask me to handle login if needed.
