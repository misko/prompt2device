# Crow r10 JLC connector rotation handoff

Use the MacBook's directly controlled, signed-in browser to capture JLC placement
data and test connector rotations. Start with pod J1, then carrier J101 and
power J1. Keep the native boards and existing r10 upload package unchanged.

**Quote-only authority:** reversible connector rotation trials, and retaining a
correction only when physical pin/peg alignment and outward opening are verified.
No purchases, payments, reservations, substitutions, sourcing/preorders, vendor
messages, checkout, manufacturing commitments or production/placement approval.
Preserve XY, side, quantity, BOM matching, stack and automatic-confirm settings.
If a translation or other change is needed, report it before acting.

This supersedes the older checklist's prohibition on rotation trials, but not its
production holds. Do not repeat the two unsuccessful TinyFish inspection passes.

## Pull and verify

Use the existing repository and shared branch
`codex/crow-jlc-source-review-20261030`. First inspect local changes. In a clean
checkout already on that branch:

```sh
git status --short
git fetch origin codex/crow-jlc-source-review-20261030
git merge --ff-only origin/codex/crow-jlc-source-review-20261030
python3 projects/crow-array/order-readiness/r10_upload_check.py
python3 projects/crow-array/order-readiness/r10-orientation-images/verify_evidence.py
```

Do not reset, discard or stash unrelated work. Use a separate worktree if needed.
The upload check must pass 213 files, 136 carrier and 29 pod factory references.
The evidence check is portable and needs no KiCad; neither check grants assembly
approval. Never upload the `*-catalog-diagnostic.kicad_pcb` files or catalog CAD.
These are inspection artifacts, not manufacturing inputs.

## Open the exact drafts

