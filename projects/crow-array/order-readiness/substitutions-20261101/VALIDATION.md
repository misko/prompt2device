# r6 validation and execution record

2026-11-01 UTC / 2026-10-31 PDT. User authorized inventory resolution and part
replacement, not purchases. Working branch `codex/crow-stock-substitutions-20261101`
starts from shared `816cc57e`; the older dirty worktree was left untouched.

Execution: find-substitute-part → bounded local part recheck → independent SOL
6.1 high capacitor/ADC/remaining-source reviews → adopt four exact identities →
metadata-only native and quote generation → KiCad/netlist checks → independent
integration review. No architecture, placement or routing backtrack was needed.
The 60 V PTC and different regulator were not adopted; exact stocked originals
avoid reopening fault-current and startup engineering. No phase admission or
release certificate was issued or copied into the derivative.

## Completed checks

| Check | Result |
|---|---|
| Independent capacitor review | PASS for the three specific existing circuit roles |
| Independent ADC review | PASS, packaging-only identity change |
| Independent integration review | PASS for exact r6 manifest below |
| Generator replay | PASS; 94 files including manifest |
| Project substitution regression tests | 9 passed; identity/reference guards, library+instance edits, malformed input, quantities/routes, real replay, refusal to overwrite and tampered ADC rejection |
| Native change proof | Byte-exact reversal of only allowed MPN/Manufacturer/Value strings in six files |
| Native netlist comparison | Unchanged connectivity for both boards |
| Schematic/PCB/BOM identity | PASS; carrier C1/C2/C11/C21/U1/U2, pod C1/C3 updated |
| BOM/CPL coverage | 137 factory placements/carrier and 29/pod; no omitted required parts |
| Batch population | 478 SMT + 28 THT + 18 home = 524; 38 distinct procurement identities |
| ERC | Zero reported violations on each board, inherited project rule settings unchanged |
| DRC | Zero violations and zero unconnected items on each board; errors/warnings/exclusions included, no ignored DRC checks |
| Gerbers and CPLs | Byte-identical to r5; no physical-layout or routing change |
| Frozen release | All 256 payload files preserved; full file census restored and verified |

ERC retains four historical disabled checks: single global label, four-way
junction, SPICE model and footprint filter. This run did not add waivers or
claim those four checks ran. Raw JSON reports retain the settings. DRC was not
run with `--schematic-parity`; separate native export comparison and actual
PCB identity checks establish the stated local parity scope. Physical hardware,
firmware execution, transient behavior and factory processes were not tested.

Final package manifest SHA-256:
`c01cb5e90b31738b6afd0102aca1b22ae3322c1e82f17fbe5492c8f198f19099`.
See [native-validation.json](validation/native-validation.json) for exact source
and result hashes and [integration-review.md](integration-review.md) for the
independent verdict. The schematic PDFs are [carrier](validation/carrier-schematic.pdf)
and [pod](validation/pod-schematic.pdf).

## Reproduce local checks

From repository root, with Python 3 and KiCad 10.0.4:

```sh
python3 projects/crow-array/order-readiness/substitute_quote.py verify projects/crow-array/order-readiness/substitutions-20261101/adopted-changes.json projects/crow-array/order-readiness/quote-draft/r6-2c8p-substitutions
python3 -B -m unittest discover -s projects/crow-array/order-readiness -p test_substitute_quote.py
/usr/bin/python3 projects/crow-array/order-readiness/substitutions-20261101/validate_native.py
python3 projects/crow-array/publication.py verify
```

`validate_native.py` verifies the retained exports; it does not itself rerun
KiCad. To refresh those exports, copy the baseline schematic resource folder
and revised `native/` folder into a fresh `mktemp -d` scratch directory. For
each board, run these commands against the COPIES, with distinct new outputs:

```sh
kicad-cli sch export netlist --format kicadxml -o before.xml BASELINE_COPY.kicad_sch
kicad-cli sch export netlist --format kicadxml -o after.xml REVISED_COPY.kicad_sch
kicad-cli sch erc --severity-all --format json --exit-code-violations -o erc.json REVISED_COPY.kicad_sch
kicad-cli sch export pdf -o schematic.pdf REVISED_COPY.kicad_sch
kicad-cli pcb drc --severity-all --format json --exit-code-violations -o drc.json REVISED_COPY.kicad_pcb
```

Keep earlier validation records before adopting refreshed reports. Use copies
because KiCad netlist/PDF export may write local `.kicad_prl` preferences beside
its input even when no design edit is requested. This happened during the first
check: publication verification rejected two extra preference files. They were
moved intact to `validation/tool-side-effects/`; no accepted source byte was
changed. The r6 generator now rejects extra/missing release inputs, and the
final package excludes these runtime files. Earlier generated drafts were
preserved in temporary folders, not silently overwritten.

The first native validation helper used an unavailable pcbnew `GetProperty`
method; it was corrected to KiCad 10's `GetFieldText` and rerun successfully.
Three existing pcbnew property-enum messages and duplicate-image-handler debug
messages appeared on this host; the CLI checks and native readback completed.
These are recorded implementation/tool issues, not hidden circuit waivers.

## Evidence and remaining limits

Independent reviews, dated public stock JSON, exact manufacturer references and
curve calculations are retained here. Raw manufacturer research PDF/archive
files are local supporting evidence, not part of the upload package or a grant
of redistribution rights. A future publication pass must preserve/reconcile
their provenance and redistribution policy; none has been pushed in this run.

This pass resolves the seven known shortages at the design/external-source-plan
level, not allocation. It does not refresh every unchanged BOM offer or establish
all 38 parts in JLC-owned stock. Four substitutions use exact public InStock pages
with primary counts unknown; three originals have adequate dated distributor
offers. Factory gross quantities, source pooling, fees, dates, previews, stack,
rails, stencil and controlled assembly remain open as listed in HANDOFF.md.
No account action, vendor message, purchase, reservation or production approval.
