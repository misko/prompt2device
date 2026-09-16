# Route-source correction handback — 2026-09-08

Outcome: PARTIAL coherent source sub-batch; NOT ROUTE-READY, DO-NOT-ORDER.
The exact partition, bulk widths, paired vias, public stack and west-ADC local
launch/return source are corrected. Other ADC/IC launches, physical current and
return proof, and actual SI closure remain actionable source work. No geometry,
count, source test or shadow receipt below is a generated-board or release PASS.

## Authority, preservation and lease

Source author: carrier_route_source_20260908, exclusive bounded child of root.
Worktree: `/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901`.
HEAD stays `5bd9a0cf86c967822305e45e9d6fdd59cef0fbd4`; source adoption ancestor
`cfb0958899fe2c926143c1d187618f36ad7b4632`, administrative ancestor
`2b38cc18e3b620fade9c075b3a57ecb7fbe3252f`. No commit/tag/push was made.

MEASURED before edits: exact29-member TaskEnvelope and complete407-row input
census verified. Envelope canonical SHA256
`16f90d1a56be7b39a879f35f4eaf2eee1595120490f5cd654fb189a544b40860`;
packet canonical SHA256
`b5a5dde4511f2b5c18f48de6516148544703bb46e871bea77d09c0e2abd25641`.
At05:47:49.479642Z, 1167 files /118994513 bytes were archived and every copy
rehashed before source editing. The archive is under
`06_build/tmp/route-source-20260908/archive/`; archive-inventory.json records
all before hashes. Historical source, native/generated schematic/netlist/PDF,
saved PCB/project/DRU, checkpoint/request/stock and review evidence remain
untouched. Terminal-integrity.json supplies exact current-vs-before changes,
unaffected counts/hashes, all29 packet revalidation and full407-row comparison.

I read the complete TASK, envelope, selected packet material, beacon/journal,
PCB-design, KiCad and JLC skills and owning contracts/references. These skills
kept authoring source-only, required archive/consumer boundaries, preserved
checkpoint/review bytes and prevented promotion of geometry or shadow results
into generated acceptance. No alternate Board, Board constructor/load/save,
conductor/resume/checkpoint retirement, prep, router/import, fabrication, review
impersonation, shared-tool edit or dirty KRT change occurred. Isolated native
footprints were loaded for source geometry only. Public-primary research used
no accounts, credentials, upload, vendor coordination or purchases.

With delivery of this terminal report and parent handback, I explicitly
relinquish the exclusive source-writer lease. I will perform no further source
edits, producers or commits under this lease. The absolute deadline remains
2026-09-08T07:10:40Z; root owns independent source adoption and any later task.
This handback is not permission to skip the remaining source work and gates.

## Exact engineering changes

1. `03_src/rules/nets.yaml`: literal partition of165 connected nets into eight
   classes; twelve true digital clock/data sections separate from three DC
   sense/OE controls, whose0.25mm clearance is explicitly retained. BUCK_BST gets
   local switched-bootstrap intent. Transient2.5A bound is retained, floor1.20mm;
   ADC_CLOCK bulk0.36mm. Add one named ADC_WEST_LOCAL0.18mm width/0.20mm clearance
   scope, exact digital reference-plane check and two complete ordered-path
   groups including every native endpoint and three pull-down branches.
2. `03_src/route.yaml`: seven literal groups own163 nonground nets; complete
   LDO_A_FILT owns only prep.seed_stubs and is explicitly excluded from generic
   routing. GND owns common zones;40NCs remain excluded. Nine exact west-ADC/
   VMID seed banks add partial leaves/returns, two ground vias and the complete
   internal-LDO filter connection. All seven explicit via definitions pair
   0.50/0.20mm. Stitch pitch0.75mm preserves copper/hole spacing and nudge-only
   repair. Power is F-only1.20mm, no automatic tap neckdown, subnominal cap5.05mm/
   eight segments. No ordinary tap, high-current transfer via or smaller family
   is introduced. A loud flow blocker says further source closure is required.
