# Composition-schema source-contract review

**PASS.** The adopted `7d674d45` move and the pending three-file contract/audit diff are truthful source-contract corrections. No producer, PCB, or generated-artifact claim is made.

`7d674d45` removes the advisory `footprint_proof` subtree from the USB4215 dossier and retains every factual item verbatim in the existing governed `layout.notes`: drawing/view/tolerance, 16 logical contacts on 12 lands, pitch and land dimensions, all four shell-slot and land dimensions, annulus/gap values, and zero locating pegs. The moved text explicitly remains descriptive human source review rather than machine-graded proof, DFM, or assembly acceptance. Its additional mouth-to-edge/installed-fit language correctly remains owed.

The two pending contract rows name real readers. `generate_board_generic.py:1935` reads each `placement.forbid[].rect`, applies the optional `margin` default of 0.3 mm, and rejects a candidate floater position when its centered footprint bounding-box proxy overlaps the expanded rectangle. `legalize()` skips pinned and `placement.keep` references, so the disclosed anchored/kept bypass is accurate. The implementation comment confirms these Python-only exclusion rectangles do not emit native board/copper keepout geometry. These limits are now stated directly in both the project and template contracts.

The pending audit change raises `PROVEN_FLOOR` from 874 to 876 with a matching explanation for the two newly declared, already-existing readers. This is a coverage ratchet only; it does not alter the parser or placement behavior. The pending tracked changes are limited to the project contract, template contract, and reader-audit floor/comment. An unrelated untracked `03_tscircuit/dist/` directory is outside this review.

This result is a source-contract/provenance finding only. It does not claim full composition, pre-route, physical, fabrication, assembly, or published-release acceptance.
