# Ground-clearance correction — source-author outcome

Disposition: SOURCE CORRECTION COMPLETE; independent schematic acceptance OWED.
This is an author report, not an independent review, topology acceptance, PCB
admission or release. DO-NOT-ORDER. No physical qualification is claimed.

## Authority and clocks

Worktree: `/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901`.
Actual administrative HEAD at start: `ae8e473d4fa705d437acbdabec9ae732b6d4f151`.
The packet's `71d10da5` is the prior review archive commit; engineering subject
`77d25f0d` was verified by exact bytes, not inferred from administrative HEAD.

- First observed task clock: 2026-09-08T00:29:52Z; source edits began after the
  initial packet, census, skill/contract reads and affected-image inspection.
  Start journal minute00:36 records that authoring transition, not task dispatch.
- Strict canonical envelope SHA256:
  `7c8c6cb5453afe9a4db61e928487ccd666da2927aea4b92f62ad9c941e0675c6`.
  Canonical immutable input-packet identity:
  `c572fc55b42ac0ea379236e8b77ca0f1e8899af927057cb7cb09adf55864017f`.
  All7 packet files and368 frozen census files were verified before edits.
  All7 packet files were reopened and verified after work; envelope unchanged.
- Scratch r1–r4 were four improving iterations, not four non-improving attempts:
  r1 reduced18 ground candidates to2; r2 cleared the remaining candidates;
  r3 corrected the still-unmarked FSYNC tail and localized ADC decoupling;
  r4 removed newly observed tight C_ISO reference/GND text spacing. No
  non-improving streak occurred; the commissioned limit was3 non-improving.
- First full conductor ended00:45:42Z at prelayout, then public-only resume
  ended00:46:18Z at PR-REVIEW. The first candidate was actually viewed19/19.
- Final source edit/freeze was before the second conductor launch00:52:17Z.
  Second full ended00:53:21Z at prelayout; public-only resume ended00:54:05Z
  at PR-REVIEW. Final all-page and affected-detail viewing finished by00:56Z.
- Identity audit rerun00:57:00Z; report/terminal checks completed before the
  absolute deadline2026-09-08T01:04:10Z. No TaskAttempt/token telemetry invented.

The required `pcb-design` and `kicad-pcb` skills, selected execution/lifecycle/
runtime/TSX/schematic procedures and applicable project contracts were read by
this author. They required source-owned corrections, scratch evidence, fresh
request/checkpoint retirement before regeneration, and stopping at review.

## Source changes and observed result

Only three engineering source/test files were authored:

- `03_tscircuit/src/schematic_presentation.tsx`: separate supervisor CT and
  ground corridors; separate all8 isolation-switch supply downlegs from GND;
  consolidate ADC grounded pins, place its supply pins together, and give
  configuration/LDO-filter connections distinct local labels; offset TDM/reset
  ground corridors; raise input clamp bus and rearrange D_QIN_GS presentation;
  move the LDO feedback branch away from C_LDO_OUT's reference; explicitly join
  both FSYNC_BUF endpoints at a named wired detour; lower C_ISO1..8 after
  final-candidate inspection found tight neighboring GND/reference spacing.
- `03_tscircuit/src/crow_audio_carrier_v1.tsx`: additive presentation-only
  `returnNet={N(b)}` prop for the local resistor-rail label helper. The resistor
  connections, every net/value/MPN/footprint and physical alias remain unchanged.
- `03_src/tests/test_schematic_ground_clearance.py`:6 project regressions,
  including good/hostile segment and foreign-label fixtures, nonzero delivered
  ground census, and a connected-or-labelled FSYNC endpoint census. The original
  delivered Circuit JSON failed the new ground regression with18 candidates.

SR77-01 root cause was routing/label geometry crossing ground-symbol ink; the
backend treats the ground anchor as an endpoint, not a complete symbol/text
clearance obstacle. The project-local test documents this shared schema gap;
no shared tooling or gate was changed. SR77-02 reference intersections were
removed by source poses/pin grouping. SR77-03 now has a continuous, explicitly
named U-shaped FSYNC_BUF wire between U_CLK.2 and R_FSYNC.1, not an unmarked free
tail. This remains a source-author observation subject to independent review.

