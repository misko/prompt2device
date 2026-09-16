---
id: 0030
date: 2026-09-13
status: proposed
---
# 0030 — coherent top-only RJ45 source correction

## Context and status

This is the coherent proposed source batch for cumulative top-only candidate4. The independent mounting/bend and width/launch/dependency decisions admit the bounded implementation; they do not accept this assembled source or its future native board. Three historical top-only native candidates and two historical ADC native candidates remain spent. No routing pilot is admitted. Fresh exact-source/native acceptance is required before adoption. FIRST-ARTICLE-ONLY / DO-NOT-ORDER and all current physical/electrical qualification holds remain.

## Protection decision

Retain Würth615008160221 jacks, Weidmüller8909650150 complete factory cords, all pins/nets and fitted parts. All fitted SMD is on F.Cu, including manual/consigned. Copper on other layers remains allowed. TI SLLSEG9C section10.1 requires connector-near, direct protected paths, gentle corners and separation from unprotected conductors. Figure12 supports ordinary45-degree changes and a nearby ground via; it supplies no numerical signal-width or9.0/7.5mm path budget. The accepted engineering construction uses ordinary segments with the final AUDIO_N right-angle corner chamfered by0.35mm on each leg. No PCB_ARC, virtual contact or fine-chord workaround is used.

At each jack the clamp remains local(2.5,8.89),180 degrees for the north-facing cell; the south bank is its180-degree transform. Nominal clamp/body-to-jack rear gap1.00mm, courtyard centerline gap0.35mm and copper-to-shell gap1.125mm are source geometry, not installed tolerances. A centered sensitivity using TI body/flash and jack drawing tolerances consumes0.35mm of nominal1mm before the unclosed installation/seating/tool stack. The rear cell avoids mouth service and side spring/locating-hole obstructions. Board width cannot remove the intrinsic shell distance from pin5. Actual fastener/rework/mate/latch/tool scenes remain separate.

All connector-to-clamp prefixes remain F.Cu, via-free and unbranched with exact pad-center endpoints. AUDIO_P source prefix length8.749330mm fits9.0mm and center8.434729 fits8.6mm; AUDIO_N length6.967176mm fits7.5mm and center5.538173 fits5.7mm. These are bounded engineering budgets for this exact cell, not TI ratings or proof of global shortest routing. A moved cell or arbitrary detour reopens the decision. Every downstream continuation must encounter its clamp pad first. The nine AUDIO_N post-clamp vias are1.00mm rearward from pad centers; their former annuli overlapped same-net SMD lands. All nine P endpoints/via sites and nine GND launch geometries/via families remain exact. Every GND launch is0.50mm wide and0.85mm long to its dedicated via. Preserve connector ground2/6/8, separate shell9/10 and all isolation/current/fault/ESD requirements.

Primary sources retained in the dossiers: TI SLLSEG9C section10.1/Figure12; Würth drawing001.003; Littelfuse GD06/10/24 exact land/body drawing. This source decision relies on their independent packet review. Native clearances, holes, topology, fill/thermals, silk, full body/model/schematic binding and electrical/physical outcomes must be graded on the assembled candidate. Historical board results are not inherited acceptance.

## Carrier implementation

Outline x16..170/y20..120 is154×100mm, versus historical150mm and153mm widths. Mounts are(21,25),(165,25),(21,115),(165,115); FID1 is(25,33). Retain candidate3 jack/fuse/clamp poses, north banks x38+32i and south x43+32i, and0.50mm north/south mouth overhang. The x21 mounting decision has independently measured0.700001mm native courtyard gap to F1, but no exact M3 fastener/tool envelope has been selected. J9 native mouth x19.08 now has3.08mm west setback; direction-only edge_faces cannot prove physical mouth exposure. Renew mate/latch/tool/pigtail/restraint/enclosure scenes under existing holds.

