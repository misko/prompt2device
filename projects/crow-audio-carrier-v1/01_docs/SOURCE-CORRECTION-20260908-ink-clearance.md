# Source correction — rendered ink clearance, 2026-09-08

Author result: all five commissioned SR-01..05 / SRDAB-01..05 presentation
findings have source-owned remedies and were visually rechecked on the final
delivered PDF. This is an author handoff, **not** an independent SOUND review,
adoption, release, electrical qualification or order authorization. The
authoritative conductor stopped at the fresh schematic-review boundary.

## Immutable input and scope

The fresh author packet was read without preloading an earlier transcript.
The complete seven named input files and the selected PCB-design/KiCad skills,
execution graph/runtime, lifecycle/backtrack, operator checkpoint,
tscircuit-folder and schematic-generation procedures and applicable project
contracts were read before source work. Their operative effect was to require
source ownership, recoverable checkpoint retirement, an authoritative rebuild,
public-only resume and a stop before independent schematic review/PCB work.

Strict `TaskEnvelope.from_json` plus duplicate-key rejection and canonical
compact-JSON SHA verification succeeded before and after the work:

- Envelope: `aae06f792d6da9ea0974d88da3f9a61935705d6ba73fb20c17cf21ca2b2d9fe6`.
- Seven-item packet: `2c225f597c56e4eb8b707a54ae0893033ebc800d2b946fd740a4119d9e470852`.
- `verify_input_packet`: 7/7 exact sizes/hashes, no failures BEFORE and AFTER.
- Frozen census: 368/368 verified before source edits. Afterwards exactly seven
  previously pinned files differ: presentation source, CJ, PDF, native
  schematic, raw netlist, provenance and prelayout request. All other frozen
  input bytes remain identical. The newly generated census verifies 368/368.
- Actual inherited HEAD: `4e17e05ec292d56ffbc180a7f5d742a2083f6bcb`; engineering
  input subject remains the packet-bound `dab4f14e` candidate.

Only `03_tscircuit/src/schematic_presentation.tsx`, a project-local test and
allowed documentation were authored. The main electrical TSX is byte-identical.
Generated CJ/native/PDF were produced by project tooling, never patched. No
parts/rules, shared tooling, reviews, bridge schematic or PCB were edited. No
delegation, commit/push, account/vendor action, placement/routing or release was
performed.

## Five exact findings and remedies

| Finding | Source-owned remedy | Final viewed evidence |
| --- | --- | --- |
| SR-01 / SRDAB-01, reset straps | U_RST2 B/VCC pins2/8 share the top rail; A/GND pins1/4 share the bottom rail. Opposite-net straps no longer nearly coincide or traverse filled body. | Page19 and enlarged page19: distinct top/bottom external straps. |
| SR-02 / SRDAB-02, nine foreign supply-plate crossings | AFE1..8 supply plates grow rightward above the body; U_AUDIO plate moves right of the PWR_EN input corridor. R_OUT1P shifts left to clear its particular output/feedback route. | Page4 enlarged and all pages6..13 plus all eight enlarged AFE crops. |
| SR-03 / SRDAB-03, U_OE NC1/plate corner | U_OE pin pitch increases to0.8, with matching local rail/Ground height calculation; C_OE moves left for separate Ground/property corridors. | Page18 enlarged: NC1 stub/endpoint visibly below and clear of TDM_SENSE_G plate. |
| SR-04 / SRDAB-04, RESET_RC/pulse contact | Q_RST1 lowers to y=-1.5 and R_RESET_GPD moves to x=3.5, reserving a lower pulse corridor. Ordinary timing labels remain; experimental redundant timing-label branches were removed. | Page19 enlarged: RESET_RC, RESET_C/C_RST_T properties and RESET_PULSE_H have separate corridors. Legitimate perpendicular crossings remain. |
| SR-05 / SRDAB-05, hidden U_PWR MR_N tie | MR_N pin3 moves beside VDD pin4 on the top side, making their same-net strap external and visible. | Page4 enlarged: visible top tie; no filled-body traversal. |

Before editing, the author independently VIEWED all five cited original detail
regions and each of the eight AFE crops. On the final exact PDF, all19 pages
were VIEWED individually at96dpi; page4/page19 were additionally viewed at144dpi,
and page18 plus each AFE plate region at192dpi. Final all-page images and details
are retained under the first archive below. No generated image was altered.
These author observations do not close root's independent review obligation.

