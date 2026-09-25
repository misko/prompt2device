# TI USB ESD canonical schematic adoption audit, 2026-09-25

**Read-only finding.** No canonical generated artifact, producer, checkpoint,
pause state, PCB, or review receipt was edited here. The governed source and
critical selection choose `U_USB_ESD = TPD2EUSB30ADRTR / C94934` with
`Package_TO_SOT_SMD:Texas_DRT-3` and pads 1=`USB_DP`, 2=`USB_DN`, 3=`GND`.
The saved canonical artifacts do not yet express that choice consistently.
This audit does not admit a product or reopen D13's schematic-only,
`PROTOTYPE_ONLY` electrical boundary.

| Artifact at audit | Identity / binding | Status |
| --- | --- | --- |
| Governed TSX `usb_device_frontend.tsx` | TI; SHA-256 `62611f919a9e41d3a13a7f9df91e000761026f6d55719d1c3bccb8623980f477` | Exact hash in `critical_part_selection.yaml`; unchanged |
| Critical selection | TI, `prototype_only`; SHA-256 `15288355fcc731ff8b1b0e35a1ae47b9faf66140223cfea0d31c91d99e9dc1ba` | Ordinary admission exits 1; `--require-prototype` exits 0 |
| Tracked `03_tscircuit/build/circuit.json` and `04_kicad/crow_carrier.kicad_sch` at `HEAD` | Nexperia 3UV; SHA-256 `ff30fe8a46bc44befa7533038bbf17d2ed0aed2e2b263b87dbd36f8fb5f3d41a`, `3794e0f05bf8acd3532d392b38026d6cb59b23af0d43119c2e02f5e7bbf6f28e` | Stale; shared worktree edits must not be overwritten blindly |
| Same two tracked files in the shared worktree | Nexperia 5UX; SHA-256 `4dc9ff79b29bd7faf2088d328a7dab8a52fe103bf946dd819c26f674c7d7bad7`, `752eb88e1c274895cf3248d1cfbd5e25d26318427e9a40d317081c89aec2b746` | Uncommitted generated edits by another workstream; still stale to TI |
| Ignored `06_build/netlists/crow_carrier.net` | Nexperia 5UX; SHA-256 `457763489019b299491c38d303b618561b45be2dc43e6298fe89b25effd8e0cd` | Stale to TI |
| Ignored pinned `03_tscircuit/kicad/crow_carrier.kicad_sch` and tracked schematic PDF | Nexperia 3UV; schematic SHA-256 `3794e0f05bf8acd3532d392b38026d6cb59b23af0d43119c2e02f5e7bbf6f28e`, PDF `41989418b96805c04e7b833b2e17d8c53dfbc18d8be1eaa866ec09de9c6947a2` | Do not replay as TI |

The existing private prototype bundle at
`06_build/prototype_only/20260925T044907Z-581549/` is an exact TI source and
schematic subject: circuit SHA-256
`580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d`,
native schematic `758e29b0d9606a6b8f123a2dca474ce62871a85e08fb2fb9024c5a7a3d04610d`,
native netlist `a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd`,
and PDF `d2e54c1195a217b231fbc2ab058e051b01dc8e45b534c65d38006978af386eed`.
Its 21 source-input and four output hashes still match. The separate
renderer-only candidate retains the first three hashes and has PDF
`c7a46f799696e7bae3399f26bc071df8cf09f9fc56a15c93f3cfbefe16ec627a`;
the dated raster recheck finds the original PDF readable too. These are
private `PROTOTYPE_ONLY` reviews, not canonical pre-route approvals. The
frozen TI source packet independently has 569 components, 1,787 pad/net
tuples, and 428 nets; TI pad numbers and nets agree with the governed TSX.

## Existing gates and stale bindings

- `01_docs/pause_state.json` SHA-256
  `70e66e83c408c14c5140ed76d1bb69298be64e95e821f51ca1f60af2b4dea4d0`
  has 10/10 matching checkpoint/receipt hashes. It binds the unchanged
  critical-selection SHA and states that the TI prototype remains held:
  XU316 transient unqualified, isolated board with 499 opens, P1 and
  connector physical fit unaccepted. Leave this file unchanged.
- Ordinary `rebuild_all.sh` and `rebuild_reuse.sh` call critical selection
  before their producers and reject `PROTOTYPE_ONLY`. The only current
  authorized conductor, `rebuild_prototype_only.sh`, writes a private
  circuit/schematic/netlist/PDF bundle and receipt; by design it never writes
  canonical `build/`, `04_kicad/`, a board, a route, or a release.
  Release preflight and rehearsal independently reject this selection.
