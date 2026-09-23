# contract: 01_docs/sourcing/

**Purpose** — what to BUY for the parts the fab will not source, and the
evidence behind each number. Produced and graded by `/shopping-list`
(`skills/shopping-list`), governed by canon **`M-QUOTE`** — the narrow instance
of `M-IMPORT` scoped to distributor facts.

**Why this folder exists rather than `06_build/cache/`.** `01_docs/` otherwise
FORBIDS stock, price and availability, and that rule stands: a market number may
never be committed **as truth**. What lives here is not truth — it is a **dated
observation with its provenance**, the same shape as a journal entry. The
distinction is load-bearing and mechanical, not rhetorical:

- every file is stamped with the date it was produced and says, in its own
  first paragraph, that the numbers are stale;
- every number carries its M-IMPORT grade and the URL/date it was read from;
- the raw API responses stay in `06_build/cache/` (gitignored, TTL'd, never
  committed), and nothing here is re-consumed by a build.

**Mutability** — APPEND-ONLY, one dated file per run. Multiple runs on the same UTC date add a `-HHMM` suffix to the date in generated report and qualification filenames. A shopping list is
evidence of what a distributor said on a day; superseding it means adding the
next dated file, never editing the old one. `manual_quotes.yaml` is the one
mutable file: it is an INPUT, and a re-read replaces the entry it re-reads.

## Allowed

| File | What | Rule |
|---|---|---|
| `shopping-list-<YYYY-MM-DD>.md` | the generated per-distributor list: MPN, distributor part number, stock, min/multiple, lifecycle, unit price at the needed break, extended price, direct product URL; every catalog record seen; a CANNOT-SOURCE section naming every failed line with its reason; and the coverage denominator | GENERATED — never hand-edited. Regenerate with `shopping_list.py PROJECT_DIR --out ...` and add a NEW dated file |
| `shopping-list-<YYYY-MM-DD>-<HHMM>.md` | the generated per-distributor list: MPN, distributor part number, stock, min/multiple, lifecycle, unit price at the needed break, extended price, direct product URL; every catalog record seen; a CANNOT-SOURCE section naming every failed line with its reason; and the coverage denominator | GENERATED — never hand-edited. Regenerate with `shopping_list.py PROJECT_DIR --out ...` and add a NEW dated file |
| `shopping-list-<YYYY-MM-DD>.json` | the machine sidecar for the same run, carrying an explicit `verdict` | GENERATED. A missing or unparseable verdict is a FAIL, never a skip |
| `shopping-list-<YYYY-MM-DD>-<HHMM>.json` | the machine sidecar for the same run, carrying an explicit `verdict` | GENERATED. A missing or unparseable verdict is a FAIL, never a skip |
| `parts-selection-<YYYY-MM-DD>.md` | dated architecture/selection evidence and the candidate BOM it qualifies | HAND-WRITTEN review record; exact identities remain authoritative in `02_parts/` and the candidate BOM |
| `two-source-qualification-<YYYY-MM-DD>.md` | dated interpretation of the machine-composed Q-2SOURCE evidence | HAND-WRITTEN review record; it must name the machine report and may not replace its verdict |
| `two-source-qualification-<YYYY-MM-DD>-<HHMM>.md` | dated interpretation of the machine-composed Q-2SOURCE evidence | HAND-WRITTEN review record; it must name the machine report and may not replace its verdict |
| `exact-parts.csv` | frozen pre-schematic candidate identity/quantity set consumed by sourcing qualification; final BOM authority remains the generated board BOM and dossiers | HAND-WRITTEN selection input; no volatile stock/price claims |
| `manual_quotes.yaml` | every DigiKey / Amazon number. One entry per `{manufacturer, mpn, distributor}` with source, URL, read date and stock/price fields | HAND-WRITTEN evidence. `manufacturer:` plus full `mpn:` is Q-MFR-IDENT and is required for a quote to count toward Q-2SOURCE. Search snippets are refused; catalog absence is the only admissible search-page use |
| `public-distributor-policy.yaml` | explicit user-approved, exact-part design-only public-stock policy | optional schema below; never purchase or allocation authority |
| `procurement-policy.yaml` | durable currency and per-line/aggregate limits for preorder cash, gross MOQ surplus cost, and nonrecoverable assembly excess cost | HAND-WRITTEN user policy. Template limits are zero so no spending authority is invented; volatile MOQ/quote observations remain in `06_build/sourcing/` |
| `evidence/` | retained primary manufacturer lifecycle pages | Exact bytes and identity/date/hash provenance; its own contract governs contents. No stock inference. |
| `jlcsearch-screen-<YYYY-MM-DD>.md` | dated interpretation of report-only jlcsearch evidence with exact URLs/times and input report hashes | observation only; never a build input or allocation receipt |
| `sourcing-review-<YYYY-MM-DD>.md` | dated cross-provider exception dispositions and proposed design-time decisions | observations only; no automatic admission or purchasing authority |
| `contracts.md` | this file | |

