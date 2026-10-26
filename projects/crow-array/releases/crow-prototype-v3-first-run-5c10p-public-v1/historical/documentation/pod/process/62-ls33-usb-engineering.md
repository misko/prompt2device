# LS33 independent engineering review — U3 micro-B plug access

2026-10-09 Pacific. Read-only design-stage check of the original Pico Rev3
SC0915 USB receptacle, current LS31 carrier, and two retained Tensility USB-A
to micro-B cable drawings. This is **not** a new scene, a source edit, a mating
receipt, or physical plug qualification. The `usb_service` interface remains
separate from the U3 shell-pool seating review.

## Exact inspected evidence

Paths are relative to `crow-sol6/recovery4`; hashes are SHA-256. I visually
read the native one-page Tensility drawing, including its front and side views,
and inspected the registered Pico STEP solids and the carrier's reopened solid.

| Evidence | SHA-256 |
| --- | --- |
| `02_parts/mechanical-ls33/10-02333.pdf` | `42f1d8056cf1e6649eb53525acbce9898c1d39857c0b939f8a876f14ac37d07b` |
| `02_parts/mechanical-ls33/10-02351.pdf` | `1be52eb9bf2158fdbe06221257c985c5ec86c0d394097a33f7534587881b527a` |
| `02_parts/mechanical-ls27/pico-r3/Pico-R3.step` | `ea5c693afee3de73e9fcaab1892a5ed44bf789438b9b1e5906e9c4f9859cab8b` |
| `03_src/recovery/ls31-scene/scene.json` | `dbf6192535e6a9878bca73923ed79548aa2a475d5dae6c4725181ccffd013330` |
| `06_build/recovery/ls31-scene/build1/scene.json` | `0cf6e12c51d12f19610f4428a80a73b04ba763f95bc5a452c161cde62745530e` |
| `06_build/recovery/ls31-scene/build1/carrier/board.step` | `f1109f4d6a02248b19087efa435ab0fd8464368860e49b867cebae7794f8bb89` |
| `06_build/recovery/ls31-staging/build1/native/source/carrier/carrier.kicad_pcb` | `c52e725e3c4aa08c0cbe3ecb7b67dc3d7649093dcee27cab1a56f090b2b2ce08` |
| `03_src/recovery/ls32-mating/requirements.json` | `a99c00b287b829b48a593a74b5485524413bbd53c8348691b33050e0c8c81e70` |

The two Tensility assemblies use the same micro-B connector item `50-00584`
and nominal boot arrangement, but the drawing expressly permits functionally
equivalent component substitutions. A release must bind the *actual* plug and
boot envelope, not assume any substitute has identical fit. The end view's
9.6 ±0.5 mm long boot axis lies across the board when the wide micro-B metal
blade is aligned to the horizontal Pico receptacle; its 5.8 ±0.5 mm short
axis is board-normal. The side view shows a **minimum** 5.4 mm exposed metal
nose between boot front and plug tip. It does **not** dimension where the boot
front sits at full electrical/mechanical engagement in this receptacle.

## Registered geometry and discriminating test

The LS31 scene registers the official Pico STEP to U3 at native board
`(165,27.55)` mm. In the carrier's native top frame (top Z=0, native Y toward
the board interior), the socket's separate front-lip solids span Y=0.75–1.35
mm, main shell spans Y=1.35–6.35 mm, and the shell's centerline is Z≈2.26 mm.
The current carrier leading edge is Y=0. Thus the mouth is **0.75 mm behind**
the carrier edge, not projected free in front of it. Its 0.75–6.35 mm metal
depth is an exterior STEP extent, **not** a proven plug insertion stop.

At the socket centerline a drawing-size boot has bottom
`2.26−5.8/2 = −0.64 mm` nominal; at the published maximum boot height 6.3 mm,
bottom is `−0.89 mm`. It therefore intrudes into the carrier's Z=0 to −1.6 mm
thickness if its front face moves over any positive native Y. This is not
resolved by an XY approach-volume PASS or a nominal module/board collision PASS;
the previous scene contains no inserted plug.

