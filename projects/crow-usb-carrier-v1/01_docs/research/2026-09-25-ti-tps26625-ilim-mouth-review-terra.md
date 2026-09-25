# Independent review — TPS26625 channel-8 ILIM mouth screen

**Disposition: reject the tested immediate and remote routes, while retaining no global ILIM-routing UNSAT claim.** This review independently reran SOL commit `ba0ab67a944172ba9645615f6adaeb63044bbe84`'s finite screen and complete-profile remote-route replay against pinned output-witness board SHA-256 `28412ec5054d3b322ea03e37516aa969551beb1e2083b2fa0d2662863969dff4`.

## Exact bounded findings

For a 0.60/0.30-mm first via in the east U.7 pocket `[191.7,47.5,191.95,47.95]`, the best constrained corner is `(191.95,47.95)`: the native effective F.Cu gap is **0.138243 mm** to U.8, below Default's 0.150-mm clearance. The same corner is only **0.150023 mm** from the existing GND return. U.6 (0.219848 mm) and PowerPAD.11 (0.825011 mm) are not limiting. This proves the stated immediate-pocket constraint for this via family and these current returns; it does not prove that every launch topology is impossible.

The wider 0.025-mm screen reproduced 53,721 sites, including 384 sites that are both via-clear and eight-neighbor reachable under its stated F.Cu centerline overapproximation. Those are necessary-condition sites only: they do not certify continuous track clearance, other-layer clearance, via interaction, or manufacturing margin. Their existence rules out treating the screen as a global UNSAT proof.

I also replayed the one 9.351547-mm remote route. It preserves the 569-footprint/27-fixed-ref ledger, reaches `R_SPOKE_ILIM8.1`, preserves the input/output witnesses and filled In1 GND polygon, and keeps GND separate from RTN. It remains rejected by full-profile native DRC: 199 to 201 violations, zero removed, 499 opens both sides, no V-PROCESS failure. The two new identities are both governed by `POD_POWER`'s 0.200-mm clearance:

1. The new ILIM via at `(191.95,45.15)` to the existing 2.250-mm B.Cu `N12V_POD8` trace at `(191.4,45.8)`: **0.1000 mm**.
2. The 5.0515-mm In2 `SPOKE_ILIM8` trace to the existing `N12V_POD8` through via at `(191.4,45.8)`: **0.1337 mm**.

The route cannot earn ILIM loop-area, current, or return credit.

## Next recut

Backtrack the **output/GND/ILIM route topology as one local set**, before moving the support placement. The immediate mouth is closed by U.8 plus the existing GND returns, while the remote escape is cut by the output leg's B.Cu trace and via. The next bounded candidate must relocate or reroute that output crossover and its GND-return mouth together with an ILIM transition, then prove all three native clearances, a complete DRC delta of zero, retained GND6-versus-RTN5/EP11 separation, and the existing input/output bypass links.

Only if that coupled copper recut has no rule-clean mouth should a coupled placement recut move the ILIM support/return group. Moving `R_SPOKE_ILIM8` alone, using a special smaller via, or reducing either clearance has no support from this evidence. No P1/P2 or thermal/current claim follows.
