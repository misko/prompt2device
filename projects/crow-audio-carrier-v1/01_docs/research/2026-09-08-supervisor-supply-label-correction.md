# Supervisor supply-label correction

Status: **SCHEMATIC ACCEPTED / 204 TESTS PASS / FRESH PLACEMENT HANDOFF / DO-NOT-ORDER**.

The fresh review of source commit77b5d69e completed at17:19:47Z with
seven PASS/one FAIL checklist items. SR-001 is a P2 presentation defect:
the U_AUDIO supply wire crosses the `5V_LDO_HOLD` lettering on page4.
The actual review is preserved verbatim in
`08_reviews/2026-09-08_77b5d69e_fresh_schematic_render.md`, SHA-256
77b8a33b3496b8755c9bcfe2b391cf3b1c9a3e4e963ae0438695a442267df741.
Root reopened460/460 packet files before transporting the actual negative
verdict; this is admissible review evidence, not schematic acceptance.

## Source repair and regression

`03_tscircuit/src/schematic_presentation.tsx` moves only U_AUDIO's supply
label anchor from(-2.8,-5) to(-3.8,-3.5), above the PWR_EN elbow. The explicit
electrical connections, all component poses, PCB floorplan, part identities,
route seeds and design rules are unchanged. Generated files were not edited.

The existing foreign-net ink screen passed the defective old rendering because
it excludes every same-net wire. The additional project-local regression
checks all four held-rail labels on the supervisor sheet against every sheet
wire, regardless of electrical ownership. It permits only an actual anchor
endpoint arriving from behind or perpendicular, never a forward or mid-span
crossing through the plate. Good and hostile fixtures pin these distinctions.
This is a bounded presentation regression, not a replacement for independent
PDF review or a new production gate. Other pages' general same-net ink and
unmodeled glyph shapes still require visual inspection.

MEASURED on the exact failed subject:11 tests,10 PASS/1 FAIL, detecting both
U_AUDIO label/trace139 and label/trace572 intersections. Red logSHA
d5ac333f52a9852bc92d576d3811ffd75012ccf7b220fc05b54db12c651286f7.
After source regeneration:11/11 PASS; green logSHA
5f8ebb534ed2ba033e4df30c38fef8ed417c01fc4f41fc4e8c24cd687e582a04.
Complete source suite: **204/204 PASS**,17:30:45–17:31:58Z,72.782s,rc0;
logSHA801e64245c8f330fdf3b20c1bbd1cfefaf33ceab63b9f0754b6546de7548c9ab.

## Exact regenerated subject

MEASURED full conductor17:29:13–17:30:27Z,73.376s,rc2 at its planned
prelayout pause. Electrical closure9/9 and selection readiness2/2 passed;
the new request covers52 exact codes and the new census pins421 inputs.
Before editing,517 files/89427659 bytes were archived/rehashed under
`06_build/verification/supervisor-plate-correction-20260908-77b5d69e/prior/`.
Eight checkpoint/catalog files were moved recoverably only after all old
input hashes matched. Archive manifestSHA
8c56f8cc7d890aaf800c67efa08eec37c6c898657e344602b1d03e6d62aa2e2a.

Independent native parser comparison:302 component identities/values/footprints
and877 pin-net entries across207 nets are identical. All421 old checkpoint
inputs were compared; only the presentation source and six generated inputs
changed. Floorplan and routing authority did not change. Exact current hashes:

- Circuit JSON:e1a80308058dbe73fecbd238f3989557ff11a6dd89c4ebe073ddeb6a51cc5a94.
- Human PDF:81cb9240d5dab6c6b41b0b045c1d06c584455e5f640a5097636ae185074a4636.
- Native SCH:aba5641a2b66e050212a4c99825e6dd9a609fb59ffb11cb97c912260d03aa1aa.
- Native NET:ef3246286055837de35c78c2ca3b70ef886a9387358ea070a06e0df4d45993bf.
- Normalized review netlist:83b1c3510e0b08d9d4f390fac59403374073615f7bfcc8f6361308b51ce84c73.
- Identity comparison log:717387d345bbabb17786642493bbbc600deed0bb91c0ad47ae520d4c5993b49f.

The new request-derived public probe is byte-identical to the prior probe,
and all52 request rows/designators/quantities and build quantity5 match.
The actual public catalog JSON/TXT were copied verbatim with their original
17:09:22Z observation time, not restamped or re-queried. The owning freshness
and exact-request checks accept this within24h. No allocation or price claim.

MEASURED public continuation17:31:58–17:32:01Z,3.074s,rc1 at PR-REVIEW:
prelayout4/4, input census421/421, ERC0 errors/2100 warnings, schematic
checkpoint7/7. Topology remains current. The old visual witness is explicitly
DEFECTIVE and binds the old PDF, so it cannot authorize the new subject.
Full producer logSHA905fde2354f98a82e997f7c45f924e999215dd09f50dce5fdb3cbc56213617bd;
resume logSHAb93ed994597941aa83e1228300dcf103648561e31797bd6884db232cb1c3f335.

## Next boundary

Commit this exact corrected source/schematic and commission a fresh all19-page
visual lens. Preserve the unchanged topology witness. After actual acceptance,
use a fresh placement worker and checkpoint-aware resume. The current PCB
still has the old capacitor pose: generation, placement verification, routing,
silk cleanup and carrier release remain owed. Pod release is untouched.
All physical qualification, first-power0.20A/TOP77 and ordering/publication
holds remain. No final PCB/release or order-readiness claim is made here.

## Fresh exact-subject acceptance

Source164b3208a49ef5d3bed4b47867f111e2c12e7dda was frozen before commission.
The fresh read-only reviewer inspected all19 pages,302 reference/page owners,
41 intentional NC pins and7 polarized capacitors. Five native-PDF enlargements
resolved wire-crossing suspects against the native netlist. All8 checklist
rows PASS; no P0/P1/P2 findings. Actual completion17:48:53Z, before the
17:56:03Z deadline. Root reverified460/460 input files and all subject hashes
before recording the returned review verbatim, including Markdown hard breaks.
ReviewSHAad36529e80b9996ab74fad1173e748915e40d16e67f233f0faf3f74fd8770dfe;
dated review `08_reviews/2026-09-08_164b3208_fresh_schematic_render.md`.
The former negative witness remains preserved, not rewritten.

MEASURED owning PR-REVIEW **2/2 PASS**,17:54:13Z,rc0. The existing independent
topology review remains current on unchanged normalized electrical/part/rule
identity. Acceptance logSHA
36e071ebba917d2713c01d14bc7b77b30d5b6e51741427b7e8d24cfa167f5a64.
The new review is accepted only for schematic readability, never realized PCB
placement, routing, manufacturing, sourcing allocation or physical qualification.

Next: commit this green schematic boundary, generate/validate a fresh compact
handoff and exact TaskEnvelope, and relinquish the mechanical continuation to
a fresh worker. One bounded checkpoint-aware resume must promote the accepted
schematic and generate the corrected PCB before any placement claim. Root's
new read-only native-board bypass assertion rejects the old board at the old
pose and1.625mm gap; it must be rerun on the actual generated board afterward.
