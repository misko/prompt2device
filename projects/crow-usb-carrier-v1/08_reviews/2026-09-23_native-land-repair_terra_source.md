# Independent land-repair review — SOUND (scoped source verdict)

Commit `1af0fe89` correctly repairs the six authored native footprints and their corresponding TSX land definitions. This is a source-geometry verdict only. It is not a regenerated-board, placement, routing, fabrication, mating, or DRC acceptance.

## Primary drawing and native-footprint check

I read the retained primary layout pages directly and loaded scratch copies of all six edited `.kicad_mod` files with KiCad's native parser. The parsed pad centres, dimensions, IDs, and signed native (Y-down) pin-1 order agree with the drawings:

| Footprint | Retained primary evidence | Independent finding |
|---|---|---|
| Samtec FTSH-105-01-L-DV-K | Rev H, sheet 1, Fig. 1 | Ten pads retained, 1.27 mm pitch; 2.79 x 0.74 mm copper; 4.07 mm opposing centre separation (X +/-2.035); odd contacts, including pin 7, remain on the lower native row. |
| TI DCK0005A | SCES214 p.35 | 0.95 x 0.40 mm, 0.65 mm pitch, X +/-1.10; pin 1 is upper-left in native Y-down coordinates. |
| TI DCT0008A | SCES203 p.20 | 1.10 x 0.40 mm, 0.65 mm pitch, X +/-1.90; pin 1 is upper-left. |
| TI DMQ0006A | SLVSEF9I p.33 | Correct 0.50 mm pitch and upper-left pin 1, retaining the asymmetric 0.60 mm left / 1.00 mm right lands. |
| TI DCU0008A | SCES766C p.24 | Correct 0.85 x 0.30 mm, 0.50 mm pitch, 3.10 mm opposing centre spacing, and upper-left pin 1. |
| TI DSE0006A | SBVS228A p.25 | Correct dormant digital-native chirality and distinct pin-1 0.80 x 0.25 mm land; other five remain 0.70 x 0.25 mm. |

For each, the edited TSX has the opposite signed pin-1 Y coordinate, as required by its Y-up coordinate system. The old same-row pad dimensions would overlap at the stated pitch for the FTSH, DCK, and DCT cases; the changed geometry removes those source-land overlaps. This supports the stated allocation: 29 pad-pad reports (7 FTSH + 10 DCT + 12 DCK) are land-geometry repairs. The remaining three U_LDO signal-pad/GND-via reports are a separate floorplan issue, not repaired or represented as solved here.

The retained schematic binds active native footprints as follows: DCK 6, DCT 2, FTSH 1, DMQ 3, DCU 1, digital DSE 0, and analog `TI_DSE0006A_Exact` 7. Thus the digital DSE native repair is latent for the checked-in schematic; it does not claim to repair an active DSE board short. FTSH pin 7 remains present and electrically untouched. The exact `-K` mating/key disposition remains a physical review condition, not a basis to delete or retarget a pin.

## Independent record-equality check

I partitioned both retained circuit JSONs by object type and sorted complete JSON records before hashing. The electrical source partition comprises `source_component`, `source_component_internal_connection`, `source_group`, `source_net`, `source_port`, and `source_trace`; it is exactly 4,280 records in both files and has the identical sorted-record SHA-256:

`a6dc252377d202176c38d5b777749f78417ee524ec407b8fedff24b93d706857`.

The schematic partition comprises `schematic_component`, `schematic_element_outside_sheet_warning`, `schematic_group`, `schematic_net_label`, `schematic_port`, `schematic_sheet`, `schematic_text`, and `schematic_trace`; it is exactly 4,572 records in both files and has the identical sorted-record SHA-256:

`419abed53da3877f1c83f5184c9a2c28402f213ef9a7c0969df81ab3b8ff3fd7`.

`U_XU` has 129 source ports, 129 distinct pin numbers, and complete coverage from 1 through 129 (including EP129). These results support the constrained claim that the dossier changes physical geometry only and carries the existing logical topology unchanged. An unchanged schematic render/PDF body is expected from this equality and is not a new canonical pre-route witness.

## Identity, limits, and remaining conditions

The actual SHA-256 of the retained new raw circuit JSON is:

`cf78dcb8d8c1fc7f696d6f5eaad20a0175c6b27ae0c193d6e1b67bb8937e9193`.

This is the checked commit's `final-circuit.json`; its baseline is `f4097cb01771b00dcd459068f3655b7dcac93e42bce8242e4c4a6762a000c231`. The envelope's subject raw SHA (`ba264e414f0ffa54a2fadf4e452ae05d353567280e11300d5bf54ba3992eb94d`) is not the raw-CJ hash and must not be substituted for it.

An EFAULT-pin gate may advance only if the root reproduction independently produces the exact raw-CJ hash above and repeats the two equality results. This review does not advance that gate on geometry evidence alone.

Before any board acceptance, regenerate from the repaired sources, establish fresh placement and KiCad DRC results, inspect silk clearance after pad growth, and separately review FTSH `-K` keying/pin-7 physical mating. Do not accept an older board or issue a canonical pre-route witness from this dossier.
