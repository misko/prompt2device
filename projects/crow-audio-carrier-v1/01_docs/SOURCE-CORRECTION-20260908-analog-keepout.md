# Analog routing keepout correction — 2026-09-08

ADR0017 changes only the virtual analog/reference routing rectangles. ROOT is
author/operator, not an independent reviewer. Baseline is clean commit
7415aed46374628a5866acaf0bf94ea8f03bd380. The before inventory covers 1,406
tracked carrier files / 105,209,940 bytes; Git retains that recoverable state.
Ignored transients are outside the census.

## Measured results

- 12:11:20Z: baseline source screen finds 307 individual launch witnesses
  among 320 analog copper pads, with 3,364,801 comparisons. The screen uses
  0.20 mm-wide, 1 mm straight launches at 48 directions, sampled within the
  actual pad. It checks foreign native copper, source segments, ordinary and
  thermal vias, drills, physical keepouts, selected User.3 masks and explicit
  scoped clearances. It is not a simultaneous route solution or P-LAND run.
- Native mask intersection census identifies eight trapped pads:
  R_ADC_PD1N.1, R_ADC_PD1P.1, U_ISO1.1/.2/.5/.6, FB_OPA.2 and C_OPA_BULK.1.
- 12:16:08Z: one keepout geometry candidate improves the analog screen to
  313/320 witnesses. No ADC fanout geometry candidate was attempted.
- 12:34:02Z: six focused source tests PASS. All 376 pads on the 103 analog
  and quiet-reference nets clear the revised mask. All seven BUCK_SW/BST
  copper items retain the chosen 3 mm halo; tightest measured margin 3.3 mm.
  The actual pre-fix mask reproduces all eight hits. Top-edge-only repair
  leaves both quiet-supply hits, and blanket removal fails hot-copper coverage.
- 12:35:11Z: adopted live source reproduces 313/320 witnesses and 3,092,994
  comparisons. The actual KRT parser reads all three closed User.3 rectangles
  from an isolated text fixture and none on User.2. This confirms parser
  semantics, not generated route-prep identity.
- 12:35:46Z: full source suite 168/168 PASS, zero failures/errors/skips.
  All tested source hashes are unchanged across execution. The terminal
  shared-runner receipt reports rc0, no timeout, 53.308 seconds; its full
  log SHA256 is
  `88f8a3edc5217fcf87d641c5e44b5f30b663406e8f75502342ef3f45b67d5a9d`.
- 12:39:09Z: preservation census finds exactly five changed existing carrier
  files, 1,401 unchanged, three new carrier files and two parent status/journal
  changes. All 30 protected generated/review/release files remain unchanged.
  Both live beacons pass the shared checker; neither claims a completed seal.
- 12:39:59Z: the unchanged structure checker reports the same 18 inherited
  findings over the baseline/current project path sets. All 38 governing
  contracts remain exact. No new finding is introduced and no debt ceiling
  is raised; this scoped comparison is not a whole-repository audit PASS.

The unresolved source-screen rows are U_ADC.15, .16, .19, .22, .42, .45 and
.46. Existing FILT/ground/strap/reset fanout participates in their rejected
launches. A missing sampled straight launch is not proof that a bent route
or legal layer transition is impossible. Keep these diagnostic findings
visible during placement/pilot routing; do not silently waive them or invent
a requirement for a completed filled board before generating its candidate.

## Attempts and scope

Raw scripts, JSON and logs live in the bounded source-backtrack evidence
directory `06_build/tmp/analog-keepout-20260908`. The first baseline attempt
had a shape-argument programming error (rc1). Its corrected naive retry
timed out at 120 seconds (rc124). The successful version hoists candidate-only
scope intersections without changing geometry, sample set or clearances.
Both failed attempts remain evidence, not geometric verdicts.

The source inspection confirms the owning P-LAND checker also defaults to
1 mm reach but grades neighbouring pad polygons, not this screen's complete
seed-copper and selected-mask obstacle set. No owning saved-board P-LAND,
DRC, route, matched-length, DCR, EMI or thermal acceptance is claimed here.

All 72 source banks, 201 straight primitives, 20 ordinary seed vias, nine
protected ADC thermal vias, 299 part poses, footprint/paste identities,
electrical topology, planes, widths, clearance scopes and current limits
are unchanged. Only the keepout rectangles and their regression ownership
change; no BOARD was constructed, loaded or saved in this correction.

Next: resolve remaining analog route intent, then fresh governed generation,
admission/reviews and actual routing. Carrier remains stale/unrouted/unreleased;
pod sourcing hold and parent commissioning hold are inherited, not regraded.
The broad structure audit's existing failure is not waived. No account,
upload, purchase, release tag, main push or energization occurred. TOP77,
the 0.20 A first-power HOLD, and both child seals plus fresh exact-base/head
P-PUBLISH PASS before main remain required.
