# LS33 independent engineering review — U3 Pico seating and shell reliefs

2026-10-09 Pacific. Scope: design-stage mechanical judgment for carrier U3,
original Raspberry Pi Pico Rev3 / SC0915, D1-only-depopulated, castellations
hand-soldered. This is an independent review input to the existing v3 mating
owner, **not** its signed review, receipt, assembly verification, physical
qualification, fabrication approval, or permission to order. USB plug service
is a separate interface and is not judged here.

## Inspected exact evidence

Paths below are relative to `crow-sol6/recovery4`; hashes are SHA-256 of the
bytes inspected. I also visually inspected the retained Figure 5 extraction and
the isolated U3 isometric/edge views; the PNGs are not dimensional proof.

| Evidence | SHA-256 |
| --- | --- |
| `02_parts/P031/manufacturer.pdf` | `757ff485227493b9fcc0c2c96c4dea9de020e1d8b2b11e2aa4f9ee8b25aa89eb` |
| `02_parts/mechanical-ls27/pico-r3/Pico-R3.step` | `ea5c693afee3de73e9fcaab1892a5ed44bf789438b9b1e5906e9c4f9859cab8b` |
| `06_build/recovery/rt7-mating-review/pico-fig5.png` | `cf95db99d4c29fc2393e95d3faf1c655e13165c75e19ca4b423eb9038332641d` |
| `03_src/recovery/ls30-relief/candidate2/native/carrier.kicad_pcb` | `c52e725e3c4aa08c0cbe3ecb7b67dc3d7649093dcee27cab1a56f090b2b2ce08` |
| `06_build/recovery/ls31-staging/build1/native/source/carrier/carrier.kicad_pcb` | `c52e725e3c4aa08c0cbe3ecb7b67dc3d7649093dcee27cab1a56f090b2b2ce08` |
| `06_build/checkpoints/ls31/placement_reviewed.json` | `b7a550dae52fe2ef2c5575a8c42c2cdd090db15b9872143d78125321dad1087e` |
| `03_src/recovery/ls31-scene/scene.json` | `dbf6192535e6a9878bca73923ed79548aa2a475d5dae6c4725181ccffd013330` |
| `03_src/recovery/ls31-scene/assembly.json` | `9f90174b7d6522c5d6f170eb0e1e4fd53969113ca797d3dc6e4b18c2ee86a9de` |
| `06_build/recovery/ls31-scene/build1/scene.json` | `0cf6e12c51d12f19610f4428a80a73b04ba763f95bc5a452c161cde62745530e` |
| `06_build/recovery/ls31-scene/build1/carrier/board.step` | `f1109f4d6a02248b19087efa435ab0fd8464368860e49b867cebae7794f8bb89` |
| `06_build/recovery/ls31-scene/build1/carrier/carrier-populated.step` | `0398bf643b63ece0df6ba369d15abe081152d80a09299465013f30c8c51cdc55` |
| `06_build/recovery/ls31-scene/build1/carrier/detail_U3_edge_east.png` | `f33e4a1bbbb9a440748c1964860757a6d3e59463d932313c4d9d4f9d173ceaa2` |
| `06_build/recovery/ls31-scene/build1/carrier/detail_U3_iso_nw.png` | `5a08782226c655d8f84e21c8e393382fc896f1a779c2c70cf68a9dae52562a40` |
| `03_src/recovery/ls30-parity-replay/relief_3d.py` | `29b44af3c67d726f4c45a106fce3c6d18de4181cd15f84e7f0661a13263eb03d` |
| `06_build/recovery/ls30-relief-3d/tolerance.json` | `7b662710e0a9d39bc5bbeb6547733a8eb83c6cc13fce2af93bddf86d61190f` |
| `06_build/recovery/ls30-relief-3d/relief-worstcase.step` | `0eb241a778a88ca80fe48166ab9ea3d4b16f6c0be8f116f66200f51d5509d940` |
| `06_build/recovery/ls29-mating-investigation/REPORT.md` | `2be0de52e82edee14a10a9cc032bea5ea73f4c46e61bc4e42bf8b6f5cb66a800` |
| `06_build/recovery/ls30-parity-review/review.md` | `57ee2f0080a5aee7670542fe43db7ab43b6fe3d99ef894bf8b27739c98f75922` |
| `03_src/recovery/ls32-mating/requirements.json` | `a99c00b287b829b48a593a74b5485524413bbd53c8348691b33050e0c8c81e70` |
| `03_src/recovery/ls32-mating/mechanical-draft.json` | `30eddffe330617b8b251d539918aa3ed37957d186dca93e476ee1d390dcd8809` |

