# Crow P1 two-island preparation (read-only, 2026-09-23)

Source inspected at root worktree HEAD `4d08db43` (which had unrelated live uncommitted changes). No PCB or placement producer was run. P1 remains behind the accepted S6 schematic/render gate.

## Minimum source change after S6

The retained capacity study is sound as a **first trial**: the existing quiet-power region is 50×29 mm while 16 exact Panasonic EEEFK1A471P courtyards total 1,596.16 mm², already more than its 1,450 mm² area. The native footprint courtyard is 11.6×8.6 mm, pad 1 positive at local x=-3.55 mm, pad 2 at +3.55 mm. The existing 69-ref `quiet_power` block comprises exactly `C_HOLD1`…`C_HOLD16` plus 53 support refs; `adc_reference` owns 64 refs. Keep the block ownership and net interfaces in `modular_plan.json` unchanged: the physical islands do not create new electrical blocks.

Edit only `03_src/floorplan.yaml` for the initial trial:

1. Add named documentary regions `hold_bank_left: [24,113,74,137]` and `hold_bank_right: [76,113,126,137]` if useful for review. **Regions only yield their center as a starting pose; they do not constrain legalizer movement.** The current broad `quiet_power` pattern still matches all 69 and would otherwise start all cans at the same region center.
2. Use existing `placement.anchors` for all 16 cans, rotation 0 (pad 1 positive to the left), four columns × two rows per island. A courtyard-valid 0.5 mm gap grid: x centers `[30.85,42.95,55.05,67.15]` for `C_HOLD1`–`C_HOLD4` at y=120.45 and `C_HOLD5`–`C_HOLD8` at y=129.55; x centers `[82.85,94.95,107.05,119.15]` for `C_HOLD9`–`C_HOLD12` at y=120.45 and `C_HOLD13`–`C_HOLD16` at y=129.55. Courtyard extents are x25.05–72.95 and x77.05–124.95, y116.15–133.85. These are proposed *centers to test*, not accepted placement or proven copper access. `anchors` are pinned by default; seeds would allow the legalizer to evict cans and would not reserve the islands.
3. Remove `C_HOLD1`…`C_HOLD16` from the broad quiet-power pattern and add exact can match patterns with the two island regions for traceable intent (anchors still control actual positions). Seed rather than pin `D_HOLD`, `R_PRE`, `Q_PRE`, `Q_PRE_EN` near the left bank/buck feed, and `U_LDO`, `C_LDO_IN`, `C_LDO_OUT_*`, `R_LDO_SET`, `C_LDO_NR*` near the right bank/ADC supply boundary. Those refs stay in `quiet_power`; avoid expanding the 20-ref `input_buck` region or disturbing analog-channel y≤84 on the first trial. The remaining 53 support refs need visible legalized room; a region name cannot guarantee this.
4. The right island overlaps the upper part of current `adc_reference` x75–145/y85–134. Move the *initial seeds* for `U_ADC_A`, `U_ADC_B` and their local AVDD/IOVDD/AREG/DREG/VREF bypass, plus VMID and input handoff, into the lower/right ADC area before judging capacity. Do not simply shrink the ADC region and claim its 64 refs fit. Keep ADC bypass pinned/placed near its served pins during P2; retain the analog differential handoff below the can row and keep the upper-right x126–145 slice available. Exact ADC/support coordinates require a native trial and inspection.

Supported schema and precedence are explicit in `generate_board_generic.py`: `placement.anchors {REF:[x,y,rot]}` wins and pins by default; `seeds {REF:[x,y]}` starts a floating footprint; first matching `patterns[].region` yields only the region center; `patterns[].near` can start at a target anchor; `placement.legalize` uses courtyard clearance 0.25 mm, edge margin 1 mm, and searches up to its configured ring limit. `post_anchors` exist but should not be used to hide an initial legalization conflict. No new island-confinement knob exists in this schema.

## Native trial and P1 record, only after S6 admission

From the project directory, first bind the exact accepted Circuit JSON to the unchanged modular ownership graph:

```sh
python3 ../../skills/pcb-design/scripts/modular_design.py 03_src/modular_plan.json 03_tscircuit/build/circuit.json --json 06_build/modular/coverage.json
```

(Use the repository-root absolute script path if the relative `../../skills` path is unavailable; from `projects/crow-usb-carrier-v1`, `../../skills` resolves correctly.) Require coverage PASS with 568/568 singly owned refs and exact crossing-net dispositions; this is not geometry admission.

For a native scratch P1 placement, using the accepted netlist and proposed floorplan:

```sh
/usr/bin/python3 ../../skills/kicad-pcb/scripts/generate_board_generic.py 03_src/floorplan.yaml --netlist 06_build/netlists/crow_carrier.net -o 06_build/modular/p1_trial.kicad_pcb
```

This invokes the same native KiCad `pcbnew` generator as canonical `rebuild_all.sh` stage [3], including its legalizer, without writing canonical `04_kicad/crow_carrier.kicad_pcb`. Create `06_build/modular/` before invoking. Generator success proves only that it found positions; inspect actual courtyard/mask/assembly, mounting-hole/edge clearance, cap pad-1 polarity, 53 quiet-power and 64 ADC-reference support positions, analog input return corridor, D_HOLD→precharge→bank→LT3045 return, LT3045 thermal/Kelvin and ADC bypass proximity. Re-run the owning placement, pin-map, model, geometry and DRC gates against the promoted candidate as in `rebuild_all.sh` [3]–[5] before placement admission; do not route from the scratch board.

`modular_plan.json` declares P1 item `p1_floorplan_all`, stage `KICAD-PLACEMENT`, max 2 attempts, output name `06_build/evidence/modular_work/p1_floorplan.json`. The generator does **not** create that P1 receipt. Record measured island/courtyard/remaining-support results and exact source/board hashes in that evidence file as the output of a bounded `TaskAttempt` with `modular_design.work_subject(plan,circuit)`; put it in the runtime's `outputs/` completion manifest and list the attempt path in an observations index. Reopen with `modular_design.py --observations INDEX --evidence-root PROJECT`. Its `WORK_RECORDED` means delivery only (`engineering_acceptance: NOT_EVALUATED`), so P2 may start only after P1 geometry is independently reviewed against the real placement/DRC gates and S6 remains valid. All P2 items depend on `p1_floorplan_all`; a failed P1 attempt backtracks under its two-attempt bound.

`route.yaml` is a later routing contract, with no P1 island knob. Leave route waves/keepouts unchanged for this trial. P2 must establish supported ADC, hold-bank, buck and return geometry; P3/P4 can then prove local rail loss, waveform/discharge and coupled corridors before P5 integrated placement review. No accepted PCB placement currently exists to reuse.

## Native trial correction (2026-09-23)

The first actual invocation disproved the scratch output-path assumption above: source `model_override` entries resolve `${KIPRJMOD}` relative to the generated board parent, so writing directly under `06_build/modular/` cannot resolve the project-relative 3D models. Generate an isolated trial under that isolated project's `04_kicad/` and preserve the exact bytes as runtime output; reopen it at its original relative location for model inspection. Do not repair generated model URIs by hand.

The next invocation exposed an upstream native pin-alias consumption defect: the accepted USB netlist uses logical pins 1–17 while its native footprint uses A/B/SH names. The existing exact dossier and parity map already describe those aliases. Shared generator repair is being independently reviewed; an alias-normalized scratch netlist is diagnostic only and cannot substitute for the accepted producer path. Neither failed invocation establishes native placement feasibility.
