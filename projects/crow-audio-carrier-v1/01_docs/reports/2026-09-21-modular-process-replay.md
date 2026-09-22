---
schema: 1
kind: pcb-human-report
report_id: 2026-09-21-modular-process-replay
title: Crow carrier modular design process replay
subtitle: Historical failure sequence and proposed decomposition in pseudocode
project: crow-audio-carrier-v1
date: 2026-09-21
status: DRAFT
evidence_status: INCOMPLETE
---

## Executive conclusion

**PROPOSED:** Decompose Crow into functional work scopes, then explicitly reunite
the scopes that compete for the same physical space. Prove those neighborhoods
before committing to extensive routing. The largest expected change is earlier
discovery of coupled failures around AUDIO_CT/AUDIO_EN and the ADC/clock field.
It is not permission to route eight independent rectangles or skip final gates.

**OWED:** This is a counterfactual process walkthrough, not an executed PCB
simulation. No routing success, saved attempts, elapsed-time improvement, or
new electrical performance is claimed.

## Question and scope

How would the proposed modular procedure have changed the work used to design
`crow-audio-carrier-v1`, particularly the September 14–15 routing incidents?
Pseudocode functions below describe intended behavior; they are not new APIs.
The scope is one carrier PCB, not a redesign into separate physical boards.

## Evidence boundary

**CITED:** Repository baseline `dcdcff574fc466e88f8b19b53b96566aa0ab4591f9`;
the current status beacon names `v0.1.8-2026-09-16`. The architecture document
contains earlier stage-status prose, so it is used here for functional topology,
not current readiness. Historical routing incidents come from the retained
retrospective and incident packet, not a fresh rerun of native geometry.

**INFERRED:** The block boundaries below are an illustrative proposal derived
from that topology. Exact component membership still needs an independent
netlist/footprint census. No new partition is adopted into the live design.

## Findings

### Functional decomposition for this carrier

**PROPOSED:** Begin with these candidate scopes, then challenge them against
actual cross-block connections and physical constraints.

| Candidate scope | Contents and responsibility | Important external dependency |
|---|---|---|
| Input power | J9, input protection and common input distribution | Pod branches, local conversion, mechanical service |
| Local supply | Buck, held supply, LT3041 and associated local support | Shared 3V3 loads, shutdown and return geometry |
| Receive channel 1–8 | Each pod connector/branch protection, coupling, AFE/filter and isolation cell | Shared bias, control and power; assigned ADC pads |
| ADC core | CS5308P, local reference/decoupling and configuration support | All eight receive channels and clock/TDM interface |
| Clock/TDM interface | MCHStreamer interface, buffering, series parts and pulldowns | ADC pin field and protected layer/via rules |
| Supervision/control | Rail supervision, enable and timing circuitry | AUDIO_CT/AUDIO_EN pin field and supply shutdown |

Board integration owns stackup, shared distribution/returns, chassis treatment,
outline, mounting and service corridors. Each component has exactly one owner.
These responsibilities do not imply a separate ground island per block.
Bias-bank components need one explicit owner, even though several channels
consume their outputs. Joint geometry tasks refer to component owners rather
than creating second owners.

### Historical sequence, compressed to the failure mechanism

**CITED:** Incidents R09–R12 describe the following pattern. This sketch omits
many successful checks and does not claim every historical attempt followed it.

```text
prepare exact board and routing rules
route an early net/tree
check that tree's local geometry
retain early work
route the next net/tree

observed example A:
    AUDIO_EN bridge passes its individual geometry screen
    replay finds AUDIO_CT connected to only 1 of its 3 pads
    investigate the shared U_AUDIO pin field
    co-design CT front-copper tree and EN off-pad transitions
    replay from the earliest affected wave; check both together

observed example B:
    early power routes block later terminals
    reverse wave order -> 8 terminals remain boxed out of 54-pad 3V3_ADC
    reserve ADC joins -> 16 ADC nets / 64 terminals pass in that trial
    EN dogbones still occupy 5 of 13 ADC attachment cells
    revise interacting geometry and recheck the combined board

observed example C:
    digital no-via constraints must be restored
    ADC exits and long MCH pulldown branches obstruct one another
    relocate passives, shorten branches, solve clock/TDM space jointly
    reroute under the restored constraints
```

Those counts describe particular historical trials, not the final board census.
The eventual repairs already contained modular reasoning. The proposal makes
that reasoning an earlier, repeatable step instead of rediscovering it during
route recovery. The current skill already includes a coupled-geometry checker;
the missing procedure helps choose its scope and timing.

### Proposed process, using the same engineering authorities

**PROPOSED:**