## Geometric finding

The accepted LS31 staged carrier is byte-identical to the LS30 relief candidate.
U3 has four unnumbered, netless NPTH shell-pool voids, not shell-ground pads:
A/B at `(162.275,3.550)`/`(167.725,3.550)` mm, nominal Ø2.60; C/D at
`(162.575,6.580)`/`(167.425,6.580)` mm, nominal Ø2.25. All have 0.40-mm
local copper clearance. The native board was zone-refilled. The LS30 parity
review records empty candidate DRC/parity violations and independently found
no copper/outline/other-drill hit within each nominal hole plus 0.25 mm. Its
nearest refilled inner-plane copper is 0.401 mm from each nominal drill edge;
C-to-SCL is 0.564 mm. These are **nominal board** distances, not finished-board
capability claims.

Maker Figure 5 explicitly warns that USB-shell solder can pool underneath the
Pico and prevent flat seating; its extra lands are a controlled *reflow*
solution. This assembly is hand-soldered and has through-voids instead, so the
maker's recommendation is neither silently implemented nor evidence that an
arbitrary received solder pool fits. Figure 5 gives A/B center coordinates and
1.10 × 1.80 mm, R0.55 drawn capsules. It gives C/D coordinates and shows a
second 1.05 × 1.45 mm, R0.525 row, but that second legend says “B,C” while
the first says “A,B”; B is duplicated and D omitted. I judge “B,C” to be the
legend error because the two drawn rows and all four separately listed centers
identify A/B then C/D. This is an engineering interpretation, **not** a
manufacturer dimensional-tolerance guarantee. The finite acceptance envelope
below independently caps the as-built C/D pool projection to the smaller row;
if a supplied module does not satisfy it, this design does not accept that
module. Merely applying the first-row 1.80-mm long dimension to C/D would
overrun the current worst-case budget by 0.075 mm; that substitution is not
allowed without redesign/recheck.

The official Pico STEP is registered by three underside drilled-contact
centers and a fourth, noncoplanar PCB surface point against maker Figure 3;
the scene reports errors below 0.001 mm, no nominal U3/board intersection,
and U3's 17 solids reopen unchanged in the populated STEP. That validates the
nominal rigid transform and represented bodies, **not** underside solder or
the modified module. The STEP has no shell-pool solids and no verified D1
instance (its generic diode is near Q1), while the carrier model is a nominal
finished dielectric without copper/mask/finish/warp. The detail view also hides
neighbors. No visual or kernel PASS from this sparse scene alone establishes
flat seating.

The LS30 independent real-solid screen instead shrinks the actual native four
holes to minimum finished Ø2.50/2.15 mm and constructs full-thickness
overbounds for each drawn capsule plus pool excess and registration. All four
give 0.10 mm nominal-to-limit radial free space, zero intersection, reopened
STEP parity, and a deliberately oversized-pool collision negative. Arithmetic:
`(2.50/2 − 1.80/2) − 0.15 − 0.10 = 0.10 mm` for A/B;
`(2.15/2 − 1.45/2) − 0.15 − 0.10 = 0.10 mm` for C/D. This is a *conditional
geometry proof*, not a statistical tolerance, supplier promise, or observed
pool measurement. Because a complete pool's XY projection is inside a true
through-void under this condition, pool height cannot make that pool bear on
the carrier top; height could still cause an unacceptable protrusion below the
carrier and must be separately bounded.

## Finite design and process limits required for this variant

These are proposed **design-owned acceptance limits**, not claimed Raspberry Pi
or fabricator tolerances. They should be made binding in the successor
fabrication/assembly instructions and checked on the actual articles before
assembly/use; nonconforming parts are rejected/reworked or the board is
redesigned. They are not a statement that inspections have occurred.

