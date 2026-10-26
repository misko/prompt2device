# JLC capability comparison — exact Crow prototype batch

Reviewed 2026-10-26, OR4. Five carriers and ten pods. Literature comparison only:
no CAD modification, supplier contact, process acceptance or order authorization.
The user will assemble the five Picos; no other manual operation is assigned to
the user by inference. Existing D1-only preparation and inspection still apply.

## Finding

JLC supports the general fabrication/partial-assembly route. Public documentation
does **not** establish all the unusually tight limits in the sealed controls.
Some of those are explicitly design-owned inspection/reject limits, not component
manufacturer tolerances. Review their engineering necessity before treating a
custom supplier guarantee as the only possible resolution. They cannot simply be
deleted: the retained clearance/fit proofs depend on bounded physical variation.

## Requirement-to-capability comparison

Sources [A]–[F] below are JLC's own publications, accessed today. “Not established”
means no applicable guarantee found in this bounded review, not proven inability.

| Area | Published support | Exact-release disposition |
|---|---|---|
| Four-layer, 1.6 mm FR-4, ENIG; carrier 200×100 / pod 85×78 mm | Within general fabrication/PCBA ranges [A,B] | Basic process supported; exact stack and job selections still need matching |
| Recesses and USB notch | Precision routed outline ±0.10 mm; minimum 50×50 mm, three tooling holes ≥1.5 mm [A] | Suitable published option; check tooling, corner radii and combined web/clearance, not just outline tolerance |
| RJ contacts 0.89±0.05 mm | Press-fit tolerance ±0.05 mm for circular 0.55–2.0 mm multilayer ENIG holes, identified in remarks [A] | Candidate explicit process; not an instruction to press-fit these soldered contacts |
| RJ pegs 3.25±0.05 mm; Pico reliefs 2.50–2.65 / 2.15–2.30 mm | Ordinary holes +0.13/−0.08 mm; larger holes outside that press-fit range [A] | Not guaranteed by listed options; NPTH-specific confirmation or revised engineering needed |
| PJ nominal 1.60 mm, required finished 1.60–1.73 mm; complete ±0.05 mm pitch pattern | Hole-position tolerance ±0.075 mm [A] | Ordinary hole lower bound is too small; individual location allowance does not establish coupled pitch |
| All installed bodies: radial displacement ≤0.10 mm, total 3D angle ≤1° | AOI and visual inspection offered [B] | No blanket final-pose guarantee found; machine capability or AOI presence is not this acceptance promise |
| Finished top ≤+0.05 mm; connector support gap ≤0.05 mm; module gaps and no-bearing/pool limits | No matching quantified guarantee found [A,B,D] | Design-owned geometry/process constraints remain unresolved; user assembly does not change fabricated geometry |
| Partial population / Pico excluded | Stencil apertures only for selected SMT parts; none for unselected/THT pads [C] | Compatible with user-installed Pico; do not select U3 for factory assembly |
| Exact paste apertures | JLC generates optimized apertures; custom requests accepted through remarks [C] | Blanket no-automatic-change control conflicts with default workflow; review specific necessary exceptions |
| Non-Pico manual parts / hidden PJ fill | Mixed SMT/THT supported; published pages describe both wave and manual routes [B,E] | Must confirm exact route for hand-only parts; no reflow/wave/wash on microphones/buzzers. General X-ray capability does not prove ≥75% PJ barrel fill |

### Assembly tier and process details

Standard PCBA provides SPI and requires rails/fiducials; Economic also offers
AOI/visual inspection but not SPI. Listed reflow temperatures differ: Standard
240±5°C and Economic 255±5°C (not adjustable). These are process inputs, not a
complete time-temperature qualification for every BOM part. Verify profiles and
the carrier R3 two-reflow limit before choosing a tier. [B]

**Standard is the preferred candidate to evaluate**, not a mandatory upgrade or
an adopted quote. Its additional process options do not automatically satisfy
our dimensional controls. Both bare-board sizes fit its listed size range.

The assembly FAQ says parts marked “wave soldering” in the library are assembled
manually, whereas the capability page describes typical THT wave soldering.
Do not infer hand-only/no-wash treatment from a library label. Ask a specific
process question for any acoustic or other manual-only component sent to JLC.
Personalized services show manual and jig-assisted work is possible, but not
that our exact metrology or hidden-fill inspection is included. [D,E]

JLC also publishes package-specific recommended component spacing. These
recommendations cover assembly/inspection/rework, not merely body collision.
Existing collision clearance is not automatically compliance with that table;
a targeted check should use its measurement convention on the actual SMT pairs.
No new layout failure is asserted without that measurement. [F]

## Recommendation and boundary

1. Preferred: perform a focused engineering review of the design-owned hole,
   pose, seating and paste constraints against a standard JLC process envelope.
   Determine which constraints are genuinely necessary, and whether equivalent
   robust fit can be demonstrated with normal production variation. Reverify
   affected mechanical/assembly evidence before any revised release. This may
   simplify procurement without needing a bespoke process promise.
2. Alternative: retain every frozen limit and seek JLC's explicit exact-job
   agreement and pricing for the exceptions. It avoids a design revision but
   may require special inspection or be declined.

Neither action is performed by this literature review. No safety/fit limit was
waived. Pico assembly ownership is recorded, not evidence of completed assembly
or of the equipment/method needed to measure all current controls. Eighty other
manual parts still need an executable owner/process. Stock, quote and later
firmware/physical qualification remain separate.

## Sources and local authority

- [A: Rigid PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities), drilling/outline tables.
- [B: PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities), tier table and THT/inspection FAQs.
- [C: Stencil preparation](https://jlcpcb.com/help/article/smt-stencil-data-prepared-for-smt-orders), updated September 9, 2026.
- [D: Personalized services](https://jlcpcb.com/help/article/jlcpcb-supported-personalized-services), updated September 9, 2026.
- [E: PCBA FAQs](https://jlcpcb.com/help/article/pcb-assembly-faqs), updated September 9, 2026.
- [F: Recommended SMD spacing](https://jlcpcb.com/help/article/minimum-spacing-for-smd-components), updated September 9, 2026.

Release authority: immutable public package `historical/documentation/carrier/instructions/`
`32-assembly-instructions.md`, `40-module-controls.md`, `42-controls.md` read
together. Historical candidate headings in retained control documents do not
override the final assembly instructions incorporating their complete limits.
No independent engineering acceptance was reassessed here.
