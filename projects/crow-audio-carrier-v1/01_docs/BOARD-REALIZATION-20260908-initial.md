# First accepted-source board realization — 2026-09-08

Outcome: **generated, not placement-accepted**. The single authoritative
continuation exited 1 at `[4m] P-MODEL`: **252/299 fitted footprints have a
renderer-resolvable 3D body; 47 do not**. No retry, source repair, manual bridge
promotion, routing, review adoption, commit, push, fabrication, account,
vendor contact, order, or bench operation occurred. DO-NOT-ORDER remains.

## Commission and observed execution

Worktree: `/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901`.
Project: `projects/crow-audio-carrier-v1`. Administrative HEAD remained
`6700b7c0437d3284770788469c9f0252e468f336`; the accepted engineering subject is
`1353d04766617721cf97ffbd80e7bf87c0055bdd`. This FRESH mechanical successor read
the complete commissioned TASK/envelope/packet, PCB-design and KiCad skills,
selected execution, lifecycle, checkpoint, placement and pin procedures, and
the relevant project contracts. The skills enforced the exact-input,
single-writer, bounded-attempt and first-red-gate boundaries. The commission's
narrower prohibition on source changes, delegation and commits governs.

The command ran exactly once, from the worktree root:

```sh
bash projects/crow-audio-carrier-v1/03_src/rebuild_all.sh --resume-after-schematic-review
```

The unchanged shared `pipeline_runtime.run_stage` owned the 480-second
process-group deadline, 10-second heartbeat and durable combined stdout/stderr
log. The observer used an explicit task-relevant environment projection and
`PYTHONDONTWRITEBYTECODE=1`; it did not alter the conductor or any gate.
This is bounded execution, not hermetic isolation. No canonical TaskAttempt,
accepted artifact bundle, token count or reviewer telemetry is fabricated.

| Observed event | UTC |
|---|---|
| First tool clock after task receipt | 2026-09-08 02:26:02 |
| Archive preparation input verification | 2026-09-08T02:31:20.455776Z |
| Archive ready | 2026-09-08T02:31:20.545600Z |
| Immediate pre-execution verification | 2026-09-08T02:31:57.355955Z |
| Shared runtime start, child PID 3431045 | 2026-09-08T02:31:57.423683Z |
| Shared runtime finish, FAIL / exit 1 | 2026-09-08T02:32:20.158503Z |
| Immediate post-execution verification | 2026-09-08T02:32:20.829853Z |
| Post-diagnosis frozen-input verification | 2026-09-08T02:34:03.724394Z |
| Post-report packet/census verification | 2026-09-08T02:38:48.989269Z |
| Archive and writer-scope verification | 2026-09-08T02:38:49.135932Z |
| Commissioned absolute deadline | 2026-09-08T02:45:22Z |

MEASURED conductor elapsed time: **22.734814 seconds**, not a timeout.
Runtime log: `06_build/verification/first-board-20260908/conductor.log`,
45,648 bytes / 294 child-output lines, SHA-256
`fe1c84d20ad563ae5e5343b840f3a0c9bebe01338545da6a0e656be386971340`.
The console sampled 200 lines and omitted 94; the durable log retains all
294. `observed-outcome.json` in the same directory is actual runtime evidence,
not a TaskAttempt; SHA-256
`21c7858de75fc62c29c7412ee74d6b4c59d507b7386597ff4f2c68b7c9544ada`.
No conductor/generator process remained in the subsequent process listing.

## Input and archive integrity

MEASURED before and after: strict closed-schema TaskEnvelope validation,
duplicate-key rejection, independently recomputed canonical envelope SHA-256
`712047d042d73d5adc753c32a2ae838c57715193a1d21fd5f391b9705e651f67`,
canonical packet SHA-256
`76b7341439762533b4f5322458d07e1198accd4f52ed6dbc6108fe8e8a7e7fa4`,
**8/8 packet members**, and **368/368 census files / 54,729,254 bytes** exact.
Both the independent per-file SHA/size loop and the owning census-set verifier
passed; the latter also rejects additions/deletions in its authored domains.
The accepted native schematic, netlist, Circuit JSON and PDF were not regenerated
or edited. The source/dossier/rule/checkpoint/review/release domains are unchanged.

