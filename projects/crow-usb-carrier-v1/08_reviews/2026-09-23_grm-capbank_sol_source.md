subject: crow-usb-carrier-v1 Murata capacitor-bank source candidate
date: 2026-09-23
reviewer: independent SOL agent /root/modular_review, source qualification
context-given: full-tree
source_commit: c9cc9db86d1f6aa8b9b343d32b22c784746e680a
board_sha256: not-generated (source-only)
design_verdict: DEFECTIVE (qualification semantics pending adjudication)
order_verdict: BLOCKED-SOURCING

# Independent review — Murata C84494 ten-cap bank

Date: 2026-09-23
Candidate: `c9cc9db86d1f6aa8b9b343d32b22c784746e680a` against `816642a4`
Verdict: **REPAIR REQUIRED before source adoption; sound as a documented engineering candidate.**

## Blocking admission defect

The candidate accurately labels Murata SimSurfing coefficients as typical small-signal model data and the 10%/12.5% factors as project engineering reserves, but the adopted `effective_capacitance_banks` rows have no provisional state. The owning reader therefore reports unconditional hard-gate success:

- TPSM output `E-CAP PASS 34.422/25 uF`
- each TPS62825 output `E-CAP PASS 12.954/10 uF`
- LT3045 input/output `E-CAP PASS 11.474/4.7` and `25.909/10 uF`
- overall `EARLY-DESIGN PASS: 4/4 gate families green`

Those PASS results assert worst-case effective capacitance, while the only DC/temperature data are typical base-die models and Murata supplies no production minimum. Wording inside `basis`/`evidence` is not consumed as a hold. The tightest row has only 1.295× modeled/reserved margin, so an unsupported lot distribution could invalidate the regulator minimum.

Before adoption, either (a) obtain an approval-sheet/manufacturer production bound that supports the encoded derating numbers, or (b) extend the owning E-CAP contract narrowly with a machine-enforced provisional/model-screen state that remains non-passing until the named qualification receipt is present. Keeping a separate blocking finding while E-CAP itself says PASS would still misstate what that gate proved. Do not invent a larger derating merely to force red.

## Accepted engineering content

- Exact identity is consistent: GRM32ER71A476KE15L, C84494, 47 uF ±10%, 10 V, X7R, -55..125 C, 1210/3225. The retained model files name base die GRM32ER71A476KE15; `L` is the reel packaging suffix. The dated exact-code JLC record supports the catalog identity and count, not allocation or placement eligibility.
- The combined-condition models are preferable to multiplying separate DC, AC and temperature curves. Retained coefficients match the report: 14.7 uF at 5.05/5.099 V and -55 C, 16.9 uF at 3.38 V and -55 C, 18.4 uF at 1.818 V, 18.7 uF at 0.92 V, and 0.657 nH/2.13 mΩ at 3.38 V and 125 C. The model is explicitly limited to small-signal typical behavior over its stated range.
- The ten-part topology is coherent: three TPSM output parts; one for each of three TPS62825 outputs; one LT3045 input; two LT3045 outputs; one OPA reservoir. The three removed TPS62825 refs are removed consistently from TSX, presentation, manifest, floorplan, modular plan, integration selections and endpoint sets. The candidate census of 490 components is therefore expected.
- One nominal 47 uF with 0.47 uH matches the marked TPS62825 Table 8-3 combination, while the former two-part nominal 94 uF is not the marked TPS62825 row. This supports the topology choice, but startup/load-step and the actual replacement inductor/distributed load remain later physical checks rather than prerequisites for authoring the candidate source.
- Murata Fig. 3 arithmetic is correct: 1.4 mm pads at ±1.8 mm give a 5.0 mm outer span and 2.2 mm inner gap, with 2.9 mm pad height. TSX and native footprint agree. The candidate honestly identifies this as test-substrate copper; stencil, paste, assembly and placement review remain owed. The 3.5×2.7 fabrication envelope and 5.5×3.4 courtyard conservatively cover the nominal 3.2×2.5 body.
- For LT3045, the ideal parallel model pair gives 0.3285 nH/1.065 mΩ and nominally leaves 1.6715 nH for the complete shared network. Deferring common pad/via/copper/return/OUTS extraction to P3 `quiet_power`, with Kelvin OUTS and common SET/output-cap ground, is the correct stage boundary. Because the component model is typical rather than maximum, P3 extraction is a screen and first-article stability/measurement remains required. This does not require a fabricated board before source authoring.

## Composition and scope

The candidate predates the accepted OPA/YXC repair and its generated artifact contains the old invalid Y_XU footprint state. Integration must compose onto the later `5ea267d3` state and rebuild the 490-component source; do not use the isolated candidate `dist` as admission evidence. Verify exact component/ref census, source errors, dossier/FPID resolution, and unchanged nets for the seven retained-bank substitutions plus the intentional removal of three parallel capacitors.

This verdict does not demand board measurement before source work. It requires the source-stage gate to describe the model evidence honestly. Placement ESL, stencil/paste, load-step, startup, lot characterization and order-time PCBA acceptance remain later obligations.
