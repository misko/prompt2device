# XU14/XU17 revised probe: silk ownership and C17 ground-via review (Terra)

**Scope.** Read-only review of committed Crow source and isolated revised candidate `/tmp/crow-xu-southwest-revised-source-sol`; no canonical PCB or source was changed. The candidate floorplan SHA-256 is `96d729e4bd6b697af8f7cb6f9626b58608dded9462fb259c78871b5b6dbb0aa1`; committed source `03_src/floorplan.yaml` remains `4a457c731c204084a83aa817a29ca8fc8acc07097723adefedc296eb4db37b98`.

## Exact silk controls

The two new ownership regressions are exactly `C_XU_VDDIO_17` (own 3.11 mm versus C14 2.28 mm) and `C_XU_VDD_14` (own 5.66 mm versus `R_QSPI_CS` 5.07 mm), as recorded by the isolated `generate.log`.

I regenerated two isolated, declarative source variants using the existing generic controls in `skills/kicad-pcb/scripts/generate_board_generic.py`:

- Prepending the exact ref `C_XU_VDD_14` to `silk.refdes.priority_refs` restores C14 to owned silk. This changes the candidate report from 258 owned / 266 degraded / 44 unplaced to 259 / 265 / 44. Priority is appropriate because it changes only placement order and still subjects the chosen text to the normal obstacle and ownership checks.
- C17 remains degraded even when placed first, so there is no owned position within the generator's existing bounded search. The bounded source control is therefore to append the exact ref `C_XU_VDDIO_17` to `silk.refdes.fab_only_refs`. With both controls, isolated generation reports 259 owned / 264 degraded / 44 unplaced and explicitly lists `C_XU_VDDIO_17` among 46 F.Fab-only waivers. The board-level F.Fab identity remains emitted because `fab_copy: true`; only its F.Silk refdes is hidden and the existing waiver report records it.

Proposed adoption, only if this placement candidate is otherwise admitted:

```yaml
silk:
  refdes:
    priority_refs: [C_XU_VDD_14, C_XU_VDDIO_10, C_XU_VDD_45, C_XU_VDD_39]
    fab_only_refs: [C_XU_VDD_39, C_XU_VDDIO_17]
```

This is not a claim that C17 silk has been made owned: it is an explicit, reviewable F.Fab-only exception. The test board was `04_kicad/crow_carrier_silk_exact_waiver_test.kicad_pcb` in the isolated copy and did not modify project source.

## C17 return via

The candidate C17 ground route ends at an ordinary 0.60/0.30-mm GND through-via centred at `(209.100, 110.500)` mm. Native C17 graphics give the F.CrtYd rectangle `[208.215, 108.865]..[209.185, 110.735]` and the physical F.Fab body `[208.400, 109.250]..[209.000, 110.350]` mm. The present via annulus envelope `[208.800, 110.200]..[209.400, 110.800]` overlaps both. Native DRC does not grade a component-body/courtyard incursion here, so its lack of such a finding is not assembly clearance evidence.

A narrower nearby corridor exists only between the C14 N0V9 branch on the west and the vertical TDM_FSYNC diagnostic strip on the east. The least-bad local trial is `(209.350, 110.500)` mm: its 0.60-mm annulus clears the F.Fab body by 0.050 mm. My temporary relocation DRC used a copied/missing-stale DRU context and reported 203 violations; it is **not authoritative** and is withdrawn as DRC evidence. It **still overlaps the C17 courtyard** (annulus extends left to x=209.050 mm), so it is a safer body site, not an admissible assembly site. At `(209.600, 110.500)`, the same temporary exercise exposed a GND/TDM_FSYNC short and a 0.125-mm clearance violation; that geometry observation remains useful, but requires repetition under the final emitted rules. Thus no same-via, same-layer nearby relocation proves both body/courtyard separation and the preserved FSYNC strip. The source-replay candidate's correctly ordered native run separately reports only the four intended dangling tracks; it does not grade this courtyard/body incursion.

The committed floorplan declares zero solder-mask expansion but does not supply a component-body keepout or a specific ordinary-via tent/fill order. JLCPCB's public capability record distinguishes ordinary vias from filled/capped via-in-pad and specifies ordering/process conditions for those cases; it does not supply a component-courtyard clearance that can be invented here. Its public via-covering guidance also distinguishes tented from bare vias and describes solder-wicking/short risk for bare vias. [JLCPCB capabilities](https://jlcpcb.com/capabilities/Capab) and [via-covering guidance](https://jlcpcb.com/help/article/pcb-via-covering) are fabrication inputs, not a waiver of the footprint geometry.

**Release implication.** Do not adopt the revised probe on this result. A follow-up must choose a C17 return topology/site that is outside the native courtyard with an explicit mask/assembly process decision, then rerun native DRC and local supply/return review. No manufacturer numerical clearance has been inferred.


## Addendum — isolated source replay prototype review

I independently inspected SOL's `37ba5ada` prototype at `/tmp/crow-xu-source-replay-prototype-sol`. The source diff is bounded: four post-anchors, four exact `prep.seed_stubs` banks added after the unchanged six PLL banks, and the two inactive exact-pin launch declarations. `prep_replay.log` supports the narrow mechanical claim: 10/10 banks served, 29 primitives/vias placed, zero refused. The four added banks account for eleven primitives (five C14 supply segments, two C17 supply segments, and two segment/via GND pairs), in addition to the prior 18 PLL primitives.

The saved final board's `04_kicad/crow_carrier.kicad_dru` has the required order: generic `DIGITAL_POWER_width`, then the TMUX POFV block, then one width rule for each XU launch. Its native replay report is the authoritative one: four `track_dangling`, 499 unconnected, and zero parity issues. The preliminary `06_build/route/r0.kicad_dru` contains repeated XU launch rules before the later POFV block, so it is not equivalent evidence and must not substitute for the final board/DRU pair.

This is a deterministic source-replay proof only. The helper remains `placement_review_required` and is not invoked by the normal build path; a future admission must make the generic-rules → POFV → helper sequence an explicit, audited build stage. It also does not close C17's courtyard/body/mask issue, C14's qualitative decoupling/return question, the four TDM diagnostic ends, 499 opens, or release acceptance.
