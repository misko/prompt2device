# XU_RESET_N: five-terminal, three-owner branch audit

**Scope.** This is a source-and-native-candidate observation only.  It does
not change `03_src/`, a checker, a route authority, or an acceptance state.
The candidate is the isolated QSPI-gap board used for the measurement below;
it has no `XU_RESET_N` copper.  Consequently this note identifies the smallest
source-owned work split and the geometry that a later routed candidate must
prove.  It is not a P1 or P2 acceptance claim.

## Exact source contract

`03_src/rules/p1_corridor_requirements.yaml`, `xmos_service_escape`, names
exactly five physical endpoints on this net under three endpoint owners:

| Owner | Endpoint(s) | Physical count |
| --- | --- | ---: |
| `debug_connector` | `J_JTAG.10` | 1 |
| `digital_power` | `R_XU_RST_PU.2`, `U_CORE_OK.1`, `U_XU_3V3_OK.6` | 3 |
| `xmos_core` | `U_XU.38` | 1 |

The same record assigns `XU_RESET_N` to the five-lane `jtag_reset` demand:
`JTAG_TCK`, `JTAG_TDI`, `JTAG_TDO`, `JTAG_TMS`, and reset on `F.Cu`, at
0.45-mm pitch, with a 2.25-mm required width.  It says the reset handoff must
have a continuous GND reference and no **unrelated** branching.  It does not
name a reset tee, segment coordinates, a reset-only width, permitted vias, or
a filled-reference proof.

The region assignment is independently repeated by `floorplan.yaml`:
`J_JTAG` is `debug_connector`; the three supervisor/pull-up parts are
`digital_power`; and `U_XU` is `xmos_core`.  `modular_plan.json` repeats the
same endpoint/owner map and says that bias, pull, timing, and protection stay
beside the endpoint whose behavior they control.  These three source files
therefore agree on ownership, but none supplies route geometry.

## Candidate-board endpoint observation

Input board SHA-256:
`fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27`.
All five pads are on `F.Cu`; coordinates are millimetres in the board frame.

| Owner | Pad | Centre (x, y) | Local GND evidence |
| --- | --- | --- | --- |
| `debug_connector` | `J_JTAG.10` | (225.4600, 47.9650) | JTAG pads 3/5/9 at y=52.0350 are GND; pad 9 is vertically aligned at x=225.4600 |
| `digital_power` | `R_XU_RST_PU.2` | (170.7100, 100.4000) | no GND pad on this two-terminal pull-up footprint |
| `digital_power` | `U_XU_3V3_OK.6` | (165.6000, 109.0000) | `U_XU_3V3_OK.2` = GND at (164.4000, 109.5000) |
| `digital_power` | `U_CORE_OK.1` | (157.0625, 120.2500) | `U_CORE_OK.2` = GND at (157.0625, 121.2000) |
| `xmos_core` | `U_XU.38` | (216.1625, 104.2000) | `U_XU.40/42/43` = GND at the same x, y=103.4000/102.6000/102.2000; pad 129 is GND at (208.5000, 100.0000) |

The board contains **zero** `XU_RESET_N` segments, **zero** reset vias, and
no reset zone.  Its only GND zone is `F.Cu`, spans the board bbox
(20, 20)–(240, 140), and is unfilled.  Thus the nearby ground pads prove
endpoint availability only; they do not prove the required continuous return.
The source has only two relevant return reservations:
`gnd_digital_return` = (145, 85)–(185, 134) and
`gnd_xu_return` = (199.825, 91.325)–(217.175, 108.675).  There is no named
JTAG-to-XMOS return reservation.  A routed result must establish GND
continuity through all three regions, including the JTAG leg, from native
filled copper rather than from these reservations.

## Minimal decomposition

The source can require this ownership decomposition, and no smaller one:

1. A `debug_connector` launch at `J_JTAG.10`.
2. A `digital_power` local three-terminal fanout containing the pull-up and
   both supervisor outputs; no other owner may absorb the behavior of these
   components.
3. An `xmos_core` receiver escape at `U_XU.38`.
4. `board_integration` owns the cross-region joining geometry and its return
   proof because `xmos_service_escape.owner` is `board_integration`.

There are five terminals, so any connected, cycle-free realization has at
least four branches.  The source does **not** identify their junction(s).
In particular, the digital three-terminal group cannot be represented as a
single two-endpoint corridor; it needs a local tree with two or more branches,
then one connection into the inter-region tree.  A tee on this same reset net
is compatible with the source's "no unrelated branching" wording; a branch
onto another net is not.

For orientation only, the Euclidean terminal MST lower bound is 126.7358 mm:
`J_JTAG.10–U_XU.38` 56.9984 mm,
`U_XU.38–R_XU_RST_PU.2` 45.6111 mm,
`R_XU_RST_PU.2–U_XU_3V3_OK.6` 10.0036 mm, and
`U_XU_3V3_OK.6–U_CORE_OK.1` 14.1227 mm.  These are straight-line lower bounds,
not a proposed route, corridor reservation, clearance result, or length rule.
They are useful only to show why the three digital terminals require a local
branch rather than a fictitious single endpoint.

## Native geometry required before a route can be accepted

* Show every reset segment and any tee on allowed layers, with the five named
  pads physically connected and no unintended branch/cycle.
* Show the reset lane's coexistence with the four JTAG lanes inside the declared
  2.25-mm `jtag_reset` demand, including pad escapes and all component bodies.
* Show a continuous filled GND reference beneath the actual signal path,
  including the presently unreserved JTAG-to-XMOS span; nearby pads and a
  source bbox are insufficient.
* Show via count, stub length, clearance, and the exact board bytes used for
  the observation.  The present source declares none of those reset-specific
  limits, so they require an explicit later decision or checker input.

## Reproduction

Run this read-only probe from a KiCad-10 Python environment, substituting the
isolated board path if it has been copied elsewhere.  It prints the endpoint
centres and every existing reset track/via; on the audited artifact it prints
five pads and no copper items.

```sh
python3 - <<'PY'
import pcbnew
b = pcbnew.LoadBoard('/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb')
n = b.FindNet('XU_RESET_N').GetNetCode()
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetNetCode() == n:
            q = p.GetPosition()
            print(f'{f.GetReference()}.{p.GetNumber()} {q.x/1e6:.4f} {q.y/1e6:.4f}')
for t in b.GetTracks():
    if t.GetNetCode() == n:
        print('via' if isinstance(t, pcbnew.PCB_VIA) else 'segment', t)
for z in b.Zones():
    if z.GetNetname() == 'GND':
        print('GND zone', z.GetLayerName(), 'filled=', z.IsFilled())
PY
```

Source input SHA-256 values at observation: `p1_corridor_requirements.yaml`
`9ef85e5f4918dea0378203a97fa631ce2e73a690170235902a97a6c8e30527d8`;
`floorplan.yaml` `cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925`;
`modular_plan.json` `7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e`.
