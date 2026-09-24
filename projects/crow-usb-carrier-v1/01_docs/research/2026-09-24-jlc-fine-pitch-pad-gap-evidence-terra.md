# JLC evidence for Crow fine-pitch pad gaps — 2026-09-24

This is a public-document and local-record review of the isolated board in [the native-clearance triage](2026-09-24-p1-native-clearance-triage-terra.md). It proposes no source change and does not approve fabrication, assembly, P1, or a purchase.

The exact intended stack is a four-layer JLC JLC04161H-7628G path with **1 oz outer and 0.5 oz inner copper**, recorded in [rf.yaml](../../03_src/rules/rf.yaml) and the cloned `03_src/floorplan.yaml`. The public [JLC rigid capability table](https://jlcpcb.com/capabilities/Capab) states 0.10 mm multilayer 1-oz track spacing, but separately specifies **0.15 mm different-net SMD-pad-to-SMD-pad clearance**, 0.10 mm pad-to-track clearance, and 0.09 mm only locally for BGA pad-to-trace. These are distinct rows; a pad-to-track or BGA-pad-to-trace limit is not evidence for BGA-pad-to-pad or via-to-SMD-pad clearance.

| Measured native relationship | Count | Fabrication result | Mask / assembly result |
| --- | ---: | --- | --- |
| Same-footprint 0.150 mm: `U_XU` 121, `U_ISO1`–`U_ISO8` 64, `U_ESD1`–`U_ESD8` 16, USB ESD 4 | 205 | Meets JLC's published 0.15-mm different-net SMD pad-to-pad minimum, exactly, provided the ordered outer copper remains 1 oz. | Saved board uses zero general mask expansion. Thus these 0.150-mm copper gaps also leave 0.150-mm mask separation under its exported geometry, above JLC's 0.10-mm 1-oz colored-mask dam minimum. This is not a stencil/reflow approval. |
| Same-footprint 0.100 mm: four centre-to-neighbor pairs on each `U_ISO1`–`U_ISO8` / 32 total | 32 | **Not verified for this order path.** The local TMUX4827 record gives a 0.4-mm BGA pitch with 0.25-mm perimeter lands and a 0.35-mm centre land ([part record](../../02_parts/TMUX4827YBHR/part.yaml), [footprint](../../03_src/lib/crow_usb_analog.pretty/TI_YBH0009_C02_TMUX4827.kicad_mod)); that geometry produces 0.100 mm copper around the centre. JLC does not publish a matching BGA pad-to-pad exception. | The centre pad's local `solder_mask_margin -0.05` reduces its opening to 0.25 mm, so its exported mask-opening separation from a 0.25-mm neighbor is 0.150 mm. That meets the mask-dam number but cannot waive the unresolved copper criterion. |
| GND via to ISO signal pad, 0.100 mm, one per `U_ISO1`–`U_ISO8` | 8 | **Not verified.** JLC's 0.10-mm pad-to-track number does not state that a through-via copper annulus can sit 0.10 mm from an SMD pad. | This is local copper/escape geometry, separate from an internal package land pattern; its mask and reflow behavior need a regenerated candidate and exact via treatment. |

The public capability table says that 1-oz green/red/yellow/blue/purple mask dams require at least 0.10 mm pad spacing, black/white require 0.13 mm, and 2-oz boards require 0.20 mm. It also says multilayer LDI supports 1:1 openings. JLC's [solder-mask explanation](https://jlcpcb.com/blog/basic-design-of-solder-mask) repeats the 1:1 multilayer and mask-dam facts, and states that narrower dams can be removed. Those facts concern solder resist, not copper isolation. JLC's [assembly component-spacing guide](https://jlcpcb.com/help/article/minimum-spacing-for-smd-components) concerns spacing between components, stencil, inspection, and rework; it does not set spacing between pads inside one component and therefore supplies no internal-pad exemption.

The narrowest defensible future rule evidence is therefore a same-footprint, pad-to-pad `0.150 mm` copper clearance rule for the exact local footprints `crow_usb_digital:TQFP-128_14x14mm_P0.4mm_EP_XU316`, `crow_usb_analog:TI_YBH0009_C02_TMUX4827`, and `Package_TO_SOT_SMD:SOT-553` (or the exact resolved ESD footprint IDs), conditioned on both objects being pads of the **same** footprint. It may clear only the 205 measured 0.150-mm rows and must retain the 32 TMUX 0.100-mm rows and every via-to-pad row. Its evidence must bind the JLC table URL, the selected four-layer/1-oz order configuration and color, the exact footprint hashes, and a regenerated native DRC. A board-wide 0.15-mm clearance, a mask-dam value used as copper clearance, any `0.10 mm` exemption, or a waiver for inter-footprint/via spacing is unsupported by this review.

**Source-rule follow-up.** `floorplan.yaml` records 0.04064-mm outer finished
copper and the exact JLC04161H-7628G dielectric section; `rf.yaml` and
`ARCHITECTURE.md` identify that source stack as four-layer, **1 oz outer / 0.5
oz inner**. That is enough to encode the public 0.150-mm *copper* row as a
source-stage rule: `same_footprint_pad_clearances` emits exact-reference
`memberOfFootprint()` predicates for `U_XU` and `U_ISO1` through `U_ISO8`, with
two pad operands required. The regenerated isolated DRC has nine such rules
and still reports 32 ISO 0.100-mm pad pairs plus eight via-to-pad pairs. ESD
references are deliberately excluded while their land correction is separate.
Mask colour is not an input to this copper rule; it remains an order-time
solder-mask/CAM question. Neither the source stack record nor this DRC rule is
an ordered-board, CAM, PCBA, or P1 acceptance claim.

Before any 0.10-mm rule could be proposed, obtain a public JLC capability statement or written order-specific CAM confirmation explicitly covering the exact 1-oz four-layer BGA pad-to-pad geometry and the via-to-SMD-pad relationship, then bind the response and a coupon/assembly outcome to the selected footprint. The local XMOS record is [XU316 part.yaml](../../02_parts/XU316-1024-TQ128-C24/part.yaml); it establishes its 0.4-mm TQFP package, while the TI TMUX and ESD records establish their exact package/land sources. They are component/footprint evidence, not a JLC manufacturing waiver.
