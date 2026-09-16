# ADC supply-feed source milestone — 2026-09-08

Disposition: adopt ADR0015 as source progress only. No generated board,
route, review/checkpoint or release acceptance. ROOT is author and operator,
not an independent reviewer. The user's dirty primary workspace is untouched.

Base549a4e793ba7f42cd971e25d96cdbbdd36f708ea was clean. The11:02:36Z
before inventory binds1,204 tracked carrier subjects/102,471,546 bytes;
ignored files are not claimed censused. Work stays on the dedicated board
development branch, with no main push, tag or manufacturing release.

## Change and observations

Two previously unresolved power groups now have real continuous F.Cu feeds
to full1.20mm local entries. The finite source scan improves69/71 to71/71
over exactly96 power pads; no denominator or pin is dropped. Entry witnesses
are1mm straight1.20/.25mm capsules, not a global route proof.

Only seven existing banks change: ADC2/3/5/8/9/10/11. The other65,
including all15 peripheral power banks, stay exact. No parts move. Two
obsolete cap nubs are retired, four CFG drops and one GND_A drop relocate;
the actual nearest-GND_A VMID return contact tree is preserved. Totals are
72 banks/201 primitives/20 vias. No power via or layer transfer is added.

Two explicit0.23mm local clearance scopes accommodate measured0.235mm
gaps between0.18mm traces and actual0.900mm-wide0603 pads. Global0.127mm
fabrication and all class floors remain exact. This local clearance change
is explicit in ADR0015; it is not a blanket isolation waiver or yield claim.

| Measured source check | Result |
|---|---|
| Full suite,11:23:15Z |155/155 PASS,zero errors/failures/skips |
| Expanded ADC geometry |127,156 comparisons clear;90 primitives/13 vias;28/28 pin contacts |
| Peripheral geometry,11:25:26Z |43,860 comparisons clear;15/15 contacts |
| Regulator/digital geometry,11:24:06Z |49,659/21,831 comparisons clear |
| Other clock entries |19/19 retained |
| Rules/net references |8/8 classes and367/367 references PASS |
| Exact-input source-shadow |205 owners;159 generic nets,unchanged |
| Local power groups |71/71 entry witnesses;96/96 pads |

The shared power narrow-length ceiling rises only by the explicitly measured
west-feed delta; whole3V3 is37.841448411mm/34. All non-west power source
remains exact. Control leaves shorten and their ceiling tightens. Conditional
branch resistance/loss accounting retains the full2.5A bound independently,
not an assumption of equal sharing or an assertion of safe fault duration.

## Evidence and remaining work

Raw logs, six candidate attempts, native gap diagnosis, regression results,
source-consumer checks and our source-only plot live in
`06_build/tmp/adc-feed-20260908`, with a last-written hash inventory.
Historical candidate scripts require the pinned baseline source/checkers;
they must not be replayed by applying their deltas to already-adopted source.
The shared runner uses120-second deadlines/10-second heartbeats. Initial
KiCad PROPERTY_ENUM diagnostics remain visible in the raw logs.

Five candidates were rejected, with10/4/4/2/1 findings; the sixth passed.
One equal-count iteration did not become a hidden three-attempt plateau.
The expanded GND_A8 screen exposed an older0.090mm same-net physical
pad-to-drill gap; relocating that via resolves the conservative0.255mm
source requirement without claiming a native PCB DRC result.

Known-bad fixtures must fail on actual geometry/connectivity, not just changed
coordinates. The pinned-baseline two-test red/green experiment is retained,
including the initial version and its strengthened geometry-first revision.
Neither fixture substitution edits live source or constitutes an independent
design review.

Next: finish EP/return/source intent and analog endpoint checks, then fresh
generation/admission/reviews, actual routing and release verification. Current
carrier PCB remains stale/unrouted/unreleased. Parent stays boardless with
COMMISSIONING-HOLD; sealed pod remains sourcing-held and DO-NOT-ORDER.
All TOP77/0.20A first-power, physical/sourcing and both-child-seals/fresh
publication-gate holds remain. No account, upload, purchase or main push.
