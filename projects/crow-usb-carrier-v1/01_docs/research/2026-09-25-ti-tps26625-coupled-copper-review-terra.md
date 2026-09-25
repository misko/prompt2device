# Independent review — coupled TPS26625 output/ILIM copper trial

**Disposition: reject SOL trial `2847467d940d60f730c3f756bd08d30a0073c4bd` on its process failure.** Native DRC cleanliness does not make the candidate manufacturable or admit either loop. This is research only, with no P1/P2, current, thermal, or source-rule claim.

## Verified facts

The trial pins source-generated witness board SHA-256 `28412ec5054d3b322ea03e37516aa969551beb1e2083b2fa0d2662863969dff4`, retains 569 footprints and the 27 fixed refs, and changes only the five `N12V_POD8` crossover primitives plus the proposed ILIM route. Its changed boxes remain in `analog_ch8`; the only native full-envelope intersections are `U_SPOKE8`, `C_SPOKE_OUT8`, and `R_SPOKE_ILIM8`. The packet records native named connectivity for U.1/C_IN.1, U.10/C_OUT.1, and U.7/R_ILIM.1, with the existing GND return on filled In1 outline 8 and a separate RTN component. ADC8N copper is outside its edit set.

The full generated KiCad DRC replay is unchanged at 199 violations and 499 reported opens, with +0/-0 identities. The required V-PROCESS result nevertheless rejects the output transition: the ordinary 0.60/0.30-mm `N12V_POD8` via at **(193.650, 46.100)** is in `C_SPOKE_OUT8.1`'s SMT land. Independent native inspection gives that land's bounding box as **x=193.150–194.150 mm, y=45.975–47.425 mm**. The V-VIP failure is therefore exact and governing; no unapproved fill/cap exception can be inferred.

The recorded 8.82-mm² output and 4.989687-mm² ILIM/RTN projections collapse layer transitions and internal component chords. They remain diagnostic only and correctly have null admitted area because the process check fails.

## Next bounded direction

Proceed to a **coupled six-part/return placement recut**, rather than another coordinate-level copper trial. The earlier output via at y=45.8 avoided C_OUT.1 land but conflicted with the ILIM escape; this y=46.1 shift resolves the copper DRC delta only by entering the capacitor land. Re-threading the narrow y<45.975-mm off-land band would not establish a new topology or assembly margin.

The recut must jointly create mouths for `U_SPOKE8`, `C_SPOKE_IN8`, `C_SPOKE_OUT8`, `R_SPOKE_ILIM8`, `C_SPOKE_DVDT8`, and `R_SPOKE_UVLO8`, while retaining the project IN/ILIM adjacency ceilings, GND6 versus RTN5/PowerPAD11 separation, an In1-backed GND bypass return, off-land ordinary vias, 27 fixed refs, and the ADC8N witness. A future candidate must pass both full-profile DRC and V-PROCESS before any projected loop geometry is considered.
