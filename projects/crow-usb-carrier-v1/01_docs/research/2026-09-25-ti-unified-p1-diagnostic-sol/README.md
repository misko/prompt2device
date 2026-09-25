# Unified Crow P1 diagnostic on one native research board

**Research-only FAIL; P1/P2/P3 remain unaccepted.** `build_trial.py` reconstructs this packet from the exact 15-footprint channel-8 candidate (`d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`). That board was replayed from the four-part ADC7 placement board; the source board, fixed connector poses, and USB geometry are unchanged by this packet. The builder pins and verifies the hashes of the board, USB/VBUS base source and contract, floorplan, modular interface, ADC7 portal, aliases, and checker before any output. It writes only this packet, never canonical Crow source or PCB.

This is the first combined native replay of the existing USB DP/DN linked two-physical path and exact VBUS/presence trees, 18-net ADC analog denominator, eight-terminal ADC7 access-only portal, and 14-net ADC timing denominator on **one** board. The base USB linked path and two geometry-free trees are copied unchanged. Analog and timing legacy ordinary reservations are removed; no scalar capacity is substituted. Every native F.Cu terminal is checked against exact source/modular owner, net, alias, uniqueness, and entire native per-net pad set. The builder regenerates exact branch records only where the current board meets the existing three-terminal and owner-containment requirements.

| Family | Exact denominator on this board | Checker state |
| --- | --- | --- |
| USB | One linked DP/DN path; VBUS 8/8 and presence 3/3 exact tree terminals | `INCOMPLETE`, no USB item diagnostics |
| ADC analog | 18 nets, 88/88 exact terminals; all 18 now fit unplaced branches | `INCOMPLETE`, no analog item diagnostics |
| ADC7 local portal | ADC7N/P, 8/8 exact terminals, eight P2 duties and In1.Cu return debt | `INCOMPLETE`, null capacity |
| ADC timing | 14 nets, 54/54 exact terminals; nine fit unplaced branches | `FAIL` |
| XMOS service | Existing three integration corridors retained | `INCOMPLETE` |
| Power boundary | Existing witnesses retained | `INCOMPLETE` with nine item diagnostics |

The 15 channel-8 placement moves change the analog classification materially: all eight `R_B1P`…`R_B8P` VMID pads now fit their true owners, so both VMID nets join the 16 ADC N/P nets as valid **geometry-free** unresolved branches. This does **not** prove VMID routing, capacitance, copper capacity, or return. `AUDIO_EN` still has three exact owner-region failures: `R_AUDIO_PD.1` and `U_AUDIO.6` west of `quiet_power`, and `U_ISO1.2` west of `analog_ch1`. `U_ISO8.2` is now inside `analog_ch8`, so the earlier fourth failure is gone. The four two-terminal `AUDIO_MCLK_1V8` and `TDM_*_1V8` nets remain outside the branch schema; no invented third terminal or unsupported capacity was added.

The full checker returns `FAIL`, `routing_realized=false`, `p1_accepted=false`, **nine global errors** and **nine item diagnostics**. The timing allocation lacks five per-net witnesses: four two-terminal schema gaps plus `AUDIO_EN` owner containment. Its nine otherwise valid branch representatives then produce nine derivative global denominator errors because allocation credit is all-or-nothing. The nine independent item diagnostics are legacy `power_boundary_windows` witnesses: eight nonlocal bridge bboxes and one P2-movable-owner witness lacking a virtual block face. `issues.json` lists every exact pad, error, allocation reason and category. The total is **14 primary source/accounting entries** (five timing nets plus nine power witnesses), with nine derivative global errors; the unrouted USB, analog, portal, service, timing, and power P2/P3 work remains open.

The ADC7 portal reports null capacity and no reservation conflict here because the old `analog_5_8` ordinary reservation was removed as part of exact analog branch accounting. It grants no shared-route capacity and does not waive foreign footprint/pad or filled-return proof. The source still needs actual local pad entry, connected traces, USB launch authority, continuous filled In1.Cu return and service/analog/timing placement and route evidence. The channel-8 fixed J8 pocket/overhang issue is separately recorded in `2026-09-25-ti-ch8-owner-pocket-review-sol.md`; this packet does not claim typed channel-8 physical-cell acceptance.

Reproduce from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-unified-p1-diagnostic-sol/build_trial.py
```

The replay writes `p1_requirements.yaml`, `coarse.json`, `floorplan.yaml`, `modular_plan.json`, `endpoint_ledger.json`, `issues.json`, and `result.json` deterministically in this directory. Their source and contract hashes are `f6f132891712bfcb1cec4d1df6714748337040ba5c42ae3fecd14fb9c35d1222` and `18936dc3f3dd6e01637182b2dab57cb472a31bfa2eb345a20bd4f7867708777f` respectively. The replay asserts all five allocation states, portal no-credit status, one USB linked path, nine global and nine item findings, and P1 rejection.
