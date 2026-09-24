# P-PREC source rebind audit, 2026-09-24

Status: **INCOMPLETE**. This note is source-diff evidence, not an independent
semantic review receipt or native-layout acceptance. The IC packet and its
receipt remain stale until the fresh project netlist and independent review
are admitted.

An isolated `tsci build --disable-pcb src/crow_carrier.tsx` used the committed
TSX source and existing frozen node modules without modifying the project
artifacts. Old and fresh `circuit.json` contain 10,551 rows each; the parsed
JSON differs in one row only,
`source_project_metadata.source_filesystem_md5_hash`. All 569
`source_component`, 1,790 `source_port`, 1,641 `source_trace`, 282
`source_net`, and schematic rows are identical. Global file SHA-256 changed
from `1f01be73e0699cd62bc734aa189b25e9d66f1097b5ce6f52a8db30533ecc6448`
to `580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d`.
P-PREC's `circuit_sha256` is an instance digest of MPN, native footprint,
value, and pad/net tuples, not this global file SHA.

The fresh JSON was converted to a native schematic with the current
`02_parts` dossiers and the explicit 18 `net_aliases.txt` aliases, then
exported with `kicad-cli sch export netlist`. Compared with the saved source
netlist, both exports contain the same 569 reference designators, 1,787
pad-to-net tuples, and 428 net names. Exactly ten component tuples change:
`U_ESD1..U_ESD8`, `U_USB_CC_ESD`, and `U_USB_VBUS_ESD` move from
`Package_TO_SOT_SMD:SOT-553` to
`crow_usb_analog:TI_DRL0005A_TPD2E2U06`; their values stay unchanged. No
other instance changes footprint, value, or pad/net identity. The exact
TI DRL land source and 0.67 × 0.30 mm, 0.50 mm-pitch geometry are recorded
in the adjacent internal-clearance/ESD-footprint research note and part
dossier; independent review of that applicability remains required.

All 69 saved application bindings carry old route-rule digest
`a7d63c15f09a043564a30f939b4500016e584f6c9df9465e13624c14f1b0c30f`.
The route field bound by P-PREC changed only in
`route.common.fab_overrides`, from the repo-root-qualified
`projects/crow-usb-carrier-v1/03_src/rules/route_fab_overrides.txt` to the
project-relative `03_src/rules/route_fab_overrides.txt`. The former exists
from the repo root but not the project working directory; the latter
resolves there to the same intended file, SHA-256
`d8285ec77a25583b21afa136de614faa4257008250f370e2b5d08d359ef6a1d9`.
This is an executable path correction and must receive explicit grouped
review, even though route widths, clearances, layers, and wave parameters
are unchanged in the bound route fields. Other route edits are under
`prep`, outside the P-PREC source digest and outside this review claim.

Checker commit `d5031a50` adds `same_footprint_pad_clearances` to the
route-rule digest. The current digest is
`40463f44d280306fcd611d7c59c2ee37aef31cb12d42f4a7b95069c9dae6b893`.
Its nine exact source references (`U_XU` and `U_ISO1..U_ISO8`), 0.15 mm
same-footprint SMD-pad exception, manufacturer/process evidence, and native
rule behavior need independent semantic review before rebinding the 69
applications. The checker regression proves that adding or changing this
field stales every prior application binding.

Acceptance sequence after the project-owned native rebuild and rule gate
repair:

1. From the repo root, run
   `python3 skills/kicad-pcb/scripts/ic_reference_check.py projects/crow-usb-carrier-v1 --print-bindings`.
   Require 69 instances and zero source-selection findings. Compare each
   instance with the saved packet: 59 circuit digests must remain exact,
   exactly the ten named ESD digests may change, and the stackup digest must
   remain `fe02435edc94729cf0d3fa88b4c15c80eda76a7720ad2ed9fafd21619e999fb2`.
2. Reconfirm the fresh project native netlist has the same 569 component
   references, 1,787 pad/net tuples, and 428 nets, with only the ten named
   FPID changes. Confirm the exact native footprint pad numbers, land sizes,
   and pin/net map against the TI DRL source and dossier.
3. Have an independent reviewer admit the ten exact-package applications,
   grouped route-path correction, and nine-ref rule exception. Update only
   source-backed packet fields; preserve all unchanged instance digests.
   Recompute packet SHA, subject digest, and evidence SHA in a new independent
   semantic receipt covering exactly all 69 references.
4. Run `python3 skills/kicad-pcb/scripts/ic_reference_check.py projects/crow-usb-carrier-v1 --require-semantic-review`.
   Require `COVERAGE_PASS` and `semantic=APPROVED`. This still does not
   establish P1 placement, physical capacity, routing, or release acceptance.
