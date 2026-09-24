# Independent P-PREC rebind admissibility review, 2026-09-24

Reviewer: `terra-p-prec-independent-review`  
Status: **conditional admission only**. This records whether a source IC
reference packet may be rebound. It is not a P1, layout, fabrication,
assembly, or release acceptance.

## Reproducible fresh source evidence

The controlled combined-source rebuild is retained at
`/tmp/crow-combined-esd-intrinsic.DwOD9o`. Its source circuit is
`03_tscircuit/build/circuit.json`, SHA-256
`70c661c18911503e7225bf0b28e7af5e36a935ad701f7b454064bdf570cab5d7`,
and its native source-declared netlist is
`06_build/netlists/crow_carrier.net`, SHA-256
`b0dcd4b47e407b8e23dc128e9dd681b5963fb62879db6c5c6fd66ad4e390ec9c`.
The derived schematic and board have SHA-256
`d1df95efcacad003ce586320326d97d1a59d12776686b9632a5f9f9577576e51`
and `d54dad46ea0d38942d38224fcb6b8b6d6d74799869e88d47653700a637d0c16e`.

It was reconstructed from the committed TSX source using `tsci build
--disable-pcb src/crow_carrier.tsx`, then the project converter, KiCad native
schematic netlist export, generic board/rule generation, and the existing
TMUX POFV generator. `count_parity.py` reports 569/569 components across
board, circuit, schematic, manifest, and netlist; model coverage is 569/569.
The combined DRC report has zero violations and 499 unconnected items. The
latter prevents any layout-stage acceptance; it does not invalidate the
limited source identity comparison here.

Running `ic_reference_check.selected_components()` against that fresh circuit
and netlist selects 69 instances with zero findings. Comparing those instance
digests to the 69 saved packet rows gives 59 exact matches. The only ten
changed digests are `U_ESD1..U_ESD8`, `U_USB_CC_ESD`, and
`U_USB_VBUS_ESD`, each changing from `Package_TO_SOT_SMD:SOT-553` to the
committed `crow_usb_analog:TI_DRL0005A_TPD2E2U06`. Their values and pad/net
tuples are unchanged. This is the bounded package/land-pattern review scope.

## Route-rule binding review

The saved packet binding is
`a7d63c15f09a043564a30f939b4500016e584f6c9df9465e13624c14f1b0c30f`.
Recomputing the checker input establishes three distinct states:

| Bound source state | Route-rule SHA-256 |
| --- | --- |
| Legacy repo-root-qualified `fab_overrides` path, without fine-pad field | `a7d63c15f09a043564a30f939b4500016e584f6c9df9465e13624c14f1b0c30f` |
| Current project-relative path, without fine-pad field | `c597d82f217d2550f30506836a0d76fe9e468609b7e8c7e146831bcf12945845` |
| Current project-relative path and `same_footprint_pad_clearances` | `40463f44d280306fcd611d7c59c2ee37aef31cb12d42f4a7b95069c9dae6b893` |

The current `03_src/rules/route_fab_overrides.txt` resolves from the project
directory and has SHA-256
`d8285ec77a25583b21afa136de614faa4257008250f370e2b5d08d359ef6a1d9`.
The former root-qualified spelling was changed in `054f9c20`; it resolves
only from the repository root. The route-path correction preserves the file
content but is still an executable source correction requiring review.

Checker change `d5031a50` deliberately binds the new
`same_footprint_pad_clearances` source field. It covers precisely `U_XU` and
`U_ISO1..U_ISO8`, only same-footprint SMD pad pairs, at 0.15 mm. Therefore a
rebind is **not** admissible as a mere path normalization: all 69 rows must
also be reviewed against this new exact routing constraint.

The fresh controlled source binding is stackup
`fe02435edc94729cf0d3fa88b4c15c80eda76a7720ad2ed9fafd21619e999fb2`,
route rules `40463f44d280306fcd611d7c59c2ee37aef31cb12d42f4a7b95069c9dae6b893`,
and subject `a8b79bc9ecd6f572ba531402abb4c841989b3dd8917333962aed6743197ec387`.

## Admission decision

A packet editor may update all 69 `reviewed_for` records only after deriving
them from the fresh controlled circuit/netlist and preserving the 59 matching
instance digests. The ten named ESD rows may receive only their fresh exact
footprint/package circuit digests. The editor must bind every row to the
current stackup and `40463…` route digest.

After that edit, this reviewer must inspect the exact packet bytes and create
a new independent semantic receipt that names all 69 references, binds the
new packet and subject hashes, and cites this note at the `Admission decision`
locator. `ic_reference_check.py --require-semantic-review` must then pass.
No receipt may claim the 0.15 mm source exception proves order/CAM/assembly
capability, clears the 499 opens, or accepts P1/P2/P3/P4 work.
