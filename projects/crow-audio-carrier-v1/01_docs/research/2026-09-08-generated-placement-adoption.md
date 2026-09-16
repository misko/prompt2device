# Generated carrier PCB: first placement failure and root verification

Status: **GENERATED / PLACEMENT NOT ACCEPTED / UNROUTED / DO-NOT-ORDER**.
This records the first actual PCB generated from the independently accepted
302-component schematic. It is not a release, physical qualification, or
permission to bypass an owning gate.

## Exact attempt and preservation

Source/review-adoption HEAD was
`2fb00d31a1f28f85787eb17ff077e96e70002386`. Fresh worker
`/root/carrier_placement_resume_2fb00d31` executed the checkpoint-aware
`rebuild_all.sh --resume-after-schematic-review` exactly once. Actual interval:
2026-09-08T16:27:23.558889Z through16:27:39.908254Z,16.347394820 seconds,
exit1, no timeout or cancellation. It stopped at stage[4c], before DRC,
route preparation, routing/import, or placement review. The nine prior
generated files remain archived and rehashed; no prior artifact was deleted.

Task evidence is under
`06_build/verification/placement-resume-20260908-2fb00d31-r2/`:

- Terminal handback: `terminal-result.json`, SHA256
  `c48d5375493026281fc77749f3ffb8e78dd771dee921963397bfb9c1c2dfbdfc`.
- Full35524-byte producer log: `resume-stdout-stderr.log`, SHA256
  `244806e26f6ca11c3069e49ef38538f51d1f014b6b2dc653b3632c0093c07dc9`.
- Actual board SHA256:
  `ee515a3f1ce92888259a50148e606fbeb16124ce99f1c5941dba5822712ba079`.
- Both current and newly promoted pinned schematic SHA256:
  `ee017cbb3597d4f14abd38db877aab62936b174365ead3d276af7a8ba40ec572`.

The worker reported lease release at16:39:01Z; its final JSON was written
at16:39:02Z, inside the16:40:22Z deadline. The earlier worker journal entry
labelled09:37:03 local describes reconciliation work, not the final observed
lease-release time. No worker process remains live.

## MEASURED root adoption

Root independently parsed the native board's balanced S-expressions, without
loading/saving it through pcbnew. All302 fitted refs match the independent
manifest, and all877 native netlist pin entries match physical pad nets,
including sanctioned NC sentinels. There are309 total footprints:302 fitted,
four mounting holes and three fiducials. The board contains936 pad objects
(825SMD,90PTH,21NPTH), zero track segments/arcs, nine source-declared thermal
vias, four GND layer-pour zones, and55 source-named rule areas.

Root rederived all nine via positions from U_ADC's source pose and thermal
field:0.60mm copper/0.30mm drill, F.Cu–B.Cu, GND, capped/filled declarations.
These are generated thermal features, not evidence that routing ran or that
thermal/assembly qualification passed. The55 rule-area names and four plane
net/layer memberships match floorplan source. The worker additionally retained
all native zone polygons and observed four one-nanometre coordinate truncations.

Root handback audit at16:40:59Z rehashed448/448 immutable packet files,
445 live baseline inputs (442 unchanged, three admitted board/pin/beacon
deltas),1926 previously tracked files (five admitted generated/document
changes),22 handback evidence files and23 output bindings. All five available
owning receipt integrity validators reopened successfully. Authored source,
review witnesses, the pod and immutable releases were unchanged. Integrity
reopening does not turn a partial stage into placement acceptance.

Independent root captures and diagnostic scripts are retained under
`06_build/verification/placement-root-adoption-20260908-2fb00d31/`.
Final native census logSHA:
`20b06e05d13341194d37101aac417a9e82c98af99e4bb07e103ed83dea3ad339`.
Handback audit logSHA:
`dd7740ecedaae704162403f1167e8849033e3082d124a5761cba4c7e73ce4a64`.

The old299-component board was a real known-bad input: the root census
rejected exactly the three absent TDM-conditioner parts and identified the old
U_TDM.2 net. Two root diagnostic setup errors are preserved, not board defects:
an incorrect zero-via assumption, then an obsolete `net_name` zone-field
assumption. The corrected reader explicitly grades source-owned thermal vias
and the observed KiCad10 string-net syntax.

## Actual placement result

MEASURED producer results, independently bound to the unchanged board:

- Source-set parity4/4 domains over302 refs; spoke8/8; pin-map48 multi-pin
  references and367 declared identities; model coverage302/302.
