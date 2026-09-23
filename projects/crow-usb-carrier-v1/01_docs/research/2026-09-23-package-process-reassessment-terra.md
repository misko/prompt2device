# Crow package/process reassessment — public-record decision

**Scope and status.** Read-only reassessment on 2026-09-23 of the retained
P1 records, native footprints, local primary PDFs, and current public pages.
No JLC account, upload, order, quotation, or authenticated API was used. This
does not reset P1 or admit another placement attempt.

## Decision

The evidence supports an **exact, narrowly-scoped advanced-process profile for
the TMUX4827 YBH B2 via-in-pad**. Do not replace
the existing qualified `0.35/0.20 mm` B2 proposal with `0.50/0.20 mm`, and do
not relax a global board rule. Preserve the coupon and express the
package/pad-specific POFV rule as the selected advanced profile. Public JLC
BGA guidance directly covers its `0.10 mm` via-copper-to-BGA-pad geometry,
whereas its generic SMD rule does not explicitly name this dual-role B2
feature. That mapping is a stated engineering inference, not a claim of an
order-specific CAM or PCBA result.

For the **TPS62825 DMQ0006A** and **USB4105**, the records do *not* yet permit
a rule update. Their exact manufacturer patterns collide with JLC's published
generic floors without a published exception that covers the actual feature.
They need a manufacturer-supported alternate land / compatible package, or a
specific JLC DFM disposition before a narrow exception could be adopted. This
is not a reason to alter package geometry speculatively.

## Keep the two TI packages separate

| Item | Actual geometry | Public/process result | Disposition |
|---|---|---|---|
| `U_ISO1..8`, **TMUX4827YBHR YBH0009-C02**, 3x3 0.4-mm DSBGA | Existing source/coupon: eight outer lands Ø0.25, B2 GND land Ø0.35, B2 POFV Ø0.35/drill Ø0.20, mask/paste opening Ø0.25. | JLC's dedicated four-layer BGA guidance says via copper to BGA pad ≥0.10; its filled-via guidance recommends inner Ø≥0.15 and solder-pad outer Ø≥0.35. Thus Ø0.35/Ø0.20 has ring `(0.35-0.20)/2 = 0.075 mm` and its Ø0.10 B2-via-copper-to-neighbor-BGA-pad relationship meets the named BGA predicate. | Adopt the narrow Type-VII/POFV profile, isolated from ordinary vias. Treat B2's simultaneous solder-pad/via-copper role as a documented inference: the article does not draw this exact 0.4-mm-pitch pattern or state PCBA acceptance. |
| `U_1V8`, `U_3V3X`, `U_CORE`, **TPS62825DMQR DMQ0006A VSON6** | TI's exact example has left lands 0.60×0.25 and right lands 1.00×0.25 at the shown geometry. Opposing copper edges are 0.100 mm apart. | JLC publishes 0.15 mm for different-net SMD-pad-to-pad clearance. No public DMQ/VSON exception was found. | Do not fold this into YBH/POFV. Obtain a TI-supported alternate land pattern that reaches 0.15 mm, or actual JLC DFM approval for this exact TI land pattern; otherwise select a compatible package/architecture. |
| `J_USB`, **GCT USB4105-GF-A-120** | GCT's recommended PCB layout contains the contacts and locating/stake geometry. Native A1/A12/B1/B12-to-NPTH clearance measures 0.1944 mm. | JLC publishes NPTH-to-track minimum 0.20 mm, but no public NPTH-to-SMD-pad value. The existing 0.25-mm blanket hole rule is too coarse, while 0.1944 is also below the only relevant public 0.20-mm bound. | Preserve exact GCT geometry. No 0.1944-mm exception now; obtain a JLC DFM disposition or use a connector/land pattern with documented clearance. |

## TMUX4827 geometry and exact consequence

This is **not** the DMQ regulator. The retained TI TMUX4827 drawing specifies
a 0.4-mm YBH ball grid and a 9×Ø0.23-mm example board land; its stencil example
is 9×Ø0.25 mm. The project deliberately retained a different conditional
coupon: Ø0.25 outer lands and a Ø0.35 B2 land supporting a Ø0.35/Ø0.20 filled,
capped B2 via. The coupon is therefore a conscious escape decision, not an
accidental ordinary-via choice.

The current generic board floors reject it mechanically:

* selected via diameter floor = 0.45 mm; candidate = 0.35 mm;
* selected annulus floor = 0.13 mm; candidate ring = `(0.35 - 0.20)/2 =
  0.075 mm`;
* B2 Ø0.35 to neighboring Ø0.25 land at 0.40-mm centres has copper edge gap
  `0.40 - 0.175 - 0.125 = 0.100 mm`.

Merely applying the ordinary alternative Ø0.50/Ø0.20 fixes its ring to
`(0.50-0.20)/2 = 0.150 mm`, but makes its nearest gap only
`0.40 - 0.250 - 0.125 = 0.025 mm`. Even Ø0.45/Ø0.20 leaves 0.050 mm.
It therefore cannot repair the coupled clearance/hole field. This confirms
the backtrack's warning rather than offering an enlarged-via workaround.

The retained coupon's `0.35/0.20` geometry is inside JLC's public filled-via
guidance: inner diameter is above 0.15 mm and outer solder-pad diameter equals
the stated ≥0.35-mm target. Its Ø0.10 copper gap is exactly the four-layer
JLC BGA page's named **via-copper-to-BGA-pad** minimum. That specialized
predicate is more exact than the generic 0.15-mm different-net SMD-pad rule
for this relationship. The conclusion that it applies when the B2 copper is
both the BGA solder pad and the filled-via outer copper is nevertheless an
inference from the published wording; the page neither illustrates this exact
0.4-mm YBH pattern nor grants an order-specific PCBA approval. The mask
geometry is less concerning on paper: the Ø0.25
center opening and Ø0.25 adjacent opening are separated by
`0.40 - 0.125 - 0.125 = 0.150 mm`; this is not a substitute for copper/assembly
acceptance.

