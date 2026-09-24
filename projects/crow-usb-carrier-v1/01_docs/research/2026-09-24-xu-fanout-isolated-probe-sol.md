# Isolated XU TDM fanout placement probe, 2026-09-24

This is a source-level placement replay and three **diagnostic**, deliberately dangling F.Cu strips in `/tmp/crow-xu-fanouts-sol`. It is not a route, P1 corridor admission, power-integrity or release result. The canonical repository was not changed for this probe. U_XU remains at `[208.5,100.0,90]`, and all 1,810 `(ref,pad,net)` identities match the starting 569-footprint board exactly.

| Part | Starting pose | Tested pose | Pad-1 to associated XU pad centre, before → after |
| --- | --- | --- | --- |
| C_XU_VDD_105 | `[196.5,97.1,0]` | `[196.5,96.5,0]` | 4.8185 → 4.8434 mm |
| C_XU_VDD_106 | `[198.6,98.2,0]` | `[198.6,99.3,0]` | 2.8328 → 3.3158 mm |
| C_XU_VDDIO_17 | `[211.0,109.4,0]` | `[211.7,109.8,90]` | 2.5162 → 3.9814 mm |
| C_PLL_1U | `[210.4,110.8,0]` | `[218.0,108.4,90]` | 9.9904 → 6.1604 mm |

C_XU_VDDIO_109 stays at `[196.5,99.3,0]`: it does not obstruct the tested west DATA strip. Moving only the first two west blockers and the two immediately adjacent south blockers preserves all nets. The closest courtyard gaps for the four moved parts are respectively 0.19, 0.09, 0.15 and 0.30 mm; the full native DRC reports no courtyard overlap. The 0.09 mm gap at C_XU_VDD_106 to C_XU_VDD_113, and the 1.4652 mm extra C_XU_VDDIO_17 supply-pin distance, need engineering review before adopting the positions.

This probe does not establish the MCLK escape or the complete four-net TDM allocation. Three 0.15 mm F.Cu diagnostic strips were added only to the isolated board: DATA from U_XU.107 `(200.8375,97.8)` to `(194.5,97.8)` (6.3375 mm), FSYNC from U_XU.20 `(209.9,107.6625)` to `(209.9,113.5)` (5.8375 mm), and BCLK from U_XU.22 `(210.7,107.6625)` to `(210.7,113.5)` (5.8375 mm). Exact native KiCad DRC with `--severity-all --refill-zones --schematic-parity --all-track-errors --save-board --format json` found **only three `track_dangling` violations at their open diagnostic ends**, 499 unconnected items and zero schematic-parity issues. It found no copper, hole, width or courtyard violation for the strips. The saved In1.Cu GND zone is filled; `SHAPE_POLY_SET.Contains` is true at all 505 sampled centreline and ±0.2 mm offset points per strip (101 longitudinal stations). This sampled coverage is not a continuous return-path or SI proof.

The replay used the worktree's `generate_board_generic.py`, `generate_rules_generic.py`, and `generate_tmux4827_pofv.py` against an isolated copy of source/netlist/schematic; `add_strips.py` inserts the three diagnostic tracks. The isolated floorplan, saved board, native project, native rules and DRC JSON SHA-256 values are respectively `d0b0f9c36e5275f0e47dc046c525f1f4aaa0998ab8d110930847ff2616a24166`, `6f7c77fbf9a815f1596b6dd5285526df8adfd027f62f110af1c82f52b7a6ff34`, `7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094`, `cd6dc2c0cdc7cfa09646e7842ab5dccb56fc31374a198817682f60b5546a52bb`, and `c4c7a6a33138265c9497d17616ea6aab54ff0b4cae06a31fab14c66b18b897ff`.

The candidate needs power/ground decoupler review, the governed connector FULL gate, all 59-net corridor/interface evidence, and completed routing/return-path checks. No firmware remap or canonical route is implied.