All19 final pages were actually viewed at ordinary-page fit. No page-size or
sheet-count increase, cropped primary circuit, missing component, tiny-page
substitution or newly observed unresolved intersection was found by this author.
The affected input, LDO, supervisor, eight channel, ADC, clock, TDM and reset
regions were examined; final isolation/ADC/clock/TDM/reset crops were also viewed.
Advisory/regression screen:0 foreign-wire or foreign-label candidates across169
ground symbols. It is deliberately not an independent visual acceptance gate.

## Exact delivered identities

| Subject | Frozen77d25f0d SHA256 | Final SHA256 |
|---|---|---|
| Circuit JSON | `a0a4818bdd30634dc727637be30465c239f467e5d3f4f7dd644580031845ee38` | `9e21d2e62649a45220f72c34232bd829d5bf8f9a5df0b57b59f9e5885ae7649c` |
| Human PDF | `9bd63701177f611b0822e30d6b8438e2c515522539007fa2502708e682ad7e89` | `603eda5f0505d66fd0a71c9b5b920a9ba15f5773d0f6bbc4c5da1d4909d6aad9` |
| Native schematic | `47e6adc0e2752fea46c1a60e5780a5f40ad8ff178353d82487b6a609366f8406` | `104bdbfa2f409cf418651608798f202494b4638b2f023f3ae1b499e7471f8130` |
| Raw native netlist | `84bf1202fa7af5b77c3d52961f3cba81da3c6e688e202e6d7b4216e71440698b` | `bcee73d163d05ce806a91280ded1eabdae1d063bc3721f1bbfb366c8f5adcc03` |
| Owning normalized netlist | `32353f2259a5b903725e25bf54d192f9b2b5bc3a290e89d145a90e65400aba70` | `f7586bb09e54b2db8e305a66670cc9e09468e32b52336e85d1b1d02f5935ada0` |

Unchanged parts digest:
`da40483f53767ef34e8d0b561eea11d36e6bc6c10162dcae50a9078cf5373e0d`.
Unchanged adopted design-rule digest:
`14603bc34e244ce702e97a3b14251090eeb88377107e26293fb6ace4d1d26fd9`.
Unchanged stale213-footprint PCB:
`0f6e2e608e72c986e2fc5d559e63df4ed23de8728e6428698eb3eba9ad7d15d1`.
Unchanged old pinned bridge under `03_tscircuit/kicad/`:
`3de395fcec185c6262b0fbd46e29ca71b36abac6012c80585b9e415c27ac16da`.
New native schematic was not manually promoted into that bridge.

The normalized netlist digest DID change and was not normalized away. The sole
remaining normalized text difference is `U_ADC / units / unit / pins` ordering
caused by the requested pin presentation regrouping. Both lists contain exactly
the same49 pin numbers. All other normalized text is identical. Raw netlist
also has the ordinary export-date/instance-UUID churn removed by the existing
owning normalizer. No net-node, value, footprint or library-pin identity changed.

Read-only `06_build/ground-clearance-identity-audit.py` reproduces the exact
owning digests, proves only U_ADC's component form differs, proves its pin
multiset unchanged and the remaining normalized text identical, and compares
the complete native pin maps and value/footprint maps. Its JSON output records
both actual49-pin orders. Measured299 components,205 native nets (165 connected
plus40 NC nets),868 pin entries including40 NC match the frozen archive exactly.
This additional diagnostic does not replace, alter or bypass PR-REVIEW.

Final M-FRESH run `51f7148ed1194b0c9659167eece3762b`, source fingerprint
`1a66d5dcfea9d2614dbc764e3bf3eee563558d6de6acc4dcf300c57195e59fac`.

## Gates on the final generated subject

- Carrier68/68 tests PASS; renderer13/13 PASS including4 known-bad fixtures;
  converter45/45 PASS including16 known-bad fixtures. All rerun after final edit.
