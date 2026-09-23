# Crow P1 backtrack census — advisory diagnosis

**Scope.** Read-only review of the second P1 candidate
`/tmp/crow-p1-repaired-trial-20260923/04_kicad/crow_carrier.kicad_pcb`, SHA-256
`37b455203fcdae0c20880a94b17a4bcfb61103fa2b8b9df9ecf095c9c97aa519`, and
its saved receipts. This neither spends/resets the P1 budget nor makes a gate,
fabrication, routing, or runtime-PASS assertion.

## Census and classification

| Evidence | Count | Classification | Reason and source owner |
|---|---:|---|---|
| DRC clearance | 63 errors | source/process defects | 56 are U_ISO1–8 (48 TMUX4827 BGA pad pairs, 8 via-associated); 7 are U_1V8/U_3V3X/U_CORE DMQ0006A land pairs. They are not routing findings. |
| DRC hole clearance | 36 errors | 32 source defects; 4 process/package validation | The 32 are the eight GND vias around U_ISO1–8. The four are J_USB A1/A12/B1/B12 to its own NPTH features. |
| DRC via diameter + annular width | 8 + 8 errors | source/process defect | Each generated GND via is 0.350/0.200 mm while board constraints require 0.450 mm diameter and 0.130 mm annulus; its annulus is 0.075 mm. |
| DRC silk over copper | 40 warnings | source artwork defect, owning-gate work | Actual F.SilkS rectangles/segments cross copper on listed logic parts, J_JTAG, and F_IN; it must be repaired before its owning gate is revisited. |
| Schematic parity | 45 warnings | 37 checker/source-representation; 8 source metadata | All 37 net conflicts are USB A/B/SH aliases versus schematic numeric pins; the lane checker independently confirms A6/A7/B6/B7 nets. Eight U_SPOKE Datasheet fields differ PCB vs schematic. |
| Unconnected items | 499 errors | later routing work | A placement candidate with no routed copper cannot satisfy connectivity. These do not diagnose a netlist defect but remain real later work. |
| 3-D model coverage | 73/568 unresolved (495 resolved) | source asset work | Missing models include 32 C_ADC_AC* 47-uF caps, 11 other 47-uF caps, 8 R_SPOKE_ILIM*, three inductors, 16 active IC/clock parts, F_IN/J_JTAG, and unresolved J_PWR/resistor URI targets. |
| Courtyard/physical placement | 16 footprints missing same-side courtyard | source library asset work | Preflight reports no overlap in the 552 footprints it can envelope, but cannot grade J_JTAG, U_1V8/U_3V3X/U_CORE and 12 ADC/digital footprints without F.Courtyard. |
| Routability contract | 2 FAIL checks | checker-schema/source-contract work | USB pair polarity naming and ESD dossier metadata reject a semantically correct declared topology. |

## High-leverage source defects

### U_ISO via family is incompatible with the selected board floors

The eight GND vias cause all eight via-diameter and annular errors, all 32
U_ISO hole-clearance errors (each is 0.175 mm from four nearby pads), and 8
of the 56 U_ISO clearance errors. The other 48 are the six repeated local
TMUX4827 BGA pad-pair clearances per U_ISO. This is a genuine generated-geometry/process
defect. The board's active minimums reject it and the vias have no demonstrated
advanced-process exception.

There is an upstream contradiction: `route.yaml` specifies normal 0.600/0.300
vias and a protected family of 0.500/0.200, capped and filled; the candidate
instead contains 0.350/0.200 vias. The placement/stitch producer and its U_ISO
thermal/ground-via policy own one redesign: use a manufacturable documented
via family, place it outside all exact pad/hole keepouts, and recheck mask,
annulus, hole-to-copper, thermal behavior, and all U_ISO pads. Do not change
global minima to make the current field pass.

### TMUX4827 and DMQ0006A are separate land-pattern/profile mismatches

U_ISO1–8 are **TMUX4827YBHR**, using
`crow_usb_analog:TI_YBH0009_C02_TMUX4827`, not DMQ0006A. That footprint has
nine 0.4-mm-grid BGA lands: 0.25-mm outer lands and a 0.35-mm center B2 land.
Its documented B2 advanced-process/via condition is distinct from the DMQ
converters. The 48 U_ISO pad-pair findings are six repeated pairs per device
under the candidate's 0.150/0.200-mm clearance requirements. The owner must
separately establish selected-process copper/mask and B2/via capability from
the retained TMUX4827/JLC public records; it must not be folded into the DMQ
remedy.