- With the stale canonical circuit/netlist, E-FAULT says source-circuit
  digest mismatch. `ic_reference_check.py --require-semantic-review` selects
  69 ICs but gives 68/69 coverage and STALE semantic subject because the
  packet and receipt already bind TI. On the frozen TI subject E-FAULT
  passes conditional source/fuse checks, and P-PREC coverage returns 69/69
  with the already recorded subject digest
  `a8b79bc9ecd6f572ba531402abb4c841989b3dd8917333962aed6743197ec387`.
  Neither `ic_reference_research.yaml` nor its independent receipt needs a
  blind hash refresh when the exact TI netlist is adopted.
- `06_build/checkpoints/schematic.json` has four of seven bindings stale
  already: `rebuild_all.sh`, circuit, schematic, and netlist. Its recorded
  circuit/schematic/netlist SHAs are respectively `ff30fe8a…`,
  `3794e0f0…`, and `43132fc7…`. Do not resume the ordinary schematic
  checkpoint or rewrite it to imply the ordinary conductor passed.
- Canonical `08_reviews/pre-route_topology.md` and
  `pre-route_schematic_render.md` review an older Nexperia 3UV subject.
  Both bind normalized netlist `d6f6bb95…`, parts `8f774274…`, and design
  rules `c5f9432e…`; the render review also binds PDF `41989418…`.
  Today's parts and rules digests are `ffc4929303fd056303a0798573660c70c18c363efeed6e0c5df01badce227266`
  and `36aa880be39c4c2d2a1927a3c266c1ffd9ea98a78538701406c730d0464d2858`.
  The frozen TI netlist's normalized digest is
  `b3d04cf63d786f66d8052541e9a830d6fd4096b1e74b34e326de892c46827805`.
  The current pre-route review checker reports six stale hash findings even
  before TI adoption. Independent canonical topology and render reviews are
  required for any later schematic-stage promotion. Prior private reviews
  may be cited as evidence, but their verdicts do not transfer automatically.

## Smallest safe adoption boundary

There is no existing command that safely promotes `PROTOTYPE_ONLY` private
schematic artifacts into canonical paths: ordinary drivers stop before their
producer, while the prototype driver deliberately writes only private paths.
An ad hoc `cp` from the private bundle would bypass that separation. The
smallest code change, if canonical TI artifacts are needed now, is a
separately reviewed, **schematic-only prototype adoption transaction**:

1. Recheck `--require-prototype`, D13's exact source/evidence hashes and the
   unchanged pause-state bindings. Verify a fresh private bundle's receipt
   and all producer inputs, diagnostics, 569-ref/1,787-pad/428-net parity,
   exact TI MPN/FPID/pad nets, ERC, E-FAULT, and P-PREC. Require zero
   non-ESD electrical changes against its reviewed TI subject.
2. Stage circuit, native schematic, netlist, and PDF together. Record their
   exact hashes in a new `PROTOTYPE_ONLY` adoption receipt and promote only
   those four schematic-stage artifacts as one reviewed set; reject a
   partial promotion. Coordinate with the owner of the current uncommitted generated
   files first. Do not create or copy a PCB, route, ordinary checkpoint,
   release artifact, or product-PASS receipt. Keep the older pinned
   `03_tscircuit/kicad` copy explicitly unusable for reuse until a separate
   independent canonical schematic review promotes exact new bytes.
3. Recheck the canonical circuit/schematic/netlist identity and all 69
   P-PREC applications, then obtain new hash-bound topology/render reviews
   if any later conductor needs the canonical schematic. Preserve
   `pause_state.json`, the open `USB-ESD-selection-transient` DESIGN_CLEAN
   finding, and the ordinary full/reuse/release gate failures. Any attempt
   to make the new prototype transaction produce a board or bypass those
   gates requires a separate policy decision and review.

Existing read-only commands from the repository root:

```sh
crow_project=projects/crow-usb-carrier-v1
python3 skills/pcb-design/scripts/critical_part_selection_admission.py "$crow_project" --require-prototype
python3 skills/kicad-pcb/scripts/early_design_check.py "$crow_project/06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project" --fault-envelope
python3 skills/kicad-pcb/scripts/ic_reference_check.py "$crow_project/06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project" --print-bindings
python3 skills/kicad-pcb/scripts/pre_route_review_check.py "$crow_project" --phase schematic --netlist 06_build/netlists/crow_carrier.net
```

To make a new private subject without touching canonical generated paths,
run `(cd "$crow_project" && bash 03_src/rebuild_prototype_only.sh)` after
checking free space. It does **not** perform the proposed adoption.