```text
facts = load_current_requirements_and_accepted_decisions()
lock(facts.assembly_side, facts.assembly_owner_per_component,
     facts.clock_and_TDM_layer_via_rules, facts.connector_interfaces)
# A later user change is permitted, but invalidates dependent work explicitly.

blocks = propose_scopes_from(circuit, part_dossiers, mechanical_constraints)
observed = independently_read_component_and_net_pad_census()
require(exactly_one_owner_for_every_component(blocks, observed))
require(every_crossing_connection_has_an_interface(blocks, observed))
require(named_owners_for_shared_board_responsibilities(blocks))

floorplan = allocate_blocks_and_shared_corridors_together()
tasks = challenge_boundaries_and_rank_physical_risks(blocks, floorplan)
tasks.include(joint_task(AUDIO_CT, AUDIO_EN, adjacent_escape_geometry))
tasks.include(joint_task(ADC_exits, MCH_clocks, TDM,
                        pulldown_branches, power_attachment_geometry))

for task in hardest_first(tasks):
    while within_existing_cumulative_attempt_budget(task):
        prepared = regenerate_from_owning_source()
        witness = propose_geometry(prepared, task, locked_rules=facts)
        result = independently_grade_combined_geometry(witness, task)

        if result passes and its declared coverage is complete:
            save_exact_evidence_and_supported_source_handoff()
            break

        record_constraint_cause_and_retired_attempt(result)
        if no_new_hypothesis or existing_plateau_limit_reached:
            backtrack_to_owner(placement, floorplan, part, or architecture)
            invalidate_dependent_evidence()
            break
        revise_owning_source_for_the_identified_cause()

pilot = prove_one_receive_channel_with_real_footprints_and_boundaries()
for channel in all_eight_receive_channels:
    check_instance(channel, pilot,
                   actual_neighbors, assigned_ADC_pads, shared_dependencies)
# A good pilot does not establish that the seven other surroundings are equal.

for partial_branch in diagnostic_local_routes:
    keep_diagnostic_only_or_expand_to_whole_net_task(partial_branch)
# An endpoint-scoped acceptance extension must be implemented/tested first.
# Dropping required-net coverage cannot turn a partial branch into acceptance.

adopt_supported_source_owned_routes_with_unique_ownership()
candidate = integrate_and_route_remaining_work_with_one_live_writer()
grade_candidate_with_existing_owning_gates(candidate)
promote_verified_route_source_through_existing_handoff()
rebuilt = replay_with_canonical_conductor()
independently_verify_connectivity_ownership_and_geometry(rebuilt)
run_all_required_whole_board_review_manufacturing_and_release_gates()
```

### One concrete simulated decision trace

**PROPOSED:** This is a conditional trace of the new procedure confronting the
documented defect, not a replay result or a guaranteed solver outcome.

```text
TASK: U_AUDIO control neighborhood
  Candidate: individually legal EN bridge
  Combined check: CT cannot reach every required terminal with this geometry
  Decision: reject neighborhood acceptance; routine routing does not advance
  Next hypothesis: CT front-copper tree + legal off-pad EN transitions
  If independent combined checks pass: retain exact scoped proof
  Otherwise: revise placement/source within the same attempt budget

TASK: ADC / MCH / TDM neighborhood
  Candidate: individually connected clocks with long pulldown branches
  Combined check: required ADC exits conflict with those branches
  Decision: reopen pulldown placement and joint corridor geometry
  Forbidden shortcut: remove the no-via requirement
  Candidate remedy: shorter branches / relocated passives / joint route
  Accept only after every declared required endpoint and constraint is graded

TASK: canonical integration
  Local proof passes, but regeneration drops a retained branch
  Decision: integration fails; fix source handoff, not generated PCB copper
  Local proof passes, but a later wave also owns the complete net
  Decision: ownership fails before accepting the integrated result
```

**INFERRED:** The expected benefit is spending early iterations on a smaller,
causally related neighborhood and avoiding downstream work based on a local
false conclusion. Whole-board checking remains necessary. A failed search
means unresolved feasibility unless an independent geometric proof establishes
impossibility. The process cannot guarantee discovery of every coupling early.

## Recommendations

**PROPOSED:** Pilot the decomposition on the carrier read-only. Start with the
two named coupled neighborhoods and one repeated receive cell. Record exact
membership, crossings and unmet assumptions before adding any schema. Keep
current no-via and assembly constraints bound to their existing authorities.

## Validation plan

**OWED:** Run matched checkpoint comparisons with the same inputs and limits.
Prove initial failure, a valid repair, and rejection of each shortcut: omitted
crossing, duplicate owner, partial-net overclaim, relaxed via policy, dropped
replayed route and duplicate downstream route ownership. Reopen native results
independently. Record attempts, time, integration rework and executed checks;
report savings only after measurement. Include a simple-board control to detect
unnecessary overhead. Synthetic coupons cannot certify the historical carrier.

## Source register

- **CITED:** [Carrier architecture](../ARCHITECTURE.md), functional topology;
  [status beacon](../STATUS.md), current recorded release posture.
- **CITED:** [Routing journal](../journal/routing.md), source ownership and
  early partial-launch limitations.
- **CITED:** [Route source](../../03_src/route.yaml) and
  [floorplan](../../03_src/floorplan.yaml), current implementation authorities.
- **CITED:** [Crow retrospective](../../../crow-roof-array-v1/01_docs/reports/2026-09-20-transcript-cost-retrospective.md),
  R07 and R09–R12, R20; draft retrospective limitations apply.
- **CITED:** [Coupled-geometry incident packet](../../../../tests/checkpoints/incidents/coupled-geometry.md),
  documented interactions, correction and reduction limits.
- **CITED:** [Process ledger](../../../../improvements.md), IMP-193 and IMP-258.
- **CITED:** [Placement procedure](../../../../skills/kicad-pcb/references/placement-and-proximity.md)
  and [candidate contract](../../../../skills/kicad-pcb/references/route-candidate-contract.md),
  scoped acceptance and current authority boundaries.
