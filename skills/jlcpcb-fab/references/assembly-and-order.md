# JLCPCB assembly and order procedure

Use this procedure to produce BOM/CPL data, prove exact part identities and
rotations, check stock, and perform the human uploader review.

## Contents

1. Deliverables
2. Export and source-identity sequence
3. Part specification and stock
4. Population and assembly coverage
5. Rotation and polarity authority
6. Uploader-side human checks

Policy/gate IDs owned here: `A-LOCATOR`, `A-BUY`, `A-POL`, `A-POP`, `A-POS`, `A-ROT`,
`A-STOCK`, `F-ECHO`, `F-ENCODE`, `F-LEGIBLE`, `F-MPN`, `F-WORDS`, `M-PROV`,
`POLARITY-CHECK`, `POLARITY-FIT`, and `ROT-DB-SUGGEST`.

## 1. Deliverables

| Upload slot | File | Required content |
|---|---|---|
| PCB | `<board>_gerbers.zip` | Copper, mask, paste, silk, edge cuts, PTH and NPTH drills; no BOM/CPL |
| Assembly BOM | `bom.csv` | `Comment,Designator,Footprint,MPN,LCSC` |
| Assembly CPL | `cpl.csv` | `Designator,Val,Package,Mid X,Mid Y,Layer,Rotation` |

Use Protel extensions with Gerber attributes. Accept KiCad-version-dependent
inner-layer extensions and optional job-file absence. Keep plot/drill origins
consistent. Use the exporter rather than hand-renaming or hand-copying files.

Group coded BOM rows by `(LCSC, footprint)`, never only by value/footprint.
Distinct catalog codes remain distinct even when their displayed values match.
Uncoded assembly exceptions remain explicit rows until assembly policy proves
why they are not machine sourced/placed.

## 2. Export and source-identity sequence

1. Require the KiCad audit, full-severity DRC, unconnected, and schematic
   parity gates to pass on the exact board.
2. Export with `export_jlc_package.py`; use the KiCad-capable Python
   interpreter. The exporter reads per-refdes LCSC identity from Circuit JSON
   and the part dossiers.
3. Run stock verification/search and the specification-confirmation pass.
4. Adopt only verified identities in source; re-export rather than editing CSV.
5. Run `bom_source_check.py` against BOM, Circuit JSON, and dossiers.
6. Run `bom_legibility_check.py` on staged bytes.
7. Run population, rotation, stock, twin, render, via-process, and payload
   coverage gates before sealing.

The public-catalog screen requires `qty per board x build_quantity` plus the
project's `assembly.yaml` `public_stock_surplus` on every coded BOM line. New
projects configure 150 units. Invoke `jlc_stock_check.py --min-stock N
--min-surplus S --assembly path/to/assembly.yaml` with those exact values and
ship its JSON sidecar; release
freshness rejects a sidecar whose recorded surplus or line arithmetic differs
from the project authority. This is one absolute buffer per aggregated LCSC
BOM line, not per reference. A shortage may be classified explicitly for a
design-sound, sourcing-blocked release, but it cannot pass part selection or
be described as order-ready.

The exporter writes `artifact_index.json` last with exact board identity and
role-keyed hashes for the Gerber archive, BOM, CPL, drill family and optional
via-order note. Downstream review/release automation resolves roles through
this index; it must not rediscover a plausible same-basename artifact.

### Optional jlcsearch catalog screen

Use `scripts/jlcsearch.py` for candidate discovery and report-only screening of
an existing preliminary PCBA request against the exact Circuit JSON identities.
The public API needs no key for tested requests; use the adapter's descriptive
User-Agent. Default Python requests have returned HTTP403. Network failures
are unknown evidence, never zero stock. The general search excludes zero-stock
parts: an empty result means not observed, not proof of zero stock or absence.

