# P-LAND D-BACK result — bounded diagnosis complete; candidate rejected

MEASURED on the exact failed native placement from commit `1ec255e4847de865f097e2e5ba9cff6df4fd6854`, dispatch `922318159b74e83e279bc50a2f401ff6ce2af8e8`. Envelope verified SHA `94cc2512e555af829afec7dd8215ea7013cfad69be2444189b8ec647677e0486`, all 512 members exact before writing. No live source/method/board/rule/model/route/review edits, route import, promotion, or approval. All diagnostic evidence is under `06_build/verification/pland-dback/pland-dback-20260910T193834Z/`.

**Verdict: COMPLETE for this bounded causal diagnosis and census. NO PASSING remediation candidate, no global gate refutation, and placement remains unaccepted.** All 14 reported landing rows reproduce. Their local native width/clearance behavior differs from the checker approximation; the one authored-copper coupon nevertheless fails whole-board native DRC on two new starved thermals and 16 dangling partial-launch ends. A maintained checker correction and its pre-fix RED/post-fix GREEN tests remain OWED. No source change is causally justified merely by these static width messages.

## Reproduction and native evidence

One exact-board P-LAND reproduction: rc **1**, **24.622536 s**, full stdout `pland-reproduction.stdout.log`, full command/start/rc/duration in `pland-reproduction.receipt.json`. This is a new independent log. The original conductor stdout was truncated and was never reconstructed.

| Artifact | Native violation rows | Raw opens | Complete refilled gaps | Parity | Whole-artifact result |
|---|---:|---:|---:|---:|---|
| Exact baseline | 0 | 499 | 514 | 0 | Unrouted, not accepted |
| Single coupon | 2 starved thermal + 16 dangling | 499 | 513 | 0 | REJECTED |
| One hostile control | 2 starved thermal + 16 dangling + 3 clearance | 499 | 513 | 0 | REJECTED as intended |

Exact-copy initial native DRC reported 199 `lib_footprint_issues` because the private directory lacked its library table. Every such row is retained in the initial `*-drc.json`. Private tables were derived from the exact source library declarations and installed KiCad footprint roots; all PCB/PRO/DRU/SCH hashes were verified unchanged. The context-only repeat removes all 199 warnings. Final files are `exact-context-drc.json`, `coupon-context-drc.json`, `control-context-drc.json`, with full stdout and rc/duration receipts. Every final native DRC command used `--severity-all --refill-zones --schematic-parity --exit-code-violations --format json`; rc5 is retained because unconnected items are real. No severity/check was disabled.

## All 14 landing rows

MEASURED native pad shapes are roundrects, with exact effective polygons in `native-board-facts.json`: ADC lands 0.200 × 0.800 mm at 0.400 mm pitch, corner radius 0.050 mm; BUCK5 1.325 × 0.600 mm, corner radius 0.150 mm. All source-launch widths, source points, neighboring pads, their netclasses, native shape-gap measurements, area intersections, and last matching pair rules are individually preserved in `fourteen-pair-rule-classification.json`. The following are the best **demonstrated source-authored** legal landing points/directions at the required local width, not a claim to have solved every continuous alternative or a complete route. P-LAND’s own sampled maxima/directions remain verbatim in the reproduction log.