Before the conductor replaced any output, `cp -a` copied the entire
`04_kicad`, `03_tscircuit/kicad` and `06_build` trees to the new recoverable
directory `/tmp/carrier-first-board-20260908-archive.2tmgx_61`.
Nothing material was deleted. Its `manifest.json` verifies 329 non-cache files;
SHA-256 `360d3f053576d908db08244ca00e6e8b44b4edd8eacdd08dac7bd4cd156585b2`.
The archived board independently reopens as 213 footprints. Full archived
reports and sidecars remain available at their original relative paths.
`preparation.json` records the archive and actual preparation clocks.

The observer's project snapshots and `changed-paths.json` record net filesystem
changes, excluding `.git`, `node_modules`, `__pycache__`, `.tscircuit`, and `dist`.
All observed conductor changes are inside the exclusive generated-output scope.
These snapshots are post-hoc evidence, not OS-level write confinement.
Root's pre-existing `01_docs/journal/schematic.md` administrative launch entry
was disclosed and preserved; it is outside the frozen census. This successor
changed only the commissioned placement journal, live beacon, this report and
generated output/evidence paths. No globally clean worktree is claimed.
Final archive verification rehashed all 329 manifest files without drift;
the scoped snapshot found 21 changed paths and zero unexpected paths.
M-BEACON passed for 1/1 beacon, and scoped documentation whitespace checks
passed. An early progress-message estimated clock was explicitly corrected;
only sampled tool/runtime clocks above are execution timing evidence.

## Exact generated identities and partial-state warning

| Artifact | Before SHA-256 | Current SHA-256 |
|---|---|---|
| `04_kicad/crow_audio_carrier_v1.kicad_pcb` | `0f6e2e608e72c986e2fc5d559e63df4ed23de8728e6428698eb3eba9ad7d15d1` | `72f4b136f2c5477167b06861b2636e48be955a6500a27cac867bd267cb4f0abb` |
| `03_tscircuit/kicad/crow_audio_carrier_v1.kicad_sch` | `3de395fcec185c6262b0fbd46e29ca71b36abac6012c80585b9e415c27ac16da` | `044c0cea6504fc08b0115a60a30e4076d96ea8ae2c05e83159a40b936755acf6` |
| `04_kicad/crow_audio_carrier_v1.kicad_pro` | `a1412a0be9513b3a291ede8c37db80725665d98f99bc44ef398950046d2854cc` | `d679205c674cc988c910a089d6c2a978221c9734c58b57c734daa2aa1eade0ac` |
| `04_kicad/crow_audio_carrier_v1.kicad_dru` | `bd54be05f191ef1c1d7a3819724b10e75ee90daabfa140e4d3c35b6c3b37f823` | unchanged |
| `04_kicad/fp-lib-table` | `34c9598478a01170e4014bf09ab97e41ad05af5140e6a8e77c2a26ceb5c88eb2` | unchanged |

The conductor alone copied the independently accepted native schematic into
the bridge at stage [2b]; current bridge and accepted native bytes match.
The current board is 1,164,539 bytes and independently reopens with 306 total
footprints: 299 fitted circuit components, H1–H4 and FID1–FID3. It has 927 KiCad
pad objects, zero track/via objects and three generated zones. These raw API
counts are not a physical-pin or filled-zone acceptance claim.

The board save reset `.kicad_pro` from six netclasses to **Default only**;
the downstream rules-generator stage was not reached. The retained `.dru` is
unchanged old output, not proof that current rules are installed. Do not route
or reuse this partial current snapshot as a finished rule-bearing board.
`06_build/provenance/pcb_layout.pending.json` remains pending; no finish/seal
was emitted. Prior `06_build/drc/pre_route.json` and
`06_build/placement_policy_audit.md` remain byte-identical to their archived
versions and are **stale for this new board**, not newly measured gates.

## Actual gate scoreboard

Every MEASURED row below comes from this conductor log or its exact reports.

