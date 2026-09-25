# TI prototype source/schematic checker screen (independent)

**Scope:** exact private `PROTOTYPE_ONLY` source/schematic packet only. This is a
source-stage diagnostic. It does not create a board, qualify USB protection, close
a finding, or grant any P1/P2/release/order acceptance.

## Subject and method

The checked private packet is
`06_build/prototype_only/20260925T044907Z-581549/`:

| Input | SHA-256 |
| --- | --- |
| `circuit.json` | `580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d` |
| `private.net` | `a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd` |
| `private.kicad_sch` | `758e29b0d9606a6b8f123a2dca474ce62871a85e08fb2fb9024c5a7a3d04610d` |

I made an isolated temporary project view, with only its circuit JSON and netlist
substituted from that packet. Canonical generated artifacts and source files were
not modified.

Commands:

```sh
python3 skills/kicad-pcb/scripts/early_design_check.py "$VIEW"
python3 skills/kicad-pcb/scripts/electrical_invariants.py "$VIEW" \
  --netlist "$VIEW/private.net"
```

## Results

`electrical_invariants.py` passed: **E-INV OK, 60/60 invariants** against the
private netlist.

The full early-design run passed D-SPEC, E-PATH, E-SURGE, and all reported E-CAP
checks, then stopped at the first failing family:

```text
E-FAULT source circuit digest mismatch; fresh reviewed circuit required
EARLY-DESIGN FAIL: 4/5 gate families green
```

The bound digest in
`03_src/rules/power_tree.yaml` is
`f09fa9f6a396f63d35eba9dac684beda37bcc4164358598e33b825f1f6f11ba9`.
The checker’s semantic digest for this exact private circuit is
`52657c324aa736b4804bf8fdd3294bdc876551b1b042ead94cba941c6a7ca6c4`.
This is a real stale binding, rather than a temporary-view corruption:
`early_design_check.py` hashes the full circuit projection except
`source_project_metadata`.

A record-by-record comparison to the prior E-FAULT-bound circuit at commit
`80397446` found the same 569 circuit records and exactly one non-metadata delta:

| Record | Prior | Private TI packet |
| --- | --- | --- |
| `U_USB_ESD` MPN | `PESD2USB3UV-TR` | `TPD2EUSB30ADRTR` |
| JLC code | `C3704436` | `C94934` |

No source ports, nets, traces, component count, or external-source/fuse records
changed in that comparison. Thus the E-FAULT mismatch is caused by the part
identity included in its global digest; it is not evidence here of a changed
external-source/fuse topology. It also does not establish that the TI protection
selection is electrically qualified.

`pin_map_check.py` was not run. Its CLI requires `--board`; no native board belongs
to this private source/schematic packet. Supplying the canonical board would mix
subjects and exceed this source-only diagnostic scope. This is **not** a pin-map
pass or failure.

## Disposition

Keep the packet `PROTOTYPE_ONLY`. The binding refresh and full E-FAULT rerun
described in the addendum below update circuit identity only; independent USB
transient/protection evidence remains required for release qualification.

## Addendum — reviewed E-FAULT binding refresh

On review, `03_src/rules/power_tree.yaml` was changed in exactly one field:
`external_source_fuse.circuit_semantic_sha256` now binds the exact private TI
semantic digest
`52657c324aa736b4804bf8fdd3294bdc876551b1b042ead94cba941c6a7ca6c4`.
The external-source limits, bound references, and all USB transient selection
finding state remain unchanged.

Re-running the same full command against the isolated TI packet after this refresh
returned:

```text
PASS E-FAULT CONDITIONAL external source/fuse: peak<=3.4 A,
cumulative >2.85 A<=10 ms, persistent<=2.85 A; PFET steady/peak=120.0/141.1 C;
nominal fuse I²t comparison=0.1156/3.152 A²s (not nonopening proof); supplier
and first-article proof owed
EARLY-DESIGN PASS: 5/5 gate families green
```

This is an E-FAULT binding/check result for the private source/schematic subject.
It preserves the stated conditional limits and owed evidence, and does not promote
a canonical generated artifact or qualify the USB ESD transient behavior.
