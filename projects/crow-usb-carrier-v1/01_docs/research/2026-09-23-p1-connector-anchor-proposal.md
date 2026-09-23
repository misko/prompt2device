# Crow P1 connector anchor proposal (source-only)

**Purpose.** Numeric placement hints for the first native floorplan candidate.
They are derived from the current board outline, current local footprints and
the existing connector placement-intent axes. They are not new connector
authority and do not prove exposure, mating, service, cable routing, reaction,
tolerance, enclosure fit, placement acceptance, routing, fabrication, or
release.

## Inputs and coordinate convention

* Board outline: `03_src/floorplan.yaml`, `x=20..240`, `y=20..140` mm.
* Intent: `01_docs/research/2026-09-22-connector-placement-intent.md` and
  `03_src/rules/connector_assemblies.yaml`: J1–J8, J_USB and J_PWR mating
  axis `[0,-1,0]`; J_JTAG mating axis `[0,0,1]` and lateral axis `[1,0,0]`.
* An anchor is the KiCad footprint local origin/pad-1 origin in the generator
  form `[x_mm, y_mm, rotation_deg]`. KiCad's +Y points down; positive rotation
  is clockwise for local geometry. This follows the transform documented in
  `skills/kicad-pcb/scripts/generate_board_generic.py`.
* The numbers below hold the **footprint courtyard** 0.50 mm inside or at the
  nominal bottom edge where the relevant footprint supplies a PCB-edge datum.
  That is only a native body/courtyard fit screen. It is deliberately not a
  claim that the mated interface has the required exposed distance.

## Proposed initial fixed features

```yaml
# Proposal only — do not treat as an applied floorplan change.
placement:
  anchors:
    J_PWR:  [30.00, 29.42,   0]
    J1:     [50.00, 26.86,   0]
    J2:     [72.00, 26.86,   0]
    J3:     [94.00, 26.86,   0]
    J4:     [116.00, 26.86,  0]
    J5:     [138.00, 26.86,  0]
    J6:     [160.00, 26.86,  0]
    J7:     [182.00, 26.86,  0]
    J8:     [204.00, 26.86,  0]
    J_USB:  [230.00, 23.675, 180]
    J_JTAG: [228.00, 50.00, 90]
```

The bottom row preserves the authored −Y mating direction: the connector
fronts face the `y=20` board edge. `J_JTAG` is a top-entry connector, so it
does not consume a board edge; `rot=90` maps the header's physical five-way
dimension (local +Y) to the declared board +X lateral axis. Its +Z mating axis
is unchanged by in-plane rotation.

## Derivation and conservative native clearance screen

| Refs | Native footprint facts used | Anchor derivation | Resulting courtyard/body span used for this screen |
|---|---|---|---|
| J1–J8 | `Wurth_615008160221_RJ45.kicad_mod`: courtyard local `x=-5.08..12.22`, `y=-6.86..7.59`; F.Fab body `x=-3.93..11.07`, `y=-6.36..7.09`. Local −Y is the plug/front side. | `y=20+6.86=26.86`, rot 0 maps local −Y to board −Y and local +X to the declared +X lateral direction. Pitch 22 mm begins at x=50. | Each courtyard x-span is anchor `−5.08..+12.22`; J1 `44.92..62.22`, J8 `198.92..216.22`; y `20.00..34.45`. Neighbor courtyard gap: `22−17.30=4.70` mm. Body rear ends at y=33.95, leaving 8.05 mm before analog region y=42. |
| J_PWR | `Molex_43650-0200.kicad_mod`: courtyard local `x=-3.83..6.83`, `y=-9.42..1.49`; F.Fab `x=-3.325..6.325`, `y=-8.92..0.98`. The horizontal header front is local −Y. | `y=20+9.42=29.42`, rot 0 preserves the authored −Y mating direction. x=30 leaves a source-only bottom-row slot before J1. | Courtyard `x=26.17..36.83`, `y=20.00..30.91`. Gap to J1 courtyard = `44.92−36.83=8.09` mm. This position is outside the existing `input_buck` region x=25..70/y=85..110, so its electrical/route consequence must be judged in P1; its edge orientation is the sole reason for the proposal. |
| J_USB | `GCT_USB4105_GF_A_120.kicad_mod`: courtyard local `x=-5.32..5.32`, `y=-4.76..4.18`; explicit `PCB EDGE` datum local y=+3.10 and footprint drawing/user edge y=+3.675. The receptacle mouth is local +Y. | To map local +Y to board −Y, use rot 180. Align the native PCB-edge datum to board y=20: `anchor_y=20+3.675=23.675`; x=230 remains inside the x=20..240 outline. | At rot 180, courtyard `x=224.68..235.32`, y=`19.495..28.435`; it straddles the nominal edge by 0.505 mm because the published courtyard contains the connector-side overhang. Board datum aligns exactly at y=20. Gap to J8 courtyard = `224.68−216.22=8.46` mm. The protruding courtyard is a review item, not an out-of-board exception. |
| J_JTAG | `Samtec_FTSH_105_01_L_DV_K.kicad_mod`: pads span local x=±0.635, local y=±2.54. Contract conservative body is x=7, y=8, z=7 in the declared local frame; contract declares local lateral y=board +X. | rot 90 maps local +Y to board +X. x=228/y=50 is the centre of the existing `debug_connector` region x=218..238/y=35..65. | Contract lateral planning span x=224..232. Existing source region contains it. This is only an in-plane candidate: the vertical mate/grip/ribbon envelope and its selected ±Y exit remain FULL-stage physical targets. |

