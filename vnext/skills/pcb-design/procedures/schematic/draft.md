# Commission schematic draft — explicitly nonaccepted

This is the `schematic-draft` commission task, not the KICAD-SCHEMATIC stage.
Only use it when the user authorizes draft design reasoning and the project
source contract explicitly permits it. Commission holds and earlier exhausted
repair budgets remain in force; a changed drawing format resets neither.
Read the project source/build contracts and project binding before live use.
Before that migration/review, use isolated synthetic projects only.

One bounded writer produces one channel on one native sheet. An independent
reviewer checks exact source, native PDF and limitations. Log attempts/reviews
in the existing commission journal; no new progress ledger. A technical export
PASS means only that this candidate was drawn consistently and passed the
selected ERC checks, never that its circuit or sourcing was approved.

## Source and commands

Track the proposed source at `03_src/drafts/<candidate>.json`. Generated output
goes only to a fresh `06_build/drafts/<attempt>/` directory; preserve failures
and choose a new attempt name. Never write canonical `04_kicad`, release files,
accepted source, STATUS, hold, admission certificate or stage completion here.
The wrapper rejects traversal, symlinked draft paths and existing output dirs.

Envelope fields (all required; no extras):

- `schema`: 2 for new attempts; `status`: `DRAFT / NOT ACCEPTED / DO NOT ORDER`.
- `inputs`: project-relative path → current SHA256, including every
  `tools/task.py` required input **except** `01_docs/STATUS.md` and
  `01_docs/journal/commission.md`, plus `03_src/contracts.md`,
  `06_build/contracts.md`, and all reports/datasheets/decisions actually used.
  Brief, hold, source contracts, capability and decisions remain freshness inputs.
  Authoritative decisions must be in BRIEF or a bound decision/report file, not
  solely in the operational journal. Schema 2 rejects operational paths in inputs.
- `components_evidence`: every circuit reference → `{identity, pinmap, notes}`.
  Grades are `CITED`, `CANDIDATE`, or `UNKNOWN`; notes explain the source and
  limitations. CITED is not approved. Candidate MPNs are not sourcing freezes.
- `circuit`: the existing `native_schematic.py` version-1 schema. Preserve all
  known pins and explicit NCs; missing known pins are an error, not a waiver.
  Unknown pin assignments must be explicitly hypothetical in evidence notes.
  Use `UNQUALIFIED` for unknown footprint rather than fabricating a package.
  Logical interface ports are not physical parts: identify them as such in
  value and evidence notes, with `UNKNOWN` identity/pinmap and `UNQUALIFIED`
  footprint. Do not invent an MPN, connector, or dossier approval for a boundary.
  Independent review must explicitly check this logical/physical distinction
  and its grades. The version-1 schema does not type boundary ports separately;
  the wrapper does not prove these semantic declarations are truthful.

Reserve the top 40 mm for draft status and complete source hash. Use readable
left-to-right flow, named functions and values; inspect the actual PDF. This
tool is deliberately limited to the existing explicit geometry and single sheet.
All absolute pin ends (including NCs) and wire vertices must be on the 1.27 mm
connection grid. Nothing is snapped or rerouted automatically. Label anchors
are deterministic grid points on their own wire, excluding other-net wires/pins;
ambiguous endpoints/overlaps or unrepresentable labels fail before export.

```sh
python3 tools/task.py --project /absolute/project --task schematic-draft --input 03_src/drafts/channel-a.json
python3 tools/draft_schematic.py build --project /absolute/project --source 03_src/drafts/channel-a.json --out 06_build/drafts/channel-a-01
python3 tools/draft_schematic.py verify --project /absolute/project --source 03_src/drafts/channel-a.json --out 06_build/drafts/channel-a-01
```

Native KiCad 10.0.4 generates the PDF/netlist/ERC from the exact schematic;
verification repeats exports and compares parity/rendered pages. Receipts bind
source/input/instruction/tool hashes and explicitly deny engineering acceptance
and manufacturing pass. Unknown facts remain unknown after a passing export.
ERC errors stop the build; partial outputs have no draft success receipt.
`native-erc-all.json` retains every severity, with counts in the native receipt;
absence of errors does not waive warnings or establish engineering acceptance.
Changing source/inputs makes a previous receipt stale. Receipts are provenance,
not tamper-proof signatures. No admission command is part of this task.

Schema 2 captures the dispatch packet once in `dispatch-context.json` and binds
its bytes in the receipt; subsequent STATUS/journal logging does not invalidate
semantic freshness. Verification still requires a valid current commission
STATUS (working/blocked); this is not historical verification after promotion.
Instructions, workflow graph, source, semantic inputs and tool hashes remain
freshness-bound. Schema 1 retains its original strict STATUS/journal binding.
Migration requires an explicitly new schema-2 source and fresh attempt, never
rewriting an old receipt or refreshing an independent approval. Updated tools
and instructions stale old receipts; historical attempts stay historical.

## Minimal live-project migration prerequisite

The project owner must explicitly add an exception to `03_src/contracts.md`
permitting tracked, noncanonical schema-2 draft envelopes containing version-1
circuit JSON under `03_src/drafts/`,
and define that namespace's draft-only contract (including any local contract
file in `inputs`). `06_build` must permit generated draft attempts. Preserve
the existing canonical source policy, hold and acceptance obligations. Review
that small exception and this tool independently before live use. This vNext
procedure does not itself change any project's contracts or grant admission.