Exactly32 AUDIO prefix/post-clamp width declarations use0.20mm, the unchanged ANALOG_AUDIO minimum. The old0.26mm fixed endcap had0.195001mm gap to adjacent NC2 and failed0.20mm prep clearance; analytical0.20mm gives0.225001mm. Retain all GND and0.60mm power widths. North N vias are(39.7875+32i,36.25), south(41.2125+32i,103.75), all0.50/0.20mm. Ordinary tracks/vias/pours retain their existing class/fabrication floors. Package exceptions PKG_PAD_ESD1..8_2_3 move to F.Cu actual pad2/pad3 union plus0.010mm x/0.005mm y slack (0.695×0.860mm), preserving exact net pairs and0.15mm pads_only:true. All original77 regions are reconciled; only those8 change for connector movement. Six separately reviewed VMID reservations bring the source total to83.

All eight F1..F8 output fanouts retain64 source segments at0.60mm reaching jack1/3/7 around locating holes. The5.0mm fuse adjacency allowance belongs only to the fixed4.845mm gap geometry; no straight route through a hole is permitted. Prep selector H reserves4 mount radius3.2mm regions; all21 NPTHs (4 mounts,16 jack pegs,1 J9) independently get0.25mm margin, with4 edge bands0.8mm and3 unchanged User.3 power rectangles:32 generated prep rectangles total. Overlapping mount/NPTH protection is intentional. Preserve isolation, return routing, route resistance/current sharing/fault and changed copper heat-sinking obligations.

All CH1..4 captions move to y38.5 and CH5..8 to y101.5. Fuse captions move to y28.6/111.4 (local−18.4/+18.4); their owner separation is2.74mm, below unchanged3mm. CH5 remains x40.5 and uses an explicit preferred visible R_X5P reference offset(−6,+5.6), giving proposed center(41.1,99.25),0.4mm upward from the old colliding reference. U_ESD5 preferred reference offset(0,−2.2) preserves its center(40.5,103.05). Exact analytical full-population text/mask checks and regenerated native silk must verify these placements. No text is filtered, suppressed or globally reduced; unrelated silk and connector objects are retained. The reference generator keeps its existing visibility, ownership and clearance rules.

## ADC and power dependencies

Compose the exact reviewed ADC overlay: six VMID return pour/via reservations; one C_VMID1_470N return-column replacement;14 precisely named full-zone pad additions; and a distinct C_VDDA1_10N.2 GND F.Cu0.30mm stub(90.52,68.5)→(90,68)→(90,67.5), via0.50/0.20mm. The historical widened-pocket claim is false: the capacitor was isolated. The separate drop closes that supply pocket analytically and must be proved after actual fill, including its prior0.009501mm full-disk F-island margin. Retain4 VMID owner/drop dominance cuts,3 LT3041 quiet-cell output-terminal cuts,5 no-F-paddle shortcuts, independent GND_A6/GND_A8/GND_D30 drops and nine paddle vias. Global min-resolved thermal spokes stays2; full-zone pads total32, all fitted SMD on F.Cu. No extra full connections are authorized.

R_PWR_PU is(32.4,53.94,90), the independently reviewed+0.04mm correction. FILTP routing still must meet470µF reservoir first and then local ceramics/ADC; U_PWR/U_AUDIO returns remain owning routing obligations. ADR0013 explicitly retains Cirrus section3.7's ambiguous “deprecated on all ground layers” wording; finite F-only barriers and continuous inner references are an engineering choice, not literal all-layer vendor-conformance or manufacturer clarification.

ADR0001/integration.yaml enumerate252 local ADC/front-end support refs excluding U_ADC, and explicitly name80 other necessary dependencies; these are functional boundaries, not minimal/module-replaceable counts. ADR0003 and the AP63205 dossier enumerate9 buck supports and truthfully classify its integrated control and MOSFETs as synchronous_buck_controller_with_integrated_mosfets. The part remains a complete converter with integrated compensation. Threshold10 and all wider power/rule requirements remain unchanged. No hidden shared dependency or unresearched module rejection is admitted.