## Regression breadth and limitations

New project test `03_src/tests/test_schematic_ink_clearance.py` computes ordinary
net-label envelopes from the pinned renderer's actual Arial glyph widths,
0.18 font and0.2 label height, including complete plate fill/border/glyph
envelopes and a conservative stroke margin. It does not infer plate length from
CJ center offset: rotated RESET_RC is a reproduced counterexample to that
inference. It grades foreign plate/wire, plate/plate, NC stub/endpoint contact,
near-coincident axis-aligned foreign strokes and filled rectangular chip-body
traversal. Same-net plate routes and different sheets are distinguished;
perpendicular crossings are explicitly allowed. Bodies have no owner exemption.

The old candidate reproduces17 broader ink contacts. Final screen: zero over
19 sheets,240 plates,67 filled chip bodies,40 NCs and632 traces. Separate
Ground screen: zero over169 Ground instances. Eight primitive/end-to-end tests
exercise hostile/good pairs, including full classifier paths for plate/net
ownership, NC/plate pairing, body intrusion and near strokes/perpendicular
crossings; the ninth test grades the delivered subject. All77 project tests
pass, including the pre-existing Ground and topology tests.

This is a broader screen, not complete rendered-ink acceptance. Component
reference/value text, general schematic_text, nonrectangular symbol ink and
border-only body contacts are not fully modeled. The initially considered0.03
body inset was removed; only a1e-8 numerical epsilon excludes exact boundary
touches. A hostile trace0.001 inside a filled boundary is detected. Arrow-tip
bounding rectangles are conservative. Metric-table shape and pinned font/label
height are guarded by assertions; missing glyph widths use the renderer's
question-mark fallback. A renderer-owned full
ink obstacle schema remains an upstream improvement; no shared policy/gate was
adopted here. Zero results never replace final PDF views.

Five cheap scratch build/render candidates were used, followed by exactly one
authoritative full rebuild. Scratch3's broader zero was rejected because
actual views exposed Ground/bypass/property contacts; scratch4's Ground zero
still left a visible reset property interaction. Scratch5 cleared these.
These bounded observed refinements did not reach three consecutive
non-improving attempts. No fabricated timing or candidate-acceptance telemetry
is asserted for the scratch work.

## Exact semantic preservation

A full s-expression tree comparison of archived original and final native
netlists, with balanced parsing, found exactly:

1. One export date changed.
2. All299 schematic-instance UUID `tstamps` changed.
3. U_RST2 unitA pin-array ordering changed from `[3,1,2,8,4,5,6,7]` to
   `[3,2,1,8,4,5,6,7]`.

There are no other tree differences. Sorting only pin arrays and replacing
only date/UUID values makes the whole trees equal. All299 component records,
values, MPN/property bytes, footprints, library pin meanings,205 nets and868
exported native pin-to-net nodes are preserved. The three declared Q_IN
physical aliases6/7/8→5 remain byte-pinned, preserving871 physical identities
and40 NC identities. No normalized-digest algorithm was changed or weakened;
the existing digest properly changes for U_RST2's presentation pin ordering.

## Final subjects

Paths below are project-relative; hashes are full SHA-256.

| Subject | SHA-256 |
| --- | --- |
| `03_tscircuit/src/crow_audio_carrier_v1.tsx` (unchanged) | `474dff14837546269c44e27aef598985659cfa916e61bb9cc04cbeef94599aed` |
| `03_tscircuit/src/schematic_presentation.tsx` | `960630a58fa7ce0f29d86c4386e1b41b900d5ac304d81245e172c5b47783d504` |
| `03_tscircuit/build/circuit.json` | `99f3d38e3b471ad7eb0592c7f6fbe4d64f8f061003b7f2d7cc9f34e839be23bb` |
| `03_tscircuit/build/schematic.pdf` | `72fd0f97d190af75c5c26b06c39ce34b17433ba95afe7956f6700501f53bda3e` |
| `04_kicad/crow_audio_carrier_v1.kicad_sch` | `044c0cea6504fc08b0115a60a30e4076d96ea8ae2c05e83159a40b936755acf6` |
| Raw `06_build/netlists/crow_audio_carrier_v1.net` | `c4ded19290cfcd88744a49fe4e9f5f380b755974937acf3d3d2474ee0fdd5b1a` |
| Existing `netlist_digest()` of that netlist | `ac2b772d357bf4c6e8e962a63fbc5cb5535e3770accaa3ce82a42b28520c227b` |
| Parts aggregate (unchanged) | `da40483f53767ef34e8d0b561eea11d36e6bc6c10162dcae50a9078cf5373e0d` |
| Design-rule digest (unchanged) | `14603bc34e244ce702e97a3b14251090eeb88377107e26293fb6ace4d1d26fd9` |
| Pinned old bridge schematic (unchanged) | `3de395fcec185c6262b0fbd46e29ca71b36abac6012c80585b9e415c27ac16da` |
| Stale213-footprint PCB (unchanged) | `0f6e2e608e72c986e2fc5d559e63df4ed23de8728e6428698eb3eba9ad7d15d1` |

