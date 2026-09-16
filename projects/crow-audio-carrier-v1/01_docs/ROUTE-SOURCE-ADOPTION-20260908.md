# Root adoption of the partial route-source correction — 2026-09-08

Disposition: source progress adopted for further engineering; NOT ROUTE-READY,
NOT a generated-board approval, DO-NOT-ORDER. The author explicitly relinquished
the exclusive writer lease at 07:05:20Z before root project edits or commits.
Baseline HEAD: `5bd9a0cf86c967822305e45e9d6fdd59cef0fbd4`.

Root fully read the 231-line [terminal report](SOURCE-CORRECTION-20260908-route-source.md),
SHA256 `f85586c6bd13f34ceb645cbbdd1c60a6d8455a6428b1adf82b75960ea63c2f84`,
the complete 210-line ADR0010, source diff, 327-line regression module and
317-line terminal integrity receipt. Earlier in-progress reports were not
treated as terminal authority. The author report and ADR remain unchanged.

## Independently measured source checks

At 07:10:10.773–07:10:16.120Z root ran four bounded, nonmutating source checks,
each with a 120-second deadline and 10-second heartbeat. All completed rc0:

- Integrity: all 29 packet members, all 1167 archived files /118994513 bytes,
  all 407 original census rows and all 50 terminal evidence members rehashed.
  Exactly five authorized source census rows changed; 402 remained identical.
  Seven existing archived paths changed within scope; 1160 remained identical.
  Four new source/report files match the terminal receipt exactly.
- Project tests: 114/114, including all 19 new route-source regressions.
  Native footprint geometry is isolated; no Board is constructed or loaded.
  The existing KiCad PROPERTY_ENUM diagnostic is retained in the full log.
- Existing rules source consumer: 8/8 classes graded, zero failures.
- Existing net-reference consumer: 328/328 resolved, zero ghost/unreached.

Full argv, measured intervals, outputs and hashes are retained under
`06_build/verification/route-source-root-20260908/`. Root check-index SHA256:
`8b15b21311e03f478cfa7f03f537c839bea65e3b2da241ab836c6b0980764fcd`.
The integrity log hash is
`9094f9756532a6a79e3a2cc801d4d014a955853f114089c5c4344833273ed764`;
the test log hash is
`00d9860f082bc117b53985d80f5fe331096f8a19815faf61393febfdea73c23c`.
The author terminal receipt hash remains
`28cbfa012876bbb020b7e1d24474edb2f50856b1a0f2cf13ff587ff12d259f54`.

M-BEACON separately passed 2/2 carrier/parent beacons, neither claiming a seal.
The authored working diff passed whitespace checking. The full staged diff
returned rc2 only for two trailing-whitespace lines (57 and61) in the preserved
public JLC HTML. Those raw source bytes are not reformatted; no full-staged
whitespace PASS is claimed.

Root explicitly reviewed and admits only these exact placement exceptions:
C_LDO_A [90.6,70,180] to [89.8,70,180]; C_VDDA1_4U7
[87.35,68.7,180] to [87.45,68.4,180]; C_VDDA2_4U7
[87.35,71.3,180] to [87.45,71.6,180]. The initial guard is preserved; before
its first terminal execution, the reviewed guard was parameterized for only
these three before/after pairs. All other placement subtrees, repeat banks,
model bindings, captions, global fabrication rules and board datums remain exact.
The durable source geometry test rechecks moved courtyards, forward/reverse
foreign-pad interference and every source seed against foreign pads and seeds.

Native identities/topology, all dossier identity/pin/rating/model fields and
all preserved generated/checkpoint/review bytes remain unchanged. The only
parts-notes edit corrects the obsolete statement about nonzero FILTxN returns.
This observation precedes root's subsequent beacon/journal update below this
adoption boundary; that metadata update is not an author integrity discrepancy.

## Engineering disposition and limits

Adopt the exact class/wave/owner partition, paired vias, public physical stack,
common second inner GND reference, explicit digital paths and west-ADC seed
sub-batch. The three pose changes have a demonstrated local routing cause and
preserve all existing proximity limits. No component or net topology changes.

INHERITED from the rehashed author geometry evidence: H3c 567 comparisons with
zero conflicts, including bulk entries, vias/holes and cap proximity. Root's
114-test rerun independently checks the durable subset; it does not rebrand
all 567 comparisons as a fresh generated/native DRC result. The rejected H1,
H2, H3a and four-clock candidate remain evidence, not adopted geometry.

The 2.5 A bulk bound is preserved. A scoped 0.18 mm short leaf is not a general
2.5 A route. Actual branch topology, fault/thermal behavior, ground-plane fill,
EP cooling and final same-bound width/extent measurement remain mandatory.
The existing wave guard is not automatically a final import/stitch guard.
Nominal 0.36 mm digital width remains an impedance hypothesis. Root's separate
numerical probes in `/tmp/carrier-atlc-20260908.e4HHeV/OBSERVATIONS.md` rejected
unphysical open-edge results; finite grounded-box masked/pour calculations are
not sufficiently converged or fabrication-bound to claim actual 50 ohm closure.
Those scratch probes did not change the adopted source or its acceptance scope.

Next source pass: remaining four U_CLK escapes and ADC MCLK/BCLK/FSYNC/TDM
launches, with exact partial/complete ownership and bounded narrow geometry.
Other ADC supply/filter/ground launches, true BUCK/LDO series exits versus
low-current IC taps, thermal returns and realized SI remain separately owed.
Use a fresh bounded source handoff under the lifecycle backtrack procedure;
do not replay producers just to rediscover already identified source defects.

No Board generation/load/save, conductor, checkpoint retirement, route/prep,
fabrication, release, tag or push occurred in this adoption. The old saved PCB
remains stale and unaccepted. TOP77, first-power 0.20 A HOLD, physical/service,
sourcing/allocation and publication limits remain unchanged. Both child seals
and a fresh exact-base/head P-PUBLISH PASS are required before a main push.
