# Four-net JTAG source-model trial

**Disposition: INCOMPLETE; the whole P1 packet FAILS.** This isolated variant
models only `JTAG_TCK`, `JTAG_TDI`, `JTAG_TDO`, and `JTAG_TMS` in the native-open
F.Cu strip `[221,65,226,84]` mm. It leaves `XU_RESET_N` as a separate
three-owner branch. No canonical source, board, governed task, or routing was
changed.

The variant splits the former five-net `jtag_reset` source demand into four
two-party JTAG nets (four 0.45-mm source slots) and a declared-incomplete reset
branch. It adds `board_integration_jtag` in the 19-mm gap between the
`debug_connector` south face at y=65 and the `xmos_core` north face at y=84.
The `usb_frontend` rectangle ends at y=64.7 instead of y=70 so its source
ownership does not overlap the 0.3-mm debug face. The exact four XU and four
fixed connector ref.pad/net identities are source-declared, with eight
pad-to-face obligations and an In1.Cu GND return obligation. The checker
validates the source corridor geometry and all four XU handoff witnesses.

On the pinned saved board, the strip has no native F.Cu rectangular obstacles.
The current optimistic `connected_capacity` screen reports 5.00 mm connected
raw width and 11 slots at 0.45 mm pitch, against four source-demand slots.
That result covers the open middle strip only. It does not include effective
clearance, a fixed-connector-to-strip access path, XU pad-to-face access, a
filled GND return, or simultaneous disjoint routes.

The checker explicitly rejects a `J_JTAG.4` integration handoff because
`J_JTAG` is P1-fixed; the same contract rule applies to the other three fixed
connector pads. The whole allocation also stops at the unchanged
`U_XU.38` reset witness, which is a nonlocal bridge across its source region.
Consequently the QSPI corridor's thirteen existing witnesses are not consumed,
and the whole-packet error remains
`qspi_gap: integration affected endpoint/layer denominator mismatch`.
This is a linked failure, not a loss of the QSPI endpoints from source. The
current coarse checker does not establish connectivity between a separate
fixed-connector access reservation and this integration reservation. A later
native graph and local reset branch allocation are required before P1 can be
assessed. The retained 59-net source coverage does not imply P1 acceptance.

`trial_receipt.json` records the exact board, source, floorplan and contract
SHA-256 values, four validated XU witnesses, the fixed-pad rejection, raw
cross-section, and whole-packet failure. Reproduce from the repository root
with KiCad 10 `pcbnew` and PyYAML. The pinned temporary board is the
regenerated QSPI-gap board described in `../QSPI_GAP.md`.

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/xu_service_variant/jtag_gap_trial/build_trial.py
python3 -m unittest skills/kicad-pcb/scripts/tests/test_p1_coarse_capacity.py
```

The builder fails if any pinned input, four-net endpoint, source corridor,
fixed-connector rejection, or whole-allocation rejection drifts. The focused
checker suite passed 45 tests. Neither result authorizes P1, P2, routing,
release, or an order.
