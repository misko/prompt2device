# Current quote draft — 2 carriers + 8 pods, JLC SMT and through-hole

2026-10-31. User-selected assembly split. **Local preparation only: no submission,
purchasing, allocation or production approval.** Supersedes r3 and older 2c8p
handoffs for ownership. Earlier files remain historical; release unchanged.

## Assembly scope

| Board | Assemble | JLC SMT/board | JLC THT/board | Home/board | JLC batch | Home batch |
|---|---:|---:|---:|---:|---:|---:|
| Carrier | 2 | 127 | 10 | 1 | 274 | 2 |
| Pod | 8 | 28 | 1 | 2 | 232 | 16 |
| Total | 10 | — | — | — | **506** | **18** |

JLC THT: **24 RJHSE-5080 Ethernet jacks, two PJ-102AH power jacks and two
R-78E5.0-0.5 modules**. JLC SMT: 478 unchanged components. Home: **two SC0915
Picos, eight CMA-4544PF-W microphones, eight CPE-203 buzzers**. Total: 524 parts,
not solder joints or purchasing quantities. Both carriers get factory-installed
connectors/regulators; neither is an SMT-only spare under this quote scope.

Candidate fabrication stays five bare carriers/ten bare pods; assembly is two/
eight. Surplus bare boards get no components. All vendor BOMs are **per board**;
do not multiply their row quantities. No purchase of home parts is authorized.

## Files and placement readiness

| Files | Status |
|---|---|
| `carrier-bom.csv`, `pod-bom.csv` | Complete requested JLC scope: 137 carrier / 29 pod references; no home parts |
| `carrier-gerbers.zip`, `pod-gerbers.zip` | Unchanged released fabrication data |
| `*-cpl-SMT-ONLY-INCOMPLETE.csv` | Unchanged SMT rows/rotations; NOT full mixed-assembly CPLs |
| `*-cpl-THT-NOT-UPLOAD.csv` | Review worksheets: centroid and vendor rotation deliberately blank |
| `tht-native-anchors-NOT-CPL.csv`, `manual-native-geometry.json` | Native pad/pose evidence; NOT vendor placement coordinates |
| `scope.csv`, `procurement-plan.csv` | Full per-reference ownership and 38-identity batch demand |
| `jlc-tht-parts.csv`, `home-install-parts.csv` | Three exact identities per installation owner |
| `manifest.json` | Source/output hashes; upload_ready=false; no purchase approval |

**The BOM/ownership update is complete; a combined upload-ready CPL is not.**
The inherited native THT origins coincide with pad 1, not verified component
centroids. Carrier J1/J101–J108/U10 and pod J1 still need the JLC centroid/datum/
orientation mapping. This is **three part-type mappings, 11 per-board positions,
28 batch installations**, not 28 independent design problems. Native coordinates
are +Y down; retained SMT CPL is +Y up. Do not copy anchors/native angles into
vendor fields or dismiss a missing-CPL warning by dropping the parts.

## Next bounded step and MacBook handoff

1. Resolve the three THT mappings using retained native pad geometry, exact
   manufacturer drawings and JLC convention/library preview. Produce reviewed
   complete CPLs with exactly **137 carrier / 29 pod** references and no home
   references, preserving every existing SMT row/rotation. Do not guess missing
   data or label a generic data test as engineering/vendor acceptance.
2. Alternatively, if JLC explicitly supports a separate manual-operation quote/
   placement-review route, obtain all **28 THT operations** as a named line item.
   Do not silently omit them or transfer them home. Contact/submission remains
   outside this local preparation authority.
3. Once complete files are reviewed and browser actions authorized, use the full
   r4 BOMs, unchanged Gerbers and reviewed complete CPLs; set assembly **2/8**.
   Restore RJ/PJ/RECOM selection in existing drafts. Review exact references,
   pin orientation and THT seating in the final production preview.
4. Restore **RECOM to JLC sourcing**: two installed; gross allowance unknown.
   C5199916 is a catalog locator, not private inventory. RECOM and ADC JLC code
   fields remain blank pending exact Global Sourcing/private offer or accepted
   consignment matching. Preserve the PJ-102AH Same Sky/CUI identity review.
5. Resolve unchanged SMT shortages too. [External stock observations](../../keyless-external-20261031/README.md)
   are leads, not JLC allocation. Keep actual job allowances separate (retained
   fuse 28 and Murata 1 µF 40 versus installed 24/12). Confirm THT attrition,
   packaging, fees and dates; never double-count shared stock.
6. Obtain complete fabrication/components/SMT/THT/setup/sourcing/shipping/tax
   pricing. Old SMT-only prices exclude this restored THT scope. Stop before
   payments, reservations, procurement or production commitments.

Do not restart design or repeat stock sweeps to solve the placement gap. After
one bounded mapping pass, report any specific missing convention/evidence and
the separate-manual-quote fallback rather than looping.

## Retained controls

No circuit, footprint, native board, sealed release or fabrication ZIP changed.
Existing stack/stencil, hole/seating, clearance and thermal limits remain binding;
current matching, preview, process and allocation holds remain open. Adding THT
labor does not authorize paste changes or adding reflow paste to THT holes.
Keep Pico/acoustic pads and holes suitable for later home assembly.

Pico remains original SC0915 with **module D1 only** removed, never carrier D1,
plus castellated soldering/inspection. Accepted prototype fit risk is unchanged.
Microphone/buzzer home assembly stays last, with retained polarity, thermal and
no-reflow/wave/wash controls and protected acoustic ports. Detailed retained
[assembly instructions](../../../releases/crow-prototype-v3-first-run-5c10p-public-v1/historical/documentation/carrier/instructions/32-assembly-instructions.md)
still govern technical handling; historical quantities/ownership there are
superseded here. No firmware/functional qualification is claimed.

## Validation and reproduction

```sh
python3 -B projects/crow-array/order-readiness/jlc_tht_quote.py verify
python3 -B -m unittest discover -s projects/crow-array/order-readiness -p 'test_*.py'
python3 -B projects/crow-array/publication.py verify
# Expected exit 2: complete THT placement mapping/CPL is still missing.
python3 -B projects/crow-array/order-readiness/jlc_tht_quote.py verify --require-upload-ready
```

`build --output UNUSED_PATH` reproduces data into a fresh directory and refuses
overwrite. Manifest binds inputs and generated outputs; README/notes are human
guidance, not acceptance receipts. Tests reject altered BOMs, invented readiness
and overwrites. Data consistency PASS is not placement or manufacturing approval.

Validation completed: 53 order-readiness tests pass (eight new r4 tests); all
256 released payload files preserve their hashes. KiCad pcbnew 10.0.4 reopened
both boards read-only and passed the native identity/pose/exclusion audit,
preserving all 25 inherited SMT angle offsets. All 11 THT geometry records match
their current released native board hashes. KiCad printed property-enum/image
handler diagnostics but completed successfully; no native file was saved.
The upload-readiness gate returned exit 2 as expected, not a false pass.

**Local and unpushed.** No MacBook/browser draft changed. Do not use r3's home-THT
instructions for a new mixed-assembly quote.