The bottom-row planning allocation also has a simple conservative **mate-body
lateral** screen, using the contract's non-physical conservative widths:

* Power mate width 8.53 mm at x=30 and J1 RJ45 mate width 14.2 mm at x=50:
  `50−7.1 − (30+4.265) = 8.635 mm` transverse gap.
* Adjacent RJ45 mates at 22 mm pitch: `22−14.2=7.8 mm` transverse gap.
* J8 at x=204 and USB mate width 12 mm at x=230:
  `230−6 − (204+7.1) = 12.9 mm` transverse gap.

These are 2-D static planning checks only. They cannot establish complete
plug/mate compatibility, latch or grip motion, actual overmold variation,
simultaneous operation, or cable bends.

## Why anchors are needed for P1

`floorplan.yaml` presently has `placement.require_anchor: true` but
`anchors: {}`. The connector refs are included in analog/input/USB/debug
**regions**, so their current fallback start points are region centres (for
example J1 in `analog_ch1`, y=63) rather than an edge-controlled placement.
The generic legalizer may move unpinned region starts; it cannot infer the
contract's service-facing direction. The proposal supplies initial fixed
features that allow P1 to inspect a real candidate against the declared axes.

## Required P1 checks before accepting any anchor

1. Generate the exact native board and measure its realized footprint origin,
   rotation, board-edge datum and bounding/courtyard extents. Confirm each
   J1–J8/J_PWR front faces −Y, USB's local edge datum maps to y=20 and its
   rotation maps its mouth to −Y, and J_JTAG's local five-position direction
   maps to +X.
2. Run the ordinary P1 collision, pad-in-outline, NPTH/hole, courtyard/model
   coverage, and region/corridor capacity checks on the generated bytes. In
   particular, decide whether J_PWR's long electrical connection from the
   bottom-right-independent edge slot to `input_buck` makes that slot
   unsuitable; do not move it to a different edge/orientation without
   updating the connector intent/contract.
3. Inspect J1–J8 rear body versus their corresponding analog islands and the
   now-allocated bottom row against the USB-front-end/debug areas. The static
   gaps above do not reserve routing corridors or decoupler/AFE placement.
4. Preserve connector FULL as INCOMPLETE. The 19 targets in
   `connector_assembly_source_gate.json` still require physical qualification
   on the exact candidate or a governed coupon before placement approval and
   routing. This proposal cannot close any of them.

## Deliberate unresolved points

* No exact mating-plane offset, edge exposure/setback allowance, service
  clearance or installed tolerance stack exists. Aligning a drawing datum is
  not evidence that exposure is adequate.
* The RJ45/USB/power selected mates and all simultaneous groups have no
  physical service proof. The apparent lateral gaps must not be translated into
  latch/grip/access acceptance.
* USB courtyard overhang beyond y=20 and all connector copper/NPTH edge
  distances need the native P1 gate's actual geometry check; the source-only
  calculation does not assume the result.
* JTAG's `board_axes` representation correctly records two candidate ±Y exits,
  but FULL must select one installed signed exit and physical evidence must
  cover route/bend/strain/clearance.
