# Crow TI schematic-only prototype adoption — 2026-09-25

The guarded `03_src/adopt_prototype_schematic.py` transaction copied the exact
previously reviewed private TI bundle into four canonical **schematic-stage**
paths. Its [receipt](adoption_receipt.json) binds the source bundle, before/after
hashes, E-FAULT/P-PREC/ERC staged checks and private backup. The ignored
[native netlist](native_netlist.net) is retained here for review; the tracked
`03_tscircuit/build/circuit.json`, `03_tscircuit/build/schematic.pdf` and
`04_kicad/crow_carrier.kicad_sch` are the other three outputs.

The exact after-hashes are circuit `580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d`,
PDF `d2e54c1195a217b231fbc2ab058e051b01dc8e45b534c65d38006978af386eed`,
native schematic `758e29b0d9606a6b8f123a2dca474ce62871a85e08fb2fb9024c5a7a3d04610d`,
and netlist `a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd`.
The private [producer receipt](private_bundle_receipt.json) retains 21 input
and four artifact hashes. The two earlier dirty generated Nexperia 5UX files
were backed up byte-for-byte in the ignored private prototype tree; their
[hash manifest](preserved_dirty_manifest.json) is retained here. The adoption
transaction separately backed up all four previous canonical destinations.

This is `PROTOTYPE_ONLY` and `SCHEMATIC_ONLY`. The original pause manifest and
ordinary schematic checkpoint were not refreshed. The pinned reuse schematic,
PCB, route and release outputs were not promoted. Native E-FAULT and P-PREC
now pass against the TI circuit (`69/69` IC applications); ordinary critical
selection still exits 1 because XU316 powered/rail-off transient coordination
is open. New hash-bound canonical topology/render review is still required
before schematic-stage promotion by an ordinary conductor. No PCB, fabrication,
assembly or electrical survival claim follows from this receipt.
