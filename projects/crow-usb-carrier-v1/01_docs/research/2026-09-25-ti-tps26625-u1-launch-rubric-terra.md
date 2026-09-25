# TPS26625 U.1 high-current launch boundary

**Scope:** source-backed research criterion for the `U_SPOKE8.1`
`N12V_PROTECTED` launch. This note does not authorize a neck, change a source
rule, or provide P1/P2 credit.

## What the primary and source actually say

The retained TI TPS2662-family dossier `SLVSDT4F` (TPS26625DRCR), package
DRC0010J, gives a 0.60 × 0.24 mm peripheral land-pattern example for each of
the ten terminals. It requires the thermal pad to be soldered for optimum
thermal/mechanical performance, asks that the PowerPAD connect directly to
the RTN plane for heat sinking, and says high-current paths must be short and
sized for at least twice full-load current. Its layout text asks to minimize
the IN/GND bypass loop. It provides **no** launch-width, pad-overlap,
neck-length, ampacity, voltage-drop, or temperature-rise number.

The current project source is narrower in authority:

* `03_src/rules/nets.yaml` assigns `N12V_PROTECTED` to `INPUT_TRUNK` with
  `min_width: 1.2mm`, `clearance: 0.2mm`, and `current: 2.85A`.
* The exact TPS26625 dossier binds U.1 to `C_SPOKE_IN8.1` with a project-owned
  2.5-mm copper-gap ceiling. It describes that ceiling as engineering support
  for TI's qualitative close-bypass guidance.
* The part dossier's 44.2-kΩ condition gives a 0.145–0.159 A eFuse overload
  range under its stated 24-V/1-V-drop condition. That does not supersede the
  source `INPUT_TRUNK` allocation; a candidate must state which current
  governs each segment and reconcile the two.

Consequently, the recent 1.20-mm trial's 0.12-mm edge contact is native-DRC
connectivity only. It is neither a TI-approved high-current launch nor an
exception to the source trunk rule.

## One testable next criterion

Do not create a local width exception by implication. A future source-generated
candidate can be screened against this **proposed project engineering
criterion**:

1. Every external `N12V_PROTECTED` copper primitive from
   `C_SPOKE_IN8.1` to U.1 retains the 1.20-mm `INPUT_TRUNK` width and
   0.20-mm clearance.
2. The final primitive's effective F.Cu shape contains the **center point**
   of the U.1 native land, not merely a tangential or edge-only collision.
   Record the land bounding box, shape intersection, and the terminal's
   unavoidable 0.60 × 0.24 mm package land geometry.
3. Recheck named-pad connectivity, full-profile native DRC/V-PROCESS, and
   the direct U.1-to-C(IN).1 project 2.5-mm ceiling. Recheck the paired GND
   return; a supply-only launch is not a bypass-loop result.

The center-containment test is deliberately a reviewable geometric criterion,
not a manufacturer numeric limit. Any different local neck needs an explicit
source decision and an equally explicit geometric/contact criterion before it
can be assessed.

## Required current and thermal evidence

Before treating even a center-contained launch as physically adequate, bind
the actual stackup copper weight/thickness and route length, assign the
governing current to each copper segment, and provide a DC resistance,
voltage-drop, and temperature-rise result for the trace, the U.1 terminal,
and every via/plane transition. The analysis must cover normal load and the
TPS26625 overload/retry condition relevant to the source allocation.

It must be accompanied by an explicit local RTN/PowerPAD copper and thermal
model: U.5 and PowerPAD.11 on an RTN island, no RTN-to-system-GND bridge, and
the thermal-via/plane geometry used in the calculation. TI's package and
layout guidance establish why this evidence is needed; they do not furnish
its numerical pass/fail thresholds. Full bypass-loop, ADC8N, owner-cell, and
J8 evidence remains separately required before P2.
