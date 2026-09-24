# Combined ESD-land and intrinsic-pad-rule isolated rebuild — 2026-09-24

This is an isolated source replay at commit `de176cada58160d2448021131a2c80e047bcb33f`, which includes the ESD DRL land correction `de176cad` and the intrinsic-rule change `3ac73059`. It does not alter the canonical PCB, approve P1, or establish fabrication, CAM, PCBA, routing, or release acceptance.

The temporary project rebuilt `crow_carrier.tsx` with `tsci build --disable-pcb`, copied the resulting `circuit.json`, converted and exported the KiCad schematic/netlist, generated the board from `floorplan.yaml`, emitted generic rules, then emitted the existing TMUX4827 POFV block. The generated artifacts hash as follows:

| Artifact | SHA-256 |
| --- | --- |
| `04_kicad/crow_carrier.kicad_pcb` | `d54dad46ea0d38942d38224fcb6b8b6d6d74799869e88d47653700a637d0c16e` |
| `04_kicad/crow_carrier.kicad_sch` | `d1df95efcacad003ce586320326d97d1a59d12776686b9632a5f9f9577576e51` |
| `03_tscircuit/build/circuit.json` | `70c661c18911503e7225bf0b28e7af5e36a935ad701f7b454064bdf570cab5d7` |

`count_parity.py` passed all 4 source representations at **569/569** references. `pin_map_check.py` passed **799** declared physical pin identities. `model_coverage_check.py` passed **569/569** fitted footprints. The fresh circuit diagnostic scan had zero embedded errors and 1,821 advisory records. Native `kicad-cli pcb drc --severity-all --refill-zones --schematic-parity` reported **0 violations, 499 unconnected items, and 0 schematic-parity issues**. The 499 unconnected items make this a failing placement/routing candidate; zero violation rows are not placement acceptance.

The ordinary source rules emit nine 0.150-mm pad-only `memberOfFootprint()` rules: `U_XU` and `U_ISO1` through `U_ISO8`. The ESD DRL references have no intrinsic exception. The existing TMUX POFV producer then emits exactly eight named B2-site profiles. Each profile contains four exact centre-pad predicates (`5` against `2`, `4`, `6`, and `8`) and four exact GND-via-to-pad predicates, all at 0.100 mm. The process checker re-derived and compared the intrinsic source blocks before admitting them, and passed the realized POFV process census: 8 protected 0.350/0.200-mm sites plus 6 protected 0.500/0.200-mm sites.

For the raw geometry census, only the generated POFV block was removed from a copy of the isolated `.kicad_dru`; the board and generic intrinsic rules were unchanged. Native DRC then reported **40 clearance violations**, comprising **32** centre-pad rows (four per ISO reference) and **8** actual GND-via-to-pad rows (one per ISO reference), with 499 unconnected and zero schematic-parity rows. Restoring the POFV block returns the 0/499/0 native report. The POFV block is therefore the exact mechanism that overrides those 40 rows; the broader 0.150-mm intrinsic rules do not override via pairs and do not create a generic 0.100-mm exception.

The conditional POFV/source process checks are not a public JLC capability or order acceptance for the 0.100-mm centre-pad/via relationships. Those remain conditional on their separately governed coupon, process, and uploader evidence. The new 0.150-mm intrinsic rule is likewise only the source encoding of the selected 1-oz outer copper path's public SMD-pad row; mask, CAM, assembly, and ordered-stack confirmation remain separate.