The retained `TI_DMQ0006A_VSON6.kicad_mod` has TI's asymmetric lands: left
0.60 x 0.25 mm, right 1.00 x 0.25 mm, on specified 0.50-mm rows. Several
opposing copper edges are 0.100 mm apart, while the candidate uses 0.150 or
0.200-mm clearance requirements. This creates the seven non-U_ISO clearance
errors (U_1V8/U_3V3X/U_CORE).

This is manufacturer-land geometry colliding with an unqualified rule profile.
The owner must bind selected JLC advanced capability and document applicable
copper/mask clearance for this footprint, or obtain a manufacturer-supported
alternate land pattern and synchronize TSX and KiCad geometry. A blanket
relaxation is unsupported.

### USB connector holes need a package/process disposition

The exact USB4105 footprint uses four SH oval PTH stakes with 0.600 x
1.400/1.700-mm drills. KiCad reports A1/A12/B1/B12-to-NPTH clearance of
0.1944 mm against a blanket 0.250-mm hole rule. The proximity is intrinsic to
the selected geometry, so moving contacts or deleting stakes would make the
footprint less faithful. Treat this as package-aware checker/process limitation
pending public GCT drawing and JLC capability comparison. Establish exact
copper-to-slot/hole allowance and mask/web treatment, then encode a narrow,
evidence-backed footprint/process exception or select a compatible land pattern.

### USB pair and ESD failures are contract-schema defects

`route.yaml` correctly declares `p: USB_DP` and `n: USB_DN`; the checker
rejects them solely because it accepts only `_P`/`+` and `_N`/`-` suffixes.
Add explicit polarity fields or accepted `*_DP`/`*_DN` aliases to the
checker/contract and retain the existing electrical names.

The receipt accepts lane mapping (A6/B6 DP, A7/B7 DN), but rejects U_USB_ESD
because `part.yaml` has pin map 1=DP, 2=DM, 3=GND yet no machine-readable
kind, signal_pads, or return_pads. The route's declared shunt topology agrees
with that dossier and its connector-side short-GND-return guidance. Add this
topology record to the TPD2EUSB30ADRTR dossier/checker schema, then audit the
realized connector-to-clamp-to-XU tree later. This descriptive repair does not
establish USB routing, impedance, return continuity, or ESD qualification.

## Coherent repair ownership and order

1. **Placement/stitch producer:** replace U_ISO via family and make exact
   pad/hole/mask/process checks intrinsic to generation. Preserve board floors.
2. **Footprint/rule-profile:** separately resolve TMUX4827 BGA and DMQ0006A
   manufacturer lands versus JLC advanced capability with public records;
   synchronize any approved geometry in native library and TSX. Separately
   disposition USB4105 stake/contact clearance from exact drawing and process;
   do not alter it for generic DRC.
3. **Library assets:** add 73 3-D assets/valid URI bindings and F.Courtyard
   primitives for 16 ungradable assembled footprints.
4. **Parity/route contract:** make USB A/B/SH aliases parity-aware, sync eight
   U_SPOKE Datasheet fields, add USB polarity aliases, and record TPD2E shunt
   topology in dossier schema.
5. **Sequenced later work:** repair silkscreen before its owning gate is
   revisited; P2 is placement, P3 is diagnostic critical-route work, and global
   routing follows only after admitted P5. The 499 unconnected items therefore
   remain later routing evidence, followed by native DRC, realized USB pair/ESD,
   return-path, stackup, thermal, and physical connector validation.

## Evidence consulted

* `06_build/modular/p1_repaired_drc.json`: 155 violations, 45 parity
  warnings, and 499 unconnected items.
* `06_build/modular/model_coverage.json`: 495 resolved of 568 fitted models.
* `06_build/modular/placement_routability_repaired.json`: courtyard,
  pair-name, and TPD2E topology failures.
* `03_src/route.yaml`, `03_src/rules/nets.yaml`, exact TMUX4827, DMQ0006A,
  and USB4105 native footprints, and `02_parts/TPD2EUSB30ADRTR/part.yaml`.
* Retained public-record notes `2026-09-23-native-geometry-repair.md` and
  `2026-09-23-p1-native-trial.md`.
