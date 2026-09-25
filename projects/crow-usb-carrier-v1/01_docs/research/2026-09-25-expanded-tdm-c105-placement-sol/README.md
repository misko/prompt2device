# Expanded TDM C105 placement probe

**Research-only `INCOMPLETE`; no P1/P2 or route credit.** The frozen expanded board already contains the earlier 27-reference coupled timing placement. This packet tests one additional P2 pose: `C_XU_VDD_105` `(196.5,96.3,180°)` → `(198.25,97.05,180°)`. The [receipt](receipt.json) pins the **expanded private board's** P1 source/floorplan packet, native source floorplan, project rules, and checkers. [replay.py](replay.py) refuses an existing output directory and writes the native board, one-post-anchor floorplan copy, full checker result, and comparative DRC only to fresh scratch. The canonical `03_src/floorplan.yaml` instead anchors C105 at `(196.5,97.1,0°)`; this packet does not bridge that source difference. Direct adoption requires generation from revised canonical source and fresh parity/placement review.

The C105 pad-1-to-owning `U_XU.105` distance improves **3.8898→2.1223 mm**. The exact non-endpoint full-envelope screen of `[188,94,190,99.84]` grows from **1.6768 to 4.5384 mm**, or **3→10 rough 0.45-mm slots**. All 33 P1-fixed poses and all other footprint poses stay unchanged; no new courtyard intersection appears. In equivalent scratch project/library contexts, refilled native DRC is **zero violations and 499 unconnected** for both boards. The full source-bound checker retains **14 timing reservations/54 P2 pad duties**, zero errors and diagnostics, and `INCOMPLETE`.

This only improves a geometric aperture. Four exact endpoint escapes, a connected corridor, filled In1.Cu return along actual paths, XU power return, timing/SI, and final silk remain open. The scratch pose and floorplan are not a source-generated production board or placement admission.

From this worktree root, reproduce to a new directory:

```sh
/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-expanded-tdm-c105-placement-sol/replay.py /tmp/crow-expanded-tdm-c105-new
cmp /tmp/crow-expanded-tdm-c105-new/receipt.json projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-expanded-tdm-c105-placement-sol/receipt.json
```
