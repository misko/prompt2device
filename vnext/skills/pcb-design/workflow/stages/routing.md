# KICAD-ROUTING — complete copper, check, repair or backtrack

**Local native-source pilot.** Use the [tooling interface](../../procedures/routing/tooling.md)
for isolated refill/build, replay/DRC and independent-review receipts. It does not
author copper automatically. Review/test the adapter and explicitly adopt it for
the project before dispatching candidate routing. Do not use legacy commands or
invent a receipt for unsupported geometry or producers. Tool availability does
not resume the user's placement checkpoint.

## Entry and deliverable

Requires current `placement_reviewed` and an explicit
[mating-clearance disposition](mating-clearance.md). On authorized resume, recheck
the placement receipt using its adopted toolchain. Preserve the accepted boards;
write routing candidates in new directories. Bind actual board/net/pad identities,
applicable manufacturer constraints, stackup evidence, design rules and remaining
placement-review obligations. Distinguish sourced limits from designer allocations.

Produce native routed boards for every board type, retained editable sources,
readable layer previews, native connectivity/DRC results and a short engineering
review packet. Partial diagnostic copper may inform the route but must be checked
against current inputs before reuse. It is not an accepted routed baseline.

Translate binding placement/mating obligations into authoring constraints and
check that export/import preserves them. If a constraint cannot be encoded,
retain an explicit native geometry check; tool defaults or clean DRC do not
prove it was honored. Inspect inherited copper as well as new routing.

After changing a block, reverify all affected connections and shared copper,
including unmoved neighbors served by it. One integration owner must preserve or
replace the complete affected services: supply, return, control/sense and thermal
duties where applicable. Preserve required functions, not obsolete trace coordinates.
Run native refill/DRC and the adopted authoring boundary before freezing; compare
shared contacts and return/thermal duties, not just component poses or open counts.
Reopen affected placement and critical-route evidence when their geometry changes;
reopen circuit acceptance only when the source changes. Keep unrelated acceptance.

Aim for a complete candidate in a bounded pass. Prioritize paths whose constraints
could force a different placement, then integrate the remaining signal/power and
return paths. Blocks organize work, not electrical ownership; check cross-block
connections and every repeated instance. Independent route alternatives are
optional when useful, not a required fan-out or a new pipeline per net.

## Verification and acceptance

The local implementation must verify source/native consistency, unchanged accepted
placement and electrical identities, complete intended connectivity, actual copper
clearances, manufacturability rules, filled-zone connections and reference returns.
Review critical loading/timing/current/thermal constraints with applicable evidence;
DRC alone does not establish them. Separate later physical qualification from a
known design contradiction. No shorts or unintended open connections may be hidden
as diagnostic leftovers or blanket exclusions. Any permitted exception needs a
specific requirement basis and independent disposition on exact subjects.

Also run `/usr/bin/python3 tools/routing_geometry.py BOARD REPORT` on each final
refilled board and bind its report and tool identity in the independent review.
Same-net DRC can miss via holes inside solder lands. Review drill intersections
and annulus contact against actual mask/paste and the adopted assembly process;
tenting alone does not close a hole inside an exposed pad. Unfilled via-in-pad
without a supported process is a routing repair, not a clean-DRC waiver. Optional
`--annulus-gap MM` and `--front-rectangle X0 Y0 X1 Y1` require explicit design or
mating authority; they are not universal clearance numbers or full 3D fit proof.

An independent review must cover completeness, physical rules, electrical/return
paths, interface fit/applicability and reproducibility of all board types. Only a
successful owning issue/check pair may produce `routed_board`. Tests must reject
stale upstream receipts, changed pads/nets or placement, missing routes, shorts,
stale zone fills, forged reports and unsupported or unknown applicability. Test
an evidence-led placement backtrack and reacceptance, not just the happy path.
Stop at the user's routing reflection checkpoint before layout seal/release.

## Orchestrator recovery interface

Use the existing [recovery procedure](../../../workflow-orchestrator/references/recover.md),
not a second routing retry loop. The graph's `recovery` mapping records default
owners for diagnosis; it is advisory, not an automatic dispatcher or permission
to change accepted inputs. Backtrack to the earliest demonstrated cause:

| Finding | Owning next action |
|---|---|
| Local copper conflict with a feasible existing placement | Repair routing |
| Pin escape, congestion, return path or geometry cannot meet requirements | Reopen placement; try a local block move or an evidence-led whole-board alternative |
| Circuit/pin/part requirement is contradictory | Reopen schematic; reopen sourcing if part identities change |
| Foundational interface or system choice causes the failure | Reopen architecture, within authority |
| Mating geometry is unknown or conflicts | Resolve mating clearance; reopen placement if geometry must change |
| Tool/evidence failure or unresolved engineering reasoning | Repair the demonstrated tool fault with a regression, or escalate a focused diagnosis |

The coordinator records the finding, causal evidence, destination, affected
acceptance, next discriminating check, owner and cumulative allowance in the
existing project journal. Reassess after the first unsuccessful attempt; after
at most two on the same causal decision, stop routine retries and choose a
materially different approach, escalation or a justified pause. New workers or
new draft names do not reset that history. Preserve the old accepted baseline;
changed candidates must regain upstream acceptance before downstream promotion.
Get user direction for changed requirements or other out-of-scope actions.
