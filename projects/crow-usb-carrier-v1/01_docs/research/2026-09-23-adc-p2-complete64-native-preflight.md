# ADC native-trial preparation checkpoint — stopped before admission

The preserved 64-reference source proposal was successfully adapted without
running generation. Repo-root patch SHA-256 is
`a69641d0bb097a4c31e44e5072ef3b1b5966bd3417289e29d58c86fa51f6e027`;
project-root normalized patch SHA-256 is
`abb2d97e358d28bcffc502df262afdaba454ffc2d72d7b7c7be62b4efdbcb21b`;
both produce floorplan SHA-256
`5f659a230905debe0dbb2dfc51651c60b3bd3ed8e75e202252ac45c2cbec3c2d`.

This patch is now superseded for admission. Independent review requires a
second local supervisor bypass, `C_ADC_3V3X_OK_VDD`, making the scope 65 refs and
staling the current schematic, circuit JSON, patch hashes, expected floorplan,
and full-scope inventory. No envelope field was silently rebound to that future
source.

The preserved full-64 inventory is `adc_scope_inventory.fixture.json`: 17
numeric refs, 20 per-pin ADC decouplers, and 27 qualitative refs. The raw
selected-90 dossier manifest remains
`/tmp/crow-p2-adc-reference-prep-20260923/selected_90_dossiers.csv`, SHA-256
`bc3f8cfadb6afb6321c77228d40f38e1d0cb9b0108e1b8aa7f45a9c5fb6450a9`.
Correct ADC functional pins are AVDD 1, IOVDD 19, AREG 2, VREF 3, AVSS 4,
and DREG 24.

The in-memory full composition passes 322,990 distinct foreign-net F.Cu pad
pair checks at 0.127 mm and 231,550 bidirectional scoped-body/foreign-pad checks
at 0.10 mm, with zero findings. This supplements the zero exact courtyard
findings. All four VREF 0.20-mm reservations retain 0.15-mm foreign-pad
clearance with zero hits. These are source-placement predictions, not native
generation, native DRC, model registration, schematic parity, or admission.

Proposed post-repair poses are `C_ADC_DIGITAL_OK: [113.1,107.0,270]` and
`C_ADC_3V3X_OK_VDD: [118.1,107.0,270]`. Each has a 1.300154-mm closest
same-net pad-centre span to its intended supervisor and passes the exact joint
courtyard predicate in memory.

Admission prerequisites still missing:

- independently reviewed 65-ref source repair and exact repo-root patch;
- regenerated schematic/netlist/circuit JSON hashes proving the added reference;
- recomputed full-65 scope inventory, pad/body/VREF checks, and expected floorplan;
- positive source and native admission decisions bound to current HEAD
  `682b862b84873c30f0de5f2721bfecc330bcd2db` and every resulting input hash.

No native task was admitted or run, and no PCB was saved.
