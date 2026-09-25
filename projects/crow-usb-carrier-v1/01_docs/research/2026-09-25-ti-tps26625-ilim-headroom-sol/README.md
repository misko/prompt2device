# One bounded ILIM first-via headroom screen

This research packet starts from the source-generated TPS26625 recut in `../2026-09-25-ti-tps26625-placement-return-sol/` (commit `96de6901`) and changes **only** the first ordinary `SPOKE_ILIM8` via center and its connecting F.Cu/In2.Cu segments. Its pose, 27 fixed refs, 569 pad identities, ADC8N, GND stitches, output route, and separate RTN topology are unchanged. It confers no P1/P2 or manufacturing acceptance.

`scan.py` evaluates a finite 0.05-mm grid, x=191.95–192.35 and y=47.60–48.05 mm, using native effective F.Cu via and 0.20-mm launch shapes against foreign F.Cu pads/tracks. Nine of 90 sampled centers meet the analytic ≥0.20-mm via gap and launch screens. The best sampled center is **(192.20,47.80)**: nearest foreign copper is U_SPOKE8.8 at **0.249267 mm**; the GND return gap is **0.260253 mm**. This is a discrete local screen, not a continuous optimum or tolerance model.

`replay.py` tests exactly that candidate with the pinned complete `.pro`/`.dru`/POFV/V-PROCESS profile. The first ILIM via moves from (192.10,47.90) to **(192.20,47.80)**. Its previous limiting GND gap of **0.200011 mm** gains **0.060242 mm**; the new minimum foreign F.Cu gap is **0.249267 mm** to U.8, or **0.049267 mm** above the 0.20-mm screen. U.6, PowerPAD.11 and output gaps are 0.490417, 1.075011 and 0.950011 mm. Both ILIM vias remain ordinary off-pad 0.60/0.30-mm vias and V-PROCESS reports no failure.

Native profile remains **199 violations / 499 reported opens**, with **+0/−0 issue identities**. Named input, output, ILIM, GND, and RTN connectivity pass; both GND stitches still contact one filled In1 GND outline, separate from RTN. The ILIM signal centerline grows from 3.823489 to **4.053741 mm** (+0.230252 mm), and its diagnostic ILIM/RTN projected area grows from 5.073437 to **5.204687 mm²** (+0.131250 mm²). These geometric tradeoffs and the remaining board/thermal/return debts require independent review; no copper current or process tolerance adequacy is claimed.

Reproduce with `python3 scan.py` and `python3 replay.py` from this directory; both use temporary native boards and commit only scripts and JSON receipts.
