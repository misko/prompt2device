# Crow DLC/USB composed circuit JSON semantic comparison (read-only)

**Verdict:** The new source-domain circuit JSON matches the archived pre-DLC/USB baseline except for the intended three TPS62822 regulators, six Samsung input capacitors, one Viking feedback resistor, and one USB4215 connector identity. This is a semantic delta audit, **not** E-FAULT approval, native schematic/PCB parity, DRC, routing, or board acceptance.

Inputs (both read-only):

- Archived `06_build/verification/pre-dlc-usb-source-baseline/03_tscircuit/build/circuit.json`: SHA-256 `cf78dcb8d8c1fc7f696d6f5eaad20a0175c6b27ae0c193d6e1b67bb8937e9193`.
- New `03_tscircuit/build/circuit.json`: SHA-256 `416d4f78a8ae2e7040c51194d97dee7af424580e4acf8dc0e36d9c7b975a20da`.
- Project root: `/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1`.
- Reproducible normalized comparison script: `/tmp/crow_cj_semantic_compare.py`; full machine delta: `/tmp/crow-dlc-usb-semantic-bridge-sol.json`.

## Exact delta

Both files have 568 source components and 282 source nets with identical names **and full source-net records**. Exactly 11 source-component records change, with only `manufacturer_part_number` and `supplier_part_numbers.jlcpcb` changed; all other source-component attributes are identical after excluding generated internal port IDs on the USB shell group:

| Refs | Count | Old exact MPN / JLC | New exact MPN / JLC |
|---|---:|---|---|
| `U_3V3X`, `U_1V8`, `U_CORE` | 3 | TPS62825DMQR / C2650334 | TPS62822DLCR / C473385 |
| `C_U_{3V3X,1V8,CORE}_IN_{1,2}` | 6 | CL21A106KOCLRNC / C318695 | CL21A106KOQNNNE / C1713 |
| `R_3V3X_FB_TOP` | 1 | RT0603BRD07453KL / C861412 | ARG03BTC4533 / C2686428 |
| `J_USB` | 1 | USB4105-GF-A-120 / C5184243 | USB4215-03-A / C37616412 |

The only changed `source_port` records belong to the three regulators. For each:

| Physical DLC pin | Source function | New source net |
|---:|---|---|
| 1 | EN | `N5V_BUCK` for `U_3V3X`/`U_1V8`; `CORE_EN` for `U_CORE` |
| 2 | FB | matching `U_*_FB` |
| 3 | AGND | GND |
| 4 | NC | unconnected |
| 5 | PGND | GND |
| 6 | SW | matching `U_*_SW` |
| 7 | VIN | `N5V_BUCK` |
| 8 | PG | unconnected |

Thus six source ports are added (two per regulator), and three source traces are added (second ground pad per regulator). There are 12 removed and 15 added normalized trace endpoints, **all on the three regulator refs**; each removed endpoint is the old physical pin assignment for FB/GND/SW/VIN, and the new endpoints carry the same named electrical nets. All 1,624 other source trace endpoint/net pairs are identical. All seven normalized `source_component_internal_connection` groups are identical, including the XMOS internal power-port grouping. `source_net` count/name/record identity is unchanged. Source component count, ref set, source group count, and net set are unchanged.

## Preserved safety and interface topology

Full normalized source-port records outside the regulator refs are identical. In particular:

- `J_PWR.1` and `F_IN.1` remain `N12V_IN`; `F_IN.2` and `Q_IN.5` remain `N12V_FUSED`; Q_IN source pads 1–3 remain `N12V_PROTECTED`, gate 4 remains `Q_IN_GATE`. Q_IN retains exactly five source ports. `D_IN` cathode/anode remain `N12V_PROTECTED`/GND. The fuse/reverse-polarity path is unchanged at the source net/port level.
- `J_USB` retains the same 20 source ports and their nets despite its exact MPN/supplier change: four VBUS pads remain only on `VBUS_USB`, GND/shell on GND, CC1/CC2 on their separate nets, both DP pads on `USB_DP`, both DM pads on `USB_DN`, and SBU1/SBU2 remain open. `VBUS_USB` remains a distinct source net from `N5V_BUCK`. `R_USB_CC1/2`, `R_VBUS_B`, `Q_VBUS`, and `U_USB_ESD` source pin/net assignments are unchanged. This establishes no new source-level direct USB VBUS power feed; it does not independently prove physical isolation on a board.
- `U_XU` retains all 129 normalized source-port records and source nets, including USB pins and rails. No XMOS source port/net assignment changed.

The source schematic records rise from 1,776 to 1,782 ports and 765 to 768 traces, consistent with the source-port/ground changes. Schematic layout metadata and generated IDs were not used as semantic identity.

## Boundary

The producer result reported by the coordinator was PASS with advisories, but this audit grades only the two supplied circuit JSON files by their verified hashes. The new CJ intentionally has a different digest; E-FAULT must be reviewed and repinned through its owning process. Native schematic/PCB parity, exact physical USB pad aliases, capacitor effective margin, thermal/sequence behavior, placement, routing, and P1 gates remain independent downstream checks. No accepted source or generated design file was modified by this audit.
