# Exact Crow QSPI integration-corridor packet — rejected

**Whole-packet result: FAIL, not P1 admission.** This is an isolated source
variant against the regenerated QSPI-gap board SHA-256
`fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27`.
The canonical Crow floorplan, P1 source and governed task state were not
changed. The checker validates the new source-declared corridor before the
allocation loop, then rejects the unchanged JTAG witness `U_XU.51` as a
nonlocal bridge. Because the allocation aborts there, its thirteen QSPI
witnesses are not consumed; the global exact-endpoint check reports
`qspi_gap: integration affected endpoint/layer denominator mismatch`.
These are linked errors, not evidence of missing QSPI pins in the packet.
The separate [declaration validation](qspi_declaration_validation.json) invokes
the native source-corridor and all thirteen witness checks directly and records
`INCOMPLETE_SOURCE_GEOMETRY`; it is deliberately not a whole-allocation verdict.

The packet derives **13 exact ref.pad/net endpoints** from the current modular
plan: six `U_XU` pads, six `U_FLASH` pads and `R_QSPI_CS.2`. It binds all six
QSPI nets and all 13 P2 pad-to-face obligations to one
`board_integration_qspi [199.8,110.5,223.2,118.5]` mm region and one F.Cu
reservation. The XU south and clock north faces are respectively
`[219,110.2,222.8,110.5]` and `[219,118.5,222.8,118.8]` mm. Each offers
3.8 mm raw span against 2.7 mm source demand, without effective clearance or
pad escape proof. The separate GND return obligation names **In1.Cu**, the
Crow F.Cu reference layer. Native board geometry has no physical
body/courtyard/pad, routed copper, foreign source region or rule-area overlap
with the corridor or faces. The checker gives no rough capacity credit for a
corridor reservation; even a completed allocation would remain `INCOMPLETE`
until P2 native pad access and filled-reference continuity are proven.

The other four allocation rows remain `INCOMPLETE`; their declarations and
the full 59-net coverage are retained. The seven non-QSPI XMOS-service nets
remain in the same allocation and are **not** cleared by this packet. The
next source repair must replace the oversized JTAG/reset witnesses with local,
owned handoffs and resolve the JTAG continuation through `usb_frontend`.
Crystal witnesses and their clock-cell reservation still need local P2 access
and effective-capacity review; the old crystal reservation was trimmed from
y=117.8 to the new clock-cell edge y=118.5 solely to avoid double allocation
of corridor space. No route, filled return, P1 capacity or acceptance is
claimed.

The first exact-board check exposed a generic footprint-envelope issue:
`GetBoundingBox(True,True)` includes movable reference/value text. For
example `C_XU_VDD_11` has a physical body ending at y=109.885 mm but text
extends to y=112.862 mm. The checker now uses native body plus F/B courtyard
and explicit pad bboxes, matching the earlier QSPI gap measurement while
still rejecting non-text graphics. The focused native fixture suite has 44
passing tests, including text-only overlap, non-text intrusion, and F/B
courtyard-only intrusion.

Reproduce with KiCad 10 `pcbnew` and PyYAML from the repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/xu_service_variant/p1_qspi_packet/build_packet.py
python3 -m unittest skills/kicad-pcb/scripts/tests/test_p1_coarse_capacity.py
```

The builder pins the canonical P1 source SHA-256
`9ef85e5f4918dea0378203a97fa631ce2e73a690170235902a97a6c8e30527d8`,
modular plan `7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e`,
USB alias part `a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e`,
and gap floorplan `cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925`.
The source variant SHA-256 is
`9a13c0999d29f17280bb5d8ffb98a5e0d59afe3ee4511eb004e436bffc13ece4`;
the contract SHA-256 is
`b17a94fedafbc334bdc0721535c640fb786f4b632b1abddf487289fdb19fbda4`.
The temporary board can be regenerated as described in
[`../QSPI_GAP.md`](../QSPI_GAP.md); `build_packet.py` fails closed on any input
hash or rejection-outcome drift.