3. `03_src/floorplan.yaml`: actual physical emitter stack matches public exact
   JLC04161H-7628; common GND added onIn2 to reference B-side signals, with no
   power pour or changed adjacency denominator. Add one permissive bounded
   rule area and finite top-only GND_A paddle-gap keepout. Only the three
   route-conflict capacitor poses below change; all other296 expanded poses,
   all11 connector datums, model bindings, captions, repeats,150x100mm outline,
   mounting holes, fourlayers and global fab floors are preserved.
4. New `03_src/rules/stackup.yaml`: shadow-only exact physical/reference
   declaration; no execution-authority promotion. `03_src/rules/rf.yaml` stays
   disabled but acknowledges single-ended50ohm digital intent and the existing
   high_speed_digital profile, without pretending the three controls are HS.
5. `02_parts/CS5308P-DN/notes.md`: only the authorized stale FILTxN statement is
   corrected: evaluation R351/R434 are0ohm and carrier physical pins17/44 stay
   common GND. No component, topology, value, MPN, pin, rating, model or other
   dossier edits. New `test_route_source_contract.py` adds19 source regressions.
6. New [ADR-0010](decisions/0010-route-stack-and-current-paths.md), this report,
   STATUS and appended routing journal record decisions, tests and remaining
   obligations. No prior ADR, report, packet member or checkpoint is rewritten.

| Reference | Before x,y,rotation | After x,y,rotation | Exact cap-to-ADC span after |
|---|---|---|---:|
| C_LDO_A |90.6,70,180|89.8,70,180|2.4830677mm <=5mm|
| C_VDDA1_4U7 |87.35,68.7,180|87.45,68.4,180|4.9275374mm <=5mm|
| C_VDDA2_4U7 |87.35,71.3,180|87.45,71.6,180|4.8621626mm <=5mm|

The exact205-row net/class/wave/owner/pin inventory is final-source-facts.json,
SHA256 `2bd3cf3e61114937b58ae1a6499f2e2a1951c8956323c495462a6b45226b70cf`.
Its rows distinguish163 route.wave +1 prep.seed_stubs +1 zone +40 NC owners;
class populations11/8/25/1/11/96/12/1 correspond to POD_POWER/POWER_TRANSIENT/
POWER_CONTROL/BOOTSTRAP/QUIET_POWER/ANALOG_AUDIO/ADC_CLOCK/GROUND.
It also records all via pairs, full physical stack arithmetic, current/drop
calculations and exact three-pose delta. Native299 refs/868 pins/205 nets remain.

## MEASURED source tests and retained evidence

Evidence root for all names below: `06_build/tmp/route-source-20260908/`.
Full finite command logs and argv/start/end/exit/hash metadata are preserved,
not replaced by summaries. Terminal-source-checks.json records the final rerun
after tightening the whole-item scope test to include the0.60mm extensions:

| Existing consumer / scope | Actual interval UTC | Outcome | Full log SHA256 |
|---|---|---|---|
| Project unittest discovery |07:02:49.262–07:02:54.095|114/114, rc0|`89359bdd43a30f4a894f89b3592fb8cff88ac37abbabfe78dbe64a4f72a3fca4`|
| rules_audit --phase source |07:02:54.095–07:02:54.131|8/8, rc0|`5f8b24e067fc5b2366b8df3ff41669ab2517425c5c2971135a433157a0a9b6d0`|
| net_reference_audit |07:02:54.131–07:02:54.374|328/328;0ghost,0unreached,rc0|`2d042e7e0d54936a8882cb00fa6aa5fd20baae582bf877b4fa142a9fb8f3466f`|

The114 count is95 inherited project tests rerun plus19 new tests. Earlier
111-test/source8/8/netreference313/313 results are preserved under the original
unprefixed logs; they predate the final scopes/paths/seeds and are not substituted
for the final denominator. Tests call existing exact wave-width, owner, native
netlist, current-width, shadow-authority and copper-length consumers. Hostile
fixtures reject stale/glob names,0.60mm transient wave, old0.45/0.20 via pair,
duplicate deterministic3V3 owner, missing power owner, missing reference plane,
duplicate shadow owner and the old companion-cap pose's courtyard conflict.