| Draft | Fabricated | Assembled | Link |
| --- | ---: | ---: | --- |
| Carrier r10 | 5 | 2 | [Carrier draft](https://cart.jlcpcb.com/smt-order/?pcbFileNo=ace1600497a949bebfdd38f3ef826f7f) |
| Pod | 10 | 8 | [Pod draft](https://cart.jlcpcb.com/smt-order/?pcbFileNo=71c384e886a94642a54e0c804cea3a97) |

Confirm draft identity and selected parts before editing. Carrier J101–J108 and
pod J1 must be Amphenol RJHSE-5080 / C599441. Carrier power J1 must be
Same Sky/CUI PJ-102AH / C3096093. There are 16 factory RJ jacks across the two
carriers plus 8 across the pods, all on top—not a two-sided placement count.
Keep every required part in scope; do not use “Do not place” to bypass issues.

## Capture the actual placement state

1. Select **pod J1** in Component Placements. Capture the selected reference,
   actual saved X/Y, absolute rotation, side, units and exact field names. A BOM
   match row or toolbar rotation increment is not a placement record. The prior
   power-jack “90°” report is unverified and may describe the increment control.
2. If fields are not displayed, use supported read-only inspection of the page's
   already-loaded placement/model data or a normal export/download control.
   Record the source field names, coordinate frame and reference association.
   Do not invent endpoints, replay write requests or modify page internals.
   Retain only relevant sanitized records; never publish cookies, auth headers,
   tokens, full unredacted HAR files, account details or private signed URLs.
3. Save **actual PNGs** locally: selected record, orthographic top close-up,
   underside/transparent view exposing model terminals and pegs, and an oblique
   view showing the opening and board edge. Keep before/after cameras identical.
   Include board landmarks and the selected reference. Save screenshots, not
   only a browser-agent description or inaccessible capture handle.
4. If supported, retain the exact viewer model and its transform. Literal pin
   labels need not be visible: identify terminals from the manufacturer drawing
   and asymmetric pattern. Distinguish model pins/pegs from bare PCB holes.
   A red orientation dot, an opening alone, or a matching BOM code is not enough.

If this direct browser cannot expose either the saved pose or inspectable
geometry, stop after one bounded attempt and report the missing evidence. Do not
keep cycling tabs, fabricate a placement row from the uploaded CPL, or contact
JLC without authorization.

## Compare against the physical references

Native top-side coordinates are millimetres, X right and Y down. All openings
point toward **native −Y**, the connector edge. CPL Y is negative native Y.
JLC may translate or rotate the view for panel rails: establish its frame from
board landmarks, not an assumed 5 mm offset. Body centres are not pin 1.

| Witness | Pod J1 RJ | Carrier J101 RJ | Carrier J1 power |
| --- | --- | --- | --- |
| Pin 1 | (7, 8.5) | (8, 8.5) | (188, 14.7), VIN12 |
| Pin 8 or pin 2 | pin 8 (14.112, 10.28) | pin 8 (15.112, 10.28) | pin 2 (188, 8.7), GND |
| Locators or pin 3 | (4.210, 5.960), (16.910, 5.960) | (5.210, 5.960), (17.910, 5.960) | pin 3 (183.3, 11.7), switch |
| Uploaded CPL centre | (10.556, −8.373) | (11.556, −8.373) | (188, −8.2) |
| Uploaded CPL angle | 0° | 0° | 180° |

RJ pin n is at X = pin1 X + (n−1)×1.016, with odd pins at Y8.5 and even pins
at Y10.28. Other carrier RJ pin1 X values are J102=26.7, J103=45.4, J104=64.1,
J105=82.8, J106=101.5, J107=120.2, J108=138.9; all at Y8.5. Their peg offsets
from pin1 are (−2.79,−2.54) and (+9.91,−2.54).

Use these retained sources:

- [Numbered-hole PNG](r10-orientation-images/numbered-holes.png),
  [carrier views](r10-orientation-images/carrier-orientation.png) and
  [pod views](r10-orientation-images/pod-orientation.png).
- [Amphenol drawing](r10-orientation-images/sources/rjhsex080.pdf),
  component-side PCB layout; [Same Sky drawing](power-jack-r10-review/source-evidence/2-P028-manufacturer.pdf), page 2.
- [All-reference native audit](r10-registration-review/native-audit.json) and
  [catalog-fit evidence](r10-orientation-images/evidence.json).

Local catalog-to-native fit found a 180° local-frame difference for both part
types. RJ residuals are at most 0.014 mm for pads and 0.004 mm for locator holes;
power-pad residual is below 0.001 mm. The local renders fit models to native
holes; they do **not** replay JLC's current interpretation of the uploaded CPL.

## Test one connector at a time

| Target | Candidate if the current saved angle equals the upload | Required evidence |
| --- | --- | --- |
| Pod J1 | 0° → 180° | All 8 terminals, both pegs and outward opening |
| Carrier J101 | 0° → 180° | Same checks in the carrier's actual frame |
| Carrier power J1 | 180° → 0° | All 3 numbered terminals and outward opening |

These are **test candidates**, not automatic corrections. If the actual saved
pose differs, reconcile it first. Record the original pose and confirm that
Undo or entering the original angle restores it before making a trial.

Perform one reversible 180° trial on pod J1, without moving XY. Capture actual
before/after records and the same pin/peg and opening views. If the original
pins already align but the mouth is wrong, investigate model registration;
do not retain a rotation that breaks physical alignment. Revert unverified or
worse changes and verify restoration. If a trial fails or cannot be verified,
stop before applying it to other references.

If both alignment and outward direction are demonstrated, save only the
quotation-draft edit and reopen to verify persistence. Then repeat independently
for carrier J101 and power J1. Apply a proven RJ mapping to J102–J108 only after
confirming the same part/model/convention; check every instance. Do not press
production/placement approval or enable automatic confirmation to save a trial.

## Return the evidence and exact final state

Save a new session folder under `projects/crow-array/order-readiness/` containing
sanitized placement records, the actual PNGs and a short report. For each of the
10 connector instances record: draft/ref/MPN/code, before and after XY/angle/side,
pin/peg agreement, opening direction, saved or reverted state, persistence check,
timestamp and evidence filenames. Explicitly mark missing values unknown.

Check that all other placements and factory reference coverage remain unchanged.
Rerun `r10_upload_check.py`. Return a diff and exact final draft state; keep full
placement/manufacturing acceptance on hold. Save evidence locally and report its
paths; publication of a new MacBook result is a separate user instruction.

Latest failed-browser findings are in the [first assessment](r10-orientation-images/jlc-browser-assessment.json)
and [focused assessment](r10-orientation-images/jlc-focused-assessment.json).
Do not adopt their unverified angle or outward-mouth claims. The original
[connector procedure](../../../skills/jlcpcb-fab/references/connector-orientation.md)
and [assembly procedure](../../../skills/jlcpcb-fab/references/assembly-and-order.md)
define the distinction between model, native placement and vendor placement.
