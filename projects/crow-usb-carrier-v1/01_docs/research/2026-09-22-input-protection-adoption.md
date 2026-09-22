# Input protection adoption

Replaced the marginal hot input PPTC with a Littelfuse 0451004.MRL 4 A
very-fast fuse. Spoke eFuses still provide resettable branch protection; this
upstream fuse requires replacement if it opens. Its 2.85 A hot continuous
engineering screen includes the manufacturer's continuous-current derating
and a conservative graphical temperature factor. It is not a guaranteed
production minimum. The exact mirrored manufacturer PDF, ordering row and
source/native land geometry are retained in the new dossier.

Also replaced C_IN_HF, formerly a 16 V capacitor on the TVS-clamped input,
with the already selected 50 V CC0805KRX7R9BB104. The component-voltage screen
now includes the directly exposed capacitor groups. Disabled spoke OVP can
pass an input pulse downstream; pod survival above 13.2 V is not qualified.

The source contract permits either bounded fuse clearing or bounded external
current-limit/hiccup behavior. A regulated supply need not produce enough
fault current to open the fuse if it limits safely. Source capacitance,
transient energy, actual copper withstand and fault recovery still require
qualification. The TVS table establishes a component pulse screen, not an
IEC, automotive, lightning or complete-product immunity rating.

Root checked the actual voltage-budget implementation and corrected the
candidate's units: `upstream_delivery.margin` is a dimensionless adverse-drop
factor, not fuse-current headroom. A 150 mΩ trunk allocation at 2.185 A with
20% additional drop margin gives an 11.006 V rounded-down protected floor.
Each spoke receives a 1710 mΩ total delivery allocation, including its switch,
PCB path and connector contacts. Native extraction must satisfy these budgets.
The input net class carries the 2.85 A continuous source-limited fault screen.

Root verification after integration:

- Full source: 460 components, 86 selected MPNs, zero source diagnostics,
  1539 ports, 1416 traces and 26 existing endpoint checks passing.
- E-MARGIN: nine graded paths pass, including the shared upstream path.
- Early design: four gate families pass; E-CAP still covers all eight banks.
- Modular coverage: 460/460 components and 53/53 crossings pass.
- Exact new fuse footprint loads in KiCad with two 1.96 × 3.15 mm lands on
  4.91 mm centers; root checked the retained manufacturer's 4 A rating row.

Full E-FAULT, source supply behavior, realized thermal/copper limits, native
schematic and placed/routed board remain open. The numerical current-limit
screen retains its datasheet test conditions; it is not a guaranteed 12 V
hard-short bound.