## Optional public distributor design policy

`manufacturing_readiness.py` reads schema1 with `scope: prelayout-only`,
`order_authorized: false`, a nonempty `directive` present verbatim in both
project-relative `brief` and `decision` files, and nonempty `rows`. The decision
must explicitly retain public-catalog/pre-layout/DO-NOT-ORDER scope. Each row
contains `lcsc`, `mpn`, `manufacturer`, `footprint`, exact `designators`,
`distributor`, exact product `url`, and `packaging`. Identity must agree with
the current generated source, request and dossier; no implicit substitution.

Supported observation: `distributor: digikey`, HTTPS
`www.digikey.com/en/products/detail/...`, one matching `manual_quotes.yaml`
entry with exact MPN/manufacturer/URL/packaging, nonempty `dpn`,
`source: product_page`, `lifecycle: Active`, timezone-bearing `checked_at`
within24hours, positive integer `stock`, `min`, and `mult`. Stock must cover
the actual minimum/multiple-expanded request. Other quote entries may remain
for other tasks; they do not grant extra policy coverage. Record the actual
public read and its limitations; hashes do not prove accurate transcription.

This path can cover only JLC `LOW_STOCK` rows in prelayout design composition.
It leaves the raw JLC report unchanged, is not Q-2SOURCE, and cannot satisfy
selection, assembly allocation, economics, order readiness or payment authority.

## Forbidden

- Hand-editing a generated list. If a number is wrong, fix the input
  (`manual_quotes.yaml`, `02_parts/<dir>/part.yaml`) and regenerate.
- A stock or price number with no `url:` and no `read_on:`.
- An invented product link, ASIN or distributor part number. A row nobody has
  is **OWED** and stays OWED — "no quote recorded" is a finding, and padding the
  table to make it look complete is the defect this whole folder exists against.
- A substituted part. A near MPN is a PROPOSAL for a human (Q-IDENT); recording
  one against the authoritative MPN's line is a silent substitution.
- Any credential. The Mouser key lives in `<repo>/.secrets/mouser.env`.

## Audit

- **Pre-selection Q-2SOURCE gate:** a component may enter the schematic only
  when at least two independent authorized distributor pools each list the
  exact authoritative MPN (or an explicitly approved dossier alternate) as
  active and orderable, with stock greater than 10 and sufficient for five
  board sets. JLCPCB/LCSC is one pool, Mouser is one, and DigiKey is one;
  marketplaces and multiple listings from the same distributor do not increase
  the count. Fewer than two qualifying pools rejects the selection rather than
  creating a release-time waiver. Run this before schematic completion and
  repeat it on order day.
- `shopping_list.py PROJECT_DIR --scope all --boards N --bom CANDIDATE.csv
  --required-pools 2 --jlc-stock-json STOCK.json` = the gate: **Q-2SOURCE**
  per exact manufacturer/MPN row and **Q-COVER** (`N/M` per
  distributor; a part it could not look up is a FAIL, never an omission),
  **Q-WIDE**, **Q-IDENT**, **Q-MFR-IDENT**, **Q-STOCK** (`stock > 10` AND
  `>= qty`), **Q-SNIPPET**, **Q-GRADE**.
- Known-bads: `tests/t1_shopping_list.py`.
- **Re-run on order day regardless.** Stock moves; a committed list is a record
  of a past answer, not a current one.
