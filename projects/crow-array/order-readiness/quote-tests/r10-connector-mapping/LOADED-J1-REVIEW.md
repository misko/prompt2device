# Pod J1: captured geometry supports test C

2 November 2026. **Diagnostic evidence, not manufacturing approval.** Native
boards, r10 uploads and all JLC drafts were unchanged during this backend review.
This assessment supersedes the earlier requirement to infer the insertion
origin solely from obscured underside screenshots.

The actual C599441 footprint captured at commit `9cec4096` supports test C:
**J1 X 10.556 mm, Y −9.390 mm, rotation 180°, Top.** Baseline A is reversed;
rotation-only B leaves a 1.017 mm translation error. There is no reason to
redesign or move the native board's correct connector footprint for this test.

## Numerical comparison

All residuals are maximum centre-position differences against the unchanged
native pod. These are nominal CAD measurements, **not permitted manufacturing
tolerances, finished-hole fit, or acceptance of the live draft**.

| Trial | JLC X, Y (mm); angle | Captured eight-pin maximum error | Captured two-peg maximum error |
| --- | --- | ---: | ---: |
| A, baseline | 10.556, −8.373; 0° | 7.655 mm | 5.843 mm |
| B, rotation only | 10.556, −8.373; 180° | 1.017 mm | 1.017 mm |
| C, rotation and origin correction | 10.556, −9.390; 180° | 0.014 mm | 0.004 mm |

The public OBJ referenced by the captured footprint was also downloaded and
measured independently of the native-hole positions. After replaying the
inspected viewer transform and test C, its eight terminal-tip profile centres
are within **0.018 mm**, and its two forked peg-bottom profile centres within
**0.022 mm**, of the native centres. Those profile centres are not a dimensional
qualification of the full metal tails or plastic peg surfaces.

The downloaded OBJ has the same UUID and 523,591-character length as the
MacBook cache observation. Its SHA-256 is
`7e16867569831cd98a298dcf3dc5d4692343d067e36dc1aed26f7216d8ff39da`.
**The browser's cached OBJ was not supplied or hashed, so byte equality remains
unproved.** Do not label this a direct measurement of the saved browser scene.

## What the viewer code establishes

