# r10: stack warning and connector registration diagnosis

Reviewed input commit `278309e057c10f46d7c3d638931a495737699169`.
Scope: read-only engineering diagnosis and a quote-only evidence plan. No
native/CPL/BOM/Gerber corrections, tolerance concessions, vendor messages,
browser edits, purchases or production approval. No new stage acceptance.

## Subsequent user decision

The user has now authorized **quote-only selection of JLC04161H-7628A**, including
the reported1.5542 mm ±10% warning, and publication of this assessment/checklist.
Recommendation1 below is selected for quotation; it is no longer awaiting that
authorization. The warning has not been accepted in a browser by this backend
task. No manufacturing tolerance waiver, placement approval, purchase or vendor
message is authorized. Use the [current MacBook checklist](MACBOOK-CHECKLIST.md).

## Bottom line

The **nominal 7628A stack already matches the design**. The warning is not
evidence of a new wrong stack or a need to redesign. Its full finished-thickness
tolerance and exact-job manufacturing acceptance are separate, still-open items.
For the connectors, the native geometry and CPL agree; **the present evidence
cannot determine JLC's model/placement transform**. A cosmetic rotation is not
an established correction. Keep the current r10 package unchanged.

## 1. Stackup: what matches, and what does not follow

The actual native stack lists, top to bottom, 0.035 / 0.218 / 0.0764 / 0.0152 /
0.865 / 0.0152 / 0.0764 / 0.218 / 0.035 mm. Its sum is **1.5542 mm**, exactly
the portal's nominal figure. The outer dielectric gaps are0.2944 mm; the core
is0.865 mm. These match JLC's published 7628A construction. The CAD general
thickness property remains1.6 mm; the retained LS20/process evidence explicitly
recognizes the different layer sum and prohibits inventing extra dielectric.
Sources: [JLC stack table](https://jlcpcb.com/impedance),
[retained construction assessment](../../releases/crow-prototype-v3-first-run-5c10p-public-v1/historical/documentation/carrier/process/04-2026-10-08-ls20-engineering.md),
[process controls](../../releases/crow-prototype-v3-first-run-5c10p-public-v1/historical/documentation/carrier/process/33-process.md).

| Quantity | Calculated value |
| --- | ---: |
| Nominal difference from1.6 mm | -0.0458 mm |
| Portal lower limit:1.5542×0.90 | 1.39878 mm |
| Portal upper limit:1.5542×1.10 | 1.70962 mm |
| Extremes relative to CAD1.6 mm | -0.20122 / +0.10962 mm |

The full range, not just the rounded0.05 mm nominal difference, must be carried
forward. Do not claim that it lies wholly within an assumed1.6±10% range:
that would start at1.44 mm, above this offer's minimum. The reviewed controls
do not establish such an assumed general range as a performed qualification.

| Design area | Assessment and exact remaining limit |
| --- | --- |
| Clock/electrical construction | Named7628A is the intended electrical basis. Current TI-clock model samples outer gaps0.23552 and0.35328 mm as engineering sensitivities, not supplier-guaranteed ply extremes. Overall board±10% cannot be assigned independently to every ply or converted into a guaranteed impedance. Retain material/copper/layer roles and existing power, waveform and thermal qualification. |
| USB | USB data routing is on the Pico module, not a new carrier USB differential pair. This warning does not by itself require a carrier USB impedance redesign. |
| Connector top-side access | Existing r10 access bounds use the actual finished top datum, seating, body and pose controls. A uniform thickness change does not automatically consume the0.90 mm plug-to-top gap. Local top/warp limits still need verification; total thickness does not prove them. |
| Holes and seating | Thickness does not determine finished hole diameter, location, annulus, solder fill or seating. All r10 hole-pattern/process requirements remain; the popup neither satisfies nor waives them. |
| Pico underside pools | The retained module rule forbids shell solder below the actual carrier underside. A thinner board can make a previously acceptable pool protrude; neither the report nor the1.6-mm CAD property proves this at1.39878 mm. Apply the same no-protrusion rule to the actual thinner article or qualify an explicit incoming pool-depth bound. Do not assume a fixed nominal pool fits. |
| Leads/support/retention | For fixed top-seated leads, the thinner extreme increases underside protrusion by0.20122 mm relative to1.6 mm. Existing restricted underside columns remain, but there is no selected enclosure/floor fit approval. Thickness affects stiffness; the existing supported mating/retention qualification remains necessary. No invented lead-strength or board-rigidity guarantee. |
| Enclosure and deployment | No compatible enclosure/roof-support dimensional specification has been established here. Neither nominal1.6 nor the offered range certifies enclosure fit. |

Module and integrated controls:
[Pico seating/underside](../../releases/crow-prototype-v3-first-run-5c10p-public-v1/historical/documentation/carrier/instructions/40-module-controls.md),
[finished-board/interface controls](../../releases/crow-prototype-v3-first-run-5c10p-public-v1/historical/documentation/carrier/instructions/42-controls.md),
[r10 correction](../power-jack-r10-review/REVIEW.md).
Historical population, oscillator and original DC-direction claims are not
re-adopted; current r10 identities, power basis and corrected DC corridor govern.

**Recommendation 1 — now authorized for quote only:** select7628A for
**quotation only**, recording1.39878..1.70962 mm and keeping all engineering/
manufacturing holds. This is reasonable for pricing the already-intended stack;
it is not unconditional acceptance of every possible finished board. Use
standard assembly as observed. If the portal's acknowledgment instead binds
production or waives the retained controls, stop rather than accepting it.

**Recommendation 2:** leave the warning unaccepted and seek exact-job thickness/
process clarification before repricing. Any vendor message requires separate
authorization. Do not switch to "No Requirement" or a different named stack
as a workaround. There is no basis here for demanding an arbitrary new precision
thickness service or redesigning the board solely over the nominal0.0458 mm.

Before ordering, record the supplier's definition of finished thickness and
finish treatment, retain the exact named stack/material/copper, and close the
actual hole/process, Pico underside and support/retention controls. If those
cannot be met across the offered range, reopen only the affected mechanical/
process decision; do not silently narrow the supplier tolerance.

## 2. Connector diagnosis: concrete witnesses

Fresh KiCad extraction of r10 verifies all nine RJHSE-5080 instances and carrier
PJ-102AH J1. Numbered pads, asymmetric locator pattern, component side and CPL
body centers agree with the retained manufacturer geometry (RJ rounding<=0.006mm).
The current [Amphenol RevJ component-side drawing](https://cdn.amphenol-cs.com/media/wysiwyg/files/drawing/p-rjhse-5080.pdf)
corroborates the contact/peg pattern. The jack uses the retained Same Sky
2024 drawing in the [r10 review sources](../power-jack-r10-review/source-evidence/2-P028-manufacturer.pdf).

Native top-view coordinates are X right/Y down, in mm. CPL Y is negative nativeY.

| Witness | Pod RJ J1 | Carrier RJ J101 | Carrier power J1 |
| --- | --- | --- | --- |
| Pin1 | (7,8.5) | (8,8.5) | VIN12(188,14.7) |
| Pin8 / pin2 | pin8(14.112,10.28) | pin8(15.112,10.28) | GND pin2(188,8.7) |
| Pegs / pin3 | (4.21,5.96),(16.91,5.96) | (5.21,5.96),(17.91,5.96) | NC pin3(183.3,11.7) |
| CPL body center, angle | (10.556,-8.373),0deg | (11.556,-8.373),0deg | (188,-8.2),180deg |
| Intended mouth | native -Y/outward | native -Y/outward | native -Y/outward |

The audit includes all other carrier RJ coordinates. A literal physical180deg
RJ reversal about its body center moves the peg row fromY5.960 toY10.786:
**4.826 mm away from its holes**. For the power jack, a literal reversal about
the current body center would move numbered pin1 to(188,1.7), pin2 to(188,7.7)
and pin3 to(192.7,4.7), also incompatible with the current numbered holes.
These counterfactuals show why rotating actual components is wrong; they do
**not** establish the numeric vendor-specific CPL correction.

JLC explicitly documents differing zero-angle conventions; its preview red dot
is an orientation marking, not universally physical pin1. Its CPL requires a
centroid and positive counterclockwise rotation. Therefore a convention offset
is plausible, but not demonstrated for these parts. Sources:
[JLC assembly FAQ](https://jlcpcb.com/help/article/pcb-assembly-faqs-part-2),
[JLC CPL specification](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly).
Do not follow the FAQ's suggestion to place an order for engineering review:
that exceeds this task's authority.

No close-up screenshots or vendor pin/model transforms were retained in the
MacBook handoff. The inward-mouth observation alone cannot distinguish:

- wrong display-only body/model registration;
- different vendor zero-angle or centroid convention;
- wrong library/package/model selection;
- an actual placement error.

The new local audit finds no demonstrated native/canonical-CPL defect. No
candidate correction is justified until the missing vendor mapping is observed.

## 3. Bounded MacBook evidence pass

Keep both current drafts unchanged during diagnosis. Carrier draft is
`ace1600497a949bebfdd38f3ef826f7f`; pod is`71c384e886a94642a54e0c804cea3a97`.

1. Capture **pod J1, carrier J101 and carrier power J1**: placement-table row
   with exact selected catalog/MPN/XY/angle/side, orthographic top, underside
   if available and one tilted view. Save actual screenshots with draft URL/time.
2. Expose terminals/pegs using transparency/hide-body controls if available.
   Identify physical numbered terminals from the drawing, not the generic red
   dot. If exportable read-only, retain the exact vendor model and its transform.
3. Register board view to at least two known mounting-hole/outline datums and
   known top side; account for display mirroring and panel rails. Do not invent
   a5-mm coordinate shift just because rails exist. Use relative vectors from
   the body center when the viewer has a different global origin.
4. Compare RJ pin1/pin8/both pegs and all three PJ terminals to the table/audit.
   Fit a single rigid in-plane transform from at least three noncollinear
   witnesses, then check all remaining pins. Record residuals; do not stretch,
   mirror or independently move pins to make a fit. Confirm all eight carrier
   RJs share the same selected part and convention, then audit every reference.

| Observation | Next action, not automatic approval |
| --- | --- |
| Terminals/pegs register correctly but modeled mouth is inward | Suspect model geometry/registration; preserve native/CPL, obtain corrected model or explicit production-pose evidence. |
| One vendor angle/centroid offset maps every terminal/peg and the correct mouth | Propose a vendor-only CPL adapter for independent review; preserve native copper and record exact component-specific offset. Then authorize a new upload/preview and audit all136/29 references. |
| Pattern cannot match without reflection/scaling, or selected package differs | Hold wrong model/library/package; do not repair by arbitrary CPL offsets. |
| UI cannot expose numbered witnesses | Stop after this bounded pass. Request authorization for one targeted JLC inquiry with maker drawings and required poses; do not repeat cosmetic rotations/screenshots indefinitely. |

No production approval follows from a preview or a price. The prior r10 estimate
**$390.97** excludes shipping, tax and HOME parts and does not price a confirmed
7628A carrier. Preserve all136/29 factory references and20 HOME installs.

## Reproducibility and exact subjects

[native-audit.json](native-audit.json) records exact source hashes, arithmetic,
all numbered-pad/peg/CPL witnesses and physical-reversal counterfactuals. Re-run
read-only with KiCad's Python, using a new output filename if saving:

```sh
/usr/bin/python3 projects/crow-array/order-readiness/r10-registration-review/audit.py
python3 projects/crow-array/order-readiness/r10_upload_check.py
```

Carrier native SHA256`1fc774524ef57efdd3a644de338328837e42ba648d3a4dd6bb78bad44e8852a1`;
carrier CPL`ea748566517886a3dee50eaaa176c173f5fde86f45fc48a42e24c97d68e5855d`;
pod native`d67134d2361f32f25a1f8841134f21f84791d3d36ede1acb74b383d5b007ceb9`.
The portable r10 check still passes213 files/105 preserved r9 files. No r10
payload, draft or production-control requirement was changed by this diagnosis.
