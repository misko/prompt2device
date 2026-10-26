# `KICAD-SCHEMATIC` — non-RF flat-board contract

This is the acceptance route. [Exploration](exploration.md) permits native drafts
earlier; reuse them after explicit contract adoption. Draft creation does not
satisfy any acceptance prerequisite below.
Common passive exact identities are resolved in the final BOM/sourcing check
after schematic development, before this acceptance route. Generic draft
positions do not require an early inventory check; electrical requirements do.

This local route supports non-RF flat boards, including repeated instances with
declared harnesses. Live execution requires explicit project adoption of these
instructions and the source/output contract below. Historical graph owners and
legacy generate/review/repair procedures are not executable fallbacks. RF and
hierarchical sheets remain unsupported; do not flatten away requirements.

## Boundary

`KICAD-SCHEMATIC` is always selected. It requires accepted `parts_locked` and,
when RF applies, `rf_source_clearance`; an omitted RF stage is not an
engineering N/A verdict. Its output role is `schematic_reviewed`, which blocks
placement. The graph's `parts_semantic`, `rules_semantic` and `source_semantic`
invalidation keys reopen this stage when relevant inputs change. High-speed
digital requires timing, loading and return-path review inside the stage;
it does not select RF by itself or authorize unavailable legacy instructions.

Before generation, reopen the commissioned brief, architecture/interfaces,
selected exact parts and source-derived facts, project capability profile,
owning contracts and current accepted identities. Resolve a failed sourcing
or RF prerequisite with its owner, not by declaring it satisfied here. Preserve
datasheet identity, revision and cited figure/page for critical part/pin facts.

## Required outputs and acceptance

The project contract adopts source-owned circuit authoring and complete design
expectations. The declaration fixes manifest/expected locations; actual board
source/output paths are authored in that manifest and hash-bound by schematic
review, not pre-bound by sourcing. Coordinator assignments name allowed writes.
Produce editable native KiCad
schematics, exported netlist and human PDF from those exact native files, plus
reopenable producer/check evidence. Follow only the adopted
[native](../../procedures/schematic/native-tooling.md) or
[imported](../../procedures/schematic/imported-tooling.md) producer manual; do not maintain
a second human drawing with different connectivity. A single-channel fixture
does not establish full-board coverage. Include every repeated channel, supply,
connector and required support circuit; multi-sheet projects require verified
cross-sheet connectivity and complete export membership.
For repeated or separate boards, check instance membership and declared harness
terminals against independently derived interface expectations as well as each
board's native netlist. A per-board PASS does not prove the cable connections.

The owning checks must establish nonzero expected component/net coverage,
source and part-value identity, producer diagnostics without embedded errors,
freshness, source/native-netlist parity, net-label survival, ERC with zero errors
and retained all-severity results (warnings reasoned), electrical/semantic closure, sourcing
and applicable SI/RF requirements. An independent reviewer checks the exact
candidate's topology and readable rendering. The schematic must communicate
power entry/protection/regulation and primary signal flow, visible pin order,
polarity, decoupling ownership, intentional NCs and unambiguous sheets. A
machine-correct label cloud is not a reviewed human document.

Only an adopted exact-subject independent review plus all applicable owning
checks can support `schematic_reviewed`. Generation alone, self-review,
zero-denominator checks, an optional diagnostic, a timed-out reviewer, or a
stale receipt cannot. A failed or incomplete candidate leaves earlier accepted
artifacts intact and enters diagnosis. The user-requested schematic reflection
checkpoint follows acceptance; it precedes any placement work.

## Execute

1. Revalidate upstream admission receipts and current selected-part evidence.
   Before sourcing acceptance, adopt `01_docs/schematic-contract.json` (version 1,
   manifest and expected project-relative JSON paths, explicit `rf: false`; version 2
   additionally declares allowed producers for [imported drafts](../../procedures/schematic/imported-tooling.md)) and cover
   it plus contracts.md and capability-profile.json in sourcing's independent
   assembly review. At STATUS
   schematic, prepare `python3 tools/task.py --project ROOT --task schematic-design`.
   Declare writer/reviewer, finite budget and exact writes in the existing journal.
   The packet binds prerequisites; it neither writes CAD nor automatically
   enforces permissions, budgets or stage acceptance.
2. Build from declared source; export PDF/netlist/ERC; verify exact identity,
   coverage, connectivity and freshness against that source.
   Derive board membership and expected assembly/harness independently from
   accepted design/part evidence. Use the built-in native source/builder or the
   explicitly adopted imported producer; retain the selected draft's circuit.
   Run the chosen producer's build/verify for each unique board, then
   `tools/schematic_assembly.py ROOT MANIFEST EXPECTED`. For repairs, include
   existing candidate sources/expectations as explicit packet inputs.
3. Independently review electrical meaning and rendered readability on exact
   output hashes, including requirements not expressible by ERC.
4. Issue a schematic acceptance receipt only when both mechanical checks and
   independent engineering review pass; bind upstream receipts, source, outputs,
   toolchain and review. Reopening any changed dependency invalidates it.
   Run `python3 tools/schematic_admission.py --project ROOT issue --review REVIEW`,
   then the same tool with `check`. Preserve an old receipt before replacement.
5. Record the user's schematic reflection stop before placement.

Keep the orchestrator's repair/backtrack/escalation loop, rather than adding a
schematic-specific scheduler. A failed producer or review cannot create a pass;
repair source or the earliest causal upstream decision and reverify affected
outputs. Missing production capability goes to migration, not a hold deletion.

Validation evidence lives in the native/import/assembly/admission/task tests.
These establish scoped mechanical behavior on synthetic and named project fixtures,
not electrical correctness or readability of a new board. Independent review
of the actual complete source and rendered PDF remains mandatory. There is no
autonomous stage scheduler or proof that a model obeyed its task budget.
