# Fresh bounded P1 campaign: preflight after coarse contract integration

This is a read-only admission checklist, not a task dispatch, accepted board,
or authorization to reuse a consumed allowance. It supplements ADR 0011 and
the archived launch/relative-path/native-evidence failures. The sole named
active root in the reviewed graph is
`p1_floorplan_569_after_native_evidence_abort` with `max_attempts: 1`;
re-read the live graph and its attempt ledger immediately before admission.
Do not run `task-repair` on an old terminal subject. The ordinary
`03_src/rebuild_all.sh` stops at connector FULL [3c]; its later P1 diagnostic
commands must be run only in a separately governed isolated candidate.

## Admission packet before spending an attempt

1. Freeze a **clean commit** and a complete isolated project copy. Record a
   manifest of SHA-256s for `03_tscircuit` source and `circuit.json`, the
   reviewed schematic PDF, KiCad schematic/netlist/checkpoint, `02_parts`
   dossiers/footprints/models, `03_src/floorplan.yaml`,
   `03_src/modular_plan.json`, `03_src/rules/p1_corridor_requirements.yaml`,
   route/nets/RF/assembly/connector contracts, `.kicad_pro`/`.kicad_dru`
   generation inputs, and checker versions. Exclude untracked generated
   `03_tscircuit/dist/`. Check that the candidate source is descended from the
   accepted source and that source/library selection, E-FAULT, ERC,
   independent schematic readability/topology review, the [2b] checkpoint,
   and `ic_reference_check.py --require-semantic-review` [3ic] match those
   exact bytes. Reopen source and schematic review if any bound input changed.
2. The integrated P1 source must retain all 59 nets exactly once across four
   signal groups and power/mechanical boundaries. Schema-2 coarse JSON must
   have one or more correct native pad/net/block-face witnesses per net,
   nonempty on-board reservations and demands, and independently expected
   source/contract hashes. Review the source-owned `p1_fixed_refs` against
   actual immutable connector, hole, hold-bank, and other mechanical poses;
   a `placement.anchors` entry alone is not immutable authority. Current
   source has no `p1_fixed_refs` and no complete coarse contract, so it cannot
   yet produce a creditable 59-net screen. The separate USB, ADC, and power
   research fragments are proposals, not substitutes for this integration.
3. Independently review a **new** schema-2 TaskEnvelope and absolute resolved
   project, work, and output paths. Verify exactly one active P1 root, all
   seven P2 dependency/backtrack edges and P4 backtrack, one attempt, zero
   replacement allowance, and the terminal archives unchanged. A dry worker
   fixture must prove copied `02_parts`, `03_src/lib`, netlist, profile,
   project sidecars and handback paths resolve from the worker CWD. The prior
   relative-path abort and mixed-board-hash receipt make these checks
   admission predicates, not convenience checks.

Set `CIRCUITS_ROOT` to the absolute frozen circuits checkout when the isolated
project sits outside a Git worktree. The supported schematic-stage command
there is `bash 03_src/rebuild_all.sh`; it stops at [2a] until the exact netlist/PDF
reviews are supplied. Continue those unchanged checkpoint bytes with
`bash 03_src/rebuild_all.sh --resume-after-schematic-review`, then verify
`06_build/checkpoints/schematic.json`, `06_build/erc.rpt`,
`06_build/erc_errors.rpt`, the reviewed schematic/netlist/PDF, and
`06_build/verification/ic_reference_semantic_admission.json`. The normal
driver will then stop at connector FULL [3c]; do not use its partial run as
an isolated P1 task receipt.

## Isolated candidate commands and bound artifacts

Run from the isolated **project root**; set `S` to the absolute path of
`skills/kicad-pcb/scripts` and `FS` to
`skills/jlcpcb-fab/scripts`. These are exact tool invocations after source
admission; paths under `06_build/p1_fresh/` are new example output names, not
existing receipts. Do not continue the canonical driver past [3c].

