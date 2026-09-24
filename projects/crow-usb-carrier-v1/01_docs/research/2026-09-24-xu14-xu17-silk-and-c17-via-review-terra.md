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

A narrower nearby corridor exists only between the C14 N0V9 branch on the west and the vertical TDM_FSYNC diagnostic strip on the east. The least-bad local trial is `(209.350, 110.500)` mm: its 0.60-mm annulus clears the F.Fab body by 0.050 mm and an otherwise identical temporary native board has the same 203 DRC violations, 499 unconnected items, and zero parity issues as the saved candidate. It **still overlaps the C17 courtyard** (annulus extends left to x=209.050 mm), so it is a safer body site, not an admissible assembly site. At `(209.600, 110.500)`, moving fully farther east causes a GND/TDM_FSYNC short and a 0.125-mm clearance violation. Thus no same-via, same-layer nearby relocation proves both body/courtyard separation and the preserved FSYNC strip.

The committed floorplan declares zero solder-mask expansion but does not supply a component-body keepout or a specific ordinary-via tent/fill order. JLCPCB's public capability record distinguishes ordinary vias from filled/capped via-in-pad and specifies ordering/process conditions for those cases; it does not supply a component-courtyard clearance that can be invented here. Its public via-covering guidance also distinguishes tented from bare vias and describes solder-wicking/short risk for bare vias. [JLCPCB capabilities](https://jlcpcb.com/capabilities/Capab) and [via-covering guidance](https://jlcpcb.com/help/article/pcb-via-covering) are fabrication inputs, not a waiver of the footprint geometry.

**Release implication.** Do not adopt the revised probe on this result. A follow-up must choose a C17 return topology/site that is outside the native courtyard with an explicit mask/assembly process decision, then rerun native DRC and local supply/return review. No manufacturer numerical clearance has been inferred.
