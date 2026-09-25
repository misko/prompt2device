# Independent review: ADC8N cap-clear north escape

**Disposition: the cap/USB/return measurements reproduce, but reject this route for P2 promotion.** It is a useful local geometry diagnostic only. Its long signal segment passes under `U_SPOKE8`'s native body, with no assembly, noise, coupling, or layout-intent qualification.

I reran immutable SOL commit `36ecb993`'s `north_probe.py`. The hash-pinned full TI profile reproduces baseline/candidate **199 violations / 499 opens**, violation delta `+0/-0`, and zero V-PROCESS failures. All 569 footprint pose/pad ledgers and the 27 fixed references remain unchanged. Native connectivity joins exactly `C_ADC_AC8N1.2` to `C_ADC_CM8N.1`; the other two ADC8N pads remain outstanding. The one filled In1 GND zone covers every 0.20-mm ribbon segment with zero uncovered area, and both named GND stitches connect to their declared pads.

The eight-segment F.Cu route is 20.016804 mm, 4.837259 mm longer than the first local route. Apart from the unavoidable named pad launch `(199.8,60.05)->(199.8,58.05)`, its full copper clears `C_ADC_AC8N1`'s checker envelope by 0.055001 mm and `usb_vbus_sense` by 0.147488 mm. Its different-net native copper gap is 0.190001 mm to `C_ADC_CM8N.2`, only 0.040001 mm over the rule. These are native geometry measurements, not fabrication margins.

The southern-throat rejection is correct. With cap south edge y=61.795 and USB north edge y=62.000, a 0.20-mm trace has at most 0.005 mm total remaining space. The tested balanced center y=61.8975 gives 0.002501 mm to each boundary; the lower test intersects the cap and the upper test is effectively tangent to USB. No physically meaningful south corridor follows.

The north route avoids those two obstacles by using `(195.05,61.6)->(190.75,65.9)`, which intersects `U_SPOKE8`'s full envelope `[187.805,60.805,192.195,65.195]` and body `[187.825,60.825,192.175,65.175]`. Electrical DRC has no pad violation because this is copper under a component body, but that does not demonstrate placement clearance, analog-noise behavior, field coupling, serviceability, or an acceptable local route. It is sufficient reason not to advance this particular path toward P2.

I also independently screened the proposed separate cap shift to y=59.85 on the southwest-cap board (commit `47ae38ea` on the shared research branch). Its translated envelope `[195.205,58.105,200.795,61.595]` has no native envelope collision, grows the USB margin to 0.405 mm, and leaves `C_A8P`/`R_B8P`/`C_FILTER8N1` gaps of 0.360/0.480/0.580 mm. It improves cap-pad-to-`U_ISO8.6` distance to 7.560589 mm but worsens cap-pad-to-`C_ADC_CM8N.1` distance to 13.964988 mm. That is a placement variable only; it needs a source-generated, full-profile route/return and ownership replay before it can replace the present anchor.

No J8 edge attachment, source physical cell, P1, or P2 credit is present or implied.

Verification run:

```sh
python3 01_docs/research/2026-09-25-ti-adc8n-cap-clear-sol/north_probe.py
```
