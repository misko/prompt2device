# Project-local footprint authority

These footprints are copied into the carrier so regeneration and review do not
depend on an ambient KiCad library revision.

`Molex_43650-0400_RA_Exact` is not a generic four-hole row. It contains four
3.00 mm-pitch plated signal holes, the two 3.00 mm non-plated locating/retention
holes, the polarized shrouded body outline, courtyard, pin-1 feature and outward mating-face
geometry of the selected right-angle 43650-0400. The footprint is used only for
J1-J8 and no compatible-alternative MPN is authorized. Its copied KiCad source
hash is `fa8877b1c3d305e884b95425f71714a3fb8bfbb6de6a08eb5707748f90c16fb7`.

`Molex_43650-0200_RA_Exact` applies the same drawing-controlled 3.00 mm signal
pitch, locating holes, body/mouth geometry and pin-1 convention to J9. Its
source hash is
`80ce662b23a6fa57b22b1db345c1e86cdac68dcfa7d9f1a9becaae7cddace94f`.

`Samtec_TMM-106-01-L-D_2x06_P2.00mm_Vertical` freezes the twelve-pad 2.00 mm
TMM-106-01-L-D land pattern used for MCHStreamer J1/J3 breakouts J10/J11. Its
source hash is
`43053a5fb3a69bbf33366a5df001c4ce228d7d01883aa4b81ef5e389d2789cdb`.
The exact selected mate is Samtec `TCSD-06-D-04.50-01`, but footprint identity
does not close the cable-assembly contract: miniDSP's board-header MPN is not
published, so module-side post fit, one-to-one continuity, socket rotation,
strain relief and simultaneous J1/J3 service access remain physical-evidence
holds.

`Cirrus_CS5308P_QFN48_6x6_P0.4_EP4.6` freezes the 48 perimeter lands and single
4.6 x 4.6 mm exposed pad. It deliberately contains no thermal vias: a selective
via-in-pad process has not been authorized. Its copied KiCad source hash was
`3b4488a5d5251cff1f4c5a1cbc7355e90d478598e7de57dd9e0e03139b8bcaee`.

`Littelfuse_SMBJ15A_SMB_Exact` freezes cathode pad 1 and the 2.50 x 2.30 mm
lands at 4.30 mm centre spacing for the input shunt clamp. Its source hash is
`63dee0873b808ac7598ebc60e3f32e22b322d87edf7e9d9e9aadd90a8a9ee7dd`.

`Coilcraft_XGL4020_Exact` freezes the manufacturer's 0.98 x 3.40 mm lands at
2.37 mm centre spacing and the 4.0 x 4.0 mm body/start-lead orientation. Its
source hash is
`f7ba0a0852797b7d837c9f113f6403b215d540618a89bf52f20d0fe066cf96d3`.
No exact supplier XGL4020 CAD is vendored. The2026-09-08 model-source backtrack
adds a reproducible nominal drawing-derived body and terminal envelope;
registration and physical qualification remain separate placement holds.

Primary drawing/PDF identities are owned by the matching `02_parts` dossiers.
Where a dossier still declares a null local path or digest, retrieval remains
OWED and cannot support placement approval. Before placement review, compare
every pad, locating hole, body edge, courtyard, pin-1 mark and mating-axis
annotation to ordinary digest-selected authority bytes.

`Panasonic_EEEFK1A471P_8x10.2_Exact` is the standard-terminal Panasonic FK
size-F land, not the vibration-proof `V`-suffix land. The official FK catalog
gives `a=3.1`, `b=4.0`, `c=2.0 mm`; the resulting pad centres are
`+/-3.55 mm`, with pad 1 positive. KiCad 10 has no stock `CP_Elec_8x10.2`
module, and the nearby `CP_Elec_8x10.5` land is not footprint authority (its
3D envelope is reused only as a conservative model).

## Source-owned models — 2026-09-08

`3dmodels/provenance.md` owns the exact public URLs, immutable KiCad commit,
retained licence, PDF hashes/pages, nominal/conservative interpretation and
omitted detail for the connector/package model-source backtrack.
`3dmodels/SHA256SUMS` pins every model and the unmodified upstream licence.
`../build_package_models.py` reproduces ten dimension-derived VRML files and
`../build_samtec_model.py` reproduces the Samtec reference VRML; the remaining
model is an unmodified KiCad capacitor STEP. Stock capacitor/fuse
footprints use narrowly enumerated `floorplan.yaml` model overrides, while
seven existing custom footprints change model clauses only. No stock
footprint is copied and no pads, graphics or electrical identities change.

