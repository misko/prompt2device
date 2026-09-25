# TI board P1 coarse-contract source screen — 2026-09-25 UTC

**Research candidate only.** `2026-09-25-ti-p1-coarse-candidate-sol.json`
(SHA-256 `fb45b7407f6d171eac031016e3a5612a8b8c73951147d5bc493119a2b83876ab`)
rebases the old unified 59-net geometry specimen onto the fresh private TI
unrouted board (SHA-256
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`).
It binds current P1 requirements
`191e5580a6ddf56bc9670aff3593c9e9a02d91e75c0c79998b500955050e82a3`,
modular interfaces
`75c3a517cea50dd6b5745fae96b051d334debd48aac143becaca3d5fe3fc35dc`,
USB pad aliases
`a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e`,
and floorplan
`0032b1202f5742b6575198d27ea50629826d49cf81cf12a31fead8a2929d9868`.
The candidate retains `status: INCOMPLETE`, `p1_accepted: false`, and
`routing_realized: false`.

The rebased XMOS service row uses the current disjoint QSPI, compact XTAL,
and JTAG corridor faces and physical-cell identities. It replaces the old
point-to-point reset reservation with the current exact five-terminal,
geometry-free unresolved branch and its P2/P3 obligations. The other rows
retain diagnostic USB, ADC/timing, analog, and ten power/mechanical boundary
windows from the old specimen for **rejection screening**, not source truth.
Ten boundary nets comprise CHASSIS plus nine ground/power/control nets.

Run the schema-2 checker with the exact board, candidate, source requirements,
modular plan, USB4215 dossier and floorplan, and the SHA-256 values above as
its five independent expected digests. The retained machine-readable result
`2026-09-25-ti-p1-coarse-evaluation-sol.json` has SHA-256
`19c45da36cb65d321ae80eb81062c3ef3aa11c2ecfd124a741d6f9492d76fa60`.
From the repository root, the exact command is:

```sh
python3 skills/kicad-pcb/scripts/p1_corridor_capacity.py \
  projects/crow-usb-carrier-v1/06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project/04_kicad/crow_carrier.kicad_pcb \
  projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-p1-coarse-candidate-sol.json \
  projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-p1-coarse-evaluation-sol.json \
  --expected-contract-sha256 fb45b7407f6d171eac031016e3a5612a8b8c73951147d5bc493119a2b83876ab \
  --source-requirements projects/crow-usb-carrier-v1/03_src/rules/p1_corridor_requirements.yaml \
  --interfaces projects/crow-usb-carrier-v1/03_src/modular_plan.json \
  --aliases projects/crow-usb-carrier-v1/02_parts/USB4215-03-A/part.yaml \
  --floorplan projects/crow-usb-carrier-v1/03_src/floorplan.yaml \
  --expected-source-sha256 191e5580a6ddf56bc9670aff3593c9e9a02d91e75c0c79998b500955050e82a3 \
  --expected-interface-sha256 75c3a517cea50dd6b5745fae96b051d334debd48aac143becaca3d5fe3fc35dc \
  --expected-alias-sha256 a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e \
  --expected-floorplan-sha256 0032b1202f5742b6575198d27ea50629826d49cf81cf12a31fead8a2929d9868
```

It returns nonzero and `INCOMPLETE`, with **zero global errors** and all five
allocation rows present:

| Allocation | Current result |
| --- | --- |
| USB device, four nets | `J_USB.4` witness is a nonlocal bridge across the source region. The connector edge/support ownership and FULL exception remain unresolved. |
| XMOS service, 13 nets | 29 witnesses / eight reservations are structurally coherent. QSPI, XTAL, JTAG access and reset each remain `INCOMPLETE` for local pad-to-face, effective capacity, filled return or tree realization. |
| ADC timing/XMOS, 14 nets | `U_ADC_A.22` is P2-movable and requires a virtual block-face witness. |
| ADC analog, 18 nets | `C_ADC_AC1N1.2` witness is a nonlocal bridge. |
| Power/mechanical, ten nets | `C_ADC_3V3X_OK_VDD.2` witness is a nonlocal bridge; current/thermal/return capacity is unproved. |

A separate temporary mutation removed `PWR_EN` from the power coverage list.
The checker returned nonzero and reported exact source-net coverage mismatch,
so a missing boundary net cannot silently earn credit. The mutation was
discarded. The positive candidate's expected contract digest was computed
locally for this diagnostic run; it is **not** an independent P1 admission.

Canonical `03_src/rules/p1_corridor_requirements.yaml` remains unchanged:
the four allocation geometries stay null and no power window is promoted.
Its source is not ready for a P1 attempt. The next bounded source repairs are
the fixed USB connector edge handoff, valid virtual ADC/timing and analog
faces, and power boundary witnesses inside their own regions; each must then
be remeasured on the same saved board with independent expected hashes and
filled-return/DRC evidence. No route, copper, acceptance or campaign slot was
created by this screen.
