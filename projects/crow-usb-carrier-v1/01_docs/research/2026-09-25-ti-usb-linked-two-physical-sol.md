# TI USB two-physical-stage linked path — 2026-09-25 UTC

**Isolated source/checker experiment only. No canonical Crow source, board,
P1/P2 acceptance, connector FULL, or fabrication release changed.** The
adjacent packet preserves the exact unrouted TI board SHA-256
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`,
modular interfaces SHA-256
`02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8`,
and public connector alias dossier
`02_parts/USB4215-03-A/part.yaml` SHA-256
`a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e`.
Its candidate source, floorplan, contract and checker result SHA-256 values are,
respectively, `6fa9b9aee4a1651a1e2f75c4d629d077b29504f4033b6062f6fb25187c0d3fcf`,
`7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0`,
`8a04d8e2370e90e572a0cd196e47b33642a42f879bcbb974822f9377fbd1ce1d`,
and `12cc178f3fe480dea4fd3f9e2ddd6a197e5e799be411516a7df7ae76e619c778`.

The ordered `usb_edge_connector → usb_frontend → xmos_core` path contains
exactly one top-level reservation for `USB_DP` and `USB_DN`. The existing edge
stage `[229,28,231,29]` has two rough 0.97-mm slots for two demanded signals
and four native J_USB fixed-pad access segments. The second physical stage
`[215.5,40,218.5,84]` has three rough slots for the same two demanded signals,
with exact ESD-to-XU endpoints, P2 face obligations, and filled In1.Cu return
debt. The ESD pads are the single `pad_anchored_physical_interstage` join per
net; the earlier virtual slice retains `pad_anchored_virtual_interstage` and
no geometry or capacity claim. The checker reports no
global errors with `--diagnose-all`, both stage measurements remain
`INCOMPLETE`, and the linked path has `capacity_slots: null` rather than
summed capacity. Native routes, impedance, P2 access, and the filled return
are unproved.

Only `usb_vbus_sense` region east changed from x220 to x215 in the isolated
floorplan. The suggested `debug_connector` west recut to x222.5 fails existing
JTAG fixed-access segments (`jtag_access_6` reaches x221.925 and
`jtag_access_8` x221.625); it is therefore **not** in the passing packet.
The USB second strip is disjoint from the unchanged JTAG region. The full
`usb_device_pair` allocation remains `INCOMPLETE` on independent `J_USB.2`:
`witness bbox is a nonlocal bridge across source region`. Other allocations
remain incomplete. This result does not resolve the VBUS transition, P1, or
connector edge registration.

Replay from repository root with the packet files as source, interfaces,
floorplan and contract, `02_parts/USB4215-03-A/part.yaml` as aliases, and the
exact TI diagnostic board under
`06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project/04_kicad/`.
Invoke `skills/kicad-pcb/scripts/p1_corridor_capacity.py` with
`--diagnose-all` and the SHA-256 values bound in `coarse.json`; the recorded
`result.json` is the machine-readable receipt. The generic first slice now
rejects physical demand below net count, branched intermediate joins, and
cross-linked reuse of stage/access geometry or IDs. These are source admission
checks, not copper proof.
