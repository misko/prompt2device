# Two power owner-region boundary probes

**Isolated research, no route or P1 credit.** `probe.py` pins the reviewed
Q_PRE-repair TI board SHA-256
`e07ed8bc663fdfd4ce39477165b656b0dcf2bfbae54d84ec501bfccf326d22ef`
and the unified source/floorplan/modular plan. It reuses the 13-cell,
69-reference `quiet_power` partition accepted in
[`quiet-power-functional-cells-sol`](../2026-09-25-quiet-power-functional-cells-sol/README.md).
Every native electrical owner, pad/net, source endpoint and fixed pose remains
unchanged. Run `python3 probe.py` here to regenerate [`result.json`](result.json).

Three actual checker trials use the full 171-terminal power denominator:

| Region trial | `_physical_cells` | Four unresolved branches |
| --- | --- | --- |
| Accepted 13-cell baseline: `analog_ch2` xmax 69.00; recut `input_buck` ymax 100.50 | PASS, 69/69 quiet refs | `N1V8` 42/42 and `N3V3X` 27/27 pass; `N3V3_ADC` stops at `U_AFE2.8`; `N5V_BUCK` stops at `U_BUCK.10` |
| `analog_ch2` xmax **69.25** only | PASS, same 69/69 cells | First analog pad is now contained, but `N3V3_ADC` stops next at `U_AFE3.8`; `N5V_BUCK` still stops at `U_BUCK.10` |
| Both requested moves: `analog_ch2` xmax 69.25 and `input_buck` ymax **100.70** | **FAIL**: `quiet_buck_edge: physical cell overlaps foreign region input_buck` | Not admitted; no branch is given invalid cell authority |

`U_AFE2.8` is `[67.3,74.195,69.25,74.795]` mm, so the 0.25 mm
`analog_ch2` eastward adjustment is geometrically allowed by the complete
quiet-power cell checker. Its next exact net endpoint, `U_AFE3.8`, is
`[89.3,74.195,91.25,74.795]` mm and exceeds the unchanged `analog_ch3`
right edge at 91.00 mm. The packet stops there rather than extending all
channel regions without a coupled review.

`U_BUCK.10` reaches y=100.70 mm, but moving the rectangular `input_buck`
region from y=100.50 to 100.70 intersects the already validated
`quiet_buck_edge` cell over `[51.675,100.525,54.975,100.70]` mm. That cell
contains `C_PWR_CT2` and `R_DUMP_PD`; the overlap is source-region geometry,
not a claim of a pad short. A narrower region could avoid this cell but would
exclude existing untagged input endpoints such as `C_OUT2.1` (x maximum
57.45 mm). A separate input-buck physical-cell partition or a physical move
would require its own full member and endpoint review.

The combined trial is **INCOMPLETE and inadmissible** because the foreign
region overlap fails before any branch can rely on the candidate cells.
Capacity remains null, P2 pad-to-tree and filled-return obligations and P3
connected-tree duties remain open. No canonical source/board/checker edit or
formal P1 attempt is made.
