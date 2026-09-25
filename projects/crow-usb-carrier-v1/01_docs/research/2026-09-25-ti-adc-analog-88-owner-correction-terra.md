# TI ADC 88-pad owner-correction review

**Research only.** Review basis is the four-part candidate bound by
`cd42936a` to board SHA-256
`046019a13094764baef313d62611b137e0f0af971079734c71ab050dbf46b3a0`.
No canonical source, board, fixed pose, stock, P1, or P2 state changes.

The 18-net/88-pad ledger correctly makes the 16 ADC N/P trees geometry-free
and carries explicit P2/P3/return debt. The two remaining VMID failures are
not an endpoint-accounting gap: `R_B1P.2` through `R_B8P.2` each lie east of
their own channel boundary, respectively entering the next analog channel
(B1–B7) or `usb_vbus_sense` (B8). A region-only repair is not honest: widening
each channel eastward overlaps its neighboring owner and merely transfers the
same exclusive-ownership conflict.

The smallest physically honest correction is therefore an isolated eight-part
placement screen: move each complete `R_BnP` footprint west into its existing
`analog_chn` owner, preserving its native pad/net identities and checking its
full physical envelope, neighboring analog parts, and local VMID return. The
ledger’s 0.24–0.78-mm pad overruns give the strict lower bound on each required
westward pad correction; no exact footprint origins are proposed here because
that would need a collision and pad-access search. Reassigning a resistor to a
neighboring channel is rejected because its endpoint owner would cease to
match the channel’s source interface.

`C_ADC_AC8N1.2` likewise enters `usb_vbus_sense`; it needs a separate
full-footprint relocation back inside `analog_ch8` or a proved typed local
cell. Extending `analog_ch8` into the USB region is rejected as a broad region
claim and would not repair the VMID resistor ownership.

No valid combined candidate exists from the ledger alone. A next isolated
placement must prove all eight resistor and the ADC8 capacitor envelopes/pads
inside their original owners, no new collisions, exact 88-pad denominator,
and explicit P2 access/return debt. It still would not prove VMID/ADC routes,
capacity, filled return, channel-8 ownership, or P1 acceptance.
