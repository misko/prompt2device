# TMUX process and native parity source repairs

These changes repair source and shared tools after the two rejected P1 attempts. They do not create or accept a new Crow placement, reset the attempt budget, or establish order readiness.

## Exact TMUX center-via profile

SOL implementation `28954702cbbe9c45491d3332667475157030b361`, adopted as `992b5c4c`, binds the eight U_ISO1–8 TMUX4827YBHR B2/pad5 GND locations to the retained coupon and native footprint hashes. Its native rules permit only the qualified 0.35/0.20 mm filled-and-capped via and the exact B2 neighbor relationships. Ordinary board minima remain 0.45 mm via diameter and 0.13 mm annulus. Both full and reuse conductors regenerate the scoped rules after generic rules.

The early working hypothesis that KiCad's board minima had to be lowered was incorrect: a native fixture with the actual scoped rule proved local overrides work. That implementation was removed before adoption. The final fixture demonstrates that removing the local override rejects B2 and that an extra ordinary 0.35/0.20 via remains rejected. Seven profile tests pass independently and in root; the reviewer also passes all 16 existing via-process tests. Source review: `08_reviews/2026-09-23_tmux-profile-code_terra_source.md`.

This closes only the source representation of the B2 process decision. The separate non-B2 TMUX pad gaps versus power-net clearances, DMQ regulator and USB hole clearances, actual board DRC, and existing order-time process acceptance remain open.

## Native schematic/PCB parity bridge

SOL implementation `7407a42e2add4b30951f486f06be005c6327be86`, adopted as `6d3ff043`, shares exact dossier pin-alias authority between native schematic and board exporters. J_USB's numeric source ports export as the physical A/B/SH pad names, preserving port functions, connections and no-connects. Q_IN remains the documented five physical lands. Both schematic emitter modes and the board exporter use the exact dossier Datasheet field, replacing stale library metadata.

The six focused tests include actual KiCad schematic-parity checks in grid and layout modes and rejection of missing unused contacts, incompatible aliases and invalid identity authority. Independent Terra source review passes; P-PINMAP passes 8/8. Root's complete-workspace converter suite passes 63/63, including 22 intentional bad fixtures. Sparse author-worktree failures were missing archived fixtures, and are not suppressed. Root focused native parity tests also pass 6/6. Root board-generator compatibility passes 83/83, including 48 intentional bad fixtures. The reader-contract follow-up `0a02e314` (root `ba20d170`) truthfully points alias fields to the shared helper; root schema audit passes 992/992. The existing pinned-floor test separately found a stale 827-row floor against 874 measured proven rows; the floor is raised monotonically to 874, never lowered.

Source review: `08_reviews/2026-09-23_native-parity-code_terra_source.md`. Diagnosis: `2026-09-23-native-parity-owner-sol.md`. The previous Crow board's 45 parity findings remain historical failures until canonical regeneration and independent review verify the new outputs.

## Next source work

The public-only regulator investigation identifies TLV62569PDDCR as a package/stock candidate, not an adopted replacement. The subsequent SOL electrical screen rejects direct TLV62569 substitution on all three rails. A closer TPS62A02-family candidate remains under investigation; power-stage values, sequencing and thermal constraints must be settled before any substitution. See `2026-09-23-dmq-resolution-options-terra.md`. The 22 unresolved model files, full model registration, support-island placement, USB clearance and connector physical evidence are still owed. Canonical schematic reviews are stale and must be refreshed against the coherent final source bundle before placement campaign reassessment.

## Completed electrical-screen follow-up

See `2026-09-23-regulator-replacement-electrical-screen-sol.md`: direct TLV62569 substitution fails. Checking packing suffixes found TPS62822DLCR / C473385 with 1,979 public units and TPS62823DLCR / C2693497 with 7,232. These supersede the initial DLCT-only stock conclusion and prioritize the closer DLC family for redesign investigation. No substitution is adopted; new pin mapping, capacitor/rail margins, sequencing and hot thermal evidence remain owed. Raw public inputs are retained locally under `06_build/verification/regulator-replacement-public-screen/`.
