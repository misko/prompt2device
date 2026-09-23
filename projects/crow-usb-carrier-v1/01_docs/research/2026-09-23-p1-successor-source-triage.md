# Crow P1 successor source triage — read-only

**Subject:** `/tmp/crow-p1-dlc-usb-successor-20260923/06_build/p1_successor/pre_route_drc.json`. The one P1 successor candidate is consumed. This memo identifies source owners and repair directions only; it makes no DRC waiver, source edit, regeneration, or model-registration claim.

## Observed findings

The prepared-rule native DRC has 41 placement violations: 40 `silk_over_copper` plus one USB `silk_edge_clearance`. Its separate `schematic_parity` array has eight identical `Description` mismatches for `U_SPOKE1` through `U_SPOKE8`.

The 40 are **not TMUX findings**. Exact grouping:

| Native reference(s) | Count | Owning source footprint | Direct cause |
|---|---:|---|---|
| `U_ADC_CLOCK_OK`, `U_ADC_DIGITAL_BAD`, `U_ADC_PWR_BAD`, `U_ADC_READY`, `U_ADC_READY_BAD`, `U_BCLK_INV` | 30 | `03_src/lib/crow_usb_digital.pretty/TI_DCK0005A_SC70_5.kicad_mod:8-13` | F.SilkS rectangle spans x=±1.0; pads extend inward to x=±0.625. Every five-pad instance clips every pad. |
| `J_JTAG` | 6 | `03_src/lib/crow_usb_digital.pretty/Samtec_FTSH_105_01_L_DV_K.kicad_mod:8-18` | x=±1.0 center silk rectangle overlaps inward ends of 2.79-mm lands at x=±2.035. |
| `F_IN` | 4 | `03_src/lib/crow_usb_power_aux.pretty/Littelfuse_451_Nano2_2410.kicad_mod:7-12` | Two full-width silk lines cross large 1.96×3.15-mm land envelopes after saved rotation. |

The edge row is real source geometry. `J_USB` is at `[230,22.995,180]`; `03_src/lib/crow_usb_carrier_v1.pretty/GCT_USB4215_03_A.kicad_mod:10` puts mouth silk at local y=+2.995, mapping at 180 degrees to board y=20.0, the Edge.Cuts datum. Physical fit remains UNKNOWN; this does not justify moving the connector or waiving edge clearance.

## Minimal repair proposals

1. **SC70 library owner:** replace the body-wide F.SilkS rectangle at `TI_DCK0005A_SC70_5.kicad_mod:8` with a manufacturer-informed small pin-1 marker outside all five mask openings, or omit F.SilkS body art and retain F.Fab/courtyard. Preserve pads, courtyard, model, nets, and TMUX profile. One repair covers 30 rows.
2. **JTAG library owner:** replace the central F.SilkS rectangle at `Samtec_FTSH_105_01_L_DV_K.kicad_mod:8` with an external/corner pin-1 marker that clears wide lands. Preserve its 8×9-mm courtyard and all ten pad centres/sizes. This is unrelated to its repaired courtyard or connector placement contract.
3. **Fuse library owner:** remove or shorten F.SilkS lines at `Littelfuse_451_Nano2_2410.kicad_mod:7-8` to clear rotated pad envelopes. The fuse is nonpolar; retain F.Fab body, courtyard, pad geometry, and reference text.
4. **USB library/connector owner:** move only the F.SilkS mouth line at `GCT_USB4215_03_A.kicad_mod:10` inward enough to meet configured edge silk clearance at the same anchor. Keep F.Fab mouth marker at y=+2.995 and preserve all pads, slots, courtyard, and `[230,22.995,180]`. Recheck transform and 19 physical FULL targets; this graphic edit does not close fit.

## Eight U_SPOKE parity findings

PCB metadata comes from `TI_DRC0010J_VSON10.kicad_mod:43-55`: `Description = "TI DRC0010J package land pattern for TPS26625DRCR"`. The schematic value is empty; e.g. `04_kicad/crow_carrier.kicad_sch:10753-10757` has Footprint/Datasheet but no Description value. The generic owner is confirmed because both `emit_component()` at `skills/kicad-pcb/scripts/circuit_json_to_kicad_sch.py:599-606` and `_emit_layout_component()` at `2534-2542` emit Reference, Value, and Footprint only. `03_tscircuit/src/crow_retained_analog.tsx:91-94` correctly declares the eight TPS26625 instances and is not the owner.

The minimal repair is to make the outlying footprint `Description` property empty at `TI_DRC0010J_VSON10.kicad_mod:43`, matching the schematic while retaining footprint `descr` at line 6 and part authority at `02_parts/TPS26625DRCR/part.yaml:14-16`. This is safer than special-casing the generic converter, which has no general footprint-description authority and could create broad new mismatches. It changes no electrical, pad, package, or provenance identity.

## Tests after separately authorized source repair

1. Load repaired footprints with `pcbnew.FootprintLoad`; measure every F.SilkS primitive against every F.Mask/pad envelope at actual saved rotations. Require zero intersections and unchanged pads, courtyard, and model records where not intentionally edited.
2. Regenerate canonical schematic and run fixture plus exact `kicad-cli pcb drc --severity-all --refill-zones --schematic-parity`. Require zero U_SPOKE Description mismatches and unchanged per-ref/pad/net identity.
3. Generate only under a separately authorized new campaign decision; confirm former 40 silk rows and USB edge row are absent without suppressions. Re-run connector geometry/FULL separately.

`model_registration` is **N-A** here. Its candidate check-status exit code is not evidence of a completed native model-registration review, so this memo does not report P-MODEL-REG PASS.
