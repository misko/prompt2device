# Independent review — rejected TPS26625 channel-8 control-leg trial

**Disposition: reject `248360b594c680c73691d4cb08e52a3b8e01fdcc` as a routing/placement candidate.** This is a replay and source-authority review only; it changes neither the board nor source rules and grants no P1/P2 or manufacturing credit.

## Replayed packet facts

`probe.py` replayed the archived full project profile and reproduced the rejection: the 199-violation/499-open reference becomes **200/499**, with one added and no removed issue identities. The new F.Cu `N12V_PROTECTED` track beginning at `(187.3,45.8)` is **0.0946 mm** from `R_SPOKE_UVLO8.2` at `(187.01,46.8)`, below its present `INPUT_TRUNK` **0.2000 mm** clearance. The six named route tests (`in`, `out`, `ilim`, both GND bypass returns, RTN/PowerPAD returns, `dvdt`, `uvlo`, and `uvlo_feed`) are connected; GND and RTN remain distinct. The packet preserves the 27 fixed references, all 569 pad identities, ADC8N copper, the six owner envelopes inside `analog_ch8 [179,42,201,84]`, and no envelope collision. Its V-PROCESS result contains no via-in-SMT failure.

The separate dVdT mouth is also too fragile to carry forward: the 0.60-mm via at `(192.5,47.05)` ends at `x=192.800`, only **0.055 mm** from `C_SPOKE_OUT8`'s native full-envelope left edge at `x=192.855`. It is not a DRC collision, but it is not a credible placement margin. The 2D reported dVdT/RTN and UVLO/input polygons are diagnostic projections, not loop-inductance, ampacity, transient, or thermal proof.

## UVLO branch authority

The exact current source is `R_SPOKE_UVLO8.1` on `N12V_PROTECTED` → the fitted **1 MΩ** `R_SPOKE_UVLO8` (`RC0402FR-071ML`) → `R_SPOKE_UVLO8.2` on `SPOKE_UVLO8` → `U_SPOKE8.2` (UVLO). The retained TI TPS2662/TPS26625 datasheet, SLVSDT4F revision F, says a UVLO function that is not used must connect IN to UVLO through at least 1 MΩ and that this limits UVLO-pin current to **less than 60 µA**; its leakage table gives up to 100 nA at 0–3.5 V and up to 38 µA at 5 V. The project uses that mandated 1 MΩ feed and ties OVP to RTN.

That supports treating the *post-fanout copper from the N12V tap to R_UVLO8.1* as a low-current sensing spur only after its topology is explicitly bounded. It does **not** relax the present rule: `03_src/rules/nets.yaml` classifies every `N12V_PROTECTED` segment as `INPUT_TRUNK` (1.2-mm minimum, 0.2-mm clearance, 2.85-A allocation), and no current source binds a particular native segment to a UVLO-only branch. Nor does the resistor fact prove startup, surge, fault, retry, hot-resistance, pulse, or resistor-temperature behavior through the actual net topology.

A future fail-closed carve-out would have to name only `R_SPOKE_UVLO8.1` and its unique copper path from a verified downstream fanout, preserve `INPUT_TRUNK` on every upstream shared neck/via/pad and `SPOKE_UVLO8` on the resistor-to-U.2 side, enforce ordinary different-net clearance, and prove the route has no alternate high-current branch. It also needs max-voltage/transient and resistor working-voltage/pulse/temperature evidence, plus native DRC/profile and production-copper review. No width or clearance exception follows here. Until that contract exists, moving the affected local geometry is safer than recoding the whole-net rule; a narrowly governed spur rule could later reduce the required move set, but is not yet safer than the existing rule.

## Required source-pose/topology backtrack

Do not tune another trace in this pocket. The mandatory moves are `R_SPOKE_UVLO8`, which owns the failing pad mouth, and the coupled `C_SPOKE_OUT8`/`C_SPOKE_DVDT8`, which own the 0.055-mm dVdT-via mouth. Re-screen those three as a placement unit while retaining the proven local constraints for `U_SPOKE8`, `C_SPOKE_IN8`, and `R_SPOKE_ILIM8`; move that latter trio only as a coupled group if the recut cannot preserve the existing IN/ILIM legs, GND6 bypass return, RTN5/PowerPAD11 island, and off-pad stitches. Reject first if any candidate loses the 27 fixed refs, 569 pad identities, ADC8N witness, owner/envelope containment, GND/RTN distinction, the existing 2.5-mm IN/ILIM engineering ceilings, full-profile DRC parity, or a materially robust full-envelope dVdT mouth.

A subsequent electrical candidate still needs realized native copper current/return topology, hot voltage-drop and temperature evidence over normal/startup/fault/retry cases, and RTN/PowerPAD thermal qualification. This packet provides none of those closure artifacts.