## Authoritative gates and retained stop

- Full renderer19/19,299 components,13 explicit display aliases,1455 font
  baseline corrections, maximum endpoint residual0.00; M-FRESH9/9 PASS and
  final project provenance audit PASS.
- S-COUNT3/3 over299 refdes; electrical closure9/9 specialist gates ACCEPTED;
  early-design4/4; manufacturing selection2/2 and public prelayout4/4 PASS.
- New exact request51/51 codes, quantity5. Public-only resume reverified its
  request, current census368/368, prelayout checkpoint11/11 and fresh public
  negative filter. Public catalog generation time remains
  `2026-09-07T23:40:29.563026+00:00`; it was not refetched or promoted to
  authenticated allocation evidence.
- Connector base remains INCOMPLETE:3 assemblies,11 instances,22/42 coverage,
  20 physical unknowns. Typed SOURCE gate admits those20 with zero source
  findings. Physical qualification, first power and TOP77 remain OWED.
- Native ERC:0 errors;2076 warnings, consisting of1587 endpoint_off_grid and
  489 lib_symbol_issues. This is not a warning-free claim.
- Final project77/77 tests PASS; renderer13/13 (4 known-bad fixtures),
  converter45/45 (16 known-bad fixtures) PASS.
- Schematic checkpoint7/7 recorded and reverified. Review gate grades2/2
  required reviews and stops with four expected failures: stale topology
  netlist hash; render verdict not SOUND; stale render PDF hash; stale render
  netlist hash. No PCB generation stage ran, and the old bridge was not promoted.

## Recoverable archives and observed clocks

`/tmp/carrier-ink-clearance-20260908.WFAAKU` retains the exact original source,
CJ/PDF, native schematic, netlist, provenance, sourcing and checkpoint bytes;
scratch evidence; final19-page PNGs and enlarged details; and full build,
public resume, project-test, renderer-test and converter-test logs. Original
PDF is `603eda5f0505d66fd0a71c9b5b920a9ba15f5773d0f6bbc4c5da1d4909d6aad9`,
original CJ `9e21d2e62649a45220f72c34232bd829d5bf8f9a5df0b57b59f9e5885ae7649c`,
and original raw netlist
`bcee73d163d05ce806a91280ded1eabdae1d063bc3721f1bbfb366c8f5adcc03`.

Immediately before the sole full rebuild,15 current source/candidate/
checkpoint/sourcing files were copied and verified byte-equal in
`/tmp/carrier-ink-pre-full-20260908.eW5PBp`. This second archive contains final
authored source with the old canonical candidate. The old request/response and
all three checkpoints were then moved recoverably into its `retired/sourcing`
and `retired/checkpoints` subtrees. No material bytes were deleted; restoration
must be owner-directed because those receipts are stale for the new subject.

Observed UTC clocks: full conductor launched01:49:24; provenance producer
started01:49:28.372225 and verified01:49:49.489720; exact request generated
01:50:10.469605. Public-only resume had completed at the fresh review gate by
01:53:39. Final full-page/detail views, strict packet-after and exact semantic
comparison were complete by01:55:56; final current-census reverify completed
by01:57:09. A final read-only pass at02:00:53 again verified strict packet7/7,
current census368/368, schematic checkpoint7/7 and clean `git diff --check`.
Deadline is02:04:46. Intermediate journal times are minute-resolution
progress labels, not instrumented operation-duration telemetry.

Handoff: root owns Git and fresh independent topology/render review. Reopen the
new exact subjects, preserve these archives and do not resume beyond the
review gate without the owning reviews. This report does not change any review
verdict or authorize release/order/PCB work.
