# Carrier generated placement: independently adopted failure and source backtrack

Status: **GENERATED / P-DRC FAIL / NOT ROUTED / DO-NOT-ORDER**.

## Exact result adopted

On September 8 at 18:28–18:30 UTC the coordinator independently reopened the
fresh placement handback at source HEAD
`043344ea1c22997e8d4d8d48ea4dce1ecaaf016d`. The worker lease is RELEASED,
its runner is terminal, and PID 1917779 is absent. There was one producer,
18.157 seconds, rc1 at the owning pre-route DRC gate; no route prep/search/import.

The exact saved PCB SHA is
`66003462ab2221377fd8ad54fdeabe3097983e496f1fe7b22c345fd7843c3060`.
Independent native measurement confirms C_LDO_A at [89.93,70.05,180], with
U_ADC.7 to C_LDO_A.1 gap **1.495 mm**, below the unchanged 1.5 mm ceiling.
The 0.005 mm nominal margin is not a manufacturing-tolerance qualification.
The owning placement receipt reports 64/64 keep-short plus 290/290 pair
budgets, all 354 reached. It does not accept the whole placement.

Independent balanced native-file parsing confirms 302/302 fitted references,
877/877 native netlist pin assignments with no differences, 4 mounting holes,
3 fiducials, 936 raw pad records, zero tracks/arcs, 9 source thermal vias,
4 GND pours and 55 rule areas. Raw pad attributes include paste-only apertures;
they are not an electrical pin denominator. The worker's separate native-layer
census distinguishes 877 fitted conductive pads, 3 fiducial copper pads,
21 NPTH and 35 paste-only records. Source and promoted schematics are identical.

Root verification rehashed 448/448 immutable packet entries, 445/445 baseline
files and all declared generated deltas, exact outputs, logs and reopened
receipt identities: 1,363 checks, no immutable-source deltas. Every original
DRC item and all 998 endpoint occurrences match the annotated census exactly.
This adopts reproducible failure evidence, not placement acceptance.

## Every reported failure has an owner

Exact DRC SHA:
`906bed7407c2490fbc5df8eaec312057b5eb5e5986725dcae63faeda539edebf`.
It contains **45 violations / 499 reported unconnected items / 0 parity findings**.
The unconnected report is capped; see the uncapped correction below.

- 15 clearance conflicts are same-footprint different-net pad geometry:
  8 U_ESD pad2–3 gaps at 0.150 mm versus 0.200 mm ANALOG_AUDIO;
  6 U_CLK adjacent pairs at 0.150 mm versus its 0.200 mm scope;
  Q_IN pad3–4 at 0.230 mm versus 0.250 mm POWER_CONTROL. Reopen the exact
  package and rule intent. No global relaxation, ignored checks or NC deletion.
- 8 F.Cu GND thermals have one spoke versus two required: C_ADC_CM3N.2,
  C_ADC_CM3P.2, C_ADC_CM6N.2, C_ADC_CM6P.2, C_LDO_NR3.2, R_AUDIO_PD.2,
  U_OE.3 and U_LDO.11. Quiet-return pour exclusions must survive correction.
  The native report establishes starvation but does not preserve filled
  contours or prove which obstacle blocked each missing spoke.
- 22 silkscreen findings: 7 overlaps, 11 solder-mask clipping and 4 J9
  edge-clipping. Owners are source captions and exact D_IN/L_BUCK/J9 library
  graphics. Preserve all pads, holes, polarity, body/courtyard and mating datums.

The 499 reported opens are classified: 478 ordinary unrouted non-GND pairs
(224 analog, 90 power-transient, 64 power/control, 56 quiet-power, 27 pod-power,
17 ADC-clock); 21 GND items (7 pour-exclusion/pending-egress, 8 pad-to-zone,
5 pad components/pending-egress, 1 split filled zone). Not a congestion diagnosis.
The saved board has no filled polygons; the report used native in-memory refill.

