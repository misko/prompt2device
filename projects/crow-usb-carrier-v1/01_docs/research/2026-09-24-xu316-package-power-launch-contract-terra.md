# XU316 package-wide power-launch contract — independent review (Terra, 2026-09-24)

**Scope.** This reviews SOL's census commit `84919f44` and derives a
project-owned future-routing contract.  It neither enables a source declaration
nor accepts a route, decoupling placement, P1, or production board.

## Census result

On the cited isolated saved board, PCB SHA-256
`d7ebbc8bb55bee39469f573cb7fa0c7885e4b71b04668106f00d26449cad3310` and
companion DRU SHA-256
`60593deeb18805231e00140abd2a9795b343cb8e509934908cbe1b124656266c`, I
independently enumerated every `U_XU` pad on `N0V9`, `N1V8`, `N3V3X`,
`PLL_0V9`, or `GND`.  The native set and the retained
`/tmp/crow-xu-power-witness.json` set are identical: 34 pads = 15 `N0V9`, 9
`N1V8`, 1 `N3V3X`, 1 PLL, and 8 GND.

The 25 `DIGITAL_POWER` supply pads are exhaustive for that board and current
net-class declaration:

| rail / XMOS roles | exact pads | current P-LAND result |
| --- | --- | --- |
| `N0V9` / `VDD` | 5, 11, 14, 18, 39, 45, 50, 54, 68, 85, 95, 104, 105, 106, 113 | `.14` 0.15-mm scoped witness; `.105` 0.60-mm ordinary witness; remaining 13 unresolved |
| `N1V8` / `VDDIOL`, `VDDIOB18`, `USB_VDD18`, `VDDIOR`, `VDDIOT` | 10, 17, 35, 56, 62, 72, 89, 109, 121 | `.17` 0.15-mm scoped witness; remaining 8 unresolved |
| `N3V3X` / `USB_VDD33` | 61 | unresolved |

Thus 3 of 25 have a finite witness and **22 are unresolved**: 5, 10, 11, 18,
35, 39, 45, 50, 54, 56, 61, 62, 68, 72, 85, 89, 95, 104, 106, 109, 113, 121.
The 9 other census pads (`PLL_0V9` and GND) have no declared P-LAND width;
that is out of scope, not a pass.  The count is limited to these exact hashed
inputs: any netlist, footprint, class, or generated-rule change requires a
fresh census.

## Source boundary

XMOS **XM-014532-PC v2.0.0**, §14 and Appendix I.2 (retained
`02_parts/XU316-1024-TQ128-C24/XM-014532-PC-v2.0.0.pdf`, SHA-256
`a2ce2dc835df06793a4e1aa6c5d226c6a01c25c979a63b09a2b57059c17321cf`; public
[manufacturer record](https://www.xmos.com/documentation/XM-014532-PC/html/))
says all supplied pins must be connected; VDD needs at least twelve 100 nF
low-inductance MLCCs close to the chip; VDDIO needs several such capacitors
close to the chip (one 100 nF 0402 per supply pin is an example); and each
capacitor ground side needs a direct path to the device centre ground.  It
also requires at least 10 uF bulk on VDD and VDDIO.  It gives **no** launch
width, neck length, capacitor-to-pin distance, via-count, or return impedance
limit.

The retained public JLC record says the selected multilayer 0.5/1-oz capability
is 0.09/0.09-mm trace/space ([JLC capability page](https://jlcpcb.com/capabilities/Capab),
recorded in `2026-09-22-usb-impedance-evidence.md`).  A 0.15-mm neck is above
that process minimum, but this is fabrication feasibility only.  It is a
project geometry choice, not an XMOS current or decoupling qualification.

## Project-owned package contract

Every one of the 25 exact pads must have one recorded disposition on a single
saved, refilled native board:

1. an ordinary 0.60-mm F.Cu launch witness, or
2. a declared exact-pad exception: `U_XU.<pad>`, its exact net, one named local
   capacitor/filter supply pad on that net, F.Cu only, a bounded pin-to-flare
   window, and a named flare point.

The exception requires a contiguous 0.15-mm path from that exact XU pad to its
flare, wholly inside its own window.  The named capacitor is beyond the flare;
the window cannot silently cover the capacitor branch.  From the flare onward,
the existing 0.60-mm `DIGITAL_POWER` floor applies.  No exception may use a
net wildcard, package-wide selector, alternate reference, other layer, via,
branch, foreign-net copper, or another thin track inside its window.  `.105`
already has the ordinary witness and needs no thin exception.  `.14` and `.17`
are examples of scoped candidates only; their existing witnesses do not
approve the other 22 entries.

For each named capacitor, archive the complete supply path from the capacitor
supply pad to the named XU pin and independently archive the complete GND-pad
return to the centre ground/ground-pin network: every track, via, layer, and
filled-zone connection.  Native DRC and netlist parity must contain no relevant
short, clearance, or unconnected finding.  The contract does not assume that
a shared return via is acceptable: its branch/current coupling must be visible
in the extracted topology and receive separate qualitative XMOS review and
first-article measurement.  The VDD/VDDIO 100-nF population and >=10-uF bulk
ownership must also be demonstrated at rail level; a local launch does not
satisfy those requirements by itself.

`PLL_0V9` is deliberately excluded.  It needs an explicit normal class and a
separate `U_XU.41` filtered-supply/`U_XU.42` return contract before any narrow
launch is considered; it must not inherit this digital-power waiver.

## Required negative evidence

The producer and its native tests must reject: unknown/duplicate pad, wrong
net/reference/target, wildcard selection, wrong layer; a window missing the
actual XU pad or flare; a widened/relocated window; a target capacitor inside
the window; an offsite narrow segment; a partially crossing segment; a
narrow branch/gap or missing 0.60-mm continuation; and foreign copper or any
via touching the window.  Tests must also prove that ordinary 0.60-mm tracks
remain required outside every window and that a changed board/DRU/netlist hash
invalidates the evidence.  Exact-board native DRC, parity, copper extraction,
and a reviewable render are required positive evidence; a P-LAND finite
witness alone is not a route, return, or current proof.

First article must measure each rail at the XU pin against its local ground
through power-up, reset release, and worst credible switching load, retain the
probe method and raw waveforms, and verify the applicable XMOS voltage and
sequencing requirements.  For any topology with common return copper/via,
measure the rails under independent and simultaneous load transitions and
retain the coupling result.  No numerical ripple, impedance, path-length, or
via-count acceptance limit is asserted without a source-owned specification.