```bash
python3 skills/jlcpcb-fab/scripts/jlcsearch.py discover 'RC0402FR-074K7L' \
  --out /tmp/jlcsearch-discovery.json
python3 skills/jlcpcb-fab/scripts/jlcsearch.py screen \
  projects/BOARD/06_build/sourcing/prelayout_request.json \
  --circuit-json projects/BOARD/03_tscircuit/build/circuit.json \
  --cache-dir projects/BOARD/06_build/cache/jlcsearch \
  --out projects/BOARD/06_build/sourcing/jlcsearch-report.json
```

Verify a saved request against current project inputs with the owning
`jlc_pcba_availability.py verify-request` command before using it. The catalog
report is a separate evidence format: do not pass it as `--jlc-stock-json` or
as an authenticated PCBA response. Excluded assembly references retain their
existing self-supplied sourcing and assembly checks.

| Existing module | Relationship |
|---|---|
| `shopping-list` | Candidate discovery; jlcsearch and direct JLC observations count as one underlying supply pool. |
| `jlc_stock_check.py` | Direct catalog checks remain; compare discrepancies without silently selecting the larger stock number. |
| `bom_source_check.py` | Exact identities and catalog values remain independently checked; search results do not rewrite dossiers or the passive ledger. |
| `manufacturing_readiness.py` | Existing policy and provider admission paths retain authority; this report grants no placement or order permission. |
| Modular P1–P5 graph | Stock-only changes reopen sourcing. Adopted part changes reopen the owning block and affected interfaces, geometry and reviews. |

Keep raw observations and report provenance in `06_build/`. Retrieval time is
not upstream stock-observation time; preserve unknown upstream timestamps.
Search proposals still need manufacturer electrical and footprint qualification.
No automatic substitutions or footprint imports occur. Do not put live network
lookups into the deterministic electrical rebuild or replace final provider
allocation/economic checks. Numeric category filters, when used directly, need
base units (`resistance=1000`, `capacitance=1e-6`); the upstream `1k` example has
returned1ohm parts. Verify returned parameters rather than trusting query text.

Before part freeze run `manufacturing_readiness.py grade PROJECT --phase
selection`. It composes exact source-code/manual disposition, exact MPN dossier
identity and the existing source-value checker into one hash-bound early
receipt. Confirm every critical or footprint-driving code in JLCPCB's PCBA
interface; LCSC `stockCount` is not assembly availability. Use the same
request/grade tool with `--phase selection` on a small candidate BOM whenever
that choice can change topology, package, escape, connector geometry, or the
fab tier. This is intentionally a targeted pre-freeze check rather than a
second full-BOM upload.

As soon as a complete preliminary PCBA BOM exists, and before placement or
routing, prepare and grade the quantity-expanded probe:

```text
jlc_pcba_availability.py prepare 03_tscircuit/build/circuit.json \
  --assembly 03_src/rules/assembly.yaml --build-quantity N \
  --procurement-policy 01_docs/sourcing/procurement-policy.yaml \
  --phase prelayout --out 06_build/sourcing/prelayout_request.json \
  --response-template 06_build/sourcing/prelayout_response.csv
# Upload/check in JLCPCB and fill the exact response rows from its UI/export.
jlc_pcba_availability.py grade 06_build/sourcing/prelayout_request.json \
  06_build/sourcing/prelayout_response.csv \
  --out 06_build/sourcing/prelayout_receipt.json
manufacturing_readiness.py grade PROJECT --phase prelayout \
  --pcba-receipt 06_build/sourcing/prelayout_receipt.json --json RECEIPT.json
```

Do not poll or silently wait: emit the request/template, report the operator
checkpoint once, and resume after evidence arrives. `AVAILABLE` is the early
state. Missing, stale, partial, insufficient, substituted, or unrecognized
rows are not accepted.

