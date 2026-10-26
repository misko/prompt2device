# KICAD-MATING-IMPORT — registered 3D interface fit

For new acceptance, use [registered 3D evidence](../../procedures/mechanical/3d-verification.md).
Verify actual board/mate solids, independently constrained registration, relevant
tolerances, intersections, minimum clearance, engagement and access. Retain STEP,
critical views and machine measurements for independent review. Unknown model
height, a 2D envelope or an unspecified accessory cannot prove a 3D fit claim.
Use [version3 admission](../../procedures/mechanical/mating-admission.md) for new
acceptance. The existing mating owner binds frozen scene replay, current placement
and complete independent feature/limitation dispositions. Historical v1 receipts
are not upgraded by changing these instructions. Adapter capability and an
individual board's engineering acceptance are separate.

**Historical local independent-review pilot.** The [routing tooling](../../procedures/routing/tooling.md)
binds/checks the earlier disposition before consuming it as `mating_clearance`.
The tool verifies subjects and review completeness; engineering fit/collision is
independently reviewed, not automatically measured by a 3D collision engine.
The historical graph selects this stage for `foreign_mating: true`, while routing
requires its output. The local adapter must explicitly resolve that conditional
dependency; an unselected stage is not an implicit PASS or a fabricated receipt.

Start from current `placement_reviewed`. Determine whether foreign mating-board
geometry applies. If applicable, retain the exact mating geometry and datum,
orientation, connector engagement, clearance/keepout evidence and independent
review. Missing relevant geometry is unresolved, not not-applicable.

If foreign mating does not apply, record the reason and scope evidence; the
consumer must verify that disposition against current inputs. Ordinary cable plug,
service access, enclosure, mount and acoustic-opening obligations still need an
explicit disposition under routing/mechanical review. Do not claim physical fit
for an unspecified enclosure. Deferred qualification needs a defensible prototype
scope; a known collision must be repaired before acceptance.

The implementation must test applicable PASS, justified not-applicable, unknown,
stale geometry and collision. Changed placement or mating geometry invalidates
the affected clearance and dependent routing evidence. Send geometry conflicts
back to placement through the existing orchestrator; this is not permission to
move a frozen footprint without reacceptance. Never waive the prerequisite merely
because its local tool is missing.
