# Standalone native schematic path

This file describes the built-in renderer. For an existing reproducible flat
draft made by another local producer, use [imported tooling](imported-tooling.md)
after explicit project-contract adoption. Both routes retain native replay,
independent membership/harness and engineering acceptance; import is not a waiver.

Scope: restrictions below govern the accepted-project route. New
[exploration](../../workflow/stages/exploration.md) runs may use this builder
for unaccepted drafts before admission. Its provenance receipt is never an
engineering acceptance receipt. No old project is silently migrated.

Use only after local stage admission and explicit adoption of this route and
the project source/output contract. This is not permission to generate a held
project's schematic. Use synthetic fixtures for tool development; never invoke
historical conductors.
The separate [draft-only commission task](draft.md) permits an explicitly
authorized nonaccepted drawing before admission, but only after its project
source exception is reviewed. Use its isolated wrapper, not this raw builder.

Use one documented, source-owned circuit/layout description and a pinned native
KiCad toolchain. Generate native schematics; derive the human PDF, exported
netlist and ERC from those exact native files. Do not maintain a separately
rendered human circuit with different connectivity. Preserve readable functional
flow, pin functions, visible values and intentional NCs; a label cloud is not
human acceptance. Source may specify explicit symbol geometry and wire paths.
The optional source `paper` selects landscape A4 (default), A3 or A2; geometry
is checked against that page. A larger page does not establish readable layout
or implement hierarchical sheets. Review the actual exported PDF at useful scale.

Require a 1.27 mm grid for absolute pin ends (including NC) and all wire
vertices; symbol origins/offsets need not individually lie on that grid when
their sum does. Reject off-grid source without snapping or changing topology.
Choose label anchors deterministically from grid points on their own segment,
excluding foreign wires/pins. Reject ambiguous foreign endpoints/overlaps or
missing safe anchors; retain native netlist parity as the owning connectivity
check. All-severity ERC output is retained and hashed alongside the error-only
check; warning counts are findings, not a general ERC or engineering PASS.

The source declares exact component identities, electrical pin types, complete
pin-to-net/NC maps and expected nonempty coverage independently of the native
export. Reject duplicate references, missing pins, unknown nets, empty circuits
and unintended pin omission. Do not make all pins passive to silence ERC.
Compare native exported reference/value/footprint and pin-net sets to source,
not just counts. Record tool version and exact source/output hashes. A failed
producer, embedded error, missing output or ERC error cannot yield acceptance.

Test native generation on a small connected fixture with real ERC and netlist
export. Include negative controls for malformed/empty source, removed or changed
native connectivity, stale output/review and an electrical conflict. Rebuilding
must preserve normalized connectivity and BOM; document nondeterministic PDF
metadata separately. The builder does not issue an engineering review verdict.

For a flat design, `tools/native_schematic.py verify-complete SOURCE OUTPUT_DIR
MEMBERSHIP.json` additionally compares separately reviewed full-design membership
before native replay. Membership schema1 contains `version: 1`, nonempty `nets`,
and `components` keyed by reference, each with `value`, `footprint` and complete
`pins` list. Derive this expectation from architecture and selected-part evidence;
copying a partial generated source is not independent completeness evidence.
The returned hashes identify checked subjects, not an acceptance receipt. This
does not implement hierarchical sheets, SI or engineering/readability review;
those remain production-route prerequisites.

For multiple board designs, the developmental `tools/schematic_assembly.py ROOT
MANIFEST.json EXPECTED.json` checks separately reviewed board-instance membership
and replays each unique flat board through verify-complete. Its module docstring
defines the small manifest/expectation schema; paths are relative to ROOT.
One design may have several named instances without duplicating its CAD source.
Derive expected instances and each board's membership from accepted architecture
and parts, not from the candidate manifest. This checks declared assembly coverage
in version 1. For inter-board wiring, version 2 additionally requires a nonempty
harness in both manifest and independent expectation: each wire names two
instance/reference/pin/local-net terminals. The module docstring defines the
schema. It rejects omitted/extra/swapped wires, wrong local pin-net bindings,
NC or nonexistent terminals, and duplicate/self wires, then replays each native
board. Derive the expected harness from reviewed interface/pin evidence, not by
copying the candidate. Identical local net names on different instances do not
imply a connection. Version 1 explicitly reports no harness verification.
An independently expected external jumper may join different terminals on the
same board instance; only a wire from a terminal to itself is rejected as such.

This checks declared wiring, not physical cable construction, twisted-pair
allocation, electrical ratings, cross-board ERC, or readable engineering intent.
Those remain independently reviewed interface obligations. It does not admit a
stage. Live use requires the scoped schematic route and project contract above.

`tools/schematic_admission.py --project ROOT issue --review
08_reviews/YYYY-MM-DD-review.md` combines upstream parts_locked revalidation,
assembly/native replay and an independent exact-subject review. `check` reopens
the canonical `06_build/checkpoints/schematic_reviewed.json`. It does not change
a project's instruction binding or substitute for its independent adoption.
It currently supports non-RF flat boards only, including repeated board designs.

Its reviewed `01_docs/schematic-contract.json` has version1, project-relative
`manifest` and `expected` paths, and explicit `rf: false`; no applicability default
is inferred. Multiple instances require assembly version2/harness checks.
If capability.signal_integrity is present, this route accepts only canonical
ordinary, high_speed_digital or rf (the last is rejected as unsupported).
Unknown or noncanonical scope must be reconciled, never defaulted to non-RF.
The independent dated review uses admission's schema1, stageKICAD-SCHEMATIC and
six PASS criteria: completeness, electrical, readability, sourcing,
signal_integrity and applicability. N/A judgments belong in reviewed rationale,
not omitted criteria. Every source, membership, native artifact and build receipt
must be hash-bound and cited by the corresponding criterion enforced in the tool;
contracts, capability and parts receipt are included. Review expected design and
harness provenance, pin/part facts, power transitions, ERC warnings and actual
rendered PDFs, not only checker output. Identity strings are not authentication,
and a passing receipt cannot determine whether review prose is truthful.
The source contract and independent applicability review own RF exclusion; an
RF design must wait for its clearance route, not falsely declare itself non-RF.

Before live use in an older project, migrate its instruction/source contract
explicitly, preserving sourcing, semantic, readability and phase-stop requirements.
Changing authoring representation must not weaken those checks.