| Gate / boundary | Actual coverage and outcome |
|---|---|
| M-FRESH / checkpoints | 1/1 adopted board; prelayout 11/11, full input census 368/368, schematic 7/7 exact |
| Governed sourcing continuation | exact request PASS; prelayout readiness 4/4; separately reopened public-catalog predicate 51/51 exact lines, build quantity 5; no authenticated receipt |
| PR-REVIEW schematic | 2/2 SOUND and current |
| Board generator | 299 components, 43 anchored, 253 floating parts legalized; 32 assertions passed |
| P-COLLIDE | 0 inter-footprint copper-pad overlaps/shorts over 892 copper pads; 0 fixed-courtyard overlaps over 50 fixed parts |
| S-COUNT | 4/4 artifact-to-manifest pairs agree over 299 references |
| CROW-SPOKE | 8/8 generated J1–J8 connectors closed |
| P-PINMAP | PASS over 47 multi-pin references / 362 declared physical-pin identities; machine consistency only, not independent package-winding review or all-component physical qualification |
| Selective critical part facts | NOT RUN: driver explicitly reports no `critical_parts.yaml`; no measured critical-part review or engineering non-applicability is inferred |
| Connector base / SOURCE / FULL | 3 assemblies / 11 instances; base 22/42 facts closed and 20 unknown; SOURCE admits exactly 20 governed deferrals with 0 findings; FULL remains INCOMPLETE with 20 findings |
| Physical placement | 3/3 predicates PASS over 299 assembled envelopes; no failures/warnings; minimum reported body clearance >=0.100 mm within checker search ceiling |
| Placement-routability compositor | 5 PASS + 2 explicit N-A across 7 rows, reported ACCEPTED; endpoint topology 8/8; 4 layer roles / 5 class maps; 205 board nets / 1 declared owner |
| Typed P-FEASIBILITY shadow | INCOMPLETE, graded 0/7, outputs empty, `P-FEAS-PROMOTION-DISABLED`; not placement promotion or a new blocking conductor exit |
| **[4m] P-MODEL** | **FAIL, 252/299 resolved, 47 affected refs; first blocking gate, conductor exit 1** |
| RF placement, P-PADSEP, placement policy/adjacency | NOT REACHED for these board bytes |
| Rules regeneration, current native placement DRC/parity, P-LAND, tier gate | NOT REACHED for these board bytes |
| Route preparation, model registration, connector orientation, exact pin/layout/render reviews | NOT REACHED; required placement-review files remain absent |
| Route import/search/stitch, routed DRC, fabrication/release/order/first article | NOT RUN / NOT AUTHORIZED |

The placement physical report measures a tightest outline margin of 1.32 mm at
J11.11 against 0.15 mm; its worst capacity cut is x=102.5 mm, 69 nets versus
310 tracks, ratio 0.22 against the 0.5 failure threshold. These are the named
static predicates, not proof of a route. The critical-route-contract row is
PASS under the explicit zero-critical-pair declaration; it is not positive
coverage of a differential pair. The two N-A rows are connector lane order
and series power paths. The shadow's zero elapsed-time field is emitter data,
not measured wall-clock runtime and is not included in execution timing.

Connector FULL's explicit INCOMPLETE was returned as the governed ADR-0007
prototype qualification deferral, not silently relabeled PASS. No physical
measurement was invented. P-MODEL is the first failure that blocked the driver.

## Read-only first-failure diagnosis

Exact failing report: `06_build/verification/model_coverage.json`, 108,456 bytes,
SHA-256 `8f78253610474065ea82877469a6388b9a2d239b51e317103db6931c7b74c470`.
The report was reopened and all 47 missing rows grouped against the saved
board's actual footprint identities. **35 refs declare an unresolved model
path; 12 refs have no model entry at all**. These are separate causes.