**Actionable next repair:** create a named `TMUX4827_YBH_B2_POFV` process
profile, limited to B2 of the eight listed `U_ISO` instances, with ENIG,
filled-and-plated-over POFV, Ø0.35 pad/Ø0.20 drill/0.075 ring, Ø0.25 mask and
paste opening, and the exact 0.10-mm B2-neighbour copper relationship. It must
replace the ordinary-via check only at those B2 sites, not change board-wide
clearance or annulus floors. Bind it to the existing coupon SHA-256
`6f39a73aad46444e6b2256ced0b64a1dea5b9792801c3f705f8b691727ce83b6` and
retain the dossier's already-recorded statement that supplier assembly
acceptance is still owed. That is an order-time/physical-feasibility unknown,
not a new prerequisite invented by this memo for source repair or P1 review.

If that disposition rejects B2 POFV, there is no ordinary through-via escape
that meets the present floors: to achieve 0.15 mm clearance from Ø0.25
neighbors, a B2 copper/via diameter would need no more than
`2 × (0.40 - 0.125 - 0.15) = 0.25 mm`; a Ø0.20 mechanical drill in Ø0.25
copper retains only `(0.25-0.20)/2 = 0.025 mm` annulus, below JLC's stated
filled-via outer-diameter target (and the public guide's 0.05-mm minimum-ring
formulation). The next credible paths are a qualified finer
HDI/microvia process with its own supplier evidence, or a switch/package/
architecture that does not require a center-ball ground escape. Neither is
proved by the present JLC public records.

## DMQ and USB consequences

The TPS62825 DMQ source footprint matches TI's published land-pattern example;
the P1 errors are not evidence that its 0.100-mm opposing gap was generated
wrong. Still, exact manufacturer geometry alone does not overrule a selected
fabricator's published 0.15-mm different-net SMD-pad rule. A profile may be
drafted as a pending exception, but it cannot become a passing production rule
until an exact JLC DFM result or a TI-approved 0.15-mm-compatible land revision
is in evidence. If neither exists, the conversion package/part or power
architecture must change. Do not reuse TMUX BGA/POFV language for DMQ.

For USB4105, the GCT drawing labels its geometry “Recommended PCB Layout” and
the native 0.1944-mm result is intrinsic to the specified contact/NPTH
relationship. It demonstrates that the 0.25-mm blanket rule produces a false
classification for an exact manufacturer layout, but it does not demonstrate
that JLC accepts 0.1944 mm. JLC's stated NPTH-to-track value is 0.20 mm, and
the page does not state a pad equivalent. The remaining 0.0056 mm shortfall
to 0.20 is too small to infer tolerance/yield acceptance. Keep the footprint
unchanged while seeking exact JLC disposition; a rejection demands a compatible
connector/land pattern rather than shifted contacts or removed locating holes.

## Sources and uncertainty

* [JLC BGA design guidelines](https://jlcpcb.com/help/article/bga-design-guidelines---pcb-layout-recommendations-for-bga-packages), updated 2026-09-09 and accessed 2026-09-23: on four-layer boards, via copper to BGA pad ≥0.10 mm; for filled via-in-pad, inner Ø≥0.15 and outer solder-pad Ø≥0.35. It also shows a smaller 0.15/0.25 inner/outer example.
* [JLC PCB Manufacturing & Assembly Capabilities](https://jlcpcb.com/capabilities/Capab), accessed 2026-09-23: BGA Ø0.20–0.25/ENIG, generic 0.15-mm different-net SMD-pad spacing, and NPTH-to-track 0.20 mm.
* [JLC via-in-pad design guide](https://jlcpcb.com/blog/via-in-pad-design-deep-dive), accessed 2026-09-23: POFV mechanical hole 0.20–0.50 mm and via-pad minimum hole+0.10 mm (0.05-mm ring). This is an explanatory public record, not an order-specific CAM approval.
* [TI TMUX4827 Rev. B datasheet](https://www.ti.com/lit/ds/symlink/tmux4827.pdf), YBH0009-C02 package pages 32–34: 0.4-mm grid, 9×Ø0.23 example board lands, and Ø0.25 stencil apertures. TI notes final dimensions vary with manufacturing tolerance and routing constraints.
* [TI TPS6282x Rev. I datasheet](https://www.ti.com/lit/ds/symlink/tps62825.pdf), DMQ0006A example-board-layout page 33: the 0.60×0.25 and 1.00×0.25 land geometry used by the project.
* [GCT USB4105 product page](https://gct.co/connector/usb4105) and [USB4105 drawing](https://gct.co/files/drawings/usb4105.pdf), accessed 2026-09-23: exact USB4105 family and recommended PCB layout.
* Retained project evidence: `02_parts/TMUX4827YBHR/qualification/coupon.kicad_pcb`, its SHA above, `02_parts/TMUX4827YBHR/part.yaml`, the native YBH/DMQ/USB footprints, and the two P1 records named in scope.

Public records omit the exact dual-role B2 illustration, an order-specific
PCBA decision, and an NPTH-to-SMD-pad value. The BGA page does, however, state
the exact via-copper-to-BGA-pad clearance and filled-via dimensions that the
nominal TMUX profile uses. Consequently this memo supports that isolated source
profile while preserving the existing supplier-acceptance uncertainty; it does
not claim fabrication or purchase acceptance.