I loaded the retained `carrier/board.step` in the same OCCT/CadQuery solid
kernel. As a conservative rectangular **plug envelope** (not a claim of exact
Tensility corner radii), I placed the maximum 10.1-mm-wide ×6.3-mm-high boot
at X=159.95–170.05 mm, Z=−0.89–5.41 mm, with its front face flush to the
Pico STEP lip at native Y=0.75 mm and its body extending toward the cable.
The actual board solid intersects that box by **6.74175 mm³**, exactly the
10.1 ×0.75 ×0.89 mm nominal rectangular overlap at this edge. It is a real
board/envelope intersection, not merely overlapping bounding boxes. A virtual
board-only notch X=158–172, native Y=0–1.5 mm removes the intersection and
leaves 0.75 mm axial solid separation in this flush-lip test. Neither box nor
notch was saved as a new source or issued as acceptance evidence; exact plug
rounded geometry, insertion sweep and tolerances still need owning review.

The engagement distinction is decisive. Let `L` be actual exposed nose length
(drawing guarantees only `L ≥ 5.4 mm`) and `D` the required engaged plug-tip
depth *behind the Pico front lip* in native +Y. The boot front reaches
`Y = 0.75 + D − L`. The current full-width carrier edge blocks the drawing
envelope whenever `D > L − 0.75`, because the boot then extends over Y>0
while its lower surface is below Z=0. For the shortest permitted nose,
**collision begins above D=4.65 mm**; at D=4.65 mm it merely touches the
edge with zero axial margin. The shell exterior extends 5.6 mm behind its
front lip, but that does **not** prove that full mating requires D=5.6 mm:
the internal stop/contact/latch datum is absent from the cable drawings and
not established by the sparse Pico STEP. Conversely, the available evidence
does not prove complete engagement by D≤4.65 mm. A flush-shoulder installation
is demonstrably obstructed; *unavoidable full-mate failure* remains unproven.

## Design decision and minimal closure options

**Current `usb_service` cannot receive a design-stage PASS.** The present
board has a demonstrated obstruction at the ordinary flush-lip plug pose and
no supported full-engagement datum to show that these cables safely stop
short. Calling this a later first-article check would evade a known design
uncertainty. The current approved board should not be represented as accepting
Tensility 10-02333/10-02351 or arbitrary micro-B cables.

The smallest robust *board* remedy is a shallow front-edge notch in the
candidate X=158–172, native Y=0–1.5 mm region, retaining the U3 footprint and
Pico location. The virtual solid test shows why it targets the interference:
14 mm width exceeds the drawing's 10.1 mm maximum boot width by 1.95 mm each
side when centered; Y=1.5 extends 0.75 mm behind the front lip. Even if the
plug tip could advance to the back of the STEP shell exterior at Y=6.35, a
minimum 5.4-mm exposed nose would put its boot face at Y=0.95, leaving
0.55 mm nominal notch-depth margin. That is a conservative geometry screen,
**not** an assumed engagement datum or manufactured tolerance. The adjacent
A/B relief hole nearest edges are at native Y≈2.25 nominal; a maximum accepted
Ø2.65 hole moved 0.10 mm toward the notch would leave ≈0.625 mm nominal
hole-to-notch web. This is a reason to check actual edge/web capability, not
to declare it accepted. The notch also needs a fresh native all-layer copper,
mask, NPTH, route, edge/DRC, mechanical-scene, access-sweep and independent
placement/mating review. It cannot be grafted onto a frozen placement receipt
or old release evidence.

An unchanged-board alternative is a specifically controlled lower-profile
plug/boot or longer exposed-nose assembly, **with** an independently supported
full-mate depth and insertion/removal sweep. At the current socket centerline,
a centered boot would need a *maximum* board-normal height below 4.52 mm just
to avoid Z<0 over the edge; even that provides zero vertical clearance and
needs an explicit positive-margin stack. A longer nose needs
`L ≥ D + 0.75 mm` before any positive axial margin. No retained source here
identifies a cable meeting either condition at verified full engagement, so
“use a slimmer cable” is not yet a design disposition.

The owner should choose one bounded remedy, bind its exact geometry and cable
identity to the scene, then independently judge registration, coverage,
clearance, tolerance, engagement and insertion/removal access. Physical lot
inspection remains separate; no enclosure, bend-radius or weather fit is
claimed here. No board/cable/source adoption or receipt was made in this review.
