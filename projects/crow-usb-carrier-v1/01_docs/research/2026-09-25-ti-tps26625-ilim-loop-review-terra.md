# Independent review — rejected TPS26625 channel-8 ILIM route

**Disposition: reject SOL trial `b863f34d31764d2991ee0c9f696ca5549443c328`; do not turn its native connection into an ILIM-loop or placement acceptance claim.** The packet uses the immutable output-loop witness (SHA-256 `28412ec5054d3b322ea03e37516aa969551beb1e2083b2fa0d2662863969dff4`) and preserves its 569-footprint/27-fixed-ref ledger.

## Independent geometry and profile check

The attempted `SPOKE_ILIM8` leg is F.Cu `(191.4,48.0)->(191.95,47.95)`, B.Cu `(191.95,47.95)->(191.825,50.2)`, then F.Cu `(191.825,50.2)->(191.825,51.0)` to `R_SPOKE_ILIM8.1`: 0.20-mm track, two 0.60/0.30-mm through vias, 3.605738-mm centerline length. All its copper boxes remain inside the declared `analog_ch8` rectangle `[179,42,201,84]`; full-envelope intersection is limited to its two endpoint footprints.

I reconstructed the first via with KiCad's native effective F.Cu shapes. Its gap to `U_SPOKE8.8` is **0.138243 mm**, reproducing the receipt and falling **0.011757 mm** below the Default 0.150-mm clearance. Other local pad gaps reproduce as U.6 0.219848 mm, U.9 0.582458 mm, and PowerPAD.11 0.825011 mm. The near GND-return gap is only 0.150023 mm, so even the other side has no meaningful margin.

The route does make `U_SPOKE8.7` and `R_SPOKE_ILIM8.1` native-connected, and the candidate preserves distinct GND and `SPOKE_RTN8` connected components. That connectivity is rejected by the full profile: 199 to 200 violations, exactly one added Default-clearance identity at 0.1382 mm, no removed identities, 499 unconnected items before/after, and no V-PROCESS failure. The reported ILIM loop area must therefore remain null; a polygon around rejected copper would be false credit.

## Backtrack order

Backtrack **local route/return topology first**, without a clearance exception. The defect occurs at the first via next to U.8, before the route reaches the resistor; moving only `R_SPOKE_ILIM8` cannot repair it. A next test may only place the first transition outside both the U.8 and GND-return 0.150-mm envelopes, then prove the resulting ILIM-to-RTN return remains distinct from GND and has a complete native DRC pass.

If no such transition exists while retaining the already-tested U.6 GND return and PowerPAD/RTN copper, the next change is a **coupled** support/return placement recut: move the ILIM resistor together with the route mouth and its RTN return, preserving the existing project IN/ILIM adjacency, GND6-versus-RTN5/EP11 separation, input/output bypass evidence, fixed refs, and ADC8N witness. Do not move the resistor alone, narrow the clearance, or assign any loop-area/current/thermal credit before a valid topology exists.