1. Supply only original non-wireless SC0915 Rev3 with **D1 only** removed and
   documented module identity. No alternate Pico, headers, underside stencil,
   shell-ground land conversion, or unreviewed D1 rework substitution.
2. Fabricate four **non-plated** reliefs at the exact native centers: finished
   A/B Ø2.50–2.65 mm, C/D Ø2.15–2.30 mm. Retain 0.40-mm local design copper
   clearance; accept only actual finished web ≥0.45 mm between neighboring
   first/second-row holes and finished-hole-to-copper separation ≥0.25 mm on
   every layer. Directly inspect the web and copper separation, because even
   two individually permitted hole shifts toward each other can consume the
   web. The nominal maximum-diameter web at unchanged centers is ≈0.570 mm;
   the LS30 review computes ≥0.276 mm inner-plane and ≥0.439 mm C-to-SCL
   separation with its 0.10-mm hole shift. A vendor's ability to hold this
   set of limits is not established here.
3. For **each** D1-depopulated module, bound the complete underside USB-shell
   solder projection, including shell-pad location variation, by the Figure 5
   A/B 1.10 × 1.80-mm capsules and the explicitly design-selected C/D
   1.05 × 1.45-mm capsules, each expanded outward by at most 0.15 mm in XY.
   Use the maker four-center/module datum, not each pool's measured center
   re-zeroed to hide offset. No other underside solder/D1 remnant may bear on
   the carrier or short adjacent features. The pool must not protrude beyond
   the finished carrier underside after seating; absent a selected backside
   enclosure, this is a conservative board-level protrusion control, not an
   enclosure-fit claim.
4. Before tacking, register the module castellated datum to the *actual*
   finished holes such that total module-to-hole radial error is ≤0.10 mm at
   **each** of A–D, with module placement and drill error combined, not two
   independent allowances. Control this with a fixture/optical check and
   reject/reposition outliers. Preserve the 40 numbered contact topology and
   pin-1 orientation; inspect hand-solder wetting/continuity separately.
5. Seat without force or rocking. The proposed LS29 four-corner gap *spread*
   ≤0.15 mm is insufficient by itself: a uniformly elevated module would
   pass it. Use an absolute contact-plane criterion as well: at four perimeter
   contact windows, module underside contact plane to corresponding finished
   carrier pad top gap must be 0–0.15 mm after tacking, with spread ≤0.15 mm,
   no pool/D1 hard stop, and no force from a fixture concealing a spring-back.
   This 0.15-mm ceiling is a design/process reject limit, **not** published
   Pico flatness or solder-joint capability. A failure reopens the module
   seating/relief design; it is not waived by an electrical continuity pass.

The actual hole diameters, hole positions, web, copper clearance, shell pools,
module flatness, D1 rework, contact-plane gap, and backside protrusion have
**not** been measured. A chosen fabricator/assembler has **not** confirmed
capability. No first article is automatically demanded merely to form a
prototype *design-stage* judgment; order/lot acceptance and physical
qualification remain separate and these controls must be executable before
ordering/assembly. The current package remains DO-NOT-ORDER.

## Design-stage verdict and owner action

**U3 relief design is geometrically viable under the finite limits above; no
source-evidenced collision requires another board edit now.** The Figure 5
legend is disposed as a drawing-label error only for the controlled envelope,
not promoted into an unspecified maker tolerance. This is a favorable
engineering *conditional* finding, not a current `module_seating` PASS: the
limits above are not yet binding successor build instructions, the LS32
mechanical draft still says UNRESOLVED, and its independent exact-subject
review/receipt has not been issued. An owner can close the **design** gap by
adopting these explicit limits (or a stricter, rechecked alternative), citing
this report and the exact LS30/LS31 evidence in each of registration, coverage,
clearance, tolerance, engagement/seating and access judgments, and disposing
the U3/board-datum limitations without calling unperformed inspection done.
If the owner cannot bind/check the pool, finished-hole/web/copper, combined
registration and absolute-seat limits, `module_seating` must remain UNRESOLVED
and the relief or assembly process must be redesigned. USB plug fit belongs to
the separate `usb_service` interface; this report does not make that PASS.
