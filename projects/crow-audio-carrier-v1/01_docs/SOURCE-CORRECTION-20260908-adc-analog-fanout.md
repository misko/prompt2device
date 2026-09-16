# ADC analog fanout source correction — 2026-09-08

ROOT continued from clean commit28571836bd194c6444240f0d12b7beccae8c2542.
The primary dirty checkout and sealed pod were not used as writer targets.
This is an author-operated source correction, not independent review or PCB
acceptance. ADR0018 owns the decision and its conditional-current accounting.

## Measured candidate sequence

| Candidate | Change tested | ADC individual exits | Native ADC/thermal findings |
|---|---|---:|---:|
| baseline | adopted ADR0017 source | 9/16 inherited from its exact report | not a new run |
| H1,12:44:48Z | two filter-negative drops outward | 11/16 | 0/0 |
| H2,12:46:18Z | longer filter-positive pitch necks, adjust ground vias | 13/16 | 0/0 |
| H3,12:47:59Z | ground bends start after the analog exit corridor | 15/16 | 0/0 |
| H4,12:49:22Z | reset dogleg and outward via | 16/16; whole analog320/320 | 0/0 |
| H5,12:53:52Z | add sixteen simultaneous straight source launches | 16 explicit partial banks | 0/0 |

The five source hypotheses improve on distinct geometry; there was no plateau.
H4's first wrapper failed with nested-string syntax before testing geometry.
H5's first wrapper failed to use the authored default clearance for NC pads.
Their corrected retries retain the same candidate geometry and both failed
logs. No failure or timeout is counted as a geometric verdict.

H4's complete analog screen grades 320 pads / 96 nets with 823,013 native
comparisons. H5 then grades the actual added capsules together: 13,824
pad comparisons, 3,472 seed comparisons (including the new launches against
one another), 464 via-copper, 464 via-drill, 1,776 physical-hole, 64 physical
keepout and 48 virtual-mask comparisons. These 20,112 checks report no finding.
They establish local simultaneous source geometry, not a complete route.

## Adopted source validation

12:59:37Z: full source suite174/174 PASS, zero errors/failures/skips. All
tested source hashes remain unchanged across execution. Shared runner rc0,
61.506998 seconds, no timeout. Full log SHA256:
`5833311696cf12dba1714410db6e7831a8f90552228475924785582094d6481f`.

13:01:45Z: after inserting the actual sixteen stubs, the complete live analog
screen still has320/320 witnesses (837,574 comparisons). The independent ADC
cell screen has130,272 comparisons with no findings; thermal40,156 with no
findings. User.3 still intersects0/376 analog/reference pads and retains all
seven switching-copper items. These remain source-only results.

The actual old filter/reset banks reproduce seven clearance-failing new
launches: ADC15/16/19/22/42/45/46. Missing and crossed launch controls fail.
All sixteen remain partial analog-wave owners; the two filter-negative
returns reach their own drops without joining ADC49 on source F.Cu.

Only `route.yaml` changes executable design geometry. Existing tests are
updated for the exact later delta, not disabled: five previous banks change,
sixty-seven remain exact and sixteen full-width/no-via inputs are added.
All 299 part poses, library footprints/paste, circuit identities, netclasses,
width/clearance areas, continuous inner planes, fabrication limits, protected
thermal fields and current allocations stay unchanged. Other power budgets
stay exact; ADR0018 explicitly records the slightly increased filter-feed
resistance under the previous nominal-copper model.

Raw attempts and diagnostic source are retained under
`06_build/tmp/adc-analog-fanout-20260908`, with a hash inventory written last.
Git retains the recoverable source baseline. No prior file is retired.

Next: finish paired analog path/trace-DCR intent and proceed through fresh
governed generation/admission/reviews and actual routing. Local 1 mm input
stubs do not prove full paired-path matching, DCR, filled return continuity,
noise/THD, impedance, thermal performance or physical fit. Carrier remains
stale/unrouted/unreleased. Pod sourcing and parent commissioning holds are
inherited, not requalified. Existing structure-audit debt remains unwaived.
No account,upload,purchase,main push,release tag or energization occurred;
TOP77/0.20 A and both-child-seals/fresh exact-base/head P-PUBLISH remain owed.
