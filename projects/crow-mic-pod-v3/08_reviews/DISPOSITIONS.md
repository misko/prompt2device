# Review dispositions — current RJ45 pod placement

| Finding | Original review | Evidence and disposition | State |
|---|---|---|---|
| U1/U2 physical pins | 2026-09-13_a44b769b_independent-analog_pin.md | Fresh primary-figure review:23electrical identities PASS across U1 and U2; group SOUND, not whole-board acceptance. | Accepted for exact current group |
| J1/U3 mounted-side frame | 2026-09-13_a44b769b_independent-interface_pin.md | Original dossier omits native mounted side. U3 reported conditional mirror mismatch is not proof of a board defect. Dedicated extractor source correction and fresh exact dossier review required. | Open — tool evidence owner |
| D1 explicit cathode label | 2026-09-13_a44b769b_independent-diodes_pin.md | Reviewer subsequently clarified that the manufacturer band is clear, no polarity ambiguity was seen, and its literal-label-only criterion exceeded the actual protocol. Original INCOMPLETE report remains immutable; source marking inference will be judged in renewed complete-side review. No physical redesign justified. | Refuted as a literal-label-only blocker; current pin aggregate still owed |
| D2 physical polarity | 2026-09-13_a44b769b_independent-diodes_pin.md | Manufacturer cathode band, native K/A mapping and two separate lead identities PASS. | Accepted for exact current group |

These records do not authorize routing, release or ordering. Earlier dated MicroFit release reviews remain historical. Root retains actual closed delivery and full evidence separately from domain acceptance. FIRST-ARTICLE-ONLY / DO-NOT-ORDER.

Fresh current render review accepted: 2026-09-13_a44b769b_independent_render.md. Current board/r0/rules hashes independently reverified before verbatim canonical adoption. No unresolved nominal render defect; all actual physical fit/assembly/environment obligations remain. Pin aggregate and layout admission are still owed.

Current layout review accepted: 2026-09-13_a44b769b_independent_layout.md, exact native board/r0/rules reverified. Routing follow-through is mandatory:

| Finding | Disposition | Owner | State |
|---|---|---|---|
| L1 C10.2 ground return at(52.12,49) | r0 ground-zone isolation must be restored and measured in saved routed copper. Reviewer measured0.92mm nominal off-pad egress room; no copper was added or route certified. Final0/0/0 gate still required. | Fresh routing/stitch successor | Open, routing completion |
| L2 square ESD elbows | P3 manufacturer-guidance advisory at(50.45,28.36)/(47.65,27.36), current critical paths pass. Assess in final route review; preserve accepted order/width/length authority. No source change approved by a placement advisory. | Route/layout review | Deferred advisory |
| L3 J1/U3 physical fit and assembly | Preserve existing first-article soldering, guide/spring finger, cable/latch/enclosure and bend qualification. Nominal placement SOUND is not manufactured fit. | First-article/mechanical owner | Held |

| POD-20260916-D1-PROSE | 2026-09-16_2685281f_final_redteam_topology.md | Invariant rationale names old 1N4007; executable pins, BOM and primary record are S1M | P2 | confirmed (exact source/dossier and final topology review) | deferred — 01_docs/DEFICIENCIES.md POD-D001; no functional defect |
