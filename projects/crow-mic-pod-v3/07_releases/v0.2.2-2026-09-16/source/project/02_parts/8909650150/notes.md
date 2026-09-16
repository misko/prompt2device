# Independent Weidmüller 8909650150 connector SOURCE review

Verdict: **ACCEPT the nominal mate/grip source representation specified below.** This is an independent source-boundary judgment, not a compiled SOURCE receipt, candidate adoption, physical-fit PASS, or board-release review. The frozen held HARTING contracts remain unadopted and unchanged. The exact integrated replacement must still be compiled and reviewed by its owning gates.

The manufacturer STEP supports a known nominal mate with `body_envelope_mm: null` and a typed manufacturer-model source. A manufacturing maximum is not necessary to make that narrower claim. Its numerical kernel tolerances do not establish manufactured dimensions, installed tolerance, latch accessibility, simultaneous mating, or environmental qualification.

## Independent numerical evidence

I reopened the frozen STEP with OCCT, verified its digest, traversed its actual BREP and independently tested containment with solid Boolean operations. The transferred source is valid: **1 solid, 1,440 faces**, volume **14,481.0814 mm³**. Bounds are approximately **13.7000002 × 18.45668755 × 279.9600002 mm** in model X/Y/Z. Internal family identity is 8909650000; the frozen exact-product source record binds these bytes to 8909650150. The 200 mm modeled cable is a placeholder, not the 15 m purchased length.

The 719 first-end faces which terminate before model Z100 reproduce **X −0.000000100…13.700000100, Y −0.000000883…18.456686665, Z −0.000000101…57.980000000 mm**. Only two faces cross Z100: the cable's two half-cylinder surfaces, radius 3 mm, from Z39.98 to239.98, axis **X6.85,Y7.38**, directed +Z. Excluding those through-going cable surfaces faithfully retains the complete modeled first-end hardware, including the rear sleeve. The boot transition at39.98 and end at57.98 are useful nominal model segmentation, not manufacturer-assigned subpart identities or toleranced dimensions. In particular, “39.98 mm plug” alone would omit the rear modeled sleeve from the declared cell.

The full X/Y bounding-box diagonal is **22.9856329200 mm**. Its midpoint Y9.228342891 differs from the cable axis Y7.38, so the diagonal formula alone does not prove a cylinder centered on the connector axis contains an asymmetric latch. I resolved that ambiguity directly: clip the original solid to Z−1…58, then subtract a cylinder centered at X6.85,Y7.38, radius **11.4928164600 mm**, extending beyond both axial ends. The clipped end remains valid (**722 faces, 1 solid, 4,921.32977084 mm³**). The difference is valid and empty: **0 faces, 0 solids, 0 mm³**. Thus the proposed diameter does contain this actual nominal BREP about the stated nominal axis; use **22.986 mm** when writing three decimal places. Vertex inspection alone was also performed but is not the containment proof. Its maximum observed radius11.313007607 mm did not produce a counterexample.

A simpler cross-section-box proof would require26.048 mm about that same axis, but it is unnecessary after the independent full-solid containment check. Neither value includes a physical manufacturing allowance. Axial57.98 is the nominal model datum, rounded at the precision of its originating geometry; model bounds differ by approximately0.0000001 mm due to kernel tolerance, which is not a manufacturing specification.

## Recommended exact authored sections

Use project-relative ordinary files for these source IDs. `spoke-cable-model` must have kind `manufacturer-3d-model` and contain the exact STEP bytes above. `spoke-cable-record` should retain the exact-product download URL, hash, 15 m specification and wiring-image provenance. `spoke-cable-nominal-review` should retain this derivation and its bound evidence archive.

```yaml
mate:
  manufacturer: Weidmuller
  mpn: '8909650150'
  part_kind: factory_15m_shielded_Cat6A_PUR_RJ45_patch_cord
  model_source_id: spoke-cable-model
  body_envelope_mm: null
  evidence:
    grade: exact
    source_ids: [spoke-cable-record, spoke-cable-model]
    rationale: >-
      The exact product download binds this manufacturer STEP to 8909650150.
      Its nominal complete plug, latch, boot and rear sleeve geometry is known.
      The internal family identifier and 200 mm cable placeholder are recorded;
      the purchased cord is 15 m. This does not establish manufactured maximum
      dimensions or installed fit.
grip:
  kind: integral_latch_boot
  across_flats_mm: null
  outer_diameter_mm: 22.986
  axial_length_mm: 57.98
  evidence:
    grade: conservative
    source_ids: [spoke-cable-model, spoke-cable-nominal-review]
    rationale: >-
      This envelope contains only the complete nominal modeled first end,
      including its latch and rear sleeve, from model Z0 to Z57.98.
      Diameter derives from the 13.7000002 by 18.45668755 mm cross-section
      diagonal and independent BREP subtraction verifies containment about
      model axis X6.85,Y7.38. The diameter rounds outward to 22.986 mm.
      No manufacturing allowance, hand-access clearance, mated datum,
      latch-motion sweep or installed tolerance is included or assumed zero.
```

