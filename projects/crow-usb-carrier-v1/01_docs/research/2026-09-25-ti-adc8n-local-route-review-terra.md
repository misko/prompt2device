# Independent review: ADC8N local route and filled return

**Disposition: accepted as a bounded local route/return research witness; not a source-owned corridor, physical-cell, P1, or P2 result.** I reviewed immutable SOL commit `09740988` and reran its hash-pinned `route_probe.py` against the complete frozen TI profile. The replay reported baseline/candidate **199 violations and 499 unconnected**, violation-identity delta `+0/-0`, zero V-PROCESS failures, six 0.20-mm F.Cu ADC8N segments totaling 15.179545 mm, and a filled In1.Cu zone.

Native connectivity on the saved filled candidate independently shows that the new component contains exactly `C_ADC_AC8N1.2` and `C_ADC_CM8N.1`. These are both `ADC8N`; the other native ADC8N pads, `C_ADC_AC8N2.2` and `U_ADC_B.13`, remain outside that local component. The route vertices and 0.20-mm width match the receipt. The tightest effective-shape gap is 0.190001 mm to `C_ADC_CM8N.2`, leaving only 0.040001 mm over the 0.150-mm rule. That is sufficient for this native research replay, but too narrow to treat as assembly/fabrication qualification.

The candidate has one filled GND `In1.Cu` zone with nine filled outlines. The packet's polygon subtraction test reports zero uncovered area for every 0.20-mm-wide route ribbon segment and puts the route, both ordinary 0.60/0.30-mm GND stitches, and the existing `U_ISO8.5` via in filled outline 8. Direct native inspection confirms the stitches at `(199.80,58.00)` and `(188.95,66.50)` and their F.Cu necks to `C_FILTER8N1.2` and `C_ADC_CM8N.2`. This supports a local reference-plane witness only; it does not prove the complete channel return-current tree.

The route is not owner-local: its diagonal enters current `usb_vbus_sense` from `(197.8,62.0)` to `(195.0,64.8)` while its source owner remains `analog_ch8`. It therefore cannot be credited as a typed cell, exclusive ADC8 pocket, or source corridor. The packet contains no `edge_attachment`, no source physical-cell change, and no J8 movement: J8 remains `(204.0,26.86)` with its existing `[198.875,19.955,216.268081,34.495]` checker envelope. It correctly claims no J8 mechanical-cell credit and no P1/P2 acceptance.

One correction is needed in the packet prose: both committed DRC JSONs contain 499 unconnected rows and their pair-identity set changes by **9 added / 9 removed**, not the README's “ten each way.” Neither DRC report names `ADC8N`, so those rows cannot establish the new connection; the native connectivity check is the valid endpoint evidence. This documentation mismatch does not change the DRC violation delta, route geometry, or local fill result.

Remaining blockers are the other two ADC8N terminals, the ADC8P/VMID2 branches, source-region/physical-cell conflict, full analog demand, and broader route/return, assembly, and connector evidence.

Verification run:

```sh
python3 01_docs/research/2026-09-25-ti-adc8n-local-route-sol/route_probe.py
```
