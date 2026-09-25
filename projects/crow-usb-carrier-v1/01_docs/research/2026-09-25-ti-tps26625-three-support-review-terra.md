# Independent review — TPS26625 channel-8 three-support witness

**Disposition: useful local geometry witness; research-only and not promotable to P1/P2.** I replayed SOL packet `9176807897e5b9f6b27b8e5fa2d9375df184de68` with its archived full project profile. It retains the source-generated 569-footprint/pad ledger, all 27 fixed references, ADC8N copper, and the unchanged `U_SPOKE8`, `C_SPOKE_IN8`, and `R_SPOKE_ILIM8` poses.

## Verified geometry and native replay

The only support-pose changes relative to the reviewed headroom pose are `R_SPOKE_UVLO8` `(186.5,46.8)→(186.5,47.1)`, `C_SPOKE_OUT8` `(194.6,46.7)→(194.9,46.7)`, and `C_SPOKE_DVDT8` `(193.9,49.5)→(194.1,49.4)` mm. All six full native envelopes are inside `analog_ch8 [179,42,201,84]`, have no foreign-region intersection or pair collision, and the added copper remains in that owner. The retained project direct-pad ceilings pass: IN→C_IN **1.655273 mm** and ILIM→R_ILIM **2.405089 mm**, each below 2.5 mm.

The two rejected mouths are materially improved. The 0.60-mm first dVdT via at `(192.5,47.05)` has a **0.355-mm** axis gap to the full `C_SPOKE_OUT8` envelope, and the 1.20-mm source-side UVLO feed has **0.690734-mm** native effective F.Cu copper clearance to `R_SPOKE_UVLO8.2`; both exceed the packet's 0.20-mm screen. The first ILIM via retains 0.260253 mm to GND and 0.249267 mm to U.8.

The replay preserves native named links for input, output, ILIM, dVdT, UVLO and UVLO feed; both bypasses return to GND6; ILIM, dVdT, OVP3, and RTN5 connect to PowerPAD11. GND and RTN remain separate, both GND stitches meet the same filled In1 GND outline, and V-PROCESS reports no failure. Full-profile DRC is **199 violations / 499 opens before and after**, with **+0/−0** issue identities. These facts demonstrate local copper connectivity, not qualified loop behavior.

## Tradeoffs and remaining closure debt

The clearance is bought by worsening TI's qualitative close-placement relationships: U.10→C_OUT.1 becomes **1.750487 mm** (from 1.450194), U.6→C_OUT.2 **3.847960 mm** (from 3.563231), U.8→C_DVDT.1 **3.060607 mm** (from 2.946166), and RTN5→C_DVDT.2 **4.488829 mm** (from 4.306640). The output projected polygon grows to 9.03 mm²; all reported projections flatten layer transitions and component/return paths, so they establish neither loop inductance nor transient performance.

Critically, the full-width UVLO stub remains *before* the 1-MΩ resistor and crosses two 0.60/0.30-mm vias. A downstream UVLO sensing-current argument therefore cannot qualify that pre-resistor trace, vias, or resistor-pad launch against source fault current, hot voltage drop, pulse `I²t`, or temperature. Filled In1 contact does not establish bypass return-current distribution, and the separate RTN/PowerPAD copper is not a thermal island qualification. Preserve this pose only as the geometry starting point for those proofs; it leaves the 499 native opens and ADC8/J8 ownership debts unresolved.
