# ADC8 positive-mouth repair bound

**Research-only rejection.** The exact subject is the isolated 15-footprint
board SHA-256 `d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`.
Run `python3 probe.py` in this directory to regenerate `receipt.json`. The
probe reads native full envelopes, the governed owner rectangles, and all
modular member lists. It changes no board or canonical source. The 27 fixed
poses and pad identities remain those of the hash-bound board.

The 0.56 mm owner/USB margin and 1.5× related-pad-distance limit are
**illustrative screens, not design rules**. A complete 0.1 mm grid of cap
origins within the current `analog_ch8` rectangle gives:

| Screen | Count |
| --- | ---: |
| At least 0.56 mm from analog right edge and USB cell | 47,664 |
| Also at least 0.15 mm from other native envelopes | 12,905 |
| Also no worse than 1.5× on both related-pad distances | 29 |
| Also at least 0.56 mm from other envelopes | **0** |
| Within 6 mm of current cap, after the 1.5× screen | **0** |

The nearest of the 29 is `(189.5,49.2)`, a **14.064 mm** cap move. Its nearest
envelope is `R_X8P`, only 0.240 mm away; the ISO6 and CM8N1 pad distances
become 12.302 and 17.708 mm. It does not establish pad entry or return.

A compact positive-boundary trial at cap origin `(197.6,59.6)` gives 0.605 mm
to the analog right edge and 0.655 mm to the USB rectangle. It physically
overlaps `C_A8P`; `R_B8P` and `C_FILTER8N1` are only 0.080 and 0.330 mm away.
For a 0.56 mm cap-to-`C_A8P` mouth at this x, `C_A8P` would need to move at
least 0.60 mm west to x≤187.85. Its full body would then overlap
`C_ADC_AC8P2` by 0.240 mm and `C_FILTER8N2` by 0.040 mm. Moving `R_B8P`
west enough for 0.56 mm to the cap would leave only 0.100 mm to `U_SPOKE8`
at the same y; a south or other coupled relocation is required. This is a
bounded neighbor-chain witness, not a proof that arbitrary larger moves fail.

Terra's native map in `0e5ef9fa` identifies room for a right-side analog/USB
divider. We screened x=202.105 mm, giving 0.56 mm from the rightmost
channel-8 body `U_AFE8`, 1.110 mm from the cap to the new divider, and 3.720
mm from the divider to the nearest USB-owned body `R_VBUS_B`. This repairs
the local cap/USB geometric pinch, but a **two-cell-only source recut fails**
the complete modular population:

- `C_ISO8`, `C_SPOKE_DVDT8`, `C_SPOKE_OUT8`, and `R_SPOKE_UVLO8` still intersect
  the unchanged `audio_clock_tdm` rectangle; `U_ESD8` intersects it too.
- `R_IN8P` and `U_ESD8` extend into `analog_ch7` and are not fully in
  `analog_ch8`.
- Fixed connector `J8` is a channel-8 modular member, but its full envelope
  `[198.875,19.955,216.268,34.495]` is outside the analog rectangle and
  intersects `usb_frontend`.

Thus neither the compact placement nor the two-cell recut is a valid typed
physical-cell candidate. A further experiment must move or explicitly
reassign that full member set and resolve the neighboring source cells, then
show cap/ISO pad entry, a route, and a continuous return. The GND zone remains
unfilled and P1/P2 remain unaccepted. No corridor capacity is credited.
