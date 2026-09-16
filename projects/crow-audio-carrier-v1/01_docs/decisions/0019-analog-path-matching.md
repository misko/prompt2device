---
id: 0019
date: 2026-09-08
status: accepted
---
# 0019 — Make post-buffer analog matching and copper resistance checkable

## Context

ADR0018 reserves the sixteen ADC input launches, but local clearance is not
complete paired routing. The existing analog class described matching and a
0.5 ohm path only in prose. The design has eight channels, each with P/N
output, filter and ADC net sections. Every section also has real feedback or
shunt branches; equal total copper inventory would not prove matched paths.

Cirrus's cached `CS530x_Schematic_Layout_Guidelines_202507.pdf`, section3.6,
page12, calls for matched signal pairs and signal-track DC resistance no more
than0.5 ohm from the buffer/filter to the ADC. It specifies no numerical length
tolerance. This is not a prohibition on the intentional10 ohm filter resistors
or the isolation switch's Ron. The15nF placement clause is CS5302P-only and is
not silently applied to this CS5308P design.

PDF SHA256: `a97e3cfbe311caf603bd56b7aeab189dd38727104168c26bb67dd24add07b62f`.
Public package: [Cirrus reference schematics and layout](https://statics.cirrus.com/pubs/software/DC5302P_4P_4S_8P_8S-ADC_Schematic_Layout.zip).

## Options

- Leave the prose: the current source would have no realized matching test.
- Match aggregate net inventory alone: branches or orphan copper can make
  totals equal while the actual source-to-load paths differ; reject.
- Force no analog vias or relax width/clearance: neither is necessary to
  express the requirement; preserve the existing F.Cu/B.Cu and0.50/0.20mm policy.
- Declare exact physical endpoint paths and a conditional resistance screen,
  retaining physical qualification separately: adopt.

## Decision

Add24 `length_match` groups to `rules/nets.yaml`: eight channels times the
three post-buffer sections. Each P/N member names every main, feedback,
differential-capacitor, common-mode-capacitor and pull-down endpoint applicable
to that section. This covers48 nets,176 native pads and128 declared paths.
The existing two digital report-only groups are unchanged.

Require a1.0mm P/N path-spread ceiling per section and per corresponding
branch. This is a project engineering target for local copper symmetry, not
a manufacturer numerical requirement, a derived phase bound or a claimed
noise/THD result. It deliberately prevents section mismatch being hidden by
opposite mismatch elsewhere. The three main-section allowances add; this is
not a1mm claim across the whole active/passive chain. Pad-entry propagation,
component delay and RC tolerances do not cancel merely because copper matches.
The legacy shared report's default6GHz phase columns are not applicable to
this audio design and must not be cited as performance evidence.

Declare deliberate meander capability, priced stack transitions and the
existing allowed vias. The analog KRT wave carries24 exact P/N net groups,
0.50mm router inventory tolerance and1.0mm meander amplitude. Those are
implementation settings, not proof: the independent saved-text endpoint gate
still applies the1mm path ceiling and rejects unexplained off-path copper.
Neither a matching flag nor a source pad-distance calculation certifies a route.

Add `check_analog_paths.py` as an explicit one-board backend-gap adapter.
Both full and reuse conductors check native endpoint membership before review,
then run saved endpoint matching/connectivity plus the resistance model before
final route acceptance. No shared gate or template is weakened or replaced.

The resistance design screen sums width-weighted straight/arc copper on all
three nets of each P/N leg, including branches, plus every ordinary via's full
nominal board-thickness barrel. It uses actual saved widths, source outer
foil thickness, the retained rho85 model, and18um hole plating as a MODEL.
The thin-wall via approximation charges slightly more than the exact annulus
at that same assumed plating. Apply a2x engineering reserve to that inventory
and require the result below0.5 ohm. This reserve is a chosen design margin,
not a manufacturer tolerance or qualified worst case.

JLCPCB publicly describes [1oz copper as35um](https://jlcpcb.com/help/article/jlcpcb-copper-weight)
and [hole plating as18um average](https://jlcpcb.com/capabilities/pcb-capabilities/)
(accessed2026-09-08). An average is not a local minimum. The source's nominal
foil, plating and board thickness cannot establish as-built resistance.
Pad spreading and solder are unpriced; intentional resistors and switch Ron
are excluded from this trace screen and retain their separate circuit roles.
Every output explicitly keeps `physical_dcr_status: UNVERIFIED`.

## Consequences

No footprint, component, part pose, seed segment/via, thermal field, keepout,
class floor, current allocation or stack geometry changes. Existing reviews
are stale against the new routing intent and conductor bytes; regenerate and
obtain fresh exact-subject reviews before routing. No PCB is produced here.

Hostiles reject absent matching, crossed native pins, missing/extra leaves,
missing router groups, excessive actual path skew, off-path copper, omitted
net measurements, underwidth/inner-layer tracks, malformed dimensions, long
inventory and unsupported via geometry. Arc length, foil thickness and via
barrels are priced by explicit fixture arithmetic, not merely counted.

Source-only PASS and conditional-model PASS are not placement acceptance,
full DRC/parity, physical DCR, thermal, acoustic or first-article approval.
Continue through fresh governed generation and review, actual routing, final
acceptance and release sealing. TOP77/0.20A HOLD, public-only sourcing,
DO-NOT-ORDER and both-child-seals/fresh P-PUBLISH before main remain intact.
