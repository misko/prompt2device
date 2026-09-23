---
review_kind: joint-p1-source-repair
design_verdict: DEFECTIVE
order_verdict: DO-NOT-ORDER
subject_raw_sha256: bcfa0806cd2bf1d80478bd67dc95118369125fd43f3fb9b000a574d59488a5db
subject_semantic_sha256: acdd740760aa45f0dee23d99dea974b04a44c987de41d4fdc41dd00a6e1fe18d
---

# Joint P1 source-repair review

## Decision: DEFECTIVE — one timing-branch constraint remains missing

The footprint scope is structurally narrow and adequate as a source repair: the five edited files change silkscreen or the PCB `Description` property only. Pad geometry, courtyards, F.Fab, models, anchors, electrical metadata, `descr`, and Datasheet survive. The coupon’s 10-instance negative/positive control changes 41 silk findings to zero, while openly retaining eight netless USB fixture findings (four clearance and four solder-mask bridge). The SC70 and rotated JTAG pin-1 marks are visible and usable; the fuse remains unmarked as a non-polar part. The USB mouth silk move is clearance-only and does not prove connector fit. Clearing PCB Description does not remove `descr` or Datasheet evidence.

The ten part dossiers correctly resolve all 310 declared budgets (from 55 unreached), retain all non-`layout` YAML fields and every numerical ceiling, and reconcile 43 actual shared-net names including `ADCx` to `ISOx`. The eight timing capacitors are each individually constrained. The three retired OE constraints apply to removed `U_OE/C_OE/R_MCH_SENSE/R_MCH_SENSE_PD`; current OE ownership is indeed `U_TDM_XLATE.15`, `Q_TDM_GATE`, and `R_TDM_OE_PU` on `TDM_OE_N`, so retaining the obsolete rows would be false coverage.

However, the actual native netlist has `U_DUMP.2`, `R_DUMP_TIME2.2`, and `R_DUMP_TIME3.2` on `DUMP_RC`; `R_DUMP_TIME1.2` branches to both `R_DUMP_TIME2.1` and `R_DUMP_TIME3.1` on `DUMP_RMID`. Retargeting the former false `U_DUMP`–`R_DUMP_TIME1` rule to the two real `R_DUMP_TIME1`–`R_DUMP_TIME2/3` segments is justified. The current dossier retains `U_DUMP`–`R_DUMP_TIME2` at 4.0 mm but has no equivalent direct `U_DUMP`–`R_DUMP_TIME3` budget even though both are parallel DUMP_RC branch endpoints. Add an explicit `U_DUMP`–`R_DUMP_TIME3` `DUMP_RC` adjacency budget with the same 4.0 mm ceiling, or provide a circuit-specific reason it is intentionally exempt. Until then, the parallel branch is underconstrained.

The post-repair audit still reports actual `P-ADJ` and `P-ADJ-PAIR` distance failures; they are retained and are not placement acceptance. The repaired source leaves current Circuit JSON (`2b9a33b6…`), PDF (`f9bfdffd…`), and native schematic (`9b4c8100…`) byte-identical to accepted commit `106ace85`. It nevertheless changes the parts-review digest through `layout` contracts. Prior SOUND topology/render witnesses therefore cannot be blindly rehashed or carried forward: commission fresh witnesses bound to the new parts digest after this source defect is corrected. No native-board equivalence is claimed.