- Legacy placement-routability receipt7/7 rows: fivePASS plus twoN-A.
  Its separate typed P-FEASIBILITY remains INCOMPLETE0/7. Neither proves a
  global route or supplies placement-review approval.
- Copper/paste separation:402920 inter-footprint copper pairs and694008
  paste-to-foreign-copper pairs passed. Current native DRC was not reached.
- All64/64 pin-specific keep-short budgets and354/354 declared relationships
  resolve. **One of290 exact-pair adjacency budgets fails:**
  U_ADC.7→C_LDO_A.1, LDO_A_FILT, native copper-bounding-box gap1.625mm against
  the unchanged1.5mm engineering ceiling. The report rounds this to1.62mm.

Owner: `03_src/floorplan.yaml` C_LDO_A pose[89.8,70,180], constrained by
`02_parts/CS5308P-DN/part.yaml` exact ADC-pin-bypass adjacency. This ceiling is
an authored engineering allocation, not a manufacturer numerical maximum.
The broad5mm center-distance screen passed; it does not replace the tighter
copper-gap predicate.

Other producer warnings remain review debt:274/302 refs on silk,28 generated
F.Fab fallbacks,107 degraded label-ownership placements and12 crowded captions.
The generated waiver list is retained as producer output, not independently
accepted release waivers. The first gate failure must not hide this later work.

Existing DRC dated2026-09-07T12:03:26 is explicitly stale/unbound. The worker
retained all35 violations and348 opens separately with exact reported
endpoints:21clearance,3starved-thermal,11silk;345pad–pad opens and three ADC
GND-pad6/30/38-to-F.Cu-zone opens associated with the old thermal findings.
None of those counts is a current-board DRC result or a congestion diagnosis.

## Bounded source-only correction investigation

Root made no project source or generated-geometry changes during these probes.
Native isolated footprints supplied877 source pads; the unchanged route source
supplied218 seed segments and20 vias. Three finite probes each finished inside
60seconds, with heartbeats and complete logs. These are local source screens,
not a replacement for regenerated placement/DRC or independent reviews.

1. Straight east shifts of0.125/0.15/0.20mm close the ADC copper gap to
   1.500/1.475/1.425mm, but violate the existing U_ADC.6 ground-via0.25mm
   clearance:0.244809/0.221419/0.175mm. Reject the blind-X correction.
2. Larger southeast shifts also encounter the U_ADC.8 ground-return seed
   and C_VDDA2_4U7 courtyard. Reject those sampled poses.
3. A bounded narrow-window probe found four feasible sampled source poses.
   For example,[89.93,70.05,180] gives1.495mm ADC copper gap and0.259098mm
   nearest foreign-via gap, with no detected local seed/via/pad/courtyard or
   body-to-foreign-pad failures. The existing two-pin LDO_A_FILT contact graph
   still reaches both U_ADC.7 and C_LDO_A.1. This has small margins and is
   **a candidate, not an adopted correction or physical tolerance guarantee**.

Probe logSHA values, in order:
`09d5b9575f0504f701e825b1ea138312d64295594b9044ad14f5d834d1423f65`,
`f448032c6edecb6aed9b8d71a7f59b826e878c37aeeea726d2e88b83ea7411a5`,
`a6aa0f082b98670e70a6a09658a25ca7c4c3e821d152bea14b325a044bee6a1d`.

## Next source action and retained holds

Reconcile the capacitor pose in authored floorplan source; preserve the1.5mm
limit, full source-net membership, exact capacitor ownership, ground-return
and seed-contact constraints. Add a known-bad regression for the actual1.625mm
case and grade both adjacency and coupled clearances. Update existing
historical-pose preservation tests only for the explicitly justified delta;
do not remove their unaffected-source assertions. Then run the complete
source suite and determine the correct checkpoint/reuse boundary from actual
source changes. Never re-stamp stale reviews or rerun TSX unnecessarily.

Only regenerated owning placement gates, current DRC and fresh exact pin,
layout and render reviews can advance to routing. The complete objective
remains both finished PCBs and a sealed release; this generated failure is
intermediate evidence. Retain conditional1.521094ns TDM setup residual,
typical-only buck startup, approximately10mV shutdown margin, TOP77,
0.20A first-power HOLD and every physical qualification. Public-catalog
admission is not authenticated PCBA allocation or order readiness. The pod
release stays immutable; both child seals and fresh exact-base/head P-PUBLISH
remain prerequisites to main publication.
