# Incident packet: coupled geometry

## Scope and provenance

This packet supports the planned **Coupled routing geometry** checkpoint family for retrospective incidents R09–R12. The retrospective source is verified at `0dd098e2b58dc8750b19ab9305a78e46a9c92c5b` (2026-09-20). The detailed engineering record below is `improvements.md` at verified revision `99557b65a4b74892b1ac61e5a3753463bab9d133` (2026-09-16), especially IMP-193 and IMP-258. Bounded `git blame` attributes the cited lines to that revision.

## Compact source excerpt (12 lines)

> A source-owned `AUDIO_EN` bridge passed its individual native pad, seed,
> annulus and drill-clearance screen, but crossed the only usable escape for
> adjacent `U_AUDIO.5/AUDIO_CT`. Full replay left `AUDIO_CT` on one of three pads.
>
> Reversing a power-wave order routed smaller rails but boxed eight terminals
> out of the 54-pad `3V3_ADC` tree. Reserving three observed joins made all
> 16 ADC nets and 64 terminals pass with zero route DRC violations, yet early
> `AUDIO_EN` dogbones still occupied five of thirteen ADC attachment cells.
>
> The later correction made `AUDIO_CT` one complete F.Cu tree and gave
> `AUDIO_EN` two off-pad transitions; their regression grades both nets together.

This is a faithful compression of IMP-193/IMP-258, not raw transcript text.

## Failure, cause and successful correction

The direct evidence establishes two defect shapes: individually legal adjacent routes that do not coexist, and an accepted early tree that encloses terminals needed by a later tree. It also establishes that route-order reversal did not resolve the geometry, and that a router success tally once missed an isolated `AUDIO_EN` pad.

The evidence supports physical corridor consumption as the cause in these observed cases. The larger claim that every failed search in this family is a geometric impossibility is **not established**. A bounded search failure remains unresolved feasibility unless a separate reachable-region, cut or analytical witness proves impossibility.

Successful corrections co-designed the `AUDIO_CT`/`AUDIO_EN` neighborhood, replayed from the earliest affected wave, reserved a geometry-derived set of ADC attachments, shortened/relocated obstructing branches, and rechecked the complete native board. Authoritative inputs and graders are:

- `projects/crow-audio-carrier-v1/03_src/route.yaml` and `03_src/route/`
- `projects/crow-audio-carrier-v1/03_src/rules/nets.yaml` and native `.kicad_dru`
- `projects/crow-audio-carrier-v1/03_src/floorplan.yaml`
- `projects/crow-audio-carrier-v1/04_kicad/crow_audio_carrier_v1.kicad_pcb`
- owning connectivity, clearance, width, layer and via gates named in `projects/crow-audio-carrier-v1/03_src/contracts.md`

## Exact regression properties

The planned family must prove:

1. Each isolated route can pass its local checks while their combined native geometry fails with a nonzero conflict or unreachable-terminal witness.
2. Reordering the same conflicting geometry is not a repair.
3. A positive successor connects every required terminal in the constrained neighborhood and passes native DRC, effective clearance/width, allowed-layer and zero-via checks.
4. Alternate legal combined geometry can pass; grading cannot require one reference polyline.
5. A route that connects only the named net, lands on the wrong same-net component, uses a forbidden via/layer, or leaves an inherited terminal split must fail.
6. A local success cannot be reported as whole-neighborhood or complete-board feasibility. Downstream native checks remain mandatory and unrelated protected artifacts remain unchanged.

These are **planned** family properties. The existing `crow-routing-geometry` case is already a useful native, synthetic two-pad F.Cu/zero-via reduction, but its own manifest says it is not the historical board, route chain or pad population. It does not yet prove combined-tree conflict, alternate-solution admission or complete inherited-terminal preservation.

## Retired approaches and reduction limits

Retired approaches: single-net acceptance in a shared pin field; repeated order/grid retries after an unchanged cut; freezing incidental diagnostic copper as a new constraint; and trusting a router group tally without native whole-board terminal enumeration. Reconsider an earlier branch only when placement, legal layers, effective rules or an independently graded crossover changes the cut; then invalidate and replay every affected successor.

A minimal fixture necessarily omits most of the 179 multi-pad nets, real placement density, stochastic search, thermal/return geometry and final fabrication/release gates. A two-tree witness demonstrates one interaction, not general routability or impossibility. Historical counts describe the cited run only. No issue-specific spending is known.