```sh
mkdir -p 06_build/p1_fresh 06_build/drc 06_build/verification
/usr/bin/python3 "$S/generate_board_generic.py" 03_src/floorplan.yaml \
  --netlist 06_build/netlists/crow_carrier.net \
  -o 04_kicad/crow_carrier.kicad_pcb
/usr/bin/python3 "$S/count_parity.py" .
/usr/bin/python3 "$S/pin_map_check.py" . \
  --board 04_kicad/crow_carrier.kicad_pcb \
  --circuit-json 03_tscircuit/build/circuit.json
/usr/bin/python3 "$S/generate_rules_generic.py" .
/usr/bin/python3 "$FS/generate_tmux4827_pofv.py" \
  04_kicad/crow_carrier.kicad_pcb --assembly 03_src/rules/assembly.yaml
/usr/bin/python3 "$FS/via_process_check.py" \
  04_kicad/crow_carrier.kicad_pcb --assembly 03_src/rules/assembly.yaml \
  --json 06_build/verification/p1_via_process.json
kicad-cli pcb drc --severity-all --refill-zones --save-board \
  --schematic-parity --format json -o 06_build/drc/p1_refill.json \
  04_kicad/crow_carrier.kicad_pcb
sha256sum 04_kicad/crow_carrier.kicad_pcb \
  04_kicad/crow_carrier.kicad_pro 04_kicad/crow_carrier.kicad_dru \
  06_build/drc/p1_refill.json > 06_build/p1_fresh/native_sha256.txt
kicad-cli pcb drc --severity-all --schematic-parity --format json \
  -o 06_build/drc/p1_saved.json 04_kicad/crow_carrier.kicad_pcb
/usr/bin/python3 "$S/placement_drc_check.py" 06_build/drc/p1_saved.json
/usr/bin/python3 "$S/model_coverage_check.py" \
  04_kicad/crow_carrier.kicad_pcb -o 06_build/verification/p1_models.json
/usr/bin/python3 "$FS/model_registration_gate.py" . \
  --board 04_kicad/crow_carrier.kicad_pcb \
  --out 06_build/verification/p1_model_registration.json
/usr/bin/python3 "$FS/connector_orientation_gate.py" . \
  --board 04_kicad/crow_carrier.kicad_pcb --machine-only \
  --outdir 06_build/verification/p1_connector_orientation
```

Check `sha256sum` on the board again after all read-only checks; if any tool
saves or changes it, repeat every board-bound receipt against the final
post-save SHA. Reproduce the candidate in a second complete isolated copy
with the same project layout and board basename; compare byte hashes and
native footprint/pad/net/zone census. A generator PASS or an old forensic
board SHA is not candidate reproducibility.

The coarse screen command below is only available after one **complete**
schema-2 contract is authored. Set all five expected digest variables from
the independently reviewed freeze manifest, not from the file being graded.

```sh
/usr/bin/python3 "$S/p1_corridor_capacity.py" \
  04_kicad/crow_carrier.kicad_pcb 03_src/rules/p1_coarse_contract.json \
  06_build/verification/p1_coarse_capacity.json \
  --source-requirements 03_src/rules/p1_corridor_requirements.yaml \
  --interfaces 03_src/modular_plan.json \
  --aliases 02_parts/USB4215-03-A/part.yaml \
  --floorplan 03_src/floorplan.yaml \
  --expected-contract-sha256 "$CONTRACT_SHA" \
  --expected-source-sha256 "$SOURCE_SHA" \
  --expected-interface-sha256 "$INTERFACE_SHA" \
  --expected-alias-sha256 "$ALIAS_SHA" \
  --expected-floorplan-sha256 "$FLOORPLAN_SHA"
```

The screen must name current capacity, fixed-only optimistic capacity,
relocation debt, overlap/outline/rule-area failures, and all 59 net witnesses.
It always leaves `p1_accepted=false`. P1 engineering review separately
checks the candidate's source/native parity, fixed anchors, board outline,
regions, service axes, hold bank, no P1-class native shorts/clearance/hole/
library or parity defects, and body/courtyard/model coverage. Classify
`P-ADJ`/`P-ADJ-PAIR` and unresolved local XU launches as measured P2 debt,
without calling them passed. Preserve KiCad's unrouted `unconnected` count
as an open routing denominator rather than a P1 short or route result.

The board-wide In1.Cu GND zone must be present in the saved board. Inventory
its **filled** polygons under the selected F.Cu reservations and record
voids/neck and transition uncertainty against the same post-save SHA. A
source return allocation, a zone bbox, and `--refill-zones` alone do not prove
continuous return. If the full native filled-reference criterion is deferred
to P3, state that explicitly in P1 and leave it uncredited; never delete the
zone to make raw capacity green. The machine-only connector report checks
native facing and board-edge geometry; separately bind J_USB's exact
USB4215-03-A footprint/drawing, Edge.Cuts segment, mouth transform/offset,
on-board copper pads, and allowed 0.53-mm body overhang. It is not the 19
target connector FULL receipt, which remains mandatory before P3, any route
preparation/import, P5 promotion, release, or order.

After independent admission only, dispatch a newly bounded attempt using
`/usr/bin/python3 "$S/pcb_flow.py" task-run "$PROJECT" --envelope
"$NEW_ENVELOPE" -- COMMAND ...`. Require candidate board, native JSON,
all source/contract/sidecar hashes, measurements, and task result in one
handback. If any is missing, stale, or mixed-SHA, preserve the terminal
`attempt.json` and board as consumed history and return to owner
reassessment. Do not repair, reset, or overwrite the old attempts.
