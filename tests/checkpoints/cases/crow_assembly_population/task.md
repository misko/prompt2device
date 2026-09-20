# Resolve Crow v1.3 assembly population evidence

Continue from the supplied mutable candidate. Follow the current `jlcpcb-fab`
skill and A-POP source contract. Determine whether the archived U1 declaration
correctly describes what the assembly supplier is instructed to do by the CPL.
Repair the source policy and regenerate any release-facing declaration from
that source. Preserve the physical part and the actual placement instruction;
do not solve a policy mismatch by deleting evidence or changing the board.

Run `python3 <repository root from START.md>/skills/jlcpcb-fab/scripts/assembly_coverage.py
06_build/candidates/crow-assembly-v1.3 --assembly 03_src/rules/assembly.yaml
--board 06_build/candidates/crow-assembly-v1.3/source/crow_recorder_central_v2.kicad_pcb
--cpl 06_build/candidates/crow-assembly-v1.3/fab/cpl.csv --bom
06_build/candidates/crow-assembly-v1.3/fab/bom.csv --manifest
06_build/candidates/crow-assembly-v1.3/MANIFEST.txt`. Stop when the candidate
passes and `HANDOFF.md` records the command and result. This is an unsealed
`06_build/candidates` reduction, never a release edit.

The sealed incident is
`archived_projects/crow-recorder-central-v2/07_releases/crow-recorder-central-v2-v1.3-2026-07-24/`
(`MANIFEST.txt`, `fab/cpl.csv`, `fab/bom.csv`, and
`source/crow_recorder_central_v2.kicad_pcb`). The fixture preserves its U1
footprint and matching fabrication rows while omitting unrelated board bytes.