New durable geometry testing loads isolated native footprints without a Board,
screens every authored segment against all source foreign F.Cu pad polygons
and every other-net seed segment, checks all three moved courtyards against
all components and forward/reverse pad-to-courtyard interference, and pins
the exact narrow scope,5.05mm/eight-segment power extent and no nonground seed
vias. It supplements, not replaces, the retained broader H3c hole/bulk screens.
The previous114-test run at06:54:51–57 is also retained under final-* filenames.
Final-source-geometry.json reopens isolated source footprints, verifies all868
copper pads against the original geometry plus only the exact three translations,
and verifies live source seeds exactly equal retained H3c geometry. SHA256:
`17ee0f19f69d9e5a7b5889465a178979c533d894fa795c94367c2e966bbe4ec4`.
KiCad's pre-existing PROPERTY_ENUM diagnostic appears on import in full logs;
the tests still completed rc0. No diagnostic is hidden or called PCB acceptance.

Shadow compile/reopen verification covers205 owned live nets in
final-shadow-authority.json, SHA256
`1afb7cf043708603fda0a873bcc198384d53985d3667aa0634dbf94015dd1e52`.
Its internal PASS is explicitly source compiler coverage, not execution authority.

## Hypotheses, rejections and source-geometry limits

- full-source-launches.json:34 exact isolated nearby-source samples on17 pads
  at0.20/0.25 clearance, not package-only or native resolved-rule P-LAND.
- adc-seed-candidate-rejected.json (H1): fixed-placement GND via had0.175mm
  foreign-pad gap and0.060mm to the power seed; reject.
- adc-seed-candidate-shift.json and cap-shift-envelopes.json (H2):87 copper
  comparisons clear after C_LDO_A west0.8mm, but both4.7uF courtyards collide;
  reject this one-cap pose. Proximity alone did not justify placement.
- three-cap-candidate.json (H3a): three poses clear bodies/proximity, but one
  0.30mm VMID return has0.1784368mm gap against0.25mm; reject that return.
- three-cap-candidate-h3b.json: the northern0.18mm dogleg clears209 comparisons;
  this did not yet screen bulk feed entries against all new return traces.
- three-cap-candidate-h3c.json at06:40:54.467Z:567 copper comparisons,0conflicts;
  includes1.20mm feed entry versus source pads/new ground traces/vias,
  all-layer via foreign pads, hole-to-copper0.255mm, all PTH/NPTH and four
  3.2mm mounting holes, and0.50mm hole separation. Courtyard/foreign-pad/proximity
  screens also clear; minimum reported body gap0.15039mm against0.10mm.
  This measured improvement was the adopted geometry, not a third stagnant try.
- clock-seed-candidate.json:41 comparisons, two0.36mm bulk-entry collisions:
  U_CLK.3 versusU_CLK.4 gap0.141039mm; U_CLK.6 versusU_CLK.5 gap0.223000mm,
  both against0.25mm. No clock seed is adopted. A later candidate must also
  recognize whether U_CLK.2 actually reaches its same-net series resistor and
  therefore changes complete-net ownership; seed presence alone cannot decide.

Initial new-test development had three harness errors (two wrong expected
exception types, one wrong drill-floor key), fixed before final runs. One H3
setup run stopped on an unnumbered noncopper object because the harness used
layer membership without IsOnCopperLayer; fixed before sampling. These earlier
interactive failures remain in the task tool record, not invented full log files.
Earlier progress commentary included guessed/future time labels, corrected when
root pointed them out; actual tool clocks and artifact timestamps govern.
The beacon was stale during local hypotheses and was corrected at06:51:48Z;
do not interpret the stale06:08 text as the final source state or silently invent
missing transition timestamps. Final logs preserve actual measured intervals.

