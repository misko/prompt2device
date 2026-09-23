# Independent read-only composition review — root 70be34e5

**Disposition: ACCEPT source composition** of the reviewed adjustable main-buck stack with the previously reviewed core-feedback correction and user D9 manual THT plan. Reviewed `/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922` at `70be34e5068fa50554308857621681ddc14bb156`. This does not qualify the PCB or sealed release.

## Source comparison

The composed root's `N5V_BUCK`, `N3V3X`, `N1V8`, and `N3V3_ADC` rail dictionaries, and all five cap-bank dictionaries touched by the main-buck candidate, equal the accepted `27854a15` candidate by parsed YAML. Its U_BUCK TSX, adjustable TPSM dossier, native RDH footprint and protection-path rule are byte-identical to the accepted stack. `N0V9` retains the core-fix executable 49.9 kΩ/100 kΩ feedback block with ±50 nA FB bias and 120 pF feedforward while its parent VIN advances to 4.91–5.13 V. The 100 kΩ core bottom code C852472 and new 10 kΩ main-buck bottom code C190095 occupy separate exact-parts CSV rows. `N3V3_ADC` parent maximum is 5.13 V.

The manifest has 509 unique references and contains each of R_CORE_FB_TOP, R_CORE_FB_BOTTOM, C_CORE_FF, R_BUCK_FB_TOP and R_BUCK_FB_BOTTOM once. Fresh diagnostic circuit `projects/crow-usb-carrier-v1/06_build/verification/mainbuck-composition/circuit.json`, SHA256 `55fe91b712aa1aabb0ad6d6316e7c763f55c0fcac6aa04870e542bbeca110391`, has 509 source components, 1,659 source ports and 89 distinct MPNs. It maps U_BUCK to TPSM63603RDHR/C5219327, its top/bottom to C852775/C190095, and U_CORE, 49.9 kΩ top, 100 kΩ bottom and 120 pF Cff to the expected exact codes.

D9 is confined to J1–J8 and C_A1–C_A8 P/N: 24 references, all present in the full design, all without JLC supplier codes in the fresh circuit, and exactly the two `not_assembled` rows in `assembly.yaml`. The floorplan's `exclude_from_pos_files` pattern covers those same 24 refs. U_ADC remains outside this manual exception and is still required for JLC placement. These are source/assembly-plan facts, not an assertion that THT parts have been purchased or fitted.

## Reproduced gates

- E-TOPO using `/tmp/crow-root-mainbuck-view` with the fresh diagnostic circuit and current source symlinks: **13/13 rails**, **3/3 converter parts**. Main feedback computes 4.917–5.124 V within declared 4.91–5.13 V; core feedback computes 0.886–0.913 V within 0.88–0.92 V. LT3045 parent maximum 5.13 V yields 477 mW versus 650 mW allowed.
- E-MARGIN: **13/13 rails**; E-CAP: all banks pass (main buck output 33.311/25 µF, core input 3.305/3 µF, core output 12.954/10 µF); E-SURGE: external input passes with selected TPSM63603RDHR identity.

Physical gates from the accepted main-buck review remain: loaded/ripple/temperature 4.91–5.13 V, 1 oz board θJA≤31.98°C/W at full 1.9 A allocation, hot D_HOLD/Q_PRE drop≤0.81 V, FB/AGND placement, capacitor lot behavior, and startup/precharge/reset waveforms. The canonical commissioning circuit is intentionally historical; the fresh circuit above is verification-only.
