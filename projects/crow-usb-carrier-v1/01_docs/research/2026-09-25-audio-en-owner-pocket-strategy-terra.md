# Strategy review — sparse AUDIO_EN owner pockets

**Choose B for bounded P1 truthfulness, while retaining A as the P2 placement target.** This is a research recommendation, not a checker/source change or P1/P2 result.

The modular design authority says that every component has one functional block owner, but “functional ownership does not require physical colocation”; endpoint attachments belong beside the endpoint they serve. It also requires a full native envelope/pad census before treating a broad block region as exclusive, and keeps P2 pad access and P3 routed/filled-return proof separate from P1. That supports a local ownership representation for an endpoint without pretending that the full block is placed.

## Comparison

**A — complete `physical_cells` now** is the right eventual placement proof, but is disproportionate and presently obstructive for the immediate ownership error. The current checker makes `physical_cells` optional; once `quiet_power` opts in, `_physical_cells` requires every owner ref exactly once across its cells, an owner-named primary cell, full envelope/pad containment, and no foreign planning-region overlap. `quiet_power` has 69 listed refs. Its current primary `[25,105,75,134]` overlaps `input_buck` and `hold_bank_left`; the broad `analog_ch1` cell cannot simply be cut for `U_ISO1` because `R_IN1P` and `U_ESD1` straddle that cut. A partial three-cell declaration would be a false partition, not progress.

**B — sparse branch-owner pockets** can make an honest, narrower advance: validate only the three out-of-primary-region AUDIO_EN endpoint attachments while retaining their existing functional owners. The measured 15-part evidence gives candidate full-envelope pockets for `quiet_power/R_AUDIO_PD`, `quiet_power/U_AUDIO`, and `analog_ch1/U_ISO1`; each contains its named footprint/pads and has no foreign native body/pad intersection. The current full AUDIO_EN denominator remains 11 pads: eight `U_ISO1..8.2` plus `R_AUDIO_PD.1`, `R_AUDIO_PU.2`, and `U_AUDIO.6`. `R_AUDIO_PU.2` still has its exact `input_buck` foreign-region debt. B cannot remove it or turn the 11-pad bus into a three-pad route.

Current checker semantics do **not** implement B: unresolved branches test pads against `regions[block]`, and physical cells are complete partitions. Therefore B is viable only as a new, explicitly no-credit source/checker feature, first tried in an isolated hash-bound packet. It is preferable to a premature complete partition because it records the actual endpoint ownership fault without falsely declaring 69 quiet-power parts exclusive.

## Minimum fail-closed contract for B

A `branch_owner_pockets` row should have an exact-key schema: `id`, `owner_block`, one or more exact owner `refs`, `bbox`, `branch_ids`, and native board/floorplan/alias hashes. It must:

- bind every listed ref to the modular owner and each listed endpoint to an exact source/native `REF.pad`, net, and branch; reject duplicate ref/pad use, aliases to one native pad, undeclared endpoint use, and a pocket that no branch consumes;
- contain the complete `_physical_envelope` and every native pad of each listed ref, stay in the board outline, and exclude every foreign native envelope/pad and foreign planning region; same-owner broad-region overlap is allowed solely because this is not a complete cell;
- require the affected branch endpoint and its P2 pad-to-unplaced-tree duty to name the pocket, while every un-pocketed endpoint still passes the ordinary primary-region test;
- reject `capacity_slots`, demands, reservation geometry, route status, `PASS`, P1 acceptance fields, and use by integration corridors, linked paths, or fixed-access witnesses; report `INCOMPLETE` only; and
- retain the complete branch denominator, exact foreign-blocker inventory, P2 continuous-filled-reference duty, P3 connected-tree duty, and native DRC/route/return requirements.

Negative controls must fail for a clipped body/pad, foreign envelope/pad or region, wrong owner/ref, stale hash, duplicate endpoint, omitted one of the 11 AUDIO_EN terminals, `R_AUDIO_PU.2` blocker deletion, a pocket presented as an ordinary `physical_cell`, and any capacity/route/PASS claim. A successful sparse pocket removes only the specific owner-region containment error. P2 must still place the coupled quiet-power/hold/buck groups, and P3/P4/P5 must establish actual routes, GND reference, local power/thermal loops, DRC, connector-FULL where applicable, and integrated release evidence.
