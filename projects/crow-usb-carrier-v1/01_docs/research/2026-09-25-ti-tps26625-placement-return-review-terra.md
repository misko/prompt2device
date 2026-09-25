# Independent review — TPS26625 channel-8 placement/return recut

**Disposition: accept as a reproducible local geometry and native-profile witness only. No P1/P2, current, thermal, or source-promotion claim follows.** I replayed SOL commit `96de6901938e0589e429fd56689be6d4ca64bc1` under its archived complete profile and restored its generated receipts.

## Verified witness

The source-generated candidate moves only `C_SPOKE_DVDT8`, from `(193.9,49.3,180)` to `(193.9,49.5,180)`. It preserves 569 footprint identities, all 27 fixed refs, ADC8N copper, and the other five TPS26625 group poses. The six native full envelopes have no collision and remain in `analog_ch8 [179,42,201,84]`; the moved capacitor's nearest group-envelope gap is 0.474131 mm to `R_SPOKE_ILIM8`.

The established project direct-pad ceilings remain satisfied: IN→C(IN) is 1.655273 mm and ILIM→R(ILIM) is 2.405089 mm, both below 2.5 mm. They remain project ceilings, not TI numeric placement limits. The move increases U.8→C(dVdT).1 from 2.838134 to 2.946166 mm and U.5→C(dVdT).2 from 4.277343 to 4.306640 mm, so it does not close TI's qualitative close-placement debt.

Native connectivity passes for input, output, ILIM, both bypass GND pads, ILIM/dVdT/U.3/U.5 RTN pads, and retains separate GND versus `SPOKE_RTN8` components. Ordinary off-pad GND stitches at `(192.0,43.8)` and `(192.7,48.5)` connect through one filled In1 GND outline (8). The process check reports no V-VIP/V-PROCESS failure. Full profile replay is unchanged at 199 violations and 499 reported opens, with +0/−0 issue identities.

The first ILIM via at `(192.1,47.9)` measures 0.212035 mm to U.8, 0.200011 mm to the GND return, and 1.050048 mm to the output trace. The 0.200011-mm GND result is only 0.000011 mm above a nominal 0.200-mm screen: treat it as an exact native pass with no fabrication, registration, copper-etch, or assembly-margin credit.

## Remaining debt

The reported 14.840625/8.37/5.073437-mm² projections are not loop inductance or return-current measurements; the input projection explicitly substitutes a straight chord for the In1 route. Current/thermal qualification still needs realized copper/return impedance, hot IR and temperature, via/pad/fillet current capacity, PowerPAD-to-RTN thermal island, and fault/retry waveform evidence. The dVdT and UVLO signal legs, incomplete pod distribution among the 499 opens, source-cell accounting, and ADC8/J8 physical-cell issues remain open. The narrow ILIM/GND clearance should be re-screened with any future placement, route, stack, or process change.
