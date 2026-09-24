# Minimal Crow P1 fixed placement authority

The source-owned `p1_fixed_refs` set in `03_src/rules/p1_corridor_requirements.yaml` contains 27 refs. It is the smallest set supported by [ADR 0011](../decisions/0011-p1-floorplan-and-p2-placement-admission.md) and the current connector/hold-bank floorplan: 11 installed connector/service datums and 16 hold-bank footprints. `placement.anchors` has 58 refs, but anchoring alone does not make the other 31 electronic support parts P1-immutable. This source change does not instantiate a coarse reservation contract, generate/promote a PCB, or dispatch P1.

| Fixed ref(s) and native pose `(x,y,deg)` | P1 reason |
|---|---|
| `J1 (50,26.86,0)`, `J2 (72,26.86,0)`, `J3 (94,26.86,0)`, `J4 (116,26.86,0)` | Each is a separate north-edge RJ45 spoke mouth, shell/NPTH and panel-spacing datum. |
| `J5 (138,26.86,0)`, `J6 (160,26.86,0)`, `J7 (182,26.86,0)`, `J8 (204,26.86,0)` | Each is a separate north-edge RJ45 spoke mouth, shell/NPTH and panel-spacing datum. |
| `J_PWR (30,29.42,0)` | External-power entry and north-edge mating datum; native NPTH hardware. |
| `J_USB (230,22.995,180)` | USB-C mouth and board-edge overhang datum; its overhang still needs the separate connector registration/FULL check. |
| `J_JTAG (228,50,90)` | Vertical debug-service access and connector-neighbor clearance datum. |
| `C_HOLD1 (30.85,120.45,0)`, `C_HOLD2 (42.95,120.45,0)`, `C_HOLD3 (55.05,120.45,0)`, `C_HOLD4 (67.15,120.45,0)` | Each reserves one authored first-row hold-bank body/assembly site under ADR 0011. |
| `C_HOLD5 (30.85,129.55,0)`, `C_HOLD6 (42.95,129.55,0)`, `C_HOLD7 (55.05,129.55,0)`, `C_HOLD8 (67.15,129.55,0)` | Each reserves one authored second-row hold-bank body/assembly site under ADR 0011. |
| `C_HOLD9 (82.85,120.45,0)`, `C_HOLD10 (94.95,120.45,0)`, `C_HOLD11 (107.05,120.45,0)`, `C_HOLD12 (119.15,120.45,0)` | Each reserves one authored first-row hold-bank body/assembly site under ADR 0011. |
| `C_HOLD13 (82.85,129.55,0)`, `C_HOLD14 (94.95,129.55,0)`, `C_HOLD15 (107.05,129.55,0)`, `C_HOLD16 (119.15,129.55,0)` | Each reserves one authored second-row hold-bank body/assembly site under ADR 0011. |

I checked the exact set against the current source floorplan and its isolated native board (pre-refill SHA-256 `18e55f44d5c1a8f7a7dd050e12ca451f6e08932b8c79893a0ad74e3b18be861b`). The check required 27 unique refs, exact equality to the 11 connector plus 16 hold refs, membership in authored anchors/post-anchors, and 27/27 native `(x,y,rotation)` matches within 0.001 mm/degree. All native NPTH-bearing refs (`J1..J8`, `J_PWR`) are in the set. It also explicitly rejected `U_XU`, `U_USB_ESD`, `U_USB_CC_ESD`, `C_XU_VDD_104/_106`, `C_PLL_100N/_1U`, and `FB_PLL` from the fixed list. **Result: PASS.**

The source-anchored XU decouplers, USB/PLL support, and other local electronics remain P2-movable obstacles for coarse capacity; their physical re-placement still requires owned electrical/clearance rechecks. The hardened checker requires every native NPTH-bearing ref explicitly in `p1_fixed_refs` and validates its source/native pose; `J1..J8` and `J_PWR` meet that requirement. No P1 capacity, connector FULL, or acceptance conclusion follows from this pose check.
