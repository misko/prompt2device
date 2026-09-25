# Crow: bounded native placement-loop validation

The scoped skill was exercised through `pcb_flow.py run --stage placement
--investigation USB-XTAL-native-realization`, with source admission, a 900 s
hard deadline and a two-launch total budget. The ledger in
`01_docs/findings.yaml` owns the launch history and assessments. These are
isolated investigations, not modular completion receipts or promoted copper.

| Measurement | Prepared baseline | Compact candidate r2 |
| --- | ---: | ---: |
| Native unconnected count, including hidden items | 1321 | 1314 |
| DRC unconnected rows emitted | 499 | 499 |
| Clearance-class findings | 40 | 40 |
| Library-footprint findings | 199 | 199 |
| New silkscreen findings | 0 | 9 |
| Schematic parity findings | 0 | 0 |
| Complete oscillator signal pad groups | 0/3 | 3/3 |

The 499 emitted DRC rows are not the native connectivity total. Absence of
an XTAL-named row did not prove its pads connected. Native connectivity and
the independent exact-track audit prove r2 connects 3 XTAL_IN pads, 4 XTAL_OUT
pads and 3 XTAL_IN_R pads. It moves five oscillator/support components and
preserves the other 564 poses. The nine new silkscreen findings and remaining
oscillator GND connections still require repair. Saved plane fill alone is
not proof that those grounds or the signal return are connected.

r1 added only six pad-escape tracks. It left the networks incomplete and
added two dangling tracks. Its legacy `xtal_unconnected_items` metric counted
rows mentioning oscillator footprints, including GND; the corrected meaning
is recorded in `r1_result.json`. Equal clearance-class counts do not establish
identical global violation sets because unrelated refill-report rows vary.

Inputs are the pinned QSPI-gap native board and its source rule inputs. The
existing rule generator prepares identical PRO/DRU authority for baseline
and candidate. This is a fresh experiment under that generated authority,
not reproduction of an earlier accepted board. Recipes refuse an existing
output directory. Native outputs remain under `06_build/candidates/xtal-r1`
and `xtal-r2`; compact JSON evidence is retained here.

The native result supports reopening the coupled oscillator placement and
its ground return, rather than extending the corridor checker. It does not
prove oscillator performance, source-region acceptance, global DRC, connector
FULL, or release readiness. Historical P1 packets retain their original plan
bindings; the scoped work-graph revision does not refresh their acceptance.

Read-only audit scripts may reopen the saved outputs. Another geometry launch
requires reassessment of this same finding and its exhausted budget; renaming
the task or changing agents does not authorize a third trial.
