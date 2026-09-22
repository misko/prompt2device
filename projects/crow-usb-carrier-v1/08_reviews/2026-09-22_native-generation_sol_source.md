# Independent review — native source conversion repair

Date: 2026-09-22

Candidate: `909f03463ab4088fb8dbf633c3208b2a681b770a`

Verdict: **ACCEPT** for source-to-native-schematic admission. This does not accept PCB placement/routing, ERC, or a physical board.

## Findings

No blocking defect remains in the reviewed delta.

- The source change declares the 40 already-authored page identities without changing the three Presented electrical domains or their connections. `rebuild_all.sh` now requests `--disable-pcb`, which is appropriate for this source/native-schematic stage; the comparison using `--routing-disabled` produced a real `pcb_packing_error` and is not admissible evidence.
- The converter fallback only runs where both `pin_number` and authoritative PCB pad identity are absent. Existing PCB-pad identity retains precedence. Fallback groups reject missing members, foreign ownership, multiple numbered parents, conflicting nets, ambiguous numeric hints, and conflicting repeated aliases.
- The exact Crow input has only three pinless ports. All three are J_USB split shield ports on the same component, carry the unique `pin17`/`17` hints, and are governed by the declared internal connection group with numbered parent 17.
- An independent overlapping-group probe assigned one unresolved port to parent pins 1 and 3. Conversion failed closed (`does not uniquely alias parent pin 3`) before an alias could be overwritten. This confirms the repeated-group case cannot silently select a parent.

## Evidence

- `python3 tests/t1_converter.py`: 63 passed, 0 failed; 22 known-bad controls failed as required.
- Fresh exact-commit producer receipt: exit 0 in 48.8261 s; 493 source components, 493 schematic components, 1,627 source ports, 1,498 source traces, 40 distinct schematic sheets, and zero `*_error` records.
- Preserved producer input: `/tmp/crow-native-909f0346-proof/circuit.json`, SHA-256 `2efeaebb429df079d905c6c55acb2f4e10b3ebc9d411124acd98ce588064095e`.
- Preserved producer log: `/tmp/crow-native-909f0346-proof/producer.log`, SHA-256 `9380314c55f6056d3ecd4b776b21198864b42ff3725cbbbaee0509d8ec1ea6ee`.
- The exact input converted successfully: 493/493 components received FPIDs, with 1,624 pins, 1,959 wires, 751 labels plus 16 safety labels, and 157 junctions. KiCad netlist export completed.

## Boundary

KiCad reported annotation warnings during netlist export. This review does not treat the successful conversion as ERC or native schematic acceptance; those warnings belong to the next native gate and must be resolved or explicitly adjudicated there. The change also intentionally emits no PCB geometry, so it grants no placement, routing, DRC, fabrication, or physical-first-article claim.
