# Same-pose service access and reset source proposal

**Research proposal only; P1 remains INCOMPLETE.** The script pins the exact
expanded board, P1 source, floorplan, coarse contract, project/custom rules and
capacity helper through the preceding [capacity packet](../2026-09-25-expanded-service-timing-capacity-sol/README.md), then reopens native F.Cu pad shapes. Board SHA-256 is
`fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16`;
P1 source is `e8ff456de1868386890dbb5413bb20dc054b5d711b7c9b97d8b02a6b4695ae92`;
custom rules are `00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a`.
No board/source/rule byte was changed.

The four *authored* JTAG fixed-access chains use 0.15-mm F.Cu strips because
the connector pad escape is tight. All 19 strips across the four chains have
zero positive-area collision with another native F.Cu pad/body envelope or
another authored chain after a 0.15-mm clearance expansion. Naively widening
each strip around its center to the Default drawing width 0.20 mm causes:

| Chain | New native-pad collision | New other-chain collision |
| --- | --- | --- |
| `J_JTAG.2` / TMS | `J_JTAG.1` | none |
| `J_JTAG.4` / TCK | `J_JTAG.9` | TDO |
| `J_JTAG.6` / TDO | none | TCK, TDI |
| `J_JTAG.8` / TDI | `J_JTAG.10` | TDO |

The project minimum is **0.15-mm track width**, Default clearance is
**0.15 mm**, and its custom rules add no Default-class track-width minimum.
Default `track_width=0.20` is a selected drawing width, not proven to be a
DRC minimum. Therefore a 0.15-mm local trace is the same-pose candidate.
The rectangle test establishes room for a straight stroke envelope; it does
not prove corner joins, native track DRC, pad contact, return or fab yield.
Moving to 0.20 mm by simply widening the current source paths is a measured
no-go. Any alternative wider path would require a separate search.

The source gives `XU_RESET_N` five exact terminals but deliberately leaves
`reset_unresolved_tree` geometry-free: fixed `J_JTAG.10`, XU `.38`, and
three `digital_power` pads. Their native F.Cu boxes are in `result.json`.
`J_JTAG.10` is the leftmost north-row signal pad, which permits a new
two-segment 0.15-mm connector access: `[221.175,47.89,225.09,48.04]` then
`[221.175,48.04,221.325,65]` mm. It touches the pad's exact left edge and
the existing JTAG strip at y=65. The native-pad/body and all four authored
JTAG-chain clearance tests find **zero hits**. The JTAG trunk is 5.0 mm wide
and its XU-side face 2.8 mm wide; both have geometric room for a fifth
0.15-mm service track with 0.15-mm intertrack clearance.

A second source reservation is needed for the reset branch from
`digital_power` to `xmos_core`. The disjoint gap `[185,100,190,110.5]` mm
touches the digital-power east face at x=185 and XU-core west face at x=190.
Its native F.Cu body/pad scan and existing-reservation scan find **zero hits**;
after 0.15-mm obstacle and edge clearance it retains a 10.2-mm horizontal
aperture. This makes a one-net boundary window plausible on the same board.
The three digital-power pads sit at x=151.0..165.95, while XU `.38` is at
x=215.425..216.9, so local pad-to-face access on both sides remains P2 work.

The smallest source candidate is to preserve the four 0.15-mm JTAG accesses,
add the reset connector access as a fifth `fixed_connector_access_segmented`
declaration, extend `jtag_strip` to five nets and ten affected boundary
endpoints, and add a disjoint `board_integration_reset` cell/window for the
digital-power branch. Keep all five reset terminals and four tree edges in
the source denominator. The current schema may require a new explicit
two-corridor branch model for one shared XU endpoint; validate that before
promotion. The present source has no such reservation, and this packet does
not establish its pad-to-face routes, one connected tree, DRC, or filled
In1.Cu return. Thus it is a concrete P1 repair direction, not P1 admission.

Reproduce from the worktree root with KiCad 10 `pcbnew` and PyYAML:

```sh
/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-expanded-service-reset-access-sol/probe.py > /tmp/crow-service-reset-probe.json
cmp /tmp/crow-service-reset-probe.json projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-expanded-service-reset-access-sol/result.json
```