| Cause / exact footprint model family | Refs | Count |
|---|---|---:|
| Unresolved `Capacitor_THT.3dshapes/C_Rect_L7.2mm_W5.0mm_P5.00mm.step` | C_A1P/N–C_A8P/N | 16 |
| Unresolved `Fuse.3dshapes/Fuse_1812_4532Metric.step` | F1–F8 | 8 |
| Unresolved `Fuse.3dshapes/Fuse_2920_7451Metric.step` | F_IN | 1 |
| Unresolved `Connector_Molex.3dshapes/Molex_Micro-Fit_3.0_43650-0400_1x04_P3.00mm_Horizontal.step` | J1–J8 | 8 |
| Unresolved `Connector_Molex.3dshapes/Molex_Micro-Fit_3.0_43650-0200_1x02_P3.00mm_Horizontal.step` | J9 | 1 |
| Unresolved `Package_DFN_QFN.3dshapes/QFN-48-1EP_6x6mm_P0.4mm_EP4.6x4.6mm.step` | U_ADC | 1 |
| No model in `Coilcraft_XGL4020_Exact` | L_BUCK | 1 |
| No model in `TI_DSE0006A_Exact` | U_AUDIO, U_PWR | 2 |
| No model in `TI_DSG0008A_Exact` | U_ISO1–U_ISO8 | 8 |
| No model in `TI_DSK0010A_Exact` | U_LDO | 1 |

All six unresolved paths begin with `${KICAD10_3DMODEL_DIR}`. The checker's
actual substitution root is `/home/mouse9911/.local/share/kicad/10.0/3dmodels`;
none of those six exact model basenames was found there. The conventional
`/usr/share/kicad/3dmodels` fallback directory does not exist on this host.
The owning resolver checks nonempty files after KiCad configuration/environment
substitution; it does not fetch them or prove body dimensions/registration.
The missing entries were confirmed in the four exact source `.kicad_mod`
files under `03_src/lib/crow_audio_carrier.pretty/`; the Molex/ADC source
footprints retain the unresolved path declarations. No source-owned
`model_override` was applied by this floorplan. A library/environment repair
alone cannot fix the 12 absent declarations, and invented generic bodies
would not establish exact manufacturer geometry or registration.

No directly usable model candidate was identified in those configured model
roots or the exact source attachments. Existing local primary documents for
`XGL4020-332MEC`, `TPS389001DSER`, `TMUX2821DSGR` and `TPS7A9201DSKR` are
source-owner geometry references, not 3D model attachments or new validation.
No new web fetch, download, installation or asset substitution was undertaken.

Smallest next source-owner task: close this **six-path asset resolution plus
four custom-footprint model-attachment** gap using exact, provenance-backed
package/body assets and source-owned attachments, then independently verify
coverage and registration on regenerated board bytes. Preserve footprint
electrical identity and copper/land geometry; do not alter a part selection,
pin map or fitted population to quiet P-MODEL. Any source change must reopen
its bound checkpoints/reviews through the owner; an unchanged resume retry is
not authorized by this completed one-attempt commission. No fix was applied.

## Remaining warnings and authority limits

The producer reports 226/299 silkscreen refdes placed and 73 generated F.Fab
waivers, 10 crowded captions and zero functional labels. Its label-ownership
inventory reports 90/306 owned, 143 degraded and 73 unplaced labels. Those
warnings and generated waivers are retained, **not independently adopted**.
They do not change P-MODEL's first-stop identity and need their owning later
policy/readability gates. KiCad emitted PROPERTY_ENUM assertions and duplicate
image-handler diagnostics; the generator still saved a parseable board and
the named machine gates ran. No all-purpose clean-generation claim is made.

The read-only source census independently confirmed all 299 refs have 43
anchors plus 256 patterns, with no uncovered ref or stale anchor. C_LDO_A and
C_LDO_D both match `power` before `adc`; `initial_pose()` returns at the first
matching region. Saved coordinates are C_LDO_A=(39.5,69.0),
C_LDO_D=(38.1,65.599999), U_ADC=(96.0,70.0) mm. These are measured origins,
not a pad-to-pad proximity verdict. Current adjacency/placement policy was
not run after P-MODEL; this remains a source-floorplan hypothesis for its owner.

INHERITED: whole-design electrical equivalence covers 299 components / 205
nets / 868 native owners / 871 physical-pin occurrences and 40 NCs; full
topology/ratings judgment remains inherited from 77d25f0d, as stated in the
verified witnesses. This mechanical attempt did not rederive that judgment.
TOP77-Q1–Q5/N1, startup/fall/reverse behavior, thermal/protection, timing,
analog performance, exact dossier-document authority, connector physical/service
qualification and first-power procedure all remain owed. No input-current
limit was raised or bench result passed. Root alone adopts this factual
outcome; this report supplies no placement, routing, release or order approval.