The Molex representations retain drawing-derived outer extents and known
board-entry tails. The depicted cavity count, end-cavity chamfers and front
roof latch make orientation/keying identity visible. Internal dimensions and
latch position/profile are explicit visual estimates, not exact supplier CAD
or tolerance-qualified mating geometry. Pegs, bend radii, retention and cable
service remain unmodeled. All current-board/checkpoint evidence is STALE for
the changed model source until the coordinator deliberately regenerates it.
Temporary package-coupon evidence never promotes the current board.

The2026-09-09 addition `Vishay_WSLP1206_50m_Exact` retains its original copper,
graphics and pin convention; only its model clause is added. The drawing-derived
model uses the exact50mOhm terminal row of Vishay30122, not a generic1206 body.
Its nominal3.20x1.60x.635mm envelope does not cover production maxima. The prior
nine generated VRML files remain byte-identical; provenance documents all
omissions. Native model attachment does not close the feed-loop electrical or
thermal analysis and is not current-board registration acceptance.

## Exact fuse lands and resistor body datum — 2026-09-11

`Littelfuse_1812L035_60_Exact` owns the published1.78x3.15mm lands at5.23mm
pitch and maximum4.73x3.41mm Fab body. Eight source anchors move0.85mm outward
to preserve capacitor clearance. `Yageo_RT0603_NominalBody` preserves stock
copper/courtyard and corrects the Fab width to nominal0.80mm. Its unchanged
KiCad STEP is vendored with immutable provenance, import recipe and licence in
`3dmodels/kicad/RT0603-provenance.md`. These source changes require normal
canonical regeneration and fresh review; diagnostic projections are not seals.

## Supervisor ground toe and derived mask — 2026-09-16

`TI_DSE0006A_GNDToe018` is an engineered carrier land pattern, not an unchanged
manufacturer footprint. `TI_DSE0006A_Exact` is retained as the former source
baseline; its name does not prove the mask interpretation described below.
Both U_PWR and U_AUDIO use the engineered variant through the TPS389001DSER
part dossier. Pin numbering, body model, courtyard, pin1 marker and copper
lands1/3/4/5/6 remain unchanged. Pad2 extends its covered outer toe0.18mm:
center(-0.69,0), copper0.88x0.25mm, corner radius0.05mm. The inward copper
edge and adjacent-pad copper clearance remain unchanged. This provides a
0.30mm ground-track launch beyond the neighboring pad ends without a via in
an SMD land. The ordinary via-in-pad guard still sees the complete larger
copper pad; anonymous mask/paste apertures confer no copper exception.

Primary source: `02_parts/TPS389001DSER/TPS3890_SLVSD65A.pdf`, SHA256
`ee79599730e7606ba9718d9820b411020e3dcd9ff7d44572f8ee63fead15b9d0`, drawing
4220552/B01/2024, PDF pages25–26. Page25 dimension leaders identify the blue
metal outlines: pin1 0.80x0.25mm and the other lands0.70x0.25mm. Its explicit
lower detail identifies pads1–3 as solder-mask-defined, with at least0.05mm
copper overlap around the opening; pads4–6 are non-mask-defined with at most
0.05mm opening expansion. The upper green outlines appear expanded on all
six pads, conflicting with that left-pad detail. This implementation follows
the explicit lower detail. The aperture dimensions are an engineering
derivation, not dimensions directly printed in the drawing:

- Pad1 mask0.70x0.15mm, centered(-0.55,-0.5).
- Pad2 mask0.60x0.15mm, centered(-0.6,0), independent of the longer covered toe.
- Pad3 mask0.60x0.15mm, centered(-0.6,0.5).
- These three openings are rectangles, the0.05mm inward offset of an original
  R0.05 rounded land. Explicit mask-only pads avoid implicit margin behavior.
- Pads4–6 explicitly use0.05mm mask expansion. Their copper is unchanged.
- Page26 paste geometry remains0.80x0.25mm for pin1 and0.70x0.25mm for the
  others, R0.05. Paste therefore overprints the smaller SMD openings; that
  follows the separate stencil figure and requires first-article assembly
  inspection, not a claim of measured solder-joint qualification.

The former source and first toe prototype reused matching copper/mask sizes;
that preservation alone did not satisfy the explicit SMD detail. Native
source regressions now distinguish copper, paste and mask, including a
hostile enlarged aperture. Native Gerber export, fresh footprint/pin/render
review, all final-board gates and first-article solder inspection remain
required at their normal boundaries. No routing, annular-ring, copper-gap,
thermal-spoke or digital zero-via floor is reduced by this change.
