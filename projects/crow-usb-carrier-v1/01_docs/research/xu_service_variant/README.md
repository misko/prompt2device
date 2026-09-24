# XU service-cell ownership variant — geometry probe

**Disposition: promising source-compatible rectangle split; INCOMPLETE research.** No canonical floorplan, requirements, net, board, or P1 state was changed. This diagnostic follows Terra's exact-source next-packet note (commit `2393f2ac`) and pins `main` source `9c73181c432b51558003a8be7e496cc8c6757d5a`: floorplan SHA-256 `a882f87682484c37c5766a9e37c5a0d93b38a8e5a775fb1ab4425011da40a275`, modular plan `7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e`, and P1 requirements `9ef85e5f4918dea0378203a97fa631ce2e73a690170235902a97a6c8e30527d8`. Native shape measurements use the exact-source generated board `/tmp/crow-usb-regions-terra-HqnO4Z/project/04_kicad/crow_carrier.kicad_pcb`, SHA-256 `60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17`.

The proposed *source rectangles* are `xmos_core [190,84,232,114]` and `clock_flash_debug [190,114,232,136]` mm. They share only the y=114 edge. The first trial with XU north edge y=82 was rejected: it overlapped `analog_ch8` by 22 mm². At y=84 the two new cells have zero interior overlap with each other or any other source region, remain inside the board outline, and retain every one of the 29 XU and eight clock/flash assigned native footprint envelopes. Each envelope is the union of KiCad's full footprint bounds and F.CrtYd when present. None of the five outer/common boundary segments crosses an envelope or native pad. This is a rectangle-only proposal compatible with the current `placement.regions` shape; it has not been regenerated as a variant board.

| Service face | Proposed segment | F.Cu span | Required span | Native window hits |
| --- | --- | ---: | ---: | --- |
| QSPI, six nets | y=114, x=200–205 mm | 5.00 mm | 2.70 mm | zero native pads, footprint envelopes, foreign source regions |
| JTAG/reset, five nets | y=84, x=222–225 mm | 3.00 mm | 2.25 mm | zero native pads, footprint envelopes, foreign source regions |

The face windows are `qspi [200,111.9,205,117.9]` and `jtag_reset [222,82,225,86]` mm. They are disjoint and inside the outline. They are **diagnostic windows**, not exclusive source-owned reservations: the QSPI window deliberately straddles the proposed XU/clock boundary, and JTAG extends north of the XU cell into unassigned space. Source ownership of these windows must be expressed and checked before a packet can pass Terra's exclusive-reservation requirement. The current floorplan has no `keepouts` and the generated board has **zero native rule areas**. Their nonintersection is vacuous; preservation under future rule areas remains unproven. The north JTAG path toward fixed `J_JTAG` also encounters the existing `usb_frontend` ownership strip at y=35–70 mm; this study proves no continuous JTAG corridor through it.

The measurement enumerates all 33 declared ref-pad endpoints with native pad/net checks, including all 27 P1-fixed references and the five fixed JTAG connector pins. Every one of the 28 movable endpoint records carries `P2_REQUIRED` pad-to-face and local-return obligations. QSPI pins, flash pads, crystal pins and local decoupling remain P2-movable; the empty faces do not credit or accept their relocation. Crystal has no measured face. ADC/timing, analog ownership, USB, return continuity, connector fit and routes remain unresolved. This is **not** a P1 receipt, P2 placement approval, route permission, impedance result or acceptance claim.

Reproduce the pinned measurement with native KiCad 10 `pcbnew` and PyYAML:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/xu_service_variant/measure.py /tmp/crow-usb-regions-terra-HqnO4Z/project/04_kicad/crow_carrier.kicad_pcb > /tmp/crow-xu-service-measurement.json
python3 projects/crow-usb-carrier-v1/01_docs/research/xu_service_variant/verify.py
```

[measurement.json](measurement.json) is the machine-readable result, including every source hash, native endpoint, ownership and boundary measurement. The script fails closed on a different source or board hash.