- TSX diagnostics0 embedded errors/1671 advisory warnings; M-FRESH9/9 source/
  producer/render assertions PASS. Source/native/manifest component sets agree
  over299 refdes,3/3 source-pair checks. E-CLOSURE9/9 ACCEPTED.
- Actual native ERC0 errors/2054 warnings:1565 `endpoint_off_grid` and489
  `lib_symbol_issues`. Frozen baseline2101=1612+489; reduction47 off-grid warnings.
  Blocking-only ERC report0 violations. Remaining warnings are not hidden.
- Prelayout exact request51/51 code rows, build quantity5; byte-independent row
  contents/quantities equal the retired requests. Public catalog generated
  2026-09-07T23:40:29.563026+00:00 remained fresh and exact-BOM at each admitted
  continuation; owning resume reverified freshness/identity. Public stock is
  only a negative filter, NOT authenticated PCBA allocation. No account used.
- Manufacturing selection2/2 and prelayout4/4 ACCEPTED under existing policy.
  Complete prelayout census368/368 and stage checkpoint11/11 verified on resume;
  schematic checkpoint7/7 recorded. Connector source gate PASS with20 explicit
  policy-deferred unknowns; base connector contract remains INCOMPLETE22/42.
- Final full rc2 at designed prelayout stop. Final public-only resume rc1 at
  `[2a] PR-REVIEW`, grading2/2 artifacts with4 expected findings: stale topology
  netlist hash, inherited DEFECTIVE render verdict, stale PDF hash and stale
  render netlist hash. No placement/PCB generation/routing stage was entered.

Logs: `06_build/ground-clearance-final-full.log`, `ground-clearance-final-resume.log`,
`ground-clearance-final-project-tests.log`, `ground-clearance-final-renderer-tests.log`,
`ground-clearance-final-converter-tests.log`, and `ground-clearance-identity-audit.json`.
These are local build evidence, not independent reviews.

## Archives, image paths and remaining work

Every nondeterministic full regeneration had a fresh recoverable archive FIRST:

- `/tmp/carrier-ground-clearance-prelayout.ML5Co6`: exact original build,
  pinned bridge, native schematic, netlist, provenance, sourcing and checkpoints;
  original live request/blank response and checkpoint directory retired here.
- `/tmp/carrier-ground-clearance-prelayout-final.LD68zX`: exact first canonical
  candidate, its sourcing/checkpoints, provenance and19-page raster set; live
  first-candidate request/blank response and checkpoints retired here. Neither
  prelayout had an authenticated receipt to retire. No archive was deleted.
- `/tmp/carrier-ground-clearance-scratch.iB0Z5H`: scratch `render.ts`, `r1`–`r4`
  Circuit JSON/PDF and detail evidence. Final scratch detail: `r4-isolation.png`.

Final actual PDF:
`/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/03_tscircuit/build/schematic.pdf`.
Final image directory:
`/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/renders/ground-clearance-20260908/`.
Its `page-01.png` through `page-19.png` are the final subject, plus
`detail-p06-isolation.png`, `detail-p14-adc.png`, `detail-p17-fsync.png`,
`detail-p18-tdm.png`, `detail-p19-reset.png`. The preceding subject's images
were archived before these final images replaced them.

Authored documentation: this report, live STATUS and appended schematic journal.
Generated replacements are confined to the commissioned build/native/netlist/
provenance/request/checkpoint scope. No parts, design rules, physical aliases,
floorplan/routing semantics, shared skill tooling,07_releases or08_reviews edits.
Parent's separate roof-array README/STATUS/journal edits are not this author's.
No commit, push, purchase, release, account or vendor action was performed.

Root's next boundary is fresh exact-PDF review and an independent electrical
equivalence/topology rebind for the actual new normalized digest. Preserve the
prior topology judgment only as inherited evidence until that rebind; do not
mechanically rewrite its hash. No remaining cited presentation defect was
observed by this author, but SR77-01..03 independent disposition remains OWED.
The backend ground-ink obstacle gap remains a documented limitation; the new
local regression is not a universal geometric proof. PCB remains stale,
connector/service evidence and eight power qualifications remain owed, and
the first-power startup-current procedure remains unresolved/unchanged.
