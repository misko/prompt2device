# D11 ordering: Connector FULL versus private routing diagnostic

**Research analysis only.** No D11 exception, routing, board generation,
fabrication, or release decision is made here.

D11 requires a base Connector FULL receipt that is `PASS` with zero unknowns,
bound to the exact board or a separately governed coupon, before **any** P3
critical-local-route proof, route preparation/import/other routing, P5
promotion, release, or order. It deliberately permits non-promoted P2 work
before FULL and requires connector evidence to be repeated if P2 changes the
represented connector-neighbor or service geometry. D13 independently leaves
`USB-ESD-selection-transient` open at `DESIGN_CLEAN`; neither choice below
closes it.

## A — governed unpowered full-field article before routing

This is the shortest path to an admissible release sequence. Freeze the
connector field only after the P2-owned neighboring/service geometry that the
coupon represents is stable, then obtain a narrow authority for one unpowered,
full-outline mechanical article. Its evidence package must bind:

- exact board/outline/connector and neighboring-population revision;
- controlled 4-layer finished thickness, edge/drill/finish and assembly
  process, including connector lands and joints;
- all eleven exact connectors, mates and cable lots, plus enclosure,
  strain-relief and far-end cable support;
- six-hole M3 restraint drawing, approved force/deflection/cycle/registration
  limits, measurement calibration and uncertainty; and
- sample-level records for all 19 interface, reaction, service, cable and
  registration target families.

A passing governed receipt can actually satisfy D11's external prerequisite.
It still does not admit P3 by itself: a fresh P1/native candidate, P2
regrades, source/schematic acceptance and all ordinary route/return checks
remain required. It also cannot resolve D13 because the unpowered article does
not exercise USB ESD. Its principal risk is requalification if later P2 or
mechanical changes alter any represented connector geometry. The mitigation is
freeze only the service-relevant field after bounded P2 work, rather than
couponing an unstable full design.

## B — one private no-fabrication routing diagnostic before FULL

A new, explicitly narrow D11 exception could permit an ignored, hash-bound
private diagnostic after native placement. It would need a fixed route scope,
net/pad list, stack/rule authority, exact no-fab/no-credit receipt, native DRC
and parity, filled-return proof where applicable, and a hard prohibition on
promotion, release, order, fabrication exports and reuse as a coupon source.
It can reveal route escape, return, skew, clearance or stack feasibility
problems earlier.

It cannot make Connector FULL pass, cannot make P3 complete under ordinary
D11, cannot promote P5, and cannot close D13. Its evidence is likely to be
invalidated if the later physical coupon finds a connector/service conflict
and changes the field. D15 demonstrates the governance cost: even its
unrouted rule screen ended `FAILED_RESEARCH` on an existing safety gate despite
clean native DRC/parity, and its single-run authority forbids retry. A routing
exception has a larger failure surface: copper/return geometry, rule precedence,
route scope and checker semantics all become additional sources of consumed
attempts without reducing the physical 19-target work.

## Recommendation and sequence

Choose **A as the critical path**. It is the only option that removes D11's
release-critical gate. Use the currently permitted P2 diagnostics first to
settle service-relevant connector-neighbor geometry, then prepare the governed
unpowered full-field article and its fixture/limits. In parallel, conduct
no-purchase route-preparation research that does not alter a board or create a
private routing candidate: pad-pocket inventory, stack/rule review, return
requirements, and routing test-plan definition.

Consider B only after A's coupon package has frozen the relevant mechanical
geometry and only if a specific electrical uncertainty remains costly enough
to justify a new decision. The exception must explicitly retain FULL before
any promotion/release and D13's `DESIGN_CLEAN` hold. That ordering avoids
hiding physical qualification behind a private route diagnostic while preserving
useful electrical planning work.

Sources: [D11](../decisions/0011-p1-floorplan-and-p2-placement-admission.md),
[D13](../decisions/0013-usb-esd-prototype-boundary.md),
[full-field article strategy](2026-09-25-connector-full-field-unpowered-article-strategy-terra.md),
and [D15 post-generation review](2026-09-25-d15-independent-postgen-review-terra.md).
