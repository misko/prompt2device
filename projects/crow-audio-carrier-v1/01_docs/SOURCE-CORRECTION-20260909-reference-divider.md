# Precision reference-divider correction — 2026-09-09

Source regression checkpoint only. No carrier release, native acceptance,
publication, allocation or order. Source base: `8e8a2910`.

## Implemented and measured

ADR0024 changes four external-reference divider resistors to the already-used
RT0603BRD0710KL/C95204, 10k, 0.1 percent, 0603 part. The actual TSX diff is
exactly two template rows expanded into four parts; a mechanical comparison
against the base commit confirms no value, net, capacitor or other source
declaration changed. Existing floorplan anchors and acceptance limits are
unchanged. Source remains 325 components, 923 physical pin occurrences and
228 nets including NCs.

MEASURED software regressions: actual old-source RED produced six failed
subtests (four identities, two low-corner failures) without import/runtime
errors. Corrected focused suite passes 17/17, including full source-native-
library clearance for the larger dividers. Full carrier source suite passes
267/267 in 112.275 seconds, completed 2026-09-09 21:38:10 UTC. Only the test's
explanatory docstring changed after that full run; no executable test or
circuit changed afterward.

The conditional initial/room-temperature DC screen changes from
1.594756–1.686885 V to 1.609283–1.671855 V against the unchanged 1.60–1.70 V
window. This is software arithmetic, not physical measurement or a
hot/lifetime/startup guarantee. Its limits are explicit in
`research/2026-09-09-reference-loading-and-model-authority.md`.
Public exact-code sourcing was checked at six resistors per board, thirty
for five boards; see the dated sourcing observation. This is not a new
Q-2SOURCE composition, whole-board check or authenticated PCBA allocation.

## Evidence and independent judgment

The companion outcome JSON retains actual command results/logs, source hashes,
the exact frozen review envelope, the coordinator's explicit condensation of
the actual review result, and public-model/cache identities. Its SHA256 is
`5587ff73b1ca4699b32ee26e4daa731e1e49b3a6b92b6dafbc5f5ab94a473eac`.

The fresh independent power review covers frozen `8e8a2910`, not the later
precision-divider identities. It reported 38/38 packet files unchanged before
and after review, finishing verification before the deadline. The coordinator
separately reverified 38/38 and the supplemental spoke contract. No canonical
TaskAttempt, execution telemetry or native PR-REVIEW witness was fabricated.

The verdict is INCOMPLETE source protection argument, not a demonstrated
protection failure. Keep OPA2320 as the candidate. First remove or bound
partial-powered analog isolation and reference-output backdrive; the bounded
comparison is in `research/2026-09-09-isolation-source-reassessment.md`.
No isolation replacement is adopted. Correlated restart, actual filter loops
and feed-current duration remain source work; physical timing/thermal/audio
qualification retains its later boundary.

The structural audit's exact FAIL-line set is unchanged against the retained
pre-correction run: 2,891 existing structural violations. The fleet ADR audit
still fails at 38 OWED versus its 37 ceiling; ADR0024 adds no derived
inequality. No ceiling or waiver was relaxed. The uncommitted-source stray
warning is bookkeeping, not engineering acceptance.

## Preserved boundaries and next action

The BRIEF change is only the ADR0024 register row. The investigation's next
decision reflects the completed review, preserving its question, milestones,
four-attempt history, six-attempt cap and one non-improving count. This routine
correction is not a new transient experiment and earns no all-state milestone.

Native board SHA256 remains
`66003462ab2221377fd8ad54fdeabe3097983e496f1fe7b22c345fd7843c3060`.
It is stale and unrouted; the microphone pod is unchanged. After source
admission, use the full conductor and fresh exact native reviews, then finish
placement/routing and release gates. No proprietary model, logged-in vendor
response or new user choice is required for the present source comparison.
DO-NOT-ORDER remains in force.