The STEP requires explicit coordinate registration before any PCB or enclosure consumer uses it: model Z is axial; X/Y form the cross-section; its stated axis is a nominal source datum. Final jack-to-plug placement, insertion depth and local-to-board transform remain interface qualification. Do not interpret the entire279.96 mm placeholder cord as the single mate's service envelope.

Preserve the existing unknown installed exposure stack. Additionally represent radial and axial growth explicitly; the existing `exposure_setback` effect does not execute either of these effects. Suggested additions for the factory-rj45-spoke profile in both carrier and pod:

```yaml
# Append to assembly tolerances:
- id: installed-plug-boot-radial-variation
  applies_to: installed_plug_latch_boot_and_sleeve_radial_variation
  effect: service_radial_growth
  minus_mm: null
  plus_mm: null
  evidence:
    grade: unknown
    source_ids: [shared-spoke-contract, spoke-cable-record]
    rationale: >-
      Nominal BREP containment is known; manufactured plug, latch, boot and
      sleeve variation and installed radial service effects remain unqualified.
      The bound first-article plan must establish these separately from
      seating/exposure and nominal model kernel tolerances.
- id: installed-plug-boot-axial-variation
  applies_to: installed_plug_latch_boot_and_sleeve_axial_variation
  effect: service_axial_growth
  minus_mm: null
  plus_mm: null
  evidence:
    grade: unknown
    source_ids: [shared-spoke-contract, spoke-cable-record]
    rationale: >-
      Manufactured axial extent and installed service reach variation remain
      unqualified. Determine these on the exact selected cord and realized
      assembly; do not reuse the receptacle drawing allowance for this purpose.
# Append to phase source_deferrals:
- assembly_id: factory-rj45-spoke
  target_kind: tolerance
  target_id: installed-plug-boot-radial-variation
  unknown_class: installed-tolerance-qualification
  plan_source_ids: [shared-spoke-contract, spoke-cable-record]
  rationale: Qualify installed plug/boot radial variation in the bound first-article plan.
- assembly_id: factory-rj45-spoke
  target_kind: tolerance
  target_id: installed-plug-boot-axial-variation
  unknown_class: installed-tolerance-qualification
  plan_source_ids: [shared-spoke-contract, spoke-cable-record]
  rationale: Qualify installed plug/boot axial variation in the bound first-article plan.
```

The cited ordinary source files must actually contain the corresponding first-article plan; a review suggestion is not evidence of a plan already adopted. Keep all existing interface, reaction, installed cable route and required operation unknowns and their exact coverage. Update obsolete HARTING/maxima blocker prose together with the selected identities. Do not add a mate/grip source deferral or turn any unknown physical bound into zero.

## Wiring and environmental boundary

I visually reopened the frozen wiring image. It depicts contact1 to1 through8 to8 with white/orange1, orange2, white/green3, blue4, white/blue5, green6, white/brown7, brown8. This supports the stated straight-through T568B pair/color map. The image itself does not prove an actual received cord's continuity or polarity, and does not show a shield conductor. Retain the manufacturer's exact-product image linkage when integrating the source record; the packet's TASK attributes the image to the exact product, but no separate wiring-image URL file was supplied.

The exact datasheet's UV claim remains unestablished in this packet. PUR alone is not evidence of UV resistance. Represent UV as unknown (for example `uv_resistant: null` and an explicit qualification-status field in the owning source schema), retain the outdoor requirement, and retain a concrete environmental qualification hold. A short first-article fit check does not establish long-term UV durability: exact-product manufacturer qualification or a suitable documented environmental qualification is needed before outdoor deployment; a negative result requires a source/design correction.

Within the accepted carrier ADR0007 scope, an unestablished UV property can remain a disclosed environmental hold while preparing a prototype design; it need not become a mandatory pre-prototype part-selection blocker. This follows the explicit separation of design release from production/outdoor deployment. It is not an assertion that this cord meets the outdoor requirement, that ordering is authorized, or that the carrier ADR automatically grants a pod lifecycle exception. No procurement or deployment decision is reviewed here. Other sourcing and source-schema gates retain authority; do not weaken a requirement or validator to manufacture a UV PASS.

The operating/installation temperature limits,6.1…6.5 mm cable OD,290 Ω/km loop resistance and15 m length in the frozen report remain manufacturer-record facts. They were not independently fetched during this no-network geometry review. The report's hot-loop arithmetic evaluates to2.1125 Ω and10.58875 V with its0.300 Ω unmeasured contact allocation; this does not qualify manufactured contact resistance or powered operation.

## Delivery and limitations

All frozen packet hashes were verified before and after analysis. Only the allocated scratch/output directories were written. Geometry subprocesses used `/usr/bin/python3 -B` through `pipeline_runtime.run_stage` with60/90 second limits, and all completed PASS. This was bounded execution, not a hermetic sandbox. No live engineering source was modified, no network source was silently substituted, and no child reviewer was launched.

Archive members preserve the input packet, methods, numerical results and complete bounded geometry logs, with SHA-256 and byte counts in evidence-manifest.json. Completion checks certify honest review/delivery completion only. **Base/FULL physical qualification remains INCOMPLETE.** No overall connector SOURCE PASS or design release is inferred until the owner integrates this exact representation, binds the evidence and runs the mandatory gates.