| Pad / net | Native source start mm; direction | Width mm | Limiting neighbor(s) | Measured gap / resolved requirement mm | Cause |
|---|---|---:|---|---|---|
| U_ADC.14 / ADC5P | [94.2, 72.95]; 90° | 0.200 | U_ADC.13 ADC5N, U_ADC.15 ADC6N | 0.200/0.200, 0.200/0.200 | blanket nearby 0.25 clearance |
| U_ADC.15 / ADC6N | [94.6, 72.95]; 90° | 0.200 | U_ADC.14 ADC5P, U_ADC.16 ADC6P | 0.200/0.200, 0.200/0.200 | blanket nearby 0.25 clearance |
| U_ADC.16 / ADC6P | [95.0, 72.95]; 90° | 0.200 | U_ADC.15 ADC6N, U_ADC.17 GND | 0.200/0.200, 0.200/0.200 | blanket nearby 0.25 clearance |
| U_ADC.19 / ADC7N | [96.2, 72.95]; 90° | 0.200 | U_ADC.18 FILT2P, U_ADC.20 ADC7P | 0.200/0.200, 0.200/0.200 | blanket nearby 0.25 clearance |
| U_ADC.20 / ADC7P | [96.6, 72.95]; 90° | 0.200 | U_ADC.19 ADC7N, U_ADC.21 ADC8N | 0.200/0.200, 0.200/0.200 | blanket nearby 0.25 clearance |
| U_ADC.21 / ADC8N | [97.0, 72.95]; 90° | 0.200 | U_ADC.20 ADC7P, U_ADC.22 ADC8P | 0.200/0.200, 0.200/0.200 | blanket nearby 0.25 clearance |
| U_ADC.22 / ADC8P | [97.4, 72.95]; 90° | 0.200 | U_ADC.21 ADC8N, U_ADC.23 ADC_RESET_N | 0.200/0.200, 0.200/0.200 | blanket nearby 0.25 clearance; existing RESET exception matches neighbor B |
| U_ADC.39 / ADC1N | [97.4, 67.05]; -90° | 0.200 | U_ADC.38 3V3_ADC, U_ADC.40 ADC1P | 0.200/0.200, 0.200/0.200 | blanket nearby 0.25 clearance |
| U_ADC.40 / ADC1P | [97.0, 67.05]; -90° | 0.200 | U_ADC.39 ADC1N, U_ADC.41 ADC2N | 0.200/0.200, 0.200/0.200 | blanket nearby 0.25 clearance |
| U_ADC.41 / ADC2N | [96.6, 67.05]; -90° | 0.200 | U_ADC.40 ADC1P, U_ADC.42 ADC2P | 0.200/0.200, 0.200/0.200 | blanket nearby 0.25 clearance |
| U_ADC.45 / ADC3N | [95.0, 67.05]; -90° | 0.200 | U_ADC.44 GND, U_ADC.46 ADC3P | 0.200/0.200, 0.200/0.200 | blanket nearby 0.25 clearance |
| U_ADC.46 / ADC3P | [94.6, 67.05]; -90° | 0.200 | U_ADC.45 ADC3N, U_ADC.47 ADC4N | 0.200/0.200, 0.200/0.200 | blanket nearby 0.25 clearance |
| U_ADC.47 / ADC4N | [94.2, 67.05]; -90° | 0.200 | U_ADC.46 ADC3P, U_ADC.48 ADC4P | 0.200/0.200, 0.200/0.200 | blanket nearby 0.25 clearance |
| U_BUCK.5 / BUCK_SW | [43.6, 66.0]; 0° | 0.750 | U_BUCK.4 GND, U_BUCK.6 BUCK_BST | 0.275/0.200, 0.275/0.250 | pad-center scope test misses off-center width area; 0.9 mm taper differs from 1 mm model |

The thirteen ADC rows retain the exact 0.200 mm `ANALOG_AUDIO_width` floor. P-LAND applies the largest class clearance of **any** other-net land within its 2.5 mm square to **every** obstacle, yielding 0.100 mm landability at 0.250 mm. The actual immediate neighbor requirements are 0.200 mm. Remote CFG/clock/reset pads with 0.250 mm classes and their individual measured gaps are enumerated per row. For ADC22, adjacent RESET23 would require 0.250 mm by classes; both native items overlap `ADC_RESET_PITCH` and the existing B-side `ADC_RESET_N` clause resolves 0.200 mm. The checker drops that B-side eligibility. Other nearest-pair scoped matches are FILT_SOUTH at ADC16/19, CS_STRAP at ADC39, and FILT_NORTH at ADC45; no new exception is proposed.

BUCK5 center is (43.1375,66.0000), 0.0625 mm west of `BUCK_SW_EXIT` x-min43.2. Native pad copper spans x42.475..43.800, so pad and the off-center track intersect the existing area. The source 0.750 mm × 0.900 mm narrow capsule is wholly inside x43.225..44.875,y65.625..66.375; area is x43.2..44.9,y65.6..66.4. It then widens to 1.200 mm for 1.315 mm to L_BUCK.1. Its minimum native pair margin is 0.025 mm against BST6 (0.275 actual/0.250 required). P-LAND instead assigns the pad the 1.200 mm bulk floor and measures a 1.000 mm constant-width launch at a blanket0.250 mm, maximum0.800 mm. These path lengths and shapes are explicitly different. Preserve the existing local length/current/thermal contract rather than lengthening a narrow track to fit this model.

