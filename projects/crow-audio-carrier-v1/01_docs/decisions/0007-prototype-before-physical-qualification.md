---
id: 0007
date: 2026-09-07
status: accepted
---
# 0007 — Build the prototype before requiring prototype measurements

## Context and user authority

The user questioned whether public information could support continued design.
The response proposed finishing documented connector design checks, layout and
a prototype release, with physical tests on the first assembled board and an
optional connector coupon. The user accepted: “This is great news! lets keep
going”. BRIEF D6 records this direction. No purchase or production approval was
given.

The previous pre-route FULL requirement made installed fit, simultaneous mating,
cable routing and tolerance measurements mandatory before routing the board on
which they would be measured. The optional coupon could satisfy that sequence,
but the user has not commissioned a mandatory separate coupon build.

## Decision

For this carrier's first-article design, require the existing connector SOURCE
gate again after candidate generation. It locks exact selected identities,
orientation authority, nonempty connector/group coverage, and a plan-bound,
closed set of physical unknowns. It does not prove physical fit or service.

Compile and retain the unchanged base and FULL receipts. Only FULL's represented
physical INCOMPLETE (exit 2), following SOURCE success, is nonblocking for
prototype placement review, routing and a design-sound release. Schema errors,
stale authority, missing identities and unclassified unknowns still block.
All independent pin, footprint, orientation, collision, placement, electrical,
DRC, fabrication and release reviews remain mandatory. A known design defect
must be corrected, not labelled a future measurement.

This explicit project-specific user scope supersedes the pre-route physical
qualification timing in the generic connector skill and earlier project
journals. It does not weaken the shared compiler or change other projects.
The existing coupon and blank worksheets remain optional historical evidence;
they must be revalidated against the eventual board before use.

## Separate acceptance boundaries

- Design release: exact reviewed source/layout/fab, with unqualified connector
  and hardware risks disclosed; no invented physical result. Existing source
  acceptance criteria are reviewed at design scope, their bench clauses later.
- Prototype order: separate user authorization, exact sealed upload review and
  current JLC allocation/economics. Public catalog stock is advisory per
  ADR-0006. Until these are present, the release is DO-NOT-ORDER.
- First power and first-article testing: exact cable continuity/polarity/fit
  checks before connecting power; staged current-limited bring-up and abort
  rules in FIRST_ARTICLE_TEST_PLAN. Obtain and verify the authorized MCH image
  before powered TDM testing. No hot-plug safety is assumed.
- FIRST_ARTICLE_TESTED: measured reset, TDM, analog, power, fault, thermal and
  full connector qualification. This is not a prerequisite for ordering the
  first article itself.
- Production/outdoor deployment: pilot and system/environmental qualification.

This supersedes A5's and ADR-0006's blanket “first-article tests before order”
timing, not their source/protection limits, sourcing controls or lab tests.
