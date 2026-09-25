# Private 4L 3313A unrouted diagnostic

**Planning only.** No board was regenerated or routed, no canonical source
changed, and this grants no P1/P2/P3, connector FULL, D13, fabrication,
assembly, order, or release credit.

## Authority boundary

D13 permits a `PROTOTYPE_ONLY` schematic subject and D14 permits an unrouted
private geometry diagnostic from the *current* TI inputs. D14 pins the current
7628G stack and its sidecars. A 3313A dielectric and thickness change is thus
outside that input authority even if the resulting board has no copper.
D11 still prohibits route preparation/import and routing before connector
FULL. A new decision must authorize one ignored, private **unrouted stack
screen** only, bind expanded board `fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16`
as pose/outline reference, require independent pre/post review, and forbid
canonical writes, fabrication exports, accepted pointers and stage credit.

## Required private-copy edits

The public solver packet is
[`2026-09-25-jlc-3313-uniform-usb-solve-sol`](2026-09-25-jlc-3313-uniform-usb-solve-sol/README.md).
It provides a cross-section calculation, not an adopted stack: special
`JLC04161H-3313A`, finished target 1.58 mm ±10%, 1-oz outer/0.5-oz inner,
L1--L2 0.2064 mm (`0.107 + 0.0994`), Er 4.1, and an 0.180-mm artwork-width /
0.100-mm gap result of 89.9172598796 ohm. The public request has `HZ0=108`
whose meaning is not recorded; call this a fixed-geometry result, never a
vendor 90-ohm recommendation.

| Private copied input | Scratch-only change | Retained unchanged |
| --- | --- | --- |
| `03_src/floorplan.yaml` | Set stack nominal/tolerance to `1.58/0.158 mm`; both outer dielectric rows to `0.2064 mm`, `NP-155F 3313 RC57% 4.2mil composite; JLC04161H-3313A`, Er `4.1`; core dielectric to `1.065 mm`, Er `4.38`. Retain four layers and final copper entries `0.04064/0.0152/0.0152/0.04064`. | Outline, all footprint/hole anchors, netlist, layer order, parts and thermal-via coordinates. |
| `03_src/rules/nets.yaml` | Add a **private exact-net, F.Cu-only** USB_DP/USB_DN pair rule: width `0.180`, pair gap `0.100`, while retaining 0.150 mm to every foreign net, pad, via and zone. Do not relax the generic `USB_HS.clearance`. | Defaults, every other class, current/thermal rules and existing pad exceptions. |
| Private RF/route-contract copy | Replace only locked 7628G cross-section facts with the named 3313A inputs/result; mark `PRIVATE_UNROUTED_SCREEN`. Retain 90-ohm intent, no-via tree, 1-mm skew and continuous-In1 requirements as unpaid obligations. | Canonical `rf.yaml`, `route.yaml` and accepted contracts. |
| Private `route_fab_overrides.txt` | Update only its explanatory aspect-ratio text: existing 0.20-mm drill is 7.90:1 at 1.58 mm and 8.69:1 at 1.738 mm. | Actual drill geometry and all process rules. |

The existing USB rule is 0.410/0.150 mm on 7628G. At the 0.400-mm XU pitch
and 0.250-mm pad width, a centered 0.180-mm trace leaves 0.185 mm to its outer
neighbor. That local screen is not a route proof. Its 0.100-mm pair gap sits
only 0.010 mm above JLC's published 0.09-mm multilayer minimum and must stay
pair-specific.

## Unrouted scratch sequence

1. Freeze the private expanded board, TI schematic/netlist receipt, connector
   contract, JLC JSON, private input copies, generator, KiCad version and rule
   seed. Obtain the separate decision and preflight.
2. Create one ignored output, apply only the table edits, and regenerate PCB,
   `.kicad_pro`, `.kicad_dru` and TMUX POFV there. Do not save filled zones,
   add tracks/vias/teardrops, or export manufacturing files.
3. Compare expected-only differences. Stack and narrow USB-pair rule may
   change; exact 569 electrical poses, 1,810 electrical pads, six holes,
   eleven connector poses, outline, net identities, footprint shapes and all
   non-USB rules must remain equal to the expanded reference.
4. Run count/pin/net parity, V-PROCESS and native DRC. Record the full open
   count and violations. Treat schematic parity as a result only if the
   hash-bound private schematic check completes; an empty list after a failed
   netlist fetch is not a pass.
5. Screen the proposed envelope at XU pads 59/60, TPD2EUSB30A and both fused
   Type-C leaves. It must show the 0.150-mm foreign clearance, mask-dam
   clearance and required fan from 0.400-mm pad centers to solved spacing.
   With no copper, this can reject geometry only; it cannot prove SI, return,
   skew or routing.
6. Record the 3313A 1.422--1.738-mm ±10% range against the present
   1.467--1.793-mm range. This overlap does not prove connector shell/cable,
   M3/fixture, enclosure, seating, registration or connector FULL behavior.
7. End with a receipt marked `RESEARCH_UNROUTED_STACK_SCREEN`, all acceptance
   and route flags false, and no fabrication payload. Reject unexpected input,
   geometry, copper, zone, rule or write-path changes.

Before any source proposal: bind a JLC quote for special-stack availability,
Standard-PCBA path, thickness/copper/mask/finish/price and impedance
commitment; clarify the calculator mapping; prove pad-fan/ESD/connector and
return geometry; then revalidate all stack-dependent power, analog, via,
thermal and POFV behavior. Coupon/TDR, USB eye, connector FULL and D13
transient evidence remain separate gates.
