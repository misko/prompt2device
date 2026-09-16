---
id: 0009
date: 2026-09-13
status: proposed
---
# 0009 — coherent top-only RJ45 source correction

## Context and status

This is the coherent proposed source batch for cumulative top-only candidate4. The independent mounting/bend and width/launch/dependency decisions admit the bounded implementation; they do not accept this assembled source or its future native board. Three historical top-only native candidates and two historical ADC native candidates remain spent. No routing pilot is admitted. Fresh exact-source/native acceptance is required before adoption. FIRST-ARTICLE-ONLY / DO-NOT-ORDER and all current physical/electrical qualification holds remain.

## Protection decision

Retain Würth615008160221 jacks, Weidmüller8909650150 complete factory cords, all pins/nets and fitted parts. All fitted SMD is on F.Cu, including manual/consigned. Copper on other layers remains allowed. TI SLLSEG9C section10.1 requires connector-near, direct protected paths, gentle corners and separation from unprotected conductors. Figure12 supports ordinary45-degree changes and a nearby ground via; it supplies no numerical signal-width or9.0/7.5mm path budget. The accepted engineering construction uses ordinary segments with the final AUDIO_N right-angle corner chamfered by0.35mm on each leg. No PCB_ARC, virtual contact or fine-chord workaround is used.

At each jack the clamp remains local(2.5,8.89),180 degrees for the north-facing cell; the south bank is its180-degree transform. Nominal clamp/body-to-jack rear gap1.00mm, courtyard centerline gap0.35mm and copper-to-shell gap1.125mm are source geometry, not installed tolerances. A centered sensitivity using TI body/flash and jack drawing tolerances consumes0.35mm of nominal1mm before the unclosed installation/seating/tool stack. The rear cell avoids mouth service and side spring/locating-hole obstructions. Board width cannot remove the intrinsic shell distance from pin5. Actual fastener/rework/mate/latch/tool scenes remain separate.

All connector-to-clamp prefixes remain F.Cu, via-free and unbranched with exact pad-center endpoints. AUDIO_P source prefix length8.749330mm fits9.0mm and center8.434729 fits8.6mm; AUDIO_N length6.967176mm fits7.5mm and center5.538173 fits5.7mm. These are bounded engineering budgets for this exact cell, not TI ratings or proof of global shortest routing. A moved cell or arbitrary detour reopens the decision. Every downstream continuation must encounter its clamp pad first. The nine AUDIO_N post-clamp vias are1.00mm rearward from pad centers; their former annuli overlapped same-net SMD lands. All nine P endpoints/via sites and nine GND launch geometries/via families remain exact. Every GND launch is0.50mm wide and0.85mm long to its dedicated via. Preserve connector ground2/6/8, separate shell9/10 and all isolation/current/fault/ESD requirements.

Primary sources retained in the dossiers: TI SLLSEG9C section10.1/Figure12; Würth drawing001.003; Littelfuse GD06/10/24 exact land/body drawing. This source decision relies on their independent packet review. Native clearances, holes, topology, fill/thermals, silk, full body/model/schematic binding and electrical/physical outcomes must be graded on the assembled candidate. Historical board results are not inherited acceptance.

## Pod implementation and residual return decision

Retain60×40mm outline, J1(45.5,25.86,0), U3 top(48,34.75,180), all31 fitted SMD top and exact44 footprint/pad/net identities. All four connector-prefix/post-clamp AUDIO width declarations stay0.26mm, above unchanged BALANCED_AUDIO0.25mm. U3.5 post-clamp via is(47.2875,36.25),0.60/0.30mm; its old horizontal annulus/land contact is a known-bad control. Source prep clearance0.15mm and ordinary routing clearance0.20mm remain. Retain6 NPTHs with0.60mm margin, H radius3mm,0.5mm edge bands and the existing User.2 rectangle.

The completed independent pod-return decision admits one ADDITIVE R13.2 AUDIO_N F.Cu0.26mm segment(62.913,36)→(62.913,34.7), explicit via0.60/0.30mm at(62.913,34.7). Current source had no R13 bank; the failed(62.4,35.6) via occurs only in historical routed candidates. The explicit source x62.913 matches actual consumer rounding from native pad x62.9125 and remains on the land. Preserve forbid_new_via_in_pad and R13.2→TP6.1 F.Cu≤9mm probe requirement; this seed does not complete that route or prove global routability.

C10 remains unchanged. Fresh independent native evidence finds it on broad F.Cu ground with two0.499mm thermal spokes and zero starved-thermal DRC rows. The historical row naming a multi-island zone UUID and C10.2 does not prove C10 isolation: the actual residual is the R7.2/C9.2 F.Cu island to the broad plane. Preserve that final route/stitch obligation, the existing separate C5 stitch-only seed and U3 dedicated GND drop. The review's memory control included optional C10 copper, so exact minimal R13-only plus top-only correction native fill remains owed. Historical three routed failures and the unqualified unsaved source proposal are retained with their original spend; no new route pilot or C10 repair is implied.


## Probe-route budget provenance

The retained 9 mm limit is an engineering routing constraint from
`03_src/rules/critical_paths.yaml`, not a manufacturer rating or a measured
completed route. The command below independently reopens the exact named
F.Cu rule so this document cannot silently change its configured ceiling.
The final `check_realized_routes.py` gate must still measure the actual
R13.2-to-TP6.1 copper path; the prepared candidate does not complete it.

<!-- bound: POD_AUDIO_N_PROBE_ROUTE -->
```yaml
id: POD_AUDIO_N_PROBE_ROUTE
claim: Retained engineering maximum for the final R13.2-to-TP6.1 F.Cu probe branch
relation: "<="
value: 9.0
unit: mm
corner: nominal
grade: ESTIMATED
why_not_rerunnable: >-
  The configured ceiling is reproducible, but no manufacturer or physical
  performance derivation establishes nine millimetres as a sufficient limit.
  The completed route is still absent and must pass the owning realized-path
  gate. Source consistency does not establish routed length or signal integrity.
command: >-
  /usr/bin/python3 -B -c "import yaml; p='projects/crow-mic-pod-v3/03_src/rules/critical_paths.yaml'; d=yaml.safe_load(open(p)); r=[x for x in d['short_paths'] if x.get('from')=='R13.2' and x.get('to')=='TP6.1']; assert len(r)==1 and r[0]['layer']=='F.Cu'; print(r[0]['max_length_mm'])"
governs:
  budget: "<= 9.0"
  unit: mm
  note: >-
    Final native copper length is graded by check_realized_routes.py using
    this exact critical_paths.yaml entry. No completed-path evaluation is
    claimed by this source budget record.
standard_value:
  explicit: [9.0]
  series_why: >-
    Routing length is continuous geometry, not an E-series component.
    The singleton records only the retained project limit and makes no
    claim about physical sufficiency or a selected component value.
chosen: 9.0
requires:
  - projects/crow-mic-pod-v3/03_src/rules/critical_paths.yaml
```
