# Standalone release-review pilot

Read the release-review stage. This local pilot covers imported flat non-RF
prototype PCB design packages, not ordering or functional qualification. It
preserves the accepted chain and exact historical toolchain; no upstream receipt
or library is refreshed to make replay pass. Linux Landlock ABI >=3 and libseccomp
are required for isolated replay; unsupported isolation fails without fallback.

## Version selection

New registered-3D releases use version2 of the contract and source manifest.
Version1 below remains a historical replay path; it does not meet the upgraded
deliverables. Adopt a new authority and current assembly receipt explicitly.
Preserve previous contracts/receipts and sealed archives before replacing live
project selections. The version2 implementation is a pilot until actual complete
archive replay and independent review pass; component tests do not promote it.

Version2 adds two manifest fields: `runtime` (project-relative capsule directory)
and `calculations` (each board maps to nonempty retained derivation paths).
It consumes accepted assembly version2, derives model/reference/limitation and
STEP/view/detail coverage, and indexes coherent native entrypoints/resources.
The CSV check reads UTF-8 bytes, quoting, exact identities and population against
accepted mapping; empty factory BOM/CPL are valid only for an empty factory scope.
Calculations require substantive independent review, not merely file existence.

Create the offline capsule once with `tools/release_runtime.py build --venv ABS
--capsule NEW_ABS --module cadquery --module OCP --module vtkmodules --module numpy`.
It inventories regular package files and compressed bytes, pins the system Python
identity/ABI, and declares system KiCad/libraries/fonts as prerequisites. It is
not an operating-system image. Replay extracts only into guarded writable scratch,
checks member hashes and required module origins, then runs the unchanged owners
with that interpreter. Network and original-workspace access remain denied and
the archive remains read-only. Allow disk space for one expanded runtime per
nested owning replay; fail rather than use the original venv or download packages.
Version2 release replay has a 1200-second bound; the seal's nested owning check
has a 2400-second bound. These are implementation limits, not automatic orchestration.

If exact scene pixels depend on host graphics, a package-only capsule is insufficient.
After demonstrating exact guarded artifact parity, use `release_runtime.py bind-renderer
--source-capsule ABS --capsule NEW_ABS --venv ABS --graphics-device EXACT_NODE`
(repeat for each proven required device). This produces runtime schema2, binding
an EGL/GL profile, explicit environment policy and narrowly enumerated character
devices. Replay checks device identity and observed renderer before executing
owners; unavailable or substituted renderers fail without fallback. Only those
GPU nodes gain read/write/ioctl capability; archive/workspace/network restrictions
remain. State the finite GPU/driver prerequisite prominently: this is not a
hardware-independent runtime. No pixel tolerance or historical artifact change
is implied. Alternatively migrate production and replay together to a selected
software renderer and reaccept affected evidence through its original owners.

Version2 adds `mechanical` and `bom_identity` review checks. Exact denominators
come from `release_evidence.units()` and `completeness()` on the staged record.
Assign independent pin/electrical, visual/mechanical/BOM, layout/power and integrated
lenses; record `lenses` with those keys (`pin_electrical`, `visual_mechanical`,
`layout_power`, `integrated`), distinct reviewer identities and sorted check names.
Each lens must review its actual subjects; the integrated reviewer combines the
indexed judgments, not a summary of the author's claims.

Candidate `INDEX.md` explicitly labels its UNREVIEWED snapshot as historical once
accepted; it must not claim its own acceptance. The seal places the authoritative
current status/review and a direct-entrypoint index outside the candidate archive.

## Historical version1 fields and shared execution

Adopt `01_docs/release-review-contract.json` with version1, authority path/hash
and current assembly_receipt_sha256. The source manifest contains version1,
release_id, boards keyed by accepted board identifiers with version and quantity,
order_policy, handoff, mechanical_basis and nonempty evidence paths. Quantities
must match accepted fabrication. Release identifiers are filesystem-safe labels,
not claims of committed provenance. Mechanical basis must justify the included
exports/models and any absent STEP/physical geometry; judgment belongs to review.

The order-policy JSON contains version1, applicability `{rf:false,evidence,
rationale}`, holds `[{id,reason,evidence,closure}]` and dispositions
`[{id,reason,evidence}]`. Evidence is project-relative. Non-RF exclusion must be
bound by the commissioned capability profile and independent commissioning
review, not only an author declaration. RF designs require an adapter extension.

```
python3 -B tools/release_review.py build --project ABS --manifest REL --output NEW_REL
python3 -B tools/release_review.py verify --project ABS --manifest REL --output REL
python3 -B tools/release_review.py replay --archive ABS
python3 -B tools/release_review.py issue --project ABS --review REL
python3 -B tools/release_review.py check --project ABS
```

Build retains exact upstream receipts, reviews, subjects and structured file
dependencies in source/project; current tools/skills and adopted historical
toolchain remain under source with their original relative topology. Convenient
fab/pdf/mechanical/verification views are byte-identical aliases, not symlinks.
Complete file inventory and live-origin mapping include every archive file.
ORDER-INSTRUCTIONS starts with every active hold and its named closure. The
placement and mating roles resolve through the active routing contract's selected
receipt paths, including versioned successors. Missing selected receipts fail;
historical default filenames are never fallback acceptance for a new revision.
mutable archive truthfully stays UNREVIEWED; the separate current independent
receipt confers design review. Seal/procurement remain separate owners.

Replay copies the archive read-only into disposable scratch, permits generated
outputs only in a separate work directory, denies original-workspace filesystem
access and networking, invokes the exact accepted assembly owner and
thus its complete upstream checks (including native schematic/PCB replot, strict
DRC, PDF and assembly replay). System runtime, fonts, /etc, /proc and /dev remain
readable; this guard is not for executing untrusted code. No network refresh or
worktree fallback is allowed. Full archive census must remain unchanged. A
copied verifier is checked against the invoking trusted toolchain, not trusted
solely because its own manifest claims a hash. KiCad version is checked upstream.

Independent release review has one JSON block: schema1, stage PCB-RELEASE-REVIEW,
distinct author/reviewer, manifest/output, design_verdict SOUND (otherwise do not
issue), order_verdict DO-NOT-ORDER, exact verify subjects, and checks
pin_identity/readability/electrical/layout_power/completeness/order_readiness.
Each check has PASS, substantive rationale, nonempty bound evidence and coverage
`{required:[...],reviewed:[...],findings:[]}`. Lists must equal actual scope:
pin_identity is sorted board/reference for every mounted reference in geometry;
readability/electrical/layout_power each cover every sorted board identifier;
completeness covers sorted board/category for source,schematic,fab,assembly,
mechanical; order_readiness covers sorted active hold IDs. Coverage is an
accountability interface, not an automatic engineering verdict. Review the
actual sources/rendered pages and material engineering limitations, not only
receipt summaries. Known defects cannot be converted into future-test holds.

Missing/stale artifacts return to their source owner; electrical/layout defects
reopen the corresponding upstream acceptance. Only root issues release_reviewed
after a fresh independent full-archive review. Stop for phase reflection; actual
Git provenance and sealed_release belong to the release-seal stage.

Downstream version adoption: this archive deliberately retains a complete exact
tool/skill snapshot. Later vNext edits need not rewrite or invalidate that history.
The seal owner must explicitly adopt the accepted archive/toolchain hashes and
invoke its preserved `source/tools/release_review.py check --project ABS` (or
restore the same tree in isolated replay), not refresh hashes to whatever the
current development tools now contain. Root-worktree check validates the current
development snapshot; preserved-toolchain check validates the admitted version.
