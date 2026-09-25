# TI VBUS_USB edge-owner handoff trial

**Disposition: INCOMPLETE and schema/geometry blocked. No P1 or power-path
acceptance.** `build_trial.py` makes a source-level variant of the retained TI
DP/DN linked-path packet and checks it against the exact unrouted TI board,
SHA-256 `8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
It writes only this research directory. The canonical source, board, stock,
route and checker are untouched.

The copied interface keeps every `VBUS_USB` endpoint: four source connector
contacts `J_USB.10/.15/.2/.7` under `usb_edge_connector`; three frontend
terminals `C_USB_VBUS.1`, `R_USB_VBUS_BLEED.1`, and `U_USB_VBUS_ESD.3`; and
`R_VBUS_B.1` under `usb_vbus_sense`. The authoritative alias dossier maps
`J_USB.2 → A4` and `J_USB.10 → B4`; an intentional `J_USB.2 → B4` probe fails
with `witness source/native alias mismatch`. The board's A4/B9 pads coincide
at `[232.1,26.1,232.7,27.25]` mm, and B4/A9 coincide at
`[227.3,26.1,227.9,27.25]` mm. Four logical connector endpoints therefore
provide two physical VBUS launch sites.

The variant splits the original mixed `usb_local_power` demand into an
incomplete `VBUS_USB` demand and an incomplete `VBUS_PRESENT_N` demand so the
existing exact-demand corridor schema can address VBUS alone. It proposes an
edge/frontend corridor `[227,28,233,29]` mm, exact physical-stage endpoint and
P2 pad-to-face declarations, a separate unresolved frontend-to-sense stage
with every endpoint and a filled In1.Cu return obligation. The proposed
connector access boxes originate at the exact native pad edges. These are
declarations, not proof of current capacity, copper continuity, or return.

The checker gives four useful negative results, preserved in `result.json`:

1. Keeping the old `vbus_entry` and `vbus_sense_entry` top-level reservations
   yields `linked path net has competing ordinary credit/witness`. A linked
   VBUS path cannot quietly add capacity on top of them.
2. Removing those ordinary VBUS claims exposes a native obstruction. The
   proposed six-millimetre-wide corridor/front face intersects
   `U_USB_CC_ESD` (body bbox `[232.075,29.01,234.525,31.195]` mm), so the
   physical stage is rejected before access accounting. Narrowing that face
   short of x=232.075 would omit the A4/B9 launch at x=232.1–232.7.
3. Adding this path alongside the existing DP/DN linked path in the same
   `usb_device_pair` allocation yields `linked path contract declaration
   mismatch`. The current first-slice schema expects exactly one linked path
   per allocation.
4. The two exact alias pairs generate identical per-endpoint access boxes.
   The current fixed-access schema requires one disjoint access per logical
   endpoint; a true VBUS handoff needs a source-declared fused-pad group or
   shared same-net launch authority. Skipping endpoints would break the exact
   denominator. This collision is measured even though the earlier native
   CC-ESD hit prevents a successful full linked-path check.

The first-slice checker also models physical linked capacity as signal slots.
That is not a current, thermal, fault or copper-width proof for `VBUS_USB`.
A later design must resolve the physical CC-ESD/edge access, support multiple
linked paths in the allocation and fused pad launches without double credit,
and retain power-specific P2 obligations. Nothing here qualifies a route,
filled return, connector FULL, placement, P1, or an order.

Reproduce from the repository root with KiCad 10 `pcbnew` and PyYAML:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-vbus-edge-handoff-trial-sol/build_trial.py
```
