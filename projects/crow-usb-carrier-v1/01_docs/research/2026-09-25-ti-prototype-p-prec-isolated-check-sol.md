# TI prototype packet P-PREC check (2026-09-25 UTC)

The private packet at `06_build/prototype_only/20260925T044907Z-581549/`
declares `PROTOTYPE_ONLY`. Its `receipt.json` SHA-256 is
`5cccaaa7b577a9ad07b647e77a7759ce203e81d8e6efd35a3fa55e7a9ab5cd42`;
the receipt binds `circuit.json` to
`580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d`
and the native `crow_carrier.net` to
`a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd`.

I ran `skills/kicad-pcb/scripts/ic_reference_check.py VIEW
--require-semantic-review --json VIEW/report.json` in an auto-removed temporary
project view. The view copied the current P-PREC source/rules, dossiers and
bound primary records, existing independent semantic receipt, and private TI
packet circuit/netlist into the checker-expected paths. No canonical generated
file was overwritten. Result: exit 0, `COVERAGE_PASS`, 69 selected ICs,
69 applications, 69 research-covered, `semantic=APPROVED`, and zero coverage
or semantic findings. The computed packet SHA-256
`a1878ac742bc0e03e674fb488ebba1428d5cffb0c0206f26ad56f80ef8a185ba`
and subject SHA-256
`a8b79bc9ecd6f572ba531402abb4c841989b3dd8917333962aed6743197ec387`
match `08_reviews/ic_reference_semantic_review.yaml` exactly. Its 69
`reviewed_refs` also match the selected census. The source bindings are
stackup `fe02435edc94729cf0d3fa88b4c15c80eda76a7720ad2ed9fafd21619e999fb2`
and route rules `40463f44d280306fcd611d7c59c2ee37aef31cb12d42f4a7b95069c9dae6b893`.

The direct canonical check still exits 2: its stale generated 5UX
`03_tscircuit/build/circuit.json` and `06_build/netlists/crow_carrier.net`
select 5UX, so the authored TI `TPD2EUSB30ADRTR` row has no selected IC and
the semantic subject digest differs. This is an artifact-coherence mismatch,
not a TI P-PREC packet or semantic-review defect. No P-PREC source rebind is
needed for the private TI packet. This check grants no canonical artifact
promotion, P1/layout acceptance, ESD qualification, release, or order claim.
