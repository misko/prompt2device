# Successor module fabrication and assembly controls

Design-owned requirements, effective for the next release candidate only.
Author: Astra, 2026-10-09 Pacific. Read with the retained ASSEMBLY-PLAN.md;
that historical source remains unchanged. This addendum is a required input to
successor mating, fabrication, assembly and release review. A release that omits
it is incomplete. No inspection, supplier capability or physical test is claimed.

## Accepted variant and finished-board limits

Original non-wireless Raspberry Pi SC0915 Rev3, D1 only depopulated by the
qualified assembler under the original electrical/identity controls. Hand-solder
all 40 castellations; no headers, underside paste stencil, or shell-ground lands.
No substitution of Pico H/W/2 or unmodified module.

At U3's exact native A/B centers (162.275,3.550), (167.725,3.550) mm,
finished non-plated holes must be 2.50–2.65 mm diameter. At C/D centers
(162.575,6.580), (167.425,6.580), finished diameter must be 2.15–2.30 mm.
Retain nominal design diameters 2.60/2.25 and 0.40-mm local copper clearance.
Actual minimum first/second-row web is 0.45 mm and actual hole-to-copper
clearance on every layer is at least 0.25 mm. These combined limits override
individual diameter/position allowances; satisfying one does not waive another.
Fabricator/process acceptance of these limits is an order hold, not established
capability. Retain inspection evidence by board lot; reject nonconforming boards.

## Incoming module and registration limits

Use the maker Figure 5 four-center/module datum. The complete A/B shell-solder
XY projections must fit 1.10 × 1.80-mm capsules, R0.55, expanded outward by no
more than 0.15 mm. C/D must fit the design-selected 1.05 × 1.45-mm capsules,
R0.525, expanded by no more than 0.15 mm. Include pad location variation in this
projection limit; do not recenter each pool. The drawing's duplicated B,C legend
does not authorize a larger C/D envelope. These are incoming reject limits,
not invented maker tolerances. Retain measured images with module identity.

Combined actual module-to-finished-hole radial registration error must be at
most 0.10 mm at each of A–D. This is one combined allowance, not separate
0.10-mm drill and placement allowances. Use a positioning fixture and optical
check before tacking; reject/reposition failures. The minimum-hole radial free
space under these bounds is 0.10 mm, demonstrated by the retained LS30 real-solid
tolerance screen. Preserve polarity and all original electrical checks.

## Absolute seating and backside controls

No shell solder, D1 remnant, debris or other unmodeled underside feature may bear
on the carrier or short nearby features. Seat without force or rocking. At four
perimeter contact windows, after tacking and releasing the positioning fixture,
module underside contact plane to corresponding finished carrier pad-top gap
must be 0–0.15 mm at each window, with spread at most 0.15 mm. Measuring spread
alone is insufficient. Check actual copper/mask/finish and warp through these
finished-contact datums rather than treating the nominal dielectric as pad top.
No shell pool may extend below the finished carrier underside after seating.
Verify solder wetting/continuity separately; continuity does not prove seating.

These process limits must be executable and confirmed before assembly. Record
actual observations per carrier serial. Nonconformance means quarantine/rework
or redesign, never a waiver under later qualification. No enclosure, weather,
USB accessory, or physical reliability verdict follows from this addendum.

## Evidence

- 02_parts/P031/manufacturer.pdf, Figures 3 and 5.
- 06_build/recovery/ls30-relief-3d/tolerance.json and relief-worstcase.step.
- 08_reviews/ls33-module-engineering.md, independent interpretation and limits.
- 06_build/checkpoints/ls31/placement_reviewed.json, current placement identity.

Prototype design acceptance and actual article qualification remain distinct.
The integrated mating receipt remains absent until all applicable interfaces
and limitations, including USB and cable service, receive independent judgments.
