# Crow commissioning brief

status: in-progress

## Raw user inputs — authoritative provenance

The original prompt, chronological decisions and capability profile are
preserved byte-for-byte at the following project-relative paths. Read them
before deriving requirements; the hashes identify this initial source snapshot.

- `01_docs/inputs/PROMPT.md` — SHA-256 `ffc7683516e2022a1bf6e2e1c834d2fbf460f8a1e17ac97b869a5bbb0542240c`
- `01_docs/inputs/USER_DECISIONS.md` — SHA-256 `c1fa2df564fba7ae4d5cf3a62d28db11ecb124b7f0d1e5b1c3f7a67014609309`
- `01_docs/capability-profile.json` — SHA-256 `d9b204845b556dbe77b7c00593d9bb377fad2ccb00c3cb244360cda40866577b`

Later decisions must explicitly identify what they supersede; preserve earlier
sources. Do not infer that every statement in a raw input is an accepted fact.

## Interpreted requirements and acceptance criteria

The raw PROMPT.md intentionally retains both the verbatim fresh request and
chronological decisions1–5. USER_DECISIONS.md is the later12-V-only clarification.
This is not an inheritance of any earlier Crow board, budget, range or parts.

| ID | Confirmed requirement / authority | Schematic-stage acceptance intent |
| --- | --- | --- |
| R1 | Two board types, carrier plus microphone pod; original prompt | Complete editable source/native drawing for both designs, no functional placeholders |
| R2 | Eight pods on an8m-diameter circle, flat roof; prompt and decision3 | Eight complete channels and explicit dedicated cable/pair/return contract |
| R3 | All eight raw audio channels over USB to Raspberry Pi; prompt | Credible shared acquisition clock, channel order, USB bandwidth and capture resources; later firmware obligation stated |
| R4 | Later direction/position or timing fingerprint, not identity/analysis; superseding decision2 | Continuous sample sequence and stable/calibratable relative timing; no crow-recognition algorithm or location guarantee |
| R5 | One independently USB-controlled calibration buzzer per pod; prompt and decision1 | Eight complete default-off drivers and command resources; acoustic qualification separate |
| R6 | CAT5/6 carrier-to-pod cable; prompt and decision4 | Exact pin/pair mapping; no implied Ethernet or PoE |
| R7 |12V sole operating input; later USER_DECISIONS.md | USB-only electronics/buzzers off; ordinary USB data and high-impedance VBUS sensing retained; no nonstandard data-only cable |
| R8 | Five complete arrays; decision3 | Five carriers plus40pods, quantity and cost basis explicit; no invented spares |
| R9 | Common R/C exact qualification deferred to final batch; decision5 | Electrical properties checked when needed; exact identities close before sourcing acceptance |

Stable process policy: only this isolated vNext package; fresh parts/architecture
without XMOS bias; Astra coordinates/plans/fixes/writes vNext, SOL authors or
independently reviews bounded tasks (latest approval substitutes gpt-6-sol for
unavailable SOL6.1), Terra may assist simple work. Independent review must not
be the author's own verdict. Use JLC-first then brief Western fallback; exact
in-stock is sufficient unless published quantity is inadequate. No two-supplier
gate. User decisions include the orchestrator's top two feasible recommendations.
Stop for reflection after schematic acceptance, before placement/routing/release.
No buying, vendor messages, firmware implementation, physical rework or tests.
Task allowances/deadlines live in the journal, not these unchanged requirements.

## Assumptions and unresolved questions

The following are proposed designer-owned envelopes for independent admission,
not new user approvals or equipment facts. They may be revised with owning review.

| Assumption | Proposed bound | Owner / closure |
| --- | --- | --- |
| Supply | Isolated regulated12V,10.8–13.2V inlet,>=1A continuous,current-limited,<=2A sustained short | Specify and verify actual adapter before connection; no exact adapter is known |
| Cable | <=6m/run, copper U/UTP CAT5e/6, four intact pairs; aggregate supply/return each<=0.5ohm hot incl contacts | Harness design/continuity check before connection; no arbitraryCAT cable guarantee |
| Environment | Internal electronics air−20..60C, co-located Pi/carrier, no separately earthed pods/cross-building cable | Enclosure/shading/site bonding review before deployment; no lightning or ingress certification |
| Acquisition |24ksps,eight24-bit transport words,useful300Hz–8kHz,sourceAC<=15mVrms for headroom model | Architecture resources and calibration design now; firmware/audio measurements later; no ENOB/range guarantee |
| Calibration | Sequential pod beeps; retain raw channels, exclude locally clipped self-pod observations | Actual phase/skew/acoustic response and frequency-dependent correction need later qualification |
| Prototype models | Padded semiconductor/capacitance/thermal allocations explicitly identified in adopted design | Known incompatible evidence reopens design; otherwise named first-article falsifiers, not fictitious maker guarantees |

No user cost ceiling, recording distance, exact adapter/Pi model/current hardware,
installed cable length or guaranteed bit accuracy exists in this fresh scope.
Use whole-system cost assessment including Pi/storage/power, cables, enclosures,
assembly and mounting; do not deduct allegedly owned equipment. Firm quotes and
physical geometry become due before their procurement/fabrication/deployment use.

Commission acceptance requires independently agreed scope, bounded input facts,
capability applicability and qualification boundary on these exact files.
Architecture, exact sourcing and final schematic/harness/readability checks are
separate downstream receipts, not established by this interpreted brief. Physical
measurements requiring a prototype are later; known contradictions are not waived.