INHERITED/independently produced by root, then copied verbatim as observations:
ADC-OBSERVATIONS.md and adc-all-lands-observed.json cover48 ADC perimeter lands
x3 clearances=144 cases. They verify920 total objects=868 copper+52 noncopper,
including16 one-nanometer coordinate differences within the prior2nm bound.
Uniform-clearance bulk shortfalls at native0.0001mm numerical tolerance are
9 at0.127,17 at0.20 and40 at0.25; all row results remain in the JSON.
Root's first two setup failures are recorded in its observation document; raw
scripts/logs remain at `/tmp/carrier-stack-root-20260908.b6Efeg/`.
NON-ADC-OBSERVATIONS.md and non-adc-ic-launches.json cover185 nonground non-ADC
SMT IC lands,22 below bulk width at0.25 uniform clearance,163 not below that
limited screen. Those use frozen pre-three-move source geometry, not this
author's final physical acceptance. Root has not independently adopted the batch.

## Public evidence, calculations and remaining owning work

ADR-0010 contains the exact primary links and engineering derivations. Raw
jlc-impedance-20260908.html is294084bytes, SHA256
`b36b132c8bef37fb6420d3499ac9830b7ebe3d9a0fb0926ec7f1e5526a6857e1`.
Public exact stack1.5862mm uses outer0.035,inner0.0152,prepreg0.2104,Dk4.4,
core1.065,Dk4.6; mask's nonuniform geometry and unallocated DF are explicitly
not solved by nominal source values. Cirrus datasheet/layout/evaluation PDFs
remain byte-preserved; the inspected page renders are retained in evidence.

Root's copied bare-microstrip-comparison.json, SHA256
`1d0135488373b4651a2848ed2eab6a976160faaefddd28180281701d13d5153a`,
supports only analytical plausibility:0.36mm bare finite-thickness microstrip
about50.922ohm,0.18mm about71.043ohm. No field solver, mask/coplanar-pour model,
realized termination discontinuity or manufacturer tolerance has been accepted.
Existing path checks cover every twelve-net endpoint/branch, not active-device
delay. Existing reference-plane projection checks tracks/vias only, not complete
filled-plane continuity, pads/holes or per-net reaches. RF remains disabled.

The2.5A bulk bound is unchanged. Normal0.15A ADC allocation gives the longest
0.18mm leaf7.730mohm,1.1595mV,0.1739mW; at2.5A it is48.31mW, with no asserted
fault duration or thermal qualification.0.60mm extensions are2.90/3.22mW at2.5A.
Actual branch topology must keep bulk/bypass current out of thin leaf copper.
Generic KRT endpoint selection can re-enter existing segment endpoints. The
wave realized-width guard is not automatically a final post-import/stitch guard;
remeasure the exact same width/extent bounds on final copper. Ordinary taps'
two-via fallback and deferred hole spacing are not a current-transfer solution.

Next actionable source rows: ADC clock/data and VDDIO, FILT positives and
LDO_D launches; four U_CLK signal launches; true series U_BUCK.5 and U_LDO.1/.2/.9
exits; separate low-current U_AUDIO.4,U_CLK.8,U_ISO1..8.8,U_PWR.3/.4,U_RST2.2/.8
taps. Complete GND_D/FILTxN outward return geometry, EP thermal plane connections,
and remaining local ground-cap sites under actual width/clearance/current rules.
The finite GND_A top keepout does not prove all filled-pour paths or forbid
every possible top bridge; common inner planes remain unsplit. Input trace
DCR<=0.5ohm and balanced-pair/feedback symmetry remain realized obligations,
not waived by class membership. No new power pour removes adjacency obligations.

After further bounded source closure, root independent adoption precedes one
combined producer cycle and fresh same-hash schematic/pin/placement/model/body/
silk/landability/rules/DRC/thermal/ground reviews and physical routing gates.
All299 identities, source electrical ratings, physical and sourcing holds,
TOP77, first-power0.20A HOLD, ADR0007/0009 prototype scope, service/publication
limits and DO-NOT-ORDER remain. This report returns useful partial correction,
not a completed route-source objective or generated-board approval.
