# Public 3313A mask and width sensitivity — 2026-09-25

**Disposition: the two input sets preserve the narrow fixed-geometry numeric
feasibility hypothesis; keep the four-file 3313A source proposal unadopted.**
This is a public, unauthenticated calculator comparison. It supplies neither
a production impedance value nor a JLC commitment to use either process-input
set for an order. The [source-adoption gate](../2026-09-25-unadopted-3313a-controlled-pair-sol/source_adoption_gate.md)
still requires current stack/geometry reconciliation, exact-order and
coupon/TDR review, and the independent endpoint/return and native parity
checks before source promotion.

The [public JLC calculator](https://jlcpcb.com/pcb-impedance-calculator)
returned named special template `JLC04161H-3313A`, key `832`, access ID
`5010a4d2e49c43daaa9fa0e75447f761`: 4L, 1.58 mm ±10% finished,
1-oz outer/0.5-oz inner, L1–L2 3313 prepregs 0.107 + 0.0994 = 0.2064 mm
at Er 4.1, and 1.065-mm core at Er 4.38. The template query was HTTP 200,
`Fri, 25 Sep 2026 21:24:47 GMT`. The live public coverlay and copper-width
config queries were HTTP 200 at `21:24:48` and `21:24:49 GMT`, respectively.
The live configuration still returned 1.0/0.6/1.0 mil mask,
1.6-mil copper, and 0.5-mil top-width reduction. JLC's
[calculator guide](https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator)
(updated 2026-09-16) describes 1.2/0.6/1.2 mil mask, Er 3.8,
1.6-mil outer copper and a 0.7-mil top-width reduction. The guide values
are manually substituted in case two; the live config endpoint did not
return them.

Both `DiffEdgeCoupledCoatedMicrostrip1B` API calculations used F.Cu to L2,
H1 0.2064 mm/Er1 4.1, base/artwork W1 0.180 mm, artwork gap S1 0.100 mm,
T1 1.6 mil, CEr 3.8, and the same remaining numeric arguments from the
[retained frontend capture](frontend_binding_capture.json). Only C1, C3,
W2, and `W2LinkW1Incr` changed; C2 stayed at 0.6 mil. W2 is the modeled top copper width. The
artwork/base width and spacing did not change.

| Input set | Mask C1/C2/C3 (mil) | Top reduction (mil) | Modeled top width (mm) | API result (Ω) | HTTP Date |
| --- | ---: | ---: | ---: | ---: | --- |
| Retained live config | 1.0 / 0.6 / 1.0 | 0.5 | 0.16730 | 89.9172598796 | Fri, 25 Sep 2026 21:24:50 GMT |
| Guide parameters | 1.2 / 0.6 / 1.2 | 0.7 | 0.16222 | 89.8423260743 | Fri, 25 Sep 2026 21:24:51 GMT |

Both response bodies report `impedance_calc_status: 0` and
`dResultValid: 1`. The guide-input result is **0.0749338053 Ω lower**
(about 0.0833% of the retained result). This small modeled change leaves the
0.180/0.100-mm, near-90-Ω hypothesis numerically plausible under both sets.
It does not resolve which process assumptions govern a production order,
actual finished width, tolerance, routing/return fit, or source adoption.

Reproduce with `python3 replay_mask_sensitivity.py` from this directory;
it reads the retained capture, refreshes only the public template and
configuration endpoints, and sends the two public `/calc` requests.
The complete selected template, exact requests, responses, validity flags,
and HTTP dates are in [mask_sensitivity_capture.json](mask_sensitivity_capture.json).
SHA-256: retained capture
`71ec96168517575b0896011f63d52ec5fcb66c67641a4d85dab12483c2d182b3`;
replay program
`07a2d3957e3384947c48d9e3b59d6857f1e35fc2acb54283c9ecc3c63e4a9713`;
new capture
`9e08ce38014bde96465cea15ce70a48c0cf0efaa7b17c19ea5a8b7f808bdae18`.
The retained frontend JS SHA-256 was
`dd57ca32426d511d6fe392ae66c205c872601a9837a56763b78c6d334ad7aec5`.
