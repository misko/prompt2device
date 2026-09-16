# Twin render faithfulness — twin_top.png (`--side top`)

board_sha256: 2685281fdb8dac636e16334c2d4eca679300bfa5322a368ac2685b59f48e3dd1
a-render_verdict: PASS
- calibration: **16.0566 px/mm** x, **16.0349 px/mm** y, anisotropy **1.0014** (tol 0.02) — orthographic, projection valid
- board edge: 19.950..80.050 x, 19.950..60.050 y mm
- courtyards drawn (F.CrtYd): **44**; footprints with no courtyard on EITHER layer: 0
- **COVERAGE: 7 measured / 32 refs with an expected body** (25 unresolvable, 0 resolvable but NOT measured, 0 with no JLC model at all)
- tolerance: **1.00 mm** on both the centre delta and the outward excursion
- pixel measurement: **populated-minus-same-camera-bare RGB delta** (threshold 12)
- expected-model register: `twin_adjudications.yaml` (3 LCSC transform entries)
- overlay: `twin_top_courtyard_overlay.png`

**Red** = footprint courtyard (what gets fabricated). **Amber** = a ref jlc_twin flagged. **Green** = EXPECTED body (mesh x JLC's own model transform x board placement). **Magenta** = MEASURED body (pixels). **Blue** = board edge.

A body outside its red box with green and magenta AGREEING is a **3D-model** defect with no board exposure — gerbers and CPL derive from pads, never from the model. Green and magenta DISAGREEING is a **render** defect: the picture is not the board, and any visual review done on it is void.

## Graded refs (7)

| ref | LCSC | fit | centre delta mm | outward mm | edge deltas L,T,R,B mm | body px | courtyard excursion mm |
|---|---|---|---|---|---|---|---|
| `U1` | C2878631 | 270deg @0.14mm | 0.245 | 0.000 | +0.58,+0.01,-1.07,-0.05 | 7973 | 0.000 |
| `D2` | C83846 | 0deg @0.21mm | 0.133 | 0.007 | -0.01,+0.37,-0.06,-0.11 | 3757 | 0.000 |
| `J1` | LOCAL | 0deg @0.00mm | 0.071 | 0.000 | +1.11,+0.00,-1.14,-0.14 | 50514 | 0.010 |
| `D1` | C144860 | NONE (best 0.57mm) -> JLC's own transform | 0.064 | 0.006 | -0.01,-0.01,-0.04,-0.11 | 2454 | 0.000 |
| `C1` | C77102 | 0deg @0.05mm | 0.054 | 0.000 | -0.02,-0.01,-0.03,-0.09 | 1726 | 0.000 |
| `C7` | C84455 | 0deg @0.05mm | 0.050 | 0.000 | +0.01,-0.02,-0.02,-0.08 | 1726 | 0.000 |
| `U2` | C16430 | 270deg @0.05mm | 0.043 | 0.000 | +0.08,+0.01,-0.10,-0.10 | 1886 | 0.000 |

## Not measurable by construction (25) — named, never silently passed

- `C10` — body 1.00x0.50 mm is under the 2.0 mm resolvability floor (8.0 px, and erosion costs 4 px)
- `C11` — body 2.00x1.30 mm is under the 2.0 mm resolvability floor (20.9 px, and erosion costs 4 px)
- `C2` — body 1.00x0.50 mm is under the 2.0 mm resolvability floor (8.0 px, and erosion costs 4 px)
- `C3` — body 1.00x0.50 mm is under the 2.0 mm resolvability floor (8.0 px, and erosion costs 4 px)
- `C4` — body 0.50x1.00 mm is under the 2.0 mm resolvability floor (8.0 px, and erosion costs 4 px)
- `C5` — body 2.00x1.30 mm is under the 2.0 mm resolvability floor (20.9 px, and erosion costs 4 px)
- `C6` — body 1.00x0.50 mm is under the 2.0 mm resolvability floor (8.0 px, and erosion costs 4 px)
- `C8` — body 0.80x1.60 mm is under the 2.0 mm resolvability floor (12.8 px, and erosion costs 4 px)
- `C9` — body 1.30x2.00 mm is under the 2.0 mm resolvability floor (20.9 px, and erosion costs 4 px)
- `F1` — body 3.20x1.70 mm is under the 2.0 mm resolvability floor (27.3 px, and erosion costs 4 px)
- `R1` — body 0.50x1.00 mm is under the 2.0 mm resolvability floor (8.0 px, and erosion costs 4 px)
- `R10` — body 0.50x1.00 mm is under the 2.0 mm resolvability floor (8.0 px, and erosion costs 4 px)
- `R11` — body 0.50x1.00 mm is under the 2.0 mm resolvability floor (8.0 px, and erosion costs 4 px)
- `R12` — body 2.00x1.30 mm is under the 2.0 mm resolvability floor (20.9 px, and erosion costs 4 px)
- `R13` — body 2.00x1.30 mm is under the 2.0 mm resolvability floor (20.9 px, and erosion costs 4 px)
- `R14` — body 1.60x3.20 mm is under the 2.0 mm resolvability floor (25.7 px, and erosion costs 4 px)
- `R2` — body 0.50x1.00 mm is under the 2.0 mm resolvability floor (8.0 px, and erosion costs 4 px)
- `R3` — body 2.00x1.30 mm is under the 2.0 mm resolvability floor (20.9 px, and erosion costs 4 px)
- `R4` — body 0.50x1.00 mm is under the 2.0 mm resolvability floor (8.0 px, and erosion costs 4 px)
- `R5` — body 0.50x1.00 mm is under the 2.0 mm resolvability floor (8.0 px, and erosion costs 4 px)
- `R6` — body 0.50x1.00 mm is under the 2.0 mm resolvability floor (8.0 px, and erosion costs 4 px)
- `R7` — body 0.50x1.00 mm is under the 2.0 mm resolvability floor (8.0 px, and erosion costs 4 px)
- `R8` — body 0.50x1.00 mm is under the 2.0 mm resolvability floor (8.0 px, and erosion costs 4 px)
- `R9` — body 0.50x1.00 mm is under the 2.0 mm resolvability floor (8.0 px, and erosion costs 4 px)
- `U3` — body 1.60x1.60 mm is under the 2.0 mm resolvability floor (25.7 px, and erosion costs 4 px)

## 1 ref(s) flagged by jlc_twin

| ref | status | detail |
|---|---|---|
| `D1` | **MOUNT-FALLBACK** | best 0.57mm at 0deg, over 0.5mm — body mounted at JLC's OWN footprint transform (offset 0, their model rot_z), NOT at the failed fit. The render is therefore what JLC's own CAD says, and is  |
