subject: crow-mic-pod-v3 exact routed board at 08b79dbce2857341632c5224263db60adb4274e5
date: 2026-09-03
review_stage: exact-final
review_kind: redteam-layout
reviewer: redteam-agent (Codex, layout/thermal/power-integrity lens)
independence: independent-from-design-author; prior verdicts were not used as evidence
context-given: full-tree; exact routed board, route authority, native DRC, realized copper, BOM/CPL and plotted fabrication outputs independently reopened
source_commit: 08b79dbce2857341632c5224263db60adb4274e5
board_sha256: a932200e0976418383fae0c131dfe2a5768c00ef261b611762ccd3507f05ca8f
design_rules_sha256: 0cbb7cab0be102a78062338cd69688b8d7de20728e9e3e40cd9907fa374ecf84
route_yaml_sha256: bbc146dcd6b1aa64d660981ce14734d66af3921abe312e5015a7387b4f60f056
prelayout_inputs_sha256: a662d56e1e32d38b22960cb37facfa29dd2fda9a3374556b98c7d4ed7b681aaa
prelayout_checkpoint_sha256: 9016b9f58a7ba8bacb16237e8d6ebdb38e3feed12b3b6ec27cd2e7e9831c8a08
native_drc_sha256: 52666334dc34f19355f0167dcea12fdf76e7da208ea153f9b49efd2cf9220d19
route_acceptance_receipt_sha256: c590e736ae947e60ef0f8fc0858f4c563bd2c73cc87cddf118bb9016f0d0c19d
realized_route_receipt_sha256: db2a88eb683583363c2011528aeb6afe8d42389af42465a025a56ef02765a3dc
bom_sha256: 905e78de505fa93aebf2c092371a62bedeb59b8cab9adc484108397f8089e49c
cpl_sha256: c310bc5e94e5689507a29849372d7103426253ad8b532c1729ace9c59eb3199e
fab_artifact_index_sha256: 0fa514af58ad57eebd7217530f7ecd1761d3c6de018f85b4523c6f396650784e
gerber_archive_sha256: 1f9708f0014b2036c31d85bf87c3b2e2a801b83084dd13e47d1ed39046b01010
model_coverage_sha256: aa8657aa91d86a45d6ed8d41f213a9cab8dff894e8f453d17c041a8b2cc2b732
rotation_human_gate_sha256: d532d9e2cdc20072b18df376e60f4fd7d8bc944be47d47c7db15480144c709e1
design_verdict: SOUND
order_verdict: BLOCKED-SOURCING
p0_findings: 0
p1_findings: 0
p2_findings: 0

# Final routed-board layout, thermal and power-integrity red-team review

## Verdict and claim boundary

The exact routed-board design is **SOUND** in this lens. I found no unresolved
P0, P1 or P2 layout, return-path, thermal, power-integrity, fabrication-geometry
or assembly-population finding. The order verdict remains
**BLOCKED-SOURCING**, so the candidate is **DO-NOT-ORDER**.

I independently inspected the exact board, top/bottom and copper-only renders,
board outline, courtyards, keepouts, service geometry, routes, vias, zones,
native connectivity, BOM/CPL and current plotted fabrication payload. I also
replayed DRC, route acceptance, realized path, class/ampacity, waiver,
population, rotation and fabrication-payload checks. This review does not
claim fabricated fit, measured temperature/noise, enclosure readiness or JLC
order resolution.

The final layout seal and handoff are intentionally downstream. Review files
are seal inputs, so a new exact seal must be issued only after all four final
reviews are committed; no pre-review seal hash is asserted here.

## Placement, service and fabrication geometry

- The board is a 60 x 40 mm, two-layer design. It contains 44 footprint
  objects: 40 electrical references and four M3 mounting holes. All 31
  machine-fitted references are top-side; J1 is a controlled manual fit, MK1
  is a two-wire off-board capsule landing, and TP1-TP7 are bare probe pads.
- J1 faces outward at the north edge. Its mating approach, two locating holes,
  pad-1 marker and pin-function silk agree. Explicit keepouts protect both
  connector pegs, the four mounting holes and the dense LDO output-bypass cell.
  All seven probe pads and both MK1 lands remain solder/probe accessible.
- F1, D1 and D2 sit directly inboard of the cable boundary; U3 sits immediately
  behind the balanced pair. The LDO and its bypass/feedback parts form a compact
  cell, while the microphone and op-amp sections remain physically partitioned
  without a courtyard, body-envelope or foreign-pad overlap.
- Exact model coverage is 32/32 fitted bodies. The assembly set is 31/31 and
  the worst CPL pad-array-centre error is 0.00000 mm. The shared rotation table
  passes 149/149 rows and exact-board rotation resolution passes all 31 CPL
  placements. U1, U2 and D1 still require the named human JLC preview gate.

