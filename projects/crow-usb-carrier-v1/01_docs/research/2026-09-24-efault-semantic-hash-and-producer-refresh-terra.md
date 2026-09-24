# Independent E-FAULT semantic-hash and producer refresh review, 2026-09-24

Status: **source evidence only**. The semantic binding remains conditional on
the declared supplier and first-article qualification; this review does not
accept a PCB, routing, P1, fabrication, or assembly outcome.

## E-FAULT binding review

Commit `71bf5894` replaces the raw generated-file hash with a fail-closed
semantic digest. `circuit_semantic_sha256()` accepts only a nonempty list of
object rows containing exactly one metadata object with exactly these two
fields: `type: source_project_metadata` and a lowercase 32-hex
`source_filesystem_md5_hash`. It removes only that row, preserves every other
row and row order, serializes canonical finite JSON, and hashes it. It rejects
a missing, duplicate, expanded, or malformed metadata row, non-object rows,
nonfinite JSON, and the legacy `circuit_sha256` field.

The focused `python3 -m unittest tests.test_external_source_fault -v` suite
passes 24/24. Changing only the metadata path fingerprint and JSON whitespace
passes; changing `R_QIN_G` resistance fails the semantic digest; and a
deliberately rebound circuit with `F_IN.2` on `GND` still fails the exact
`N12V_FUSED` topology assertion. The full `early_design_check.py` also passes
E-FAULT while retaining its explicit conditional/first-article-owed result.

## Canonical producer refresh

The locked local producer was invoked as `tsci build --disable-pcb
src/crow_carrier.tsx`; no PCB producer was invoked. Its output was copied to
the canonical circuit bridge and passed `circuit_json_diagnostics.py` with
zero embedded errors and 1,821 advisory warnings. The current canonical
`03_tscircuit/build/circuit.json` SHA-256 is
`70c661c18911503e7225bf0b28e7af5e36a935ad701f7b454064bdf570cab5d7`.
Its tracked diff is only `source_project_metadata.source_filesystem_md5_hash`;
the E-FAULT semantic digest remains
`52657c324aa736b4804bf8fdd3294bdc876551b1b042ead94cba941c6a7ca6c4`.

A fresh converter trial changed 7,754 schematic lines through UUID/date and
presentation churn, so it was rejected. The existing de176cad-pinned
schematic was restored unchanged, SHA-256
`2d5f02da91e745f0a4732f75e6092f053c87488ca3a16711caa752e693985997`.
The native netlist was then exported from that pinned file; its SHA-256 is
`e7ef7dbd752b9431ade0933ca77ee998963bfe3871c3caf65cddc56442f1371d`.
It has 569 components, 1,787 pad-to-net tuples, and 428 nets, including the
exact ten TI DRL ESD FPIDs: `U_ESD1..U_ESD8`, `U_USB_CC_ESD`, and
`U_USB_VBUS_ESD`.

`ic_reference_check.py --print-bindings` now selects 69 instances with zero
findings. Its stack digest is
`fe02435edc94729cf0d3fa88b4c15c80eda76a7720ad2ed9fafd21619e999fb2`,
route digest is
`40463f44d280306fcd611d7c59c2ee37aef31cb12d42f4a7b95069c9dae6b893`,
and source subject digest is
`a8b79bc9ecd6f572ba531402abb4c841989b3dd8917333962aed6743197ec387`.
This satisfies the producer prerequisite for the separately controlled all-69
P-PREC packet refresh; that refresh and its independent receipt remain
separate work.