The [KiCad 10 custom-rule manual](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#custom-design-rules) confirms any-part area intersection and pair-wise A/B evaluation in both orderings. The independent explanatory resolver retains all A/B area/net clauses, pad/track types, layer scope and file-order last match. Its measurements supplement native DRC; they do not replace it. A method fix must also retain `Type == Pad` restrictions in package-pad exceptions. Treating every parsed area/net fragment as a general track relaxation would be an unsafe broadening.

## Single candidate and control: complete failure classification

The sole coupon adds exactly 18 F.Cu track primitives: the source’s sixteen simultaneous 1.000 mm ×0.200 mm ADC analog launches and the two BUCK5 primitives. It retains all actual neighboring geometry, 340 footprint poses, 1002 pad facts, 333 source identities, 937 source pins, exact net assignments, zones, existing11vias, and unchanged project/rules/schematic. Reopened native comparisons are in `final-identity-bindings.json`. It adds no vias. The BUCK track connects U_BUCK.5 to L_BUCK.1, reducing only that net’s deficit from2 to1; C_BUCK_BST.2 remains disconnected. Every ADC launch remains a partial net.

Both starved thermals are exact `GND` F.Cu reliefs: `C_FILT1_1U.2` at (97.375,64.599999) and `C_FILT2_1U.2` at (97.375,75.400000), zone UUID8050ba2a-be25-4e03-a09e-94ade4fe671f. Native DRC requires two spokes and finds one on each after these simultaneous launches. Neither exists in baseline. The experiment identifies the added launch set as the trigger, not an independently isolated one-track cause; no deletion experiment was authorized. Their dedicated authored GND source banks exist but were not imported in this landing-only coupon. Full source-prep/ground-return integration must own the resolution and prove actual fill; this limited experiment does not establish that the full authored source is defective.

The 16 dangling findings are one outer endpoint on each ADC1N/P..ADC8N/P source launch; all exact UUIDs, positions and descriptions remain in `coupon-context-drc.json`. They are intentional endpoints of this partial diagnostic, but still prevent whole-coupon DRC acceptance and are never omitted from its result. The later analog owner must connect each full source net, including isolation, shunt and bias members, not merely remove the warning.

The sole control changes only ADC5P/U_ADC14 width0.200→0.300 and BUCK5’s0.900 mm neck width0.750→1.200. Native DRC adds exactly three clearance findings: ADC5P track versus ADC6N pad15, actual0.150/required0.200; ADC5P track versus ADC5N track,0.150/0.200; BUCK_SW track versus U_BUCK4/GND,0.050/0.200. All21control violation rows are retained and classified; there is no parity delta. Native checking therefore rejects concrete too-wide copper under the unchanged rules.

Running the original P-LAND on that same unchanged coupon still gives14failures and13`MODEL-REFUTED` diagnostic messages. `coverage_and_regressions.py` labels the local disagreement `RED`, but the wrapper itself exits0; it is a diagnostic classification, **not an executed new maintained regression assertion**. No patched checker was run. Maintained pre-fix RED/new-code GREEN tests remain OWED. The original messages cannot override the coupon’s overall native rejection.

## Every pad and both connectivity halves

MEASURED denominator: 1002physical pads =940copper +62noncopper. P-LAND940 =677graded +42no declared width floor +218nominal same-net-pour exclusions +0via-on-pad bucket +3no-net +0unreadable. Graded677 =663passing +14failing;68use scoped width and40use scoped clearance. `complete-pad-denominator.json` retains every physical row and original graded message. All42floorless nets are singleton source NCs with Default class; none contributes an open deficit. The three no-net copper pads are FID1/2/3. All62noncopper rows are enumerated by actual ref/pad/layer/geometry.

There are **0 trace segments and11actualvias** in baseline. Nine existing vias have their centers on U_ADC49 and two on U_LDO15; `physical-vias.json` records each. The checker’s via-on-pad bucket is0 because its pour exemption runs first. No inference of zero physical vias, or a claim that these11vias are tracks, is valid. All218nominalpour pads are GND; native fill contacts204, leaving14without any filled-zone contact. These14are real open return components, not the fourteen P-LAND width rows.

Native Build/RecalculateRatsnest measures717unfilled→514refilled. Independent transitive GetConnectedItems union over every actual pad/track/via gives514across220nets; all220partitions match the root’s saved census, with no discrepancy. The GND network has15components: one215-item main component (204pads+11vias), plus14singleton pads. Every separately filled polygon was intersected with native item shapes; all three F.Cu islands, and the separately retained polygons on each other copper layer, reach main component1. Thus the six raw whole-zone references map to component1 by physical island contacts, without ever unioning a whole zone UUID. `saved-complete-endpoints.json` retains all499original rows/998endpoints and exact source memberships; its rows equal the independent exact-run rows, and unresolved count is0.

The complete deficit is14GND +500other-net gaps. Raw499contains14GND +485other-net gaps;15additional independent gaps are outside the report cap. Missing groups: 12V_POD6:1, 12V_POD8:1, AIN_N1:1, AIN_N3:1, AIN_P6:1, AIN_P8:1, FB_N2:1, FB_P6:2, OPA_N1:2, OPA_N2:2, OPA_P3:2. Full component memberships and omitted-edge groups remain in the JSON, not inferred from report length.

| Isolated GND source endpoint | Native center mm | Owning source action still owed |
|---|---|---|
| C_LDO_NR4.2 | [69.28, 72.0] | Exact authored GND seed exists; realize and refill it before return acceptance |
| C_LDO_NR5.2 | [69.28, 73.3] | Exact authored GND seed exists; realize and refill it before return acceptance |
| R_LDO_SET.2 | [69.625, 74.6] | Exact authored GND seed exists; realize and refill it before return acceptance |
| U_ADC.17 | [95.4, 72.95] | Exact authored GND seed exists; realize and refill it before return acceptance |
| U_ADC.30 | [98.95, 70.2] | Exact authored GND seed exists; realize and refill it before return acceptance |
| U_ADC.35 | [98.95, 68.2] | Exact authored GND seed exists; realize and refill it before return acceptance |
| U_ADC.36 | [98.95, 67.8] | Exact authored GND seed exists; realize and refill it before return acceptance |
| U_ADC.37 | [98.2, 67.05] | Exact authored GND seed exists; realize and refill it before return acceptance |
| U_ADC.4 | [93.05, 69.0] | Exact authored GND seed exists; realize and refill it before return acceptance |
| U_ADC.44 | [95.4, 67.05] | Exact authored GND seed exists; realize and refill it before return acceptance |
| U_ADC.6 | [93.05, 69.8] | Exact authored GND seed exists; realize and refill it before return acceptance |
| U_ADC.8 | [93.05, 70.6] | Exact authored GND seed exists; realize and refill it before return acceptance |
| U_AUDIO.2 | [32.4, 61.1] | No exact-pin prep seed; GND stitch/fallback owner must connect and qualify return |
| U_PWR.2 | [32.4, 56.7] | No exact-pin prep seed; GND stitch/fallback owner must connect and qualify return |

`complete-connectivity-ownership.json` carries all220nets, every source member, every native component, existing authored banks, and all514independent gap-basis rows. The basis is a mathematical component-spanning tree, not an invented route or a claim that a particular corridor is blocked. Source-owner totals are analog256, power108, control61, pod_power28, references22, clocks16, GND14, deterministic8, bootstrap1. Deterministic gaps are FSYNC_BUF1, LDO_A_FILT1, LDO_D_FILT2, VMID1=2, VMID2=2. These remain real before their source copper is realized. No open net is summarized as generic congestion.

## Owning follow-up and limits

1. Maintained P-LAND method author: implement pair-specific clearance with both item conditions, native area-overlap semantics and last-match precedence; preserve pad-only exception restrictions. Support the already-authored BUCK transition without silently allowing longer/thinner copper. Add narrow known-good and known-bad fixtures for remote-class contamination, B-side-only net match, off-center area membership, reversed A/B order, outside-area partner, Pad/Pad versus Track/Pad, and bounded taper length. Demonstrate each new assertion RED against original method and GREEN only after its supported correction. No live method patch was authorized here.
2. Source-prep/ground-return owner: re-open the two coupon thermal findings with full authorized source-ground geometry, all14isolated GND endpoints and all220net partitions; explicitly own supervisor ground pins without exact prep seeds. Preserve the existing width, voltage/current, thermal, SI and fabrication bounds and source-capsule limits. No local source patch is justified by count alone.
3. Coordinator: any adopted frozen source/method change requires the strict full canonical restart and fresh bound review; do not reuse this private copper as a promoted route. Subsequent layout/routing acceptance must classify both physical and unconnected halves. Downstream models/orientation, electrical-current qualification, thermal/SI and fabrication/ordering authority were outside this diagnosis.

The exact electrical requirements/BRIEF and relevant part dossiers/ADRs were reopened as scope authority. Their electrical limits are inherited design commitments, not newly proven device/current/thermal results. This diagnosis proposes no width reduction, global floor relaxation, new via-in-pad, or package/source change. Proposed source/method patch: **NONE**, patchSHA **null**; private copper deltas are explicit manifests, not an adopted patch.

## Hashes, commands and delivery

| Exact input | SHA256 |
|---|---|
| kicad_dru | `94251d1c7cb043c66d402d55b5cf89bac74f7ae0927b012556113ae56d7a2471` |
| kicad_pcb | `89d33bae8eaf67457fde887eae9db187d9284ea54be386f0d31e3d7dfe92bf2e` |
| kicad_pro | `4a1040e34967d6610bd5032e46b3c2d0e24863370106f7e220d88d4dd633c61d` |
| kicad_sch | `b95cfca75a079b4b155a4fa24aa2c548fcaef779cd72271e5212a18529856674` |
| NET raw | `3364e97284060bace699f887900baf1fc8fcc8090355f5f6b2c35332901bdb44` |
| pcb_ast_sha (independently defined AST normalization) | `318b4e917c1f0d13c4aece39ca8d65ea4ad19398253d2e4ee022507e322ad97a` |
| sch_ast_sha (independently defined AST normalization) | `80e12b32a4ffc58fb2af5c06e1e47a83bf3a0691cda7efbdc22686d703127a80` |
| net_ast_sha (independently defined AST normalization) | `4795ee63091e19f6313f4a7e902474763edc54a8effa2db0b0703d586222d293` |
| dru_ast_sha (independently defined AST normalization) | `324c7ff5d96274553b7be4a201ae4384e09ac190bedfe156e581dad93db5c2f9` |
| parts cohort (177 members) | `4043025c0fac96983c6d22ed40f8f2e470da3625c7a76a312815f8fc87c99783` |
| rules cohort (16 members) | `36c7aa05e5d26223fbec45194ecf3591b60f60efe66723f3b440d02c3052426d` |
| source cohort (59 members) | `e7b36c809e106e3e5dbe601fd9f72af09691cd9b915b6318b0326fd6297951e9` |
| private coupon PCB | `72bf72e28bf9d3026648c3dd582db9461c98edcb5fb166c889b809701390ca1a` |
| private control PCB | `37fa62911312a2de915120e7bd8278cde2a80803f0c74f8f1a4742afa9dba321` |

`final-identity-bindings.json` defines these semantic/cohort digests and retains333source identities/937source nodes with0native mismatches. `commands.json` lists every timed engineering/diagnostic command, rc, duration and exact stdout path. Initial failed diagnostic invocations are retained separately: unsupported LIB_ID accessor before evidence creation, then a heterogeneous source-library-list parser failure before context repair; no geometry candidate was changed in response. Complete compact-handoff/validation logs and final protected-input/mutation verification accompany this result.


### Actual handback completion

MEASURED compact handoff generated at 2026-09-10T19:59:08Z: rc0, 1.166883s; actual `pcb_flow.py validate` rc0, 1.067132s. Full logs are `compact-handoff.stdout.log` and `compact-validate.stdout.log`. Final audit reopened all512 packet members:511 unchanged, one authorized mutation (`06_build/agent_handoff.yaml`), zero unexpected changes. Tracked mutations are exactly STATUS.md, placement journal and compact handoff; private new diagnostics/result are individually hashed in `mutation-inventory.json`. No source/method/test/model/routing/board/part/rule/review input changed. No patch exists to adopt.