## Copper closure and power integrity

Fresh native KiCad DRC on the immutable board reports zero violations, zero
unconnected items and zero schematic-parity findings. The routed subject has
255 track segments, 57 through vias and 20 zone/rule-area objects: one real GND
zone on each copper layer plus 18 local pad-rescue rule areas. All 57 vias are
0.60/0.30 mm; the realized aspect ratio is 5.333 against the tier limit of 10.
No special via process is declared or needed.

The project-specific realized-copper replay passes 22/22 checks. In particular,
the D1-to-D2 path is 11.020691 mm and remains the unavoidable prefix to every
protected-input load; both connector-to-U3 clamp paths are F.Cu-only and no
longer than 4.097307 mm. Every LDO input/output/feedback/NR bypass path and the
OPA1679 local bypass is F.Cu-only, via-free and under its 3 mm bound. The two
audio probe branches are each 3.500024 mm and remain downstream of U3.

The generated class audit passes 14/14 checks. The 0.5 mm `POD_INPUT` class is
ample for its 0.10 A allocation, and the 0.4 mm `QUIET_POWER` class is ample
for 20 mA. The three deliberately unpoured input nets are covered by the exact
R-POUR waiver: 3/3 cited facts regenerate, the summed ideal 35 um copper
resistance is 0.08570 ohm, and the 0.10 A allocation therefore predicts only
8.570 mV board-copper drop. This is not a cable or connector-drop claim.

## Ground plane, return paths and thermal paths

The bottom copper plot contains one continuous GND region across the board;
the top GND zone resolves into eight filled regions around routed clearances.
Thirty-nine GND stitches join the two layers. The largest local opposite-plane
gap I measured along the 5 V route is about 2.45 mm. There is no controlled-
impedance, phase-matched or RF net: every intentional signal is ordinary audio
or DC below 20 kHz. On that explicit applicability boundary, the continuous
bottom plane, dense stitching and short top-layer analog cells close the
otherwise-human R-PLANE review. Cable CMRR, noise and EMC remain measurements.

U2's exposed GND pad has a direct 0.3 mm top trace to a GND via about 1.7 mm
away. The nearest return vias to the LDO input/output capacitors are about
1.05-2.10 mm away; U3 and the OPA1679 bypass return are about 1.04 mm and
1.05 mm away respectively. These are short local current loops backed by both
planes. The modeled U2 dissipation is 168 mW against the project's conservative
300 mW limit. R12/R13's worst modeled single-line condition is about 111 mW
against their 125 mW at-70-C bound. Enclosure temperature and actual copper
rise remain mandatory first-article measurements.

## Track-centre and same-net overlap disposition

The project suppresses KiCad's `track_not_centered_on_via` style diagnostic.
I re-enabled it as a warning in an isolated copy of this exact board/project.
It produced five style warnings and no additional electrical finding: three
joins around the `MIC_AC` via at (65.1, 43.4) mm and two around the VREF via at
(56.3, 50.3) mm. Every warned segment and via is on the same net, and the
recomputed copper-overlap margin is positive; the smallest is about 0.206 mm.
Native DRC remains 0/0/0 and KiCad connectivity retains each union.

I separately inspected the apparent side-entry `PRE_OUT` join at (53.8, 53.1)
mm. Its F.Cu segment passes 0.290 mm from the 0.60 mm via centre with 0.26 mm
width, leaving approximately 0.140 mm positive same-net copper overlap. KiCad
does not emit a centre warning for that pass-through, its B.Cu continuation is
centred, and the net's native connected set remains complete. These joins are
therefore a centreline/style imperfection, not an open, neck, foreign-net
short or fabrication P2. Any future copper regeneration or via relocation
must re-run this adjudication; no later mutating pass is authorized on the
reviewed board.

## Plotted payload and remaining holds

The current fabrication index reopens all 18/18 role entries by hash and size.
Its 11-file Gerber/drill archive is readable and byte-identical to the loose
plots. The payload census passes distinct front/back copper and proves one
G36 region for the B.Cu zone and eight for the F.Cu zone. The exact BOM and CPL
remain the same 31-reference population described above.

Those export checks prove file integrity, not manufacturability approval or an
order. No authenticated JLC BOM allocation/economics receipt or resolved
placement preview exists. Connector mating/service, microphone wiring and
strain relief, enclosure/weather protection, exact 4 m/15 m cable noise/CMRR/
stability, rail/transient behavior, temperatures, ESD/EMC and acoustic
performance all remain physical holds. The design is **SOUND**, but ordering
remains **BLOCKED-SOURCING / DO-NOT-ORDER**.
