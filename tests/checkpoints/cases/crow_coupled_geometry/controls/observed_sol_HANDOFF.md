# Coupled MCH clock / ADC TDM checkpoint handoff

Result: **PASS**

## Source repair

Changed `03_src/route_geometry.yaml` so the complete `MCH_CLK` tree leaves its
inherited `(5.0, 10.6)` seed toward the left, passes around the `U_ADC` launch
at x=3.4, and returns along y=9.0 to the inherited `J_CLK` seed. Its branch now
runs directly from `(5.0, 10.6)` to the inherited `R_CLK` seed at `(5.0,
12.0)`. The complete `ADC_TDM` tree remains connected on its existing straight
trunk and terminal branch.

The repair preserves all six inherited seed segments, all six fixed pads, the
exact two-net pad population, 0.25 mm route widths, F.Cu-only routing, and zero
vias.

## Regeneration and owning gate

Regenerated the native prepared and combined witness boards with:

```text
/usr/bin/python3 build_native.py
```

The first gate invocation did not grade because the supplied JSON output path
already contained the prior receipt. I removed that stale generated receipt
and ran the required gate against the fresh
`06_build/coupled/gate/repair-1` workspace. Exact final command outcome:

```text
exit 0
COUPLED-GEOMETRY PASS: 2 required net(s); receipt=/tmp/crow-coupled-sol-trial-20260920-01/workspace/06_build/coupled/coupled-receipt.json
```

Final receipt status is `PASS` with 3/3 expected checks present and one coupled
neighborhood covering two required nets:

- candidate: `PASS` (`candidate workspace verdict ACCEPTED`)
- connectivity: `PASS` (`0 failed required net(s)`)
- physical DRC: `PASS` (`0 hard / 0 partial-stage violation(s)`)
- via-in-pad: `PASS` (`0 router-created vias in SMD lands`)
- route base: `PASS` (`0 finding(s); 6 footprints / 0 vias / 6 inherited tracks compared`)
- realized policy: `PASS` (`2 net policy census; 0 finding(s)`), with both nets
  layer-restricted, no-via, and checked against native width rules

This receipt is only a combined feasibility witness for the reduced synthetic
neighborhood. It is not a completed routing stage, a full-board route, a layout
seal, or a release claim.

## Changed files

- `03_src/route_geometry.yaml`
- `06_build/coupled/prepared.kicad_pcb`
- `06_build/coupled/prepared.kicad_prl`
- `06_build/coupled/prepared.kicad_pro`
- `06_build/coupled/prepared.kicad_dru`
- `06_build/coupled/witness.kicad_pcb`
- `06_build/coupled/coupled-receipt.json`
- `06_build/coupled/gate/repair-1/**`
- `06_build/coupled/gate/repair-1-current-rules/**`
- `HANDOFF.md`

Usage: UNKNOWN