## ADC1 whole-capsule scope reconciliation — 2026-09-13

The independent return-scope decision (report SHA-256
`e4e6feb60f65c9bc0ef25c5aea1d891cd1c77bfc4db3d5b224268855f3baad8b`,
archive SHA-256 `1345f8f0cc3f631282ea19e6530d02cdd8459be238cc0ab7fbf6c0481052c097`)
finds the previous source DEFECTIVE and supports this bounded correction.
The exact partial CHASSIS/census proposal remains historically INCOMPLETE:
19 of20 normal methods passed; the remaining method had two failed endpoint
subtests. Partial acceptance and an in-memory sensitivity are not full GREEN.

Preserve the accepted C_VMID1_470N.2 north return column and all route copper.
Its0.18mm specification1 primitives (89.45,68.7)→(89.45,69.17) and
(89.45,69.17)→(91.2,69.17) have full-radius boxes
[89.36,68.61,89.54,69.26] and [89.36,69.08,91.29,69.26]. Both exceed the old
ADC_WEST_LOCAL xmin89.5 by0.14mm. Change only that rectangle's west edge to
89.35; retain y67.7..72.35, xmax93.6, F.Cu and deny:[]. This supplies0.01mm
source margin, expanding area19.065→19.7625mm² (delta0.6975mm²). It is a
source-representation margin, not a manufacturing tolerance or yield claim.
ADR0015's whole-capsule requirement remains mandatory. KiCad insideArea overlap
semantics do not discharge that stronger obligation; no native DRC width
violation is asserted.

The geography of both existing rules changes: width0.18mm and paired
clearance0.20mm retain exactly [3V3_ADC,LDO_A_FILT,GND]. For clearance both
items overlap the area and either item's authorized net suffices. The independent
complete population has identical old/new actual membership:26 width-eligible
source tracks and1290 distinct-net clearance pairs, not the superseded470
both-net diagnostic. Overlapping populations remain18 electrical pads,
38 source tracks,5 seed vias and17 named areas, with no new overlapping object;
the added strip contacts one already-overlapping C_LDO_A.2 pad, three existing
tracks and four named-area boundaries/regions. Larger future geometric
permission is explicit even though present membership is unchanged. The
orthogonal-union alternative adds0.1005mm² but needs a different polygon
checker; retaining the existing rectangle uses one changed source coordinate.
No numerical width, clearance, fabrication, current or thermal floor is lowered.

The maintained source regression expands all216 point specifications from154
banks into391 straight primitives and pins every narrow GND identity:
10 banks/10 specifications/20 primitives,17 at0.18mm and3 at0.20mm, total
15.509834613921mm. Each complete capsule must fit an eligible exact-net/layer
scope whose minimum width permits it. Ordinary GND remains0.30mm; empty,
missing, substituted or non-seed populations cannot silently satisfy coverage.
The accepted ADC2 pad-clearance union and ADR0015 amendment remain exact, as do
all other82 areas, the four VMID owner/drop cuts, three LT quiet-cell cuts,
five ADC paddle exclusions, independent GND_A6/GND_A8/GND_D30 drops,54 source
vias,32 full-zone pad targets, minimum resolved spokes2 and0.50mm thermal
settings. Their declarations do not prove future filled return connectivity.

This five-file source proposal requires ROOT's exact composed source preflight
and independent acceptance. It neither admits nor constructs candidate5;
all four prior native outcomes and closed4/4 history remain intact. Any later
single candidate admission belongs to ROOT under the changed reviewed premise,
with ordinary placement DRC before prep and complete later source/native
return proofs. No sixth trial or routing pilot is authorized. Thermal/current,
return-cut, assembly, orientation, order and release qualification remain open;
FIRST-ARTICLE-ONLY / DO-NOT-ORDER still applies.
