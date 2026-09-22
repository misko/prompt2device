# Independent schema-source normalization review — 2026-09-22

Verdict: **ACCEPT**

Reviewed commit: `6ca2c6339d1e3fe6c599122b0dba128818046689`

## Engineering-preservation findings

- Every removed orphan field class is retained in `01_docs/research/2026-09-22-schema-normalization-evidence.md`. The retained blocks include the LT3045 programming, rail, thermal and stability calculations; W25 boot/protocol facts; all 129 XU316 pin-domain annotations; TPS26625 binding and qualification cautions; passive derating screens; layout geometry; sourcing observations; and removed power-tree prose.
- No executable constraint was found to depend on a removed dossier key. The 13.2 V source maximum remains in the machine-read external-output requirement and surge path and is exercised by `early_design_check.py`. Rail IR component budgets, load floor and delivery margin remain machine fields. LT3045 effective-capacitance and rail bounds remain in `power_tree.yaml`. Part identity, pins, limits, escape facts and layout constraints remain in their canonical dossier fields.
- The five passive-fault `*_evidence_locator` declarations are honestly marked `OWED`. They have zero current instances; adjacent numeric values and evidence grades remain machine-read. This corrects stale claimed reader ownership without changing a live verdict.
- The exact FA-238 crystal catalog identity `C2650433` remains in `02_parts/FA-238-24.0000MD30X-W5/part.yaml` and was outside the candidate diff.
- The LT3045 evidence block contains one `capacity_ratio: 2.0` entry. A duplicate seen in one captured tool-output rendering is absent from the working file and the committed blob.

## Independent checks

- `schema_reader_audit.py --root .`: PASS, 969/969 declared keys; 856 PROVEN, 66 ADVISORY, 47 OWED; zero UNREAD, UNPROVABLE or ORPHAN.
- `early_design_check.py projects/crow-usb-carrier-v1`: PASS, 4/4 gate families, including the 10.8–13.2 V D-SPEC window and 13.2 V E-SURGE bound.
- All 16 modified YAML files load with `yaml.safe_load`; `git diff --check b54cfac6..6ca2c633` passes.
- `tests/t1_contracts.py`: its relevant orphan-schema known-bad passes. The aggregate suite reports 14 pass / 3 fail due to pre-existing fleet contract debt outside this candidate (old `usb-hub-3s-v3` allowlist rows and absent debt-ceiling rows for two other projects).
- Parent independently reported `skill_authority` PASS, `t1_skill_progressive_disclosure` 14/14, and `t1_pcb_documentation` 15/15 against this candidate.

No native schematic, PCB, release, procurement, or physical acceptance is inferred by this source-schema review.
