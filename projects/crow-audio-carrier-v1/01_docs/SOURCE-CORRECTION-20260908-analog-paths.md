# Executable analog path intent — 2026-09-08

ROOT continued from clean6b31017090831965530a32c24618cbaecbffa0b8 in the
dedicated development worktree. The previous turn was progress: the ADC
fanout correction was committed. This turn adds executable routing intent and
a conditional resistance screen; it does not certify a routed PCB.

## Source measurements

13:14:20Z: isolated native footprints resolve24 P/N section groups,48 nets,
176 endpoints and128 paths after the buffers. All section endpoints equal the
native netlist's complete pad sets. The main ADC-section octilinear P/N floor
spreads are1.707107,1.707107,0.121320,1.292893,1.292893,1.292893,1.121320 and
1.707107mm. Seven exceed the adopted1mm section target, so deliberate
lengthening is required; changing router effort alone is not the mechanism.
These are source pad-center floors, not saved routed lengths or a feasibility
proof. Some shunt branches also need adjustment.

ADR0019 adds24 exact `length_match` groups, preserving the two old digital
groups. All128 analog paths have explicit physical endpoints. The analog KRT
wave has24 paired-net matching groups at0.50mm inventory tolerance; the
independent saved endpoint gate retains its1mm path ceiling and off-path
rejection. Inventory matching is not substituted for path matching.

The new one-board adapter makes the0.5ohm signal-track requirement reachable
through an explicit nominal-copper/average-plating model with2x engineering
reserve. It charges every post-buffer branch and ordinary via, and refuses
unmeasured nets, malformed/unsupported geometry, underwidth tracks or analog
pours. It keeps pad spreading, solder and component terms explicit and always
reports physical DCR as UNVERIFIED. See ADR0019 for primary sources and model
limits; source availability is not fabrication qualification.

## Validation and negative controls

- Initial11-test direct run:7 pass and4 fail in a fixture census, before any
  geometry/model verdict. The fixture's broad ADC-name match included the
  reset net. The same uncorrected bytes were immediately rerun with the bounded
  runner and full log retained:13:23:08Z rc1,4 failures. The corrected fixture
  selects exact channels and supplies the native reader's leading newline;
  no production criterion is relaxed.
- 13:23:49Z:11/11 new tests PASS. Coverage includes native swapped pins,
  missing/extra leaves, absent router groups, real shared endpoint skew and
  off-path rejection, width/layer/measurement failures, long inventory, arc
  length, copper thickness and via barrel arithmetic. Both conductors enforce
  the new source and saved-copper checks.
- 13:27:00Z: full185/185 source tests PASS,0 failures/errors/skips, source
  hashes unchanged across execution. Shared-runner rc0,64.291655s, no timeout.
  Full log SHA256:
  `47eb64d0f564e414871832284783dadf6a36f733be92a73d45ef6d4fb5f9bebc`.
  The actual source CLI reports24 groups/48 nets/176 pads/128 paths. The real
  octilinear consumer accepts all24 declarations with the explicit recipe;
  this is not routing acceptance. Both `bash -n` driver checks pass.
- 13:29:23Z: the saved-board CLI correctly refuses the unchanged old/unrouted
  board with rc2/INCOMPLETE:0/138 total digital+analog paths measured and26
  unreached groups. It does not run the resistance model on absent copper.
  Board SHA remains
  `72f4b136f2c5477167b06861b2636e48be955a6500a27cac867bd267cb4f0abb`.

## Scope and next action

All source seed copper,299 part poses, library geometry,88 seed banks/218
segments/20 ordinary plus9 thermal vias, current/fabrication limits, keepouts,
continuous inner-plane intent and two digital path groups remain unchanged.
Historical tests restore only the exact new matching keys when comparing
earlier temporal snapshots; the new tests own that narrow additive delta.
The source contract gains one documented adapter row, not a new policy waiver.

Full attempt logs and source diagnostics live in
`06_build/tmp/analog-paths-20260908`; its inventory is written last. The
stale board was read as text only, never loaded/saved as a BOARD. No producer,
prep/import, routed candidate, review, checkpoint or release was written.

Next is fresh governed generation/admission and exact-subject schematic then
placement review, followed by real routing. Do not add source-only rituals in
place of this next producer boundary. Analog matching/DCR still need actual
saved-copper results, and physical qualification remains separate. All
TOP77/0.20A, sourcing/order, first-article and both-child-seals/fresh exact-base/
head P-PUBLISH holds remain. No account,upload,purchase,main push,release tag
or energization occurred. Existing broad structure debt remains unwaived.