## Evidence and next boundary

Worker packet: `06_build/verification/placement-resume-20260908-043344ea-r1/`.
Terminal SHA:
`a1e7dc2500f1d21f76b8785ff8fece6654815027c2a7a4f3cdf4ab89f946536c`.
Root bounded read-only runs, each rc0:

- native bypass: log SHA `dbec8f13e1c6e281c90354ac07bcf43d238505685fdc4f2b483a3d9ecbca60c9`;
- independent native census: `c4e4e0db28dfa91762aa156d3b62de64b79c11844b6f11724293089d802da3b4`;
- handback identity/classification: `7c0ba13878b8b615fdf7d5c17c86178203badc6f6425ea43a5229ab07cd0c9fa`.

Next: fix authored layout/footprint intent, test hostile old geometry as well
as the correction, preserve the old checkpoint cohort, regenerate and regrade.
Do not route through P-DRC or claim the pre-generation handoff accepts this PCB.
The typed feasibility shadow is INCOMPLETE; connector physical evidence remains
owed. Schematic acceptance and 204/204 source tests are inherited from the
unchanged prior source, not advance acceptance of a future correction.

TOP77, 0.20 A first power, all conditional timing/startup/analog/thermal/physical
holds, authenticated assembly allocation and order-preview holds remain.
Public information admits design progression only. Pod seal is untouched;
both child releases and fresh exact-base/head P-PUBLISH are still required
before publication. This report is not order or deployment authority.

## 19:15 UTC addendum — tested silk source, unchanged electrical connectivity

**MEASURED**, not canonical placement acceptance: a disposable regeneration
using only the three corrected exact footprint libraries and five source
caption presentations reduces 45 violations to **23: 15 clearance and 8
starved thermal**. All 22 silk findings disappear. Physical projection of all
309 footprints and 936 raw pads is unchanged; rule/project/schematic bytes
are identical. Canonical `04_kicad` remains the failed board SHA above.

The source edits preserve every pad, hole, body/courtyard, model, polarity
marker, connector pose and warning message. The diode outline/cathode bar and
inductor start-lead dot now clear their own solder-mask apertures; J9's silk
stops before the board edge without moving its complete mating geometry.
Five legends occupy independently screened empty strips. No clearance,
ampacity, electrical, thermal or placement budget was changed for this repair.

Nine source-silk regressions include the actual old library/caption geometry
as failing controls and reject hostile non-silk changes. Valid pre-fix runs
were RED, followed by GREEN. The full source suite is **213/213 PASS**, with
complete log SHA
`3dd11b58921b20f5c7ba02077058719e5ea964dc6f0e511e5add49c54fe035e9`.
Five historical whole-floor comparators exclude only later caption presentation;
the dedicated caption tests independently own messages, poses and unchanged
remaining captions. They do not assert printed legibility or layout acceptance.

The producer still reports **30 F.Fab-only refdes fallbacks** (previously 28),
102 degraded labels (previously 107), and seven crowded CH1/2/4/5/6/7/8 legends.
This is explicit remaining silk/visual-review debt, not waived by clean silk DRC.

### Correction to the earlier 499-item completeness claim