Fill the generated columns exactly. `Requested LCSC` is immutable;
`Resolved LCSC` records what JLC actually selected; `PCBA Status` uses
`AVAILABLE|ALLOCATED|UNAVAILABLE|INSUFFICIENT|NOT_FOUND|UNKNOWN`;
`Available Qty` is an integer; `Checked At` is RFC3339 with timezone; and
`Evidence` names the saved uploader row/export/screenshot. The checker
recomputes the receipt from these saved bytes, so editing its verdict has no
effect.

Schema-v2 responses also require an explicit fulfillment/economic disposition.
Use `PUBLIC_STOCK|MY_PARTS|PREORDER|GLOBAL_SOURCING|CONSIGN` and
`NO_MINIMUM_COST|QUOTED|UNKNOWN`. Capture public/My Parts quantities,
attrition, MOQ, order multiple, actual preorder purchase quantity, exact quoted
part subtotal and fees, and any assembly charged quantity/subtotal. Use the
cart/quote subtotal at the actual purchase break; never multiply a search-card
price. `NO_MINIMUM_COST` is an explicit assertion with zero purchase/minimum
charge values, not a blank shortcut. Missing economics is `INCOMPLETE`.

The receipt grades availability and economics independently. For preorders it
reports both total cash outlay and **gross surplus cost**; raw surplus count and
ratio are diagnostic only. It separately reports nonrecoverable assembly excess
cost because JLC assembly minimum/attrition units may be charged and discarded
rather than retained in My Parts. Only an explicit durable policy may authorize
nonzero per-line and aggregate exposure. Speculative future reuse never reduces
gross surplus cost.

Before an order claim, repeat against the exact staged `fab/bom.csv` with
`--phase order`. Every line must read `ALLOCATED`, not merely `AVAILABLE`, and
the receipt must verify against that BOM hash:

```text
manufacturing_readiness.py grade PROJECT --phase order --release RELEASE \
  --pcba-receipt ORDER_RECEIPT.json --json ORDER_READINESS.json
```

Selection and prelayout receipts prevent avoidable backtracking but cannot
satisfy final allocation. Generic passives may use reviewed equivalent pools
with identical value, tolerance, voltage, dielectric, package and relevant
temperature/precision constraints; critical parts remain exact-MPN locked.

An explicit user-approved design-only public-stock policy may supplement a
JLC `LOW_STOCK` observation with the same exact part at a distributor. Use
`manufacturing_readiness.py grade --phase prelayout --distributor-policy ...
--distributor-quotes ...` alongside the ordinary catalog inputs. The schema and
supported provider are documented in the sourcing contract. Preserve the
original JLC report; do not rewrite its stock or verdict. The composed result
names distributor-covered rows separately, rejects missing/network-failed JLC
rows, and cannot be used for selection, authenticated receipt composition or
order. It is not Q-2SOURCE or assembly acceptance. No public observation or
policy authorizes payment, procurement exposure or a substituted part.
The external observation must cover `required_qty + public_stock_surplus`,
including supplier minimum/multiple expansion. A narrowly admitted ECIA
TrustedParts authorized-channel aggregate may prove exact-MPN public
availability when it declares authorized-only coverage; because it is not a
reservation or supplier quote, it has the same pre-layout/DO-NOT-ORDER limit.

`bom_source_check` proves semantic identity. `bom_legibility_check` proves the
recipient can parse what was written:

- `F-MPN`: coded rows carry MPN and LCSC from dossiers or the vetted passive
  ledger, and independent resolution paths agree;
- `F-WORDS`: no source placeholder or LCSC code masquerades as Comment;
- `F-ENCODE`: BOM decodes equivalently under UTF-8 and CP936 expectations.

The exporter enforces these constraints; the staged check independently
regrades the actual upload bytes. A manual repair is a producer defect. Stop,
fix the exporter/source, and regenerate.

## 3. Part specification and stock

Search suggestions match strings and packages; they cannot prove voltage,
tolerance, dielectric, power, polarity, orientation, or exact IC identity.
Before adopting a code verify:

- ceramic voltage and effective capacitance under bias;
- resistor tolerance and dissipation;
- electrolytic/polymer voltage, ripple, height, and diameter;
- exact IC/diode MPN or a deliberately accepted equivalent;
- connector series, pin count, gender, and orientation;
- component class—NTC/PTC/fuse/bead is not a generic resistor.

Run catalog verification with a JSON sidecar and parse the final verdict as an
advisory negative filter. It cannot produce `SOURCING: CLEAR`. Require the
prelayout JLCPCB PCBA receipt before layout and the final allocation receipt on
order day. Missing/unparseable authority fails. Treat the unofficial catalog
endpoint as network work with polite serialization,
backoff, heartbeat, and deadline; fall back to a current catalog mirror or
manual JLC search when unavailable.

Escalate a part absent from JLC in this order:

1. select a placeable equivalent;
2. consign it—still placed, remains in CPL, with MSL/handling declaration;
3. declare a dated, evidenced `not_assembled` disposition and exclude it from
   position files.

Never leave an uncoded part on the CPL. Never use a fake catalog code.

## 4. Population and assembly coverage (`A-POP`)

Run `assembly_coverage.py` against the staged archive. It independently
re-derives board population minus CPL and must not reuse exporter filtering
logic. Every footprint is one of:

- JLC sourced and placed;
- consigned and placed;
- declared not assembled with closed-vocabulary reason, dated evidence, and
  position-file exclusion;
- board-only mechanical item.

Declare `sides` as a non-empty list of distinct `top`/`bottom` values. The
coverage gate compares this policy to native mounted layers for every fitted
SMD, including manual/consigned parts absent from the CPL. Removing an SMD
from machine placement does not exempt its assembly side. Each `not_assembled`
reference must have exactly one disposition; duplicate or conflicting records
fail and cannot remove a component from the fitted-population denominator. Explicit DNP and
bare test-point declarations represent nonpopulation; THT solder joints and
thermal vias do not create a second SMD population. Each CPL side must match
its native footprint mounting layer. The report includes the fitted SMD side
histogram and graded denominator. A missing legacy policy is explicitly
ungraded and cannot support a single-side claim. This check does not prove
body clearance, paste access or solderability; those layout/process gates remain.

Keep the population declaration only in `03_src/rules/assembly.yaml`. Generate
manifest summaries from it. A hand-typed `--also` list or release note is not a
second population authority.

Ship coverage and stock sidecars in verification with explicit denominators.
`0 findings` without a population denominator is not assembly evidence.

## 5. Rotation and polarity authority (`A-ROT`, `A-POL`, `M-PROV`)

The exporter currently enforces A-ROT. It exits nonzero, deletes stale BOM/CPL,
and writes `rotations_unsourced.csv` when any placement lacks measured
per-LCSC authority. The footprint-name database is advisory only.

Clear an unsourced placement by:

1. Run `jlc_rotation_measure.py BOARD REF=LCSC --row`.
2. Compare numbered-pad fit and numbering-free polarity/orientation channels.
3. Validate against the manufacturer terminal/pin drawing and JLC's own cached
   footprint/model.
4. Add one measured row to `jlc_lcsc_rotations.csv` with independent evidence.
5. Run `jlc_rotation_audit.py --table`.
6. Re-export the CPL before sealing.

Never populate rotation authority from `jlc_twin`'s fitted offset or from a
table derived by the checker being graded. A symmetric footprint exemption is
measurement of pad/graphics symmetry, not a name heuristic.

Every ref listed in `rotation_human_gate.txt` must be checked in the JLC order
preview. This includes single-channel polarity cases, disagreements, THT
operator orientation, and bottom-side placements. Preview review is an
independent downstream backstop, not the primary source of rotations.

## 6. Uploader-side human checks

The first order of a board requires evidence captured from JLC's resolved UI:

1. Upload Gerber zip, BOM, and CPL in that order.
2. Save JLC's resolved/matched BOM table and run the `F-ECHO` comparison. A
   redirected LCSC code is a finding; zero overlap means the wrong table was
   saved.
3. Confirm every `rotation_human_gate.txt` row in the 2D/3D preview.
4. Capture layer count, stackup, controlled-impedance choice, via-fill/cap
   selections, BOM mapping, CPL rotation, and THT/manual-assembly previews.
5. Re-run stock on order day.
6. Confirm DNP semantics and that no real part was excluded by a ref/value
   naming heuristic.

Re-uploading BOM can reset matching/DNP choices; CPL re-upload changes
placements. Record the actual final previews. Do not claim `ORDER` until these
operator-side facts exist. When boards arrive, verify power-entry polarity and
continuity with a meter before applying the normal source.


## Evidence-backed assembly locators (A-LOCATOR)

Use `03_src/rules/assembly_locator.yaml` only after an independent reviewer
finds that the exact omitted references can be identified safely from an atlas.
This does not authorize blanket omissions or changes to silk size/clearance.
The locator supports mixed-side full-board context and top-side 1–4 pad
exceptions whose native CPL datums/rotations coincide; unsupported exceptions
fail explicitly. Native mounted-side Fab and silkscreen determine each body
and omission. The offline map automatically selects the mounted side when a
reference is searched, and offers an explicit side selector. Bottom is viewed
from below after flipping left-to-right about the native board-frame centre:
X increases leftward, Y down. Text and displayed native coordinates/rotations
are never reflected. Top exception pages show top components only; bottom
context remains available for every bottom reference in the interactive map.
The source orientation describes the top side. Source and generated schema1
shapes remain unchanged; generated `side` and `view` declare the convention,
and exact producer/template/checker hashes require fresh bundles after change.

The config names title, owner, orientation and full exception records (reference,
value, MPN, supplier code, native position/rotation/side, pad/net identities).
The source `policy_waivers.yaml` names exactly the same refs with a project-specific
rationale and runnable evidence: `assembly_locator_check.py project <project>`.
The generator does not author or approve that waiver.

`export_jlc_package.py` discovers the selected config and generates the offline
HTML/JSON and numbered PNG/PDF atlas from that run's PCB and BOM/CPL. It calls the
separate checker before writing its artifact index. For an isolated diagnosis:

```text
/usr/bin/python3 assembly_locator.py BOARD BOM CPL CONFIG OUT
/usr/bin/python3 assembly_locator_check.py exact BOARD BOM CPL CONFIG OUT
```

PR-REVIEW requires the current bundle in `06_build/pre_route/current_assembly`.
Each record and page is checked, not merely the total. The manifest binds all
inputs and source tools; HTML's data, clickable geometry and executable must
agree, and each PDF page must contain the corresponding PNG image at the
expected transform. Independent visual review still grades clarity and intent.

Ship the entire indexed locator role with the release, along with
`source/assembly_locator.yaml`, `source/policy_waivers.yaml` and the exact three
locator tool/template files under `source/locator_tools/`. The release freshness
gate validates this archive without consulting current project files. The
ORDER_README links both `fab/assembly_locator.html` and `fab/assembly_locator.pdf`.
A later change to the PCB, BOM, CPL, exception identities or locator source
stales the bundle and requires regeneration and affected independent review.

Structural `exact` checking prepares a bundle for review. The `project` and
`release` checks additionally require the existing independent render review
to name `locator_manifest_sha256` and `locator_reviewed_refs` (a JSON array of
all reviewed exceptions), along with reviewer, completion date, render kind,
SOUND design verdict and exact board hash. These fields are supplied by the
independent reviewer, never by the generator. Missing or stale visual acceptance
blocks the consuming gate even when structural identity checks pass. The normal
`tests/run_tests.sh` suite runs the public CLI and all locator hostile controls
through `tests/t1_assembly_locator.py`.