Source: [JLCEDA/EasyEDA Official Library](https://lceda.cn/) and
[EasyEDA](https://easyeda.com/). The full captured record, including its original
attribution, remains unchanged in [the MacBook extraction](macbook-j1-cache-20261102/README.md).

The inspected public [engine 3.2.37.6ef6298e](https://modules.lceda.cn/smt-gl-engine/3.2.37.6ef6298e/smt-gl-engine.js)
has SHA-256 `e291df6d440e67289a430eda8244ad48138841d6fa74b5faafe2e73ecfc246e7`.
The [UI 1.0.213.a3dc0292](https://modules.lceda.cn/smt-ui/1.0.213.a3dc0292/smt-foreign-trade.js)
has SHA-256 `5226c650bdcfc213fa6b8bd216778719c0fa2162723e6f7d2e09b755ae3b461e`.
These versions match the prior MacBook report; later versions require review.

- Footprint parser `Ld` subtracts canvas fields 16/17, `(3985.945, 2993.504)`.
  Raw coordinates are 10-mil units, or 0.254 mm, despite the canvas display-unit
  string `mm`. The independently specified locator span becomes 12.70 mm.
- `Ld` uses the model UUID in `SVGNODE.attrs.uuid`, namely
  `7d3d1c9e95104606a19576559311bb67`. It does not consume the different header
  `uuid_3d`. That metadata discrepancy therefore does not block this transform
  calculation; its historical cause is still unknown.
- The shape has no `transformV2`; its rotations are zero. The projected-outline
  centre differs from `c_origin` by only 0.0005 mil per axis, below the engine's
  0.1-mil override threshold. No origin override is triggered.
- For this real-model path, `N$` recentres the OBJ's XY bounding box, subtracts
  its minimum Z, applies uniform scale, and then applies the shape offset.
  In millimetres the resulting uniform scale is 0.999998 and the model origin
  relative to the footprint is `(0, −1.0230104, −2.999994)` in viewer Y-up axes.
  This model recentering does **not** recenter the footprint's numbered pads.
- CPL coordinates then translate/rotate the component. The captured baseline
  has zero panel offsets/angle and no recorded polarity-quadrant override.
  This analysis is conditional on those effective transforms remaining true.

The existing original-skill measurement code verifies native numbered pads
against retained manufacturer references, fits the catalog by pin number, and
replays the candidate without refitting. The new calculation substitutes the
actual captured JLC footprint for the previously retained converted footprint.
It also measures the public model's bottom profiles without fitting them to
board holes. Full per-feature results are in [loaded-j1-analysis.json](loaded-j1-analysis.json).

## Next MacBook handoff: one controlled C test

Use only [POD J1 AB TEST NOT FOR ORDER](https://cart.jlcpcb.com/smt-order/?pcbFileNo=1f8dfa850b474dc9b4ac3860b26bbd59).
Keep native files, original r10 package and original production-intent drafts
unchanged. No purchases, reservations, substitutions, vendor messages or
manufacturing approvals. Keep all required parts selected.

1. Confirm baseline A, exact RJHSE-5080 / C599441, 10 fabricated / 8 assembled,
   and both review preferences set to **Do not confirm automatically**. Recheck
   current loaded versions, package/model identities and zero panel transform.
2. Export only the already-loaded OBJ cache string for model
   `7d3d1c9e95104606a19576559311bb67`, or compute its UTF-8 SHA-256 locally.
   Reuse the working read-only cache access from the last extraction; do not
   search arbitrary private endpoints or export unrelated cache/account data.
   Compare with the hash above. If different, retain that exact asset for
   backend interpretation; do not assume the fresh download equals it.
3. If identities/transforms match, upload the existing
   [test C CPL](generated/pod-ALL-CONNECTORS-RAW-ORIGIN-TEST-ONLY.csv).
   This changes only J1 relative to A. **Do not repeat B or drag/rotate manually.**
4. Record J1's saved/effective row: **X 10.556, Y −9.390, angle 180°, Top**.
   Capture the complete effective component/panel transform, not merely the
   toolbar's rotation increment. Reopen and confirm persistence. The expected
   native-board centres are pin 1 `(7.000, 8.500)`, pin 8 `(14.112, 10.280)`,
   and pegs `(4.210, 5.960)` / `(16.910, 5.960)` mm; all eight pins are recorded
   in the calculation, not just these endpoints.
5. Capture top/oblique views identifying the board notch, connector body and
   actual cable-entry mouth. The mouth should face the native **−Y edge**.
   If pins remain visually occluded, matching the exact cached asset plus
   effective transform supplies numerical registration evidence; do not call
   another opaque screenshot a failed physical alignment test. Conversely,
   an unexpected extra transform or visibly inward mouth requires a stop and
   a focused evidence capture, not a second arbitrary correction.
6. Restore [baseline A](../r10-pod-j1-180/pod-cpl-J1-000-BASELINE.csv), reopen to
   confirm restoration, and leave the diagnostic draft on HOLD. Return the
   file hashes, before/C/restored effective rows, identity/asset check and
   labeled mouth views for backend review. Do not copy C to production drafts.

If the cache or saved transform cannot be accessed, return the exact missing
item once. Do not reopen the same visual-only investigation indefinitely.
Carrier J101–J108 still require instance-level checks after the pod review;
carrier power J1 uses a different package and requires its own loaded-geometry
check. This report closes neither carrier mapping nor overall order readiness.

## Reproduction

`loaded_j1_analysis.py` is deliberately limited to this hash-bound snapshot,
not a general-purpose OBJ metrology tool. Its fixed-asset terminal extraction
checks eight four-vertex tip groups and two peg-bottom profiles. A changed
asset fails closed. The four new tests cover units/origin, A/B failures, C's
complete feature registration, and swapped pin labels; the existing ten
mapping tests continue to cover quarter-turns and source/CPL preservation.

From the repository root, download the public OBJ to a temporary directory
and verify the hash above (no sign-in is needed):

```sh
curl --fail --location https://modules.lceda.cn/3dmodel/7d3d1c9e95104606a19576559311bb67 --output /tmp/crow-j1-live-model-7d3d1c9e.obj
/usr/bin/python3 -B projects/crow-array/order-readiness/quote-tests/r10-connector-mapping/loaded_j1_analysis.py --model /tmp/crow-j1-live-model-7d3d1c9e.obj --output projects/crow-array/order-readiness/quote-tests/r10-connector-mapping/loaded-j1-analysis.json
/usr/bin/python3 -B -m unittest discover -s projects/crow-array/order-readiness/quote-tests/r10-connector-mapping -p 'test_*.py'
python3 projects/crow-array/order-readiness/r10_upload_check.py
```

The script creates a missing report or checks identical existing bytes; it does
not overwrite a differing report. KiCad Python emitted enum/image-handler
diagnostics in this environment, but the tests completed successfully.
