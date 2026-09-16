# Root adoption of bounded digital launches — 2026-09-08

Disposition: adopt this source milestone for further engineering. NOT
ROUTE-READY, not generated-board or SI acceptance, DO-NOT-ORDER. The author
explicitly relinquished the exclusive writer lease at 07:57:21Z; root made
no project edits or commits before that handback. Baseline HEAD is
05a1eb52b5ea8bdc6bb38dccbdf3008ac38743ac.

Root fully read the terminal report, ADR0011, all 334 lines of the new tests,
the existing-test modifications and the complete engineering source diff.
Report SHA256:
6271b387a33dd4056496e0538aeb53a556977bd52c2e65f769b1d51feb7f42d4.
ADR0011 SHA256:
78e271483f33f482f937a04d32af6fb40fa99975e201bdd5c2110fe309105e25.
Both author documents remain immutable; this record supplies root disposition.

## Measured root verification

Five bounded checks ran 07:59:25.001951–07:59:39.867232Z. Each had a
120-second deadline and 10-second heartbeat; all completed rc0 without timeout
or cancellation. Outputs and exact argv are preserved under
`06_build/verification/digital-source-root-20260908/`.

- Integrity: all 20 packet members, 1,289 archived files / 127,635,305 bytes,
  409 census rows and 71 terminal evidence members rehashed. Exactly six
  existing files and three new source/doc files matched the author's terminal
  receipt; 1,283 existing files and 406 census rows remained identical.
- Project suite: 124/124 tests passed, including ten digital regressions.
  Existing KiCad property-enum and parser ResourceWarning messages remain in
  the raw log; rc0 is not a warning-free claim.
- Fresh source measurement rerun: 18 new primitives, 18,357 native-shape
  checks with zero findings; all eight declared launch pins reached. The
  other 19 digital endpoints retain full-width 0.36/0.25 mm, 1 mm witnesses.
  These are project source methods rerun by root, not an independent native
  PCB DRC implementation or routing acceptance.
- Rules source consumer: 8/8 classes, zero failures.
- Net-reference consumer: 334/334 resolved, zero ghost or unreached names.

Root check-index SHA256:
94bb9d9f11366b95db617135ee638d50ab128ff1df73225fc6db95fcf5f5b265.
Fresh source-measurement JSON SHA256:
e230a837a72cdadd5ae68b0c501a5669af0cc6edf3dca47350d20ebd0526a571.
Root test-log SHA256:
73f1e6e702511e8af7c0d06e6056a6c5c493e633f6df8d869381de9279a8f3a5.
Author evidence-index SHA256:
0a2ef16b4535792192082d155d65d02d73b59ca7df56336b5c842e221fe971fc.
Author terminal-integrity SHA256:
b7266c885b06588e689a0c2cb167a8b921f2aeaa4f71a7938ca2396638d4e198.

## Engineering disposition

Adopt eight F.Cu launch banks: six short 0.18 mm banks and two off-centre ADC
corner banks that retain full 0.36 mm width. No digital vias or placement
changes. Four small named width scopes and six clearance scopes leave the
ordinary twelve-net clock class at 0.36/0.25 mm. Tests bound complete capsule
containment and exact per-net lengths; item overlap alone is insufficient.

FSYNC_BUF's one 1.40 mm segment reaches both native pads, so it is completely
owned by preparation and excluded from the generic clock wave. The remaining
seven banks are partial. The partition remains exact over 205 nets: 162 generic,
two deterministic, one common ground and 40 intentional NCs. All 299 fitted
identities, 868 pin memberships, placement/connector datums, previous nine
west-ADC banks, power-wave parameters and global fabrication rules are exact.

The existing many-pad power ownership preflight does not reject duplicate
ownership of a two-pad digital net. The shadow authority compiler does, and
the regression explicitly demonstrates both facts. No shared checker changed.
The clock wave guard is not a final post-import/stitch guard, and does not
visit excluded FSYNC_BUF. Final geometry must remeasure the same bounds,
including that net's exact 1.40 mm / one-item extent and all real branches.
No local width allocation is claimed as a solved impedance or delay limit.

## Next source work and retained probes

Root independently screened the regulator exits and a one-capacitor move
while the digital author held the lease. Those scratch probes are preserved
unchanged under `06_build/tmp/power-source-root-probes-20260908/`; read both
OBSERVATIONS.md and CAP-AND-CELL-OBSERVATIONS.md with their explicit limits.
Case A conflicts with C_RAW_HOLD; Case B moves only C_LDO_OUT to [61,66.5,180]
and clears the declared placement screen. Case C's extra R_LDO_TOP move is
unnecessary. The subsequent 34-segment/six-via candidate clears 18,194 source
geometry checks. NONE of these power coordinates has been adopted into source.

A bounded power-source continuation must independently rederive the candidate
against current digital source, establish exact owner/width scopes and current
path limits, address quiet ground-pour bypass/thermal return strategy, and
retain native geometry/negative tests. Other ADC supply/filter/ground exits,
low-current branches and actual digital SI remain owed before combined
generation and fresh exact-hash reviews. Do not replay producers merely to
rediscover known source defects.

No Board generation/load/save, conductor, checkpoint retirement, prep/router,
fabrication, release, tag or push occurred. All old generated/checkpoint/review
bytes remain stale and unaccepted. The unchanged 2.5 A transient bound,
first-power 0.20 A HOLD, TOP77, physical/service and sourcing/allocation limits
remain. Both child seals and a fresh exact-base/head P-PUBLISH PASS are still
required before pushing main. Repository PCB/KiCad skills caused this explicit
source-only adoption and bounded handoff, not a new external-information hold.
