# Independent review — TPS26625 channel-8 whole-group trial

**Subject:** SOL packet `c35c79df`, `2026-09-25-ti-tps26625-whole-group-sol`.
This candidate is **research-only and rejected**. It must not be promoted to
canonical source, P1, or P2.

## Verified result

The packet binds the frozen TI floorplan, netlist, integrated-pose ledger, and
board generator to the same source hashes as the preceding ADC8 packets. The
source-generated board has 569 footprints. Compared with the immediately
preceding coupled board, exactly these six references change pose; all pad
number/net/layer/shape/size identities are preserved and every one of the 27
fixed references is identical to both that baseline and the frozen TI board:

`U_SPOKE8`, `C_SPOKE_IN8`, `C_SPOKE_OUT8`, `R_SPOKE_ILIM8`,
`C_SPOKE_DVDT8`, and `R_SPOKE_UVLO8`.

The six candidate centers are `(190.00,47.50)`, `(189.75,44.00)`,
`(194.20,46.70)`, `(194.00,49.50)`, `(185.80,48.90)`, and
`(185.80,46.80)` mm in that order. Each is still owned by `analog_ch8`, lies
inside its source rectangle, and has zero native full-envelope collisions or
foreign-source-rectangle intersections.

I independently recomputed the direct native F.Cu pad-shape gaps. The receipt
values reproduce exactly:

| Direct loop contact | Gap (mm) |
| --- | ---: |
| U.1→C(IN).1 / U.6→C(IN).2 | 1.655273 / **3.661193** |
| U.10→C(OUT).1 / U.6→C(OUT).2 | 1.050108 / **3.186949** |
| U.7→R(ILIM).1 / U.5→R(ILIM).2 | 1.512450 / **5.563658** |
| U.8→C(dVdT).1 / U.5→C(dVdT).2 | **5.619506** / 1.747740 |
| U.2→R(UVLO).2 / U.1→R(UVLO).1 | 1.720274 / **2.741088** |

The separate PowerPAD.11-to-return gaps are 3.636474 mm for R(ILIM) and
2.615660 mm for C(dVdT). U.6 and both bypass returns are `GND`; U.3, U.5,
and PowerPAD.11 are `SPOKE_RTN8`. The packet correctly keeps those nets
distinct, but it supplies no local RTN copper island or completed GND/RTN
loop routes.

The retained ADC8N link still joins only `C_ADC_AC8N1.2` to
`C_ADC_CM8N.1`. Its filled In1 GND ribbon has zero uncovered area, clears the
foreign `usb_vbus_sense` rectangle by 0.200001 mm, and clears the closest
other footprint envelope (`C_A8N`) by 0.205001 mm. I replayed the archived
project/rules, POFV generation, via-process check, refill, and native DRC in
a temporary directory: baseline and trial both give **199 violations / 499
opens**, with **+0/-0** violation identities and no via-process failures.
The candidate contains one filled In1 GND zone with nine outlines.

## Correct interpretation and next evidence

The decisive miss is U.6 GND→C(IN).2 at 3.661193 mm; R(ILIM)'s RTN contact
and the dVdT contact also miss. This fails the **proposed project 2.5-mm
all-loop research target** from `a2ddd7b6`. It is not a violation of a TI
numeric placement distance: TI SLVSDT4F provides qualitative close/short-loop
guidance, while the existing canonical 2.5-mm engineering ceilings cover only
the IN bypass and ILIM connection.

Retain those existing IN/ILIM ceilings. Do not present the proposed all-loop
extension as TI authority. The next evidence should replace an un-routed
pad-gap proxy with one native routed board that proves all five loops:

1. IN: U.1→C(IN).1 and C(IN).2→U.6; OUT: U.10→C(OUT).1 and
   C(OUT).2→U.6.
2. Control/return: U.7→R(ILIM).1→R(ILIM).2→U.5/PowerPAD RTN;
   U.8→C(dVdT).1→C(dVdT).2→U.5/PowerPAD RTN; and
   U.1→R(UVLO).1→R(UVLO).2→U.2.
3. A measured polygonal copper loop area and path length for each loop,
   explicit local RTN-island/PowerPAD connectivity, and native proof that the
   island remains distinct from U.6 system GND.

That board must additionally pass full-profile DRC, native envelope/region
screens, and the project-owned IN/ILIM ceilings. Numeric area or additional
loop-length acceptance thresholds require an explicit project decision or
analysis; TI's qualitative wording does not supply them. This review does not
infer physical impossibility from the one rejected pose.