KiCad 10.0.4 caps `DRCE_UNCONNECTED_ITEMS` at **499** in the
[native DRC engine](https://gitlab.com/kicad/code/kicad/-/raw/10.0.4/pcbnew/drc/drc_engine.cpp).
The earlier worker packet and journal accurately classify their reported rows,
but those rows are **not the whole board connectivity census**. Those historical
artifacts remain preserved; this addendum corrects their completeness wording.

Reopening saved, CLI-filled boards and calling the native connectivity graph's
`GetUnconnectedCount(False)` yields **500 before and 500 after**. All **877
netted-pad connected-component memberships** are equal. Native component joins
account for 479 non-GND opens and 21 GND opens. The capped reports share 498
rows: the original includes U_LDO_EN.4→U_LDO.7 on LDO_EN, while the regenerated
report instead includes C_BUCK_BST.1→U_BUCK.6 on BUCK_BST. Both are genuinely
unrouted; the latter bootstrap-loop connection is the additional omitted item
in the original 478 non-GND classification. Their union has 500 reported pairs.
The Python edge callback is not bound by the installed SWIG interface, so this
is not represented as direct native-edge enumeration.

The independent geometry comparison uses actual saved copper, not in-memory
fill assumptions. Each of **F.Cu, B.Cu, In1.Cu and In2.Cu** has exactly **zero
added and zero removed polygon area** under native Boolean subtraction.
Contour vertex sequences differ, so they are not claimed byte-identical.
The first diagnostic accidentally keyed all zones by the inherited item layer
name; it is superseded by `native-connectivity-comparison-r2.json`, which uses
the board-resolved zone layer, rejects duplicate keys and requires four layers.

### Exact diagnostic and archive identities

All paths below are under
`06_build/verification/placement-drc-correction-20260908-8d542d4c/`:

- `prior/`: recoverable 519-file old cohort, 89,892,198 bytes. Manifest SHA
  `22fb8ebf49cdee5fad8dcda31be19d9bbbf725ac0bfebcdb99493bcff40327cc`.
  All 421 frozen inputs were verified before archive. Eight live tracked
  checkpoint/request/response/public-stock files were moved here, deliberately
  invalidating resume authority. Their old bytes remain recoverable in Git too.
  No operator fields were filled and no authenticated receipt existed.
- `silk-source-experiment/project/04_kicad/crow_audio_carrier_v1.kicad_pcb`:
  `7b2a71b15216e42ed6da1a0ad6026958342fce542b7eba76a781af1e5cb5492d`;
  `silk-source-experiment/drc.json`:
  `c4b56b65b21c6992df18143bcab1171df5366aeed5f10d46793e5a6d173055b0`.
- Saved native-filled original PCB:
  `ccdb6b5aeb4917e0d020b1befced72797664c75ee424e8c2b969963c6e99e7c1`;
  saved native-filled silk candidate:
  `f3762778faa7c95abf0c8c14af6639c581eb7bfa9b26f0eb6d78d346c622ebb4`.
- `silk-source-experiment/native-connectivity-comparison-r2.json`:
  `ef31864b4ce56c0666d721718cef73475587ef9716aeaff2f7bc994726142823`.
  Final source/physical/DRC comparison log:
  `44b2ac35a08dfafd551f00506a87d289baa9f984aaab1b099048f431e3d8c4f3`.
- `captures-silk-20260908-1915/`: 707 original diagnostic/helper files,
  3,982,408 bytes, including failed drafts, not 707 passing checks. Manifest
  `0cca80c41ff2a7f289c2b00e319af9aa3cc15909590f85bc7ce587b220bc2755`.
  These reproducible build captures are not committed release authority.

### Next electrical correction

The saved native-fill inspection and actual contour image identify the eight
thermal sites without removing the five LDO quiet-pour exclusions. All five
have zero F.Cu fill overlap. Four common-mode ground pads join local isolated
pad pairs; C_LDO_NR3.2 has zero pad/fill overlap. Pad overlap is not itself a
connectivity verdict. Scope any solid-pad connection to its named source owner,
retain quiet-return egress, and regrade filled copper and all disconnected
components. The 15 same-package pad/clearance conflicts need separately
evidenced package-local rules, never lower global isolation or width floors.
Full conductor regeneration, fresh owning reviews, routing and release gates
remain required. Public stock timestamp 2026-09-08T17:09:22Z is preserved, not
refreshed by copying; exact-BOM public-only design admission is not allocation.

## 19:28 UTC addendum — eight solid GND pad connections verified

**MEASURED source correction**, not canonical placement or thermal qualification:
the existing `placement.patterns[].pad_overrides` mechanism now declares solid
connections on exactly C_ADC_CM3N.2, C_ADC_CM3P.2, C_ADC_CM6N.2, C_ADC_CM6P.2,
C_LDO_NR3.2, R_AUDIO_PD.2, U_OE.3 and U_LDO.11. Each selector is exact-ref,
exact-pad and GND-guarded. No library land, hole, model, pose, route source,
quiet exclusion, fabrication process or design-rule byte changes.

The source test first failed on the real pre-fix source at
`84db6eb2cf30f1edb3ac53dc4418cf82caf19f53`: six tests, one expected failure,
log `25508cd5ec620ee3d313414066a6e48ef66ffcad841316d94623f647bd60f077`.
Six pass after correction, including hostile broad-ref, wrong-net, extra-pad
and clearance-override controls. Ten older source-history comparisons exclude
only these later pad-override patterns; the new suite independently constrains
all their fields and every remaining floorplan/route/rule datum. The first full
219-test run exposed five additional historical-scope comparisons, preserved
as a failed diagnostic. The corrected full suite is **219/219 PASS** in
76.282 seconds; complete log
`f01789e25140bd57b3be43d189d2b455d3b5c0ed647f5c4581cc77ac5b5f1b6d`.

Disposable full native refill reports **15 clearance violations, zero thermal
or silk findings, 498 unconnected items, and zero parity**. The 15 clearance
items are the exact previous same-package conflicts. Independent native
comparison proves all 309 footprint poses/identities, 936 raw pad geometries
and nine source thermal vias unchanged; only the eight declared pad modes differ.
Native uncapped connectivity is **498**, agreeing with the now-below-cap report.
All non-GND component memberships are unchanged. The four common-mode pads
previously occupied two isolated local islands; they now join the main ground
network, accounting for the two removed connections. This does not route the
remaining 479 non-GND connections.

All five LDO quiet exclusions retain **zero filled overlap area**. All eight
quiet endpoints (NR1–5.2, R_LDO_BOT.2, U_LDO.4 and U_LDO.6) remain isolated,
as in the prior unrouted board. In particular, the solid setting on NR3.2
does not create an early plane bypass; its authored dedicated return still
must be emitted and measured. No achieved thermal resistance, solder-joint
yield, quiet-loop impedance or first-power safety is inferred.

Every current DRC row is annotated against native endpoint identities: 15
clearances and 498 opens/996 endpoint occurrences. Opens comprise 224 analog,
90 transient-power, 64 control, 56 quiet-power, 27 pod-power, 17 clock and one
bootstrap connection; the 19 GND opens are separately owned by eight LDO
quiet-return source connections, nine ADC return source connections and two
supervisor ground-egress/stitch obligations. No congestion diagnosis or
successful future rescue is assumed.

Exact artifacts under the same correction packet:

- `ground-source-experiment/project/04_kicad/crow_audio_carrier_v1.kicad_pcb`
  SHA `af0f7a19462053719703c627c73a62e3217ee61a99bde352fe6169b5b72f923d`;
  `ground-source-experiment/drc.json`
  SHA `763432149ef08b10860e4e7189dcbe46ac45d50ab22e03f9a0f63e4b303ca3e2`.
- Source floor SHA
  `ca0fed4d609048cb7d325f35b17918d82afe5d2b8af2fec050a43c6b86b99127`;
  `ground-source-experiment/independent-comparison.json`
  SHA `85ffa43b827161214417b1ee388360cbe4c8cee65af89b9b54cf1b07c4d159b5`.
- `ground-source-experiment/drc-classification.json`
  SHA `0077b639bf156b6f76afd1edf3a83802d7bf71c06898216394f9ad87a65aa4f6`.
- `captures-ground-20260908-1928/`: 41 retained helpers/logs/attempt records,
  140,487 bytes, including failed drafts. Manifest
  `320643e2eebf3b7de6a3b7be667d709cccf88ac14485c951c3ce4899be605902`.

Next: evidence-backed package-local clearance treatment for U_ESD1–8, U_CLK
and Q_IN; preserve global fabrication and routing isolation/width floors.
The canonical generated board remains the prior unaccepted subject. Full
regeneration, fresh exact-subject reviews, silk ownership/readability closure,
routing and final release gates remain owed. All order/physical holds persist.

## 19:59 UTC addendum — all 15 package-clearance findings resolved in source

**MEASURED source correction, not canonical placement or release acceptance.**
ADR0020 records the retained package lands, exact primary-document pages and
the deliberate distinction between TI's example land patterns and KiCad's
larger alternatives. Manufacturer land-page PNGs were viewed. No pin, pad,
footprint, placement, route copper, mask/paste, current floor, global clearance
or DRC severity was changed.

Fifteen `PKG_PAD_*` F.Cu permissive areas each admit exactly one native pad
pair. The matching symmetric singleton net-pair scopes retain the measured
nominal gaps: 0.150mm on U_ESD1–8.2/.3 and U_CLK.1/.2, .2/.3, .3/.4, .5/.6,
.6/.7, .7/.8; 0.230mm on Q_IN.3/.4. The existing generic rule mechanism now
accepts strict-boolean `pads_only`, adding two-sided native pad-type guards.
Absent/false is backward compatible; malformed values fail generation.
Route preflight excludes pad-only and malformed entries from route authority.
The template and carrier rule contracts were updated together.

Independent native comparison of the saved filled boards proves:

- 309 footprint poses/identities, 936 raw pad geometries/modes, 877 netted-pad
  connected-component memberships and 9 source vias are unchanged.
- All 55 existing rule areas and four GND zone outlines are unchanged; exactly
  15 pad-only areas are added and their full native pad membership equals the
  previous DRC pair set. No foreign pad is admitted.
- All four actual filled layers have zero Boolean added/removed area. This
  also preserves the five quiet-pour exclusions and isolated quiet endpoints.
- Native uncapped opens remain 498; the complete report retains all 498 rows.
  Native DRC now reports **0 violations / 498 unconnected / 0 parity**.
  This is an unrouted diagnostic result, not the final 0/0/0 release gate.
- Generated `.kicad_pro` and schematic bytes match the preceding experiment;
  only source-authored rule areas and `.kicad_dru` package scopes differ.

Exact artifacts in this packet's `clearance-source-experiment/`:

- Board `project/04_kicad/crow_audio_carrier_v1.kicad_pcb`:
  `8634227fe41772225b7bcad8bc96ed9e830179af050acc665f0ef9b0ad0e7e23`.
- Native `drc.json`:
  `63ca0b7f9fcb13b8c8492552e61855a705d89ba61b5b1f8cc18d236f564ccc4f`.
- `independent-comparison.json`:
  `2cd5dc5fbf29ef99f754ffea63a1c4e5cd3d8177e67aaf5940d9f939faa9d084`.
- Source floor:
  `4137985c2b781b5a35b499bd75c73287f4879fd6e90e44180485849528449012`;
  source nets:
  `0b399e1d844f889eef77d9d44fb512a252889f9698182aadbae2313b9d0333ec`.

The full source suite is **224/224 PASS** (80.841s), log
`46f2fac9baf738b55830fe160bfa6de2dbeb05b283225a2bd12547b4ecfb1d60`.
Its first two runs found nine, then one historical whole-source comparisons
that also needed to exclude the later pad-scope delta. Those failures are
retained, not passed off as physical regressions. The five new source tests
own every new scope field and real pad membership. Their positive test was
run against the actual old source and failed on missing rule/area coverage;
the two hostile-mutator tests additionally errored because old scopes were
absent. RED log
`cff3979d16853253e854d1ff5f0229ee4d505aa582cafc1842293561ef725d68`.

Shared verification:

- Rule-emitter suite **52/52**, including 28 known-bad fixtures; log
  `6b90edaf24b7e32c52073f24c8a78ca914760ae579461d0a1b3581bb414f0778`.
- Preflight suite **32/32**, including 22 known-bad fixtures; log
  `408c45e87f331f76b65cf27b94b0c271bd498182dd3928bbf22c774cde51be80`.
- Native DRC controls **18/18 sites across two arms**: correct/reversed pad
  pairs pass; wrong-net, outside, one-sided and below-local-floor pairs fail.
  The guarded board has six intended clearance findings versus four without
  the guard; the two extra are tight track/pad and via/pad pairs. Filled-zone
  isolation stays unchanged in both arms and does not distinguish the old
  emitter. Final log
  `6a404fda4286ce8953f7ba6220d41929e9dc88e9d4591912c726f63f8fec1499`.
- The exact pre-fix emitter from `06d3bd3e` fails that native test by missing
  the track/via findings. RED log
  `75f8e70634a269e6ed236b0737802c83f1bfd5e7349761eca8a23172db3a385e`.
  The earlier type-guard and preflight unit tests also ran RED before editing
  the implementations. Failed native-fixture drafts remain captured; an
  initial draft mistakenly ignored the harness return code and is not PASS.
- Schema-reader audit **846/846 declared keys**, 741 proven readers, zero
  orphan keys; 42 OWED rows and nine ungoverned families are explicitly not
  upgraded. Skill authority, disclosure **14/14**, documentation **15/15**
  and targeted skill/contract synchronization all pass.
- Carrier tier preflight is **0 FAIL / 2 WARN**: the existing analog-wave
  clearance coverage warning and legalization/via-pocket warning remain.
  Its derivation lists only the previous 18 route-capable scopes, not these
  15 pad-only entries. This is config screening, not route acceptance.

The **full repository contract suite is not green: 13 pass / 4 fail**. It
reports the existing publication-fixture `projects/child-a` C-ISO literal
(confirmed in HEAD), project/fleet contract debt and a stale tight
proven-parts orphan-count expectation. The `--present` check also sees the
new uncommitted source/test files until this commit. These broader failures
are recorded, not relaxed or represented as a successful whole-repo audit;
full log `268badfc8108cf4dd96c07d8af002c3970308a22cf870b69db359edd6f43d096`.

Original scripts, attempts, land-page PNGs and native control artifacts are
retained under `captures-clearance-20260908-2000/`: 145 files / 1,023,317 bytes,
manifest `787d8bcf0c072c77db6f44788f3b3a78ba3c2582c77a1cfe9f6a1a2f7363feaf`.
These include failed drafts and are not 145 passing tests or sealed payload.

Next: full conductor regeneration from committed source and fresh exact-subject
reviews, then silk ownership/readability closure and routing. The canonical
PCB remains SHA `66003462ab2221377fd8ad54fdeabe3097983e496f1fe7b22c345fd7843c3060`;
no disposable board was hand-promoted, no archived checkpoint was restamped,
and no main push occurred. Pod seal unchanged. All TOP77/0.20A, order and
physical-qualification holds remain; public-only design work can continue.

### 20:03 UTC schema-ratchet closure

The new proven `pads_only` reader raises the exact schema-adoption floor
740→741. The existing tight-floor test first failed on 741 measured versus
740 recorded (RED log `c001feb55ec84179c6ae1c3758d9f945089e3deddfff183aa66d40fbb8e4d4bc`);
the evidence-earned increment now passes the full schema-reader suite:
**28/28**, including 13 known-bad controls and one declared blind spot, log
`045afc1792066dc8440e8e702422abaa65f6aaa496031b0b0be0c97bfd2e90a0`.
No threshold was lowered and no schema wildcard was broadened. Late originals
are retained separately under `captures-clearance-schema-20260908-2003/`.
The seven-file / 8,596-byte late capture manifest is
`4449eb862c5e25f6662931362190324ef7a59ad4b8c1b6c7c75035a3ce837333`.
