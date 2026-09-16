# Root regulator source adoption — 2026-09-08

Adopt H3 as a source milestone for further engineering. NOT ROUTE-READY;
DO-NOT-ORDER. The author explicitly relinquished the sole writer lease at
08:50:11Z. Root made no project edits during that lease. Administrative base
is1602a507cc20f63a1980b6605784c918b5ece10c; preceding source adoption isa8e8ac31.

Root read the complete125-line terminal report,141-line ADR0012, complete
new regulator tests, changed existing tests and engineering source diff.
The author report and proposed ADR remain immutable; this record supplies
root's source disposition, not an independent layout-review verdict.

Report SHA2565631449996329b10f0b7071be835727488db01ab626dd14b1b0a83c26414b0db.
ADR SHA25685d6449603e4ede91037df2a18994897722189c5accd0178ef921eaeb2a11b2b.

## Root verification

Five bounded checks ran08:51:18.417091–08:51:36.894525Z, each with a120-second
deadline and10-second heartbeat. All completed rc0 without timeout/cancellation.
Exact commands, full logs and output hashes are preserved in
`06_build/verification/regulator-source-root-20260908/`.

- Integrity:22 packet members, all1,412 archived files/131,740,120 bytes,
  all410 census rows and1,490 author evidence members rehashed. The four
  inventory/self-run exclusions were separately rehashed by root as well.
  Exactly eight permitted existing changes and three new durable files;
  1,404 existing subjects and405 census rows unchanged.
- Project suite:134/134 tests pass, including ten new regulator regressions.
  Existing KiCad enum diagnostics and parser ResourceWarnings remain in logs.
- Fresh source-diagnostic invocation:44,882 regulator and19,239 digital native
  shape comparisons, zero reported geometry/quiet-return/placement findings.
  This reruns project methods; it is NOT an independent PCB DRC implementation.
- Existing source consumers:8/8 classes and339/339 net references pass.
- Shadow preparation authority verifies162 generic nets, two complete
  deterministic nets, common GND and40 intentional NC nets. No Board is opened.

After root metadata edits, the bounded08:56:22Z M-BEACON check grades both
carrier and parent beacons2/2, rc0. Neither claims a completed seal. The
terminal integrity invocation above binds the pre-root-metadata handback;
its exact dirty-file/HEAD assertions are not intended for post-commit replay.

Authored source/docs pass staged whitespace checking. The unfiltered staged
check returns rc2 only for preserved raw bytes: trailing blank lines in ADC
h1-measured.log and regulator hypothesis-1.log, and seven blank context lines
in regulator source.diff. All other staged files pass the same check. These
three forensic artifacts remain byte-exact; no diagnostic hash is normalized.

Root check-index SHA2565098747c6e172ac801cc62e628605695df70de2b32d3c01dd334287146b64d9c.
Root native result SHA2568914491cf5ea6696f4d1e48936739020e11c9e3525269b5853acae64dbb283f7.
Root test log SHA25691808e396515854f08b38e9706be80e48c91b2ac3f60caa0da74d71668bafca7.
Author inventory SHA2563bb002ce92111e6b3536c6929dc6443a8a8151db5e0a5ba9a72afcffb60652f0.
Author terminal integrity SHA2562f5996b90bb777d54ce315ad59c24d660025b6a42c34c4b902b2e406b0702f5e.

## Adopted scope and limits

One C_LDO_OUT move to[61,66.5,180];15 new banks/37 F.Cu primitives and six
0.50/0.20 mm off-pad ground vias. Native in-pad off-centre starts permit
1.10 mm main IN/OUT,0.40 mm companion-pin and0.75 mm SW exits, with ordinary
0.25 mm clearance. Exact local width areas confine whole rounded primitives.
Quiet NR/lower-feedback/GND4 returns are reserved from top pour/via bypass;
SS6 reaches EP, separate EP drops avoid touching that quiet tree before EP,
and local power-cap grounds have an explicit1.20 mm return. Inner GND is unsplit.

All17 previous banks,299 component identities/868 memberships/205 nets,
electrical/model bindings, stackup,11 connector datums and other poses remain
unchanged. Dossier additions affect only layout_refs/gotchas. No class or
clearance floor changes. BUCK_SW retains its real bootstrap branch/generic owner.
The old ADC5.05 mm/eight-item subtotal stays exact; the additive3V3 guard is
7.770061 mm/13 items. Full2.5 A branch accounting does not assume equal sharing.

These are source reservations, not final filled topology. Quiet-mask coverage
uses5 um centreline sampling with radial margins; later generic/stitch copper
must not bypass the intended return. Nominal-copper resistance estimates do
not establish temperature rise, fault duration, barrel ampacity or achieved
thermal resistance. Physical qualification and first-power0.20 A HOLD remain.

## Preserved next-work candidates

Root ADC probes made during the lease are retained byte-for-byte under
`06_build/tmp/adc-source-root-probes-20260908/`. Read OBSERVATIONS.md and
FILTER-OBSERVATIONS.md, including rejected/setup attempts. They use frozen
a8e8ac31, deliberately EXCLUDING this regulator batch, and are NOT adopted.
East H3 clears27,207 declared source checks; the combined mirrored filter
candidate clears52,916. A separate56-pair native graph includes every actual
FILT positive pad and proves both nets remain PARTIAL, not complete owners.

Next source work must rederive these against the adopted regulator source,
handle exact F/B width/extent and current/return obligations, and check the
remaining ADC control/ground/VMID and other low-current IC exits. Whole-board
generation, fresh exact-hash reviews, routing, post-fill/thermal/SI checks and
release verification remain owed. Existing generated/checkpoint/review bytes
are unchanged, stale and unaccepted; no old review is rebound to new source.

Preserved evidence indexes distinguish committed diagnostic records from the
large local forensic archive; archive copies were rehashed, not duplicated
into this source commit. Repository PCB/KiCad skills require this source-only
boundary. No external access or private JLC result is needed for this work.
No release/tag/push/order/power-up occurred. Both child seals and a fresh
exact-base/head P-PUBLISH PASS remain prerequisites for main publication.
