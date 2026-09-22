# Crow modular trial reconstruction provenance

The carrier trial input was prepared from commit
`d7c3ac4416b1ee3c233b98de869ad410e2e61788`, whose Crow carrier project tree is
`aa582e5ac63c235731140bed64fd5070504ad522`. There is no historical revision
that combines the current selected parts with a genuinely untouched
post-selection/pre-placement state. This tree is therefore labeled a
**reconstructed current-parts replay input**, not a recovered checkpoint.

The preparer copied selected part dossiers, exact footprint/model libraries,
TSX schematic intent, and accepted electrical/interface/assembly/stackup
authority. It generated a fresh input floorplan intended to contain only an
inherited envelope and mounting-hole set, stackup, fabrication minima, pin/net
assertions and connector edge-facing constraints. Its component anchor map is
empty.

Preparation finding: the initial 304-member run incorrectly narrowed the
pinned baseline outline from `x1: 172.0` (156 mm width) to ADR-0030's proposed
`x1: 170.0` (154 mm width), while leaving the baseline M3 centers unchanged.
The initial manifest and hashes remain preserved as forensic truth for the
already launched schematic envelope. The preparer is corrected for future runs
to copy the pinned baseline `board.outline` and `board.mounting_holes` values
verbatim and label them inherited trial inputs, not hard requirements. The
active child is intentionally not rewritten under its running owner. Its next
placement handoff must explicitly restore or adjudicate the missing 2 mm and
record the resulting source-bound envelope before any physical claim.

The fresh schematic trial also exposed a missing inherited input:
`rules/protection_paths.yaml` references `01_docs/FIRST_ARTICLE_TEST_PLAN.md`,
which the initial selection omitted. The source E-SURGE check correctly
remained incomplete. Future preparation includes that requirements document;
the active run must restore its exact pinned bytes and recheck the source gate
at the next boundary. This is a reconstruction repair, not a relaxed rule or
physical first-article evidence.

The reconstruction excludes generated CAD, netlists and PDFs; build output;
release payloads; reviews; journal, research and report archives; current
`route.yaml`; promoted/final route chains; route seeds; learned component
anchors/repeated-cell poses/regions; placement keepouts and zones; locator and
model-registration poses; and solution-specific waivers. The old solved board
and copper are unavailable inside the child directory.

`crow_modular_trial.py prepare` required the complete live source project to be
clean against the pinned baseline, captured SHA-256 identities for every
selected source file before copying, compared them again afterward, and
rechecked the baseline diff. `crow_modular_trial.py verify` reopened every
copied member, reproduced the input-tree digest, rejected forbidden paths, and
confirmed that no learned placement anchors, zones or keepouts survived.
That verification applies to the frozen initial input. Once the trial writes
fresh schematic or physical candidates, runtime provenance and explicit
source-bound comparisons must track those outputs; the initial-input verifier
is expected to reject the mutated working tree rather than bless later work.

No schematic producer, KiCad native generator, placement tool, router, DRC,
review, fabrication or release command was run during reconstruction. The
inherited TSX is schematic intent only. Fresh schematic generation and review
are the first trial result; every physical result remains owed.
