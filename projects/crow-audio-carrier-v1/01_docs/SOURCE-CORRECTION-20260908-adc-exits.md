# ADC source milestone — 2026-09-08

Disposition: accept the bounded **authored-source** change under ADR0013.
NOT ROUTE-READY; no native PCB DRC, layout seal, release, order or power-up
claim. ROOT is author and diagnostic operator, not an independent PCB reviewer.

Starting commit:358f87bb3ca5a5fa7d089cce41b808258a2d0b8c. Before editing,
969 tracked carrier subjects/100,617,233 bytes were hash-bound against the
clean committed tree at09:43:19Z. That Git commit is the recoverable archive;
ignored files are not falsely included in this census.

## Accepted delta

- Two capacitor poses, C_LDO_D and C_VDDIO; all other placements exact.
- Replace only ADC5/9 power knees among32 old banks; preserve the other30.
- Add25 supply/filter/VMID/control/return banks:57 total,151 primitives,
  20 vias. This change grades75 primitives and12 new0.50/0.20mm drops.
- Seven named width floors, nine pin-pitch clearances and three F.Cu
  paddle-gap barriers; no inner-plane split or global fabrication relaxation.
- Complete three-pad LDO_D_FILT/VMID1/VMID2 owners removed from generic
  groups and added to exclusions. Five local owners plus159 generic/GND/40NC
  cover205 live nets. Native topology remains299 refs/868 pin memberships.
- Preserve F.Cu-only power distribution,1.20mm bulk,2.5A transient bound,
  exact clock source and all regulator geometry/current subtotals.

See ADR0013 for exact additive length/count and conditional resistance data.
3V3_ADC is18.27177620562909mm/20 subnominal items; control maximum3.154070/3.
These are bounded geometry allocations, not safe fault-duration or thermal
results. FILT reservoir feeds and control continuations remain partial.

## Measured scoreboard

| Check | Result |
|---|---|
| Final full project suite,09:58:18Z |141/141 PASS |
| Final live ADC native screen,09:57:57Z |104,559 checks;zero findings;27/27 contacts |
| Moved-cap geometry/proximity |6,987 checks;zero findings;three exact pin/cap pairs |
| Existing regulator/digital source,10:00:07Z |47,745/20,931 checks;zero findings |
| Rules source / native net references,10:00:08Z |8/8 classes;351/351 references |
| Exact-input source-shadow ownership |205/205;159 generic plus5 local/GND/40NC |

The source-native comparison is not the saved-board DRC. Filled-plane edges
are deliberately absent from the contact graph. Neither record grants routing
admission or overrides stale generation/review evidence.

## Rejections and preserved evidence

Raw finite-run scripts/logs/results are in `06_build/tmp/adc-source-20260908`.
OBSERVATIONS records the improving candidate sequence, exact runtime windows,
parser/plot diagnostics, all failed hypotheses and the later source fixes.
Each executable attempt uses the shared bounded runner,120s deadline/10s
heartbeat (direct public fetch additionally90s curl/10s connect limits).

The first two live suites returned137/141 and140/141. They exposed duplicate
generic ownership and the older widened-entry0.25mm requirement. The latter
found actual0.245059/0.214530mm gaps; the two0.60mm extensions were shortened
to0.05mm, without reducing width or waiving clearance. Old test populations
were scoped to their actual owners; the new native ADC checker separately
grades all cross-interactions, physical via layers, pad holes and masks.

The Cirrus public ZIP was already known. New inspection of PCB/PADS/IPC/
Gerber/stack bytes strengthened the dossier;49/49 independently exported pad
positions and four CFG drops reconcile. Different stack, smaller vias,
4.8mm EP land and older CN/B0 descriptor prevent numerical transplantation.
Only derived measurements/hashes and OUR source geometry are preserved;
no vendor board/Gerber/PCB-PDF assets are added to the repository.

## Next boundary

Finish remaining source egress/current-return intent, then exact-source
generation/admission and fresh independent schematic/pin/placement/render
reviews. Run bounded routing and grade actual filled return, complete current
paths, thermal/fault limits, width/extent and SI on the produced board.
Complete immutable release verification afterward. The flow blocker prose
now distinguishes these stages instead of requiring a future filled-board
verdict before generating that board.

The next source check is **wide-power landing and branch reach**, especially
the west C_VDDA1/2_10N taps: their0.60mm cap-side items do not prove that the
generic1.20mm trunk can reach them. Also check the still-partial FILT reservoir
feeds and ADC exposed-pad thermal/plane return. Analog input waves already
declare0.20mm width/clearance; do not mistakenly treat them as0.25mm or claim
the analog input fanout was included in this75-item source screen.

Carrier still has no release. The pod seal is unchanged and sourcing-held;
the parent remains boardless/commissioning-held. Preserve TOP77 and the
0.20A first-power HOLD. No purchase, account, upload, private information,
energization, sealed artifact mutation or main push. Both child seals and a
fresh exact-base/head P-PUBLISH PASS remain prerequisites for main.
