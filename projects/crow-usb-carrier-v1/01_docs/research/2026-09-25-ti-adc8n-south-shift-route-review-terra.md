# Independent review — south-shifted ADC8N route

**Subject.** SOL packet `e74414c5`,
`2026-09-25-ti-adc8n-south-shift-route-sol`.  This is a reproducible local
geometry result, but is **rejected for physical/P2 promotion**.  It makes no
P1 or P2 acceptance claim.

## Independent checks

The packet pins the frozen TI floorplan, netlist, integrated-pose ledger, and
governed board generator at, respectively,
`0032b120…299868`, `a40b45c…35e9bd`, `76ba7ace…a647bb`, and
`8a5fa1d4…2215b3c`.  I independently recomputed each complete SHA-256 value;
each matches the receipt.  The generated-unfilled-board observation is
`a90fcc2c…6a4a6d8`.

Direct PCB inspection of the saved full-profile board found 569 footprints.
Its pad number/net/layer/shape/size identities equal both the southwest-cap
baseline and the frozen TI board.  The only pose/pad-center delta from the
southwest-cap baseline is `C_ADC_AC8N1`: `(198.00,60.05)` to
`(198.00,59.85)` mm.  All 27 `p1_fixed_refs` retain their complete
footprint/pad ledger, including against the frozen TI board.

The exact route is eight 0.20-mm F.Cu segments from
`C_ADC_AC8N1.2` (`ADC8N`, `(199.8,59.85)`) to `C_ADC_CM8N.1`
(`ADC8N`, `(187.52,66.5)`), length **15.777464 mm**.  The native link joins
those two pads only; it does not prove the other ADC8N terminals or the wider
branch.  Its measured different-net copper minimum is **0.190001 mm** to
`C_ADC_CM8N.2`.

The moved cap's native full envelope is
`[195.205,58.105,200.795,61.595]` mm.  Post-launch copper clears it by
**0.105001 mm** and clears the `usb_vbus_sense` source rectangle
`[195,62,220,82]` by **0.100001 mm**.  The shifted cap itself has no
full-envelope contact; its nearest stated support gaps are `C_A8P` 0.360 mm,
`R_B8P` 0.480 mm, and `C_FILTER8N1` 0.580 mm.

I independently replayed the archived full profile in a temporary directory
(archived `.pro`/`.dru`, generated POFV areas, via-process check, refill, and
native DRC).  It reproduces **199 violations / 499 unconnected** for both
baseline and candidate, with **+0/-0 violation identities** and zero
via-process failures.  The saved candidate has one filled `In1.Cu` GND zone
with nine filled outlines.  The packet's route-ribbon screen reports zero
uncovered area for every 0.20-mm segment; the two GND stitches connect to
`C_FILTER8N1.2` and `C_ADC_CM8N.2` in filled outline 8.

## Promotion disposition

The route's closest non-endpoint full footprint is `U_SPOKE8`, only
**0.048494 mm** from the 0.20-mm copper.  The limiting diagonal is the segment
from `(194.8,62.8)` to `(191.7,65.9)` beside the native U_SPOKE8 physical
envelope.  It does not collide and native DRC therefore remains unchanged,
but a 48.5-µm physical-envelope margin beside an unrelated power part is not
a credible routed-cell clearance.  It is substantially narrower than the
already small 0.100/0.105-mm cap/USB margins and provides no robust assembly,
analog-noise, or source-owner boundary evidence.

Accordingly, retain this only as a bounded geometry/filled-return witness.
Do not promote the one-cap move or route until a reroute/placement gives a
meaningful U_SPOKE8 physical-envelope margin and the separate ADC8 owner-cell,
J8 mechanical-cell, remaining-net, and return/ESD obligations are discharged.
