# ADC8N west-before-USB exit screen

**Disposition: no physically useful west exit exists under the current source boundary.** A 0.20-mm copper-only grid can reach x<195 before entering y>62, but it uses a zero-margin tangency to `usb_vbus_sense` and only 0.005 mm to the native cap courtyard. It is not a source-owned corridor or a candidate route/return result.

The screen used the immutable southwest-cap board SHA-256 `0b9d017706845ad4d77c2b579dd36f2e34c0ecf55a7b699ace4fca97465c5b93`, checker `_physical_envelope`, all native pad boxes, the 0.20-mm F.Cu width, and the 0.150-mm different-net clearance. The exact launch is `C_ADC_AC8N1.2` at `(199.80,60.05)` on `ADC8N`; the local target is `C_ADC_CM8N.1` at `(187.52,66.50)`. Current `usb_vbus_sense` is `[195,62,220,82]`.

`C_ADC_AC8N1` has a full native envelope `[195.205,58.305,200.795,61.795]`. To leave below it without a courtyard intersection, a 0.20-mm stroke needs center y >= 61.895. To remain at or below the USB rectangle's north face, it needs center y <= 61.900. The available vertical band is consequently **0.005 mm**. A conservative pad-clear grid finds this limiting centerline:

```text
(199.80,60.05) -> (197.90,61.90) -> (194.50,61.90)
```

It crosses x=195 while its top edge is exactly y=62.000. Thus it has no positive source-boundary clearance; treating closed geometric boundaries as intersecting rejects it outright. Moving the trace down to give a positive USB gap intersects the cap courtyard. Moving it up enters `usb_vbus_sense` before it is west of x=195.

After this degenerate exit, a full-envelope screen can route around other native bodies on the west side, for example through `(194.50,63.10)`, `(191.70,65.90)`, `(188.10,65.90)`, then the target. That observation does not repair the launch: it only confirms that `U_SPOKE8` need not be the limiting body once x<195. The launch's 0.005-mm gap is the governing obstruction.

SOL's immutable local-route packet `09740988` proves filled In1 coverage only beneath its *different* route, which crosses `usb_vbus_sense` by about 3.96 mm. Its fill, DRC result, GND stitches, and local connectivity cannot be transferred to this hypothetical west route. A new candidate would need fresh native DRC, a filled In1 ribbon check, exact endpoint connectivity, and source-region/physical-cell authority. No J8 edge attachment or mechanical-cell credit is used or implied here.
