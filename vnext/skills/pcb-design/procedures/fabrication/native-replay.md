# Portable circuit and 2D PCB replay component

This is one fabrication/release dependency, not a complete standalone release
or stage adapter. It copies native PCB/settings/local footprint libraries,
Gerber/drill plots and ZIPs, PCB/layer and top/bottom assembly PDFs, strict DRC
evidence and the replot toolchain. Public export also includes the accepted flat
schematic's declared authoring inputs, local libraries, native schematic, intent,
membership and assembly/harness expectations, plus regenerated netlist/ERC/PDF.
No links to the working project are used for replay. KiCad and Python/pcbnew
remain explicit installed runtime dependencies, pinned by the recorded version;
PDF comparison also requires Poppler's pdftoppm.

```
/usr/bin/python3 tools/fab_replay.py build --project ABS --output NEW_REL
/usr/bin/python3 PACKAGE/tools/fab_replay.py verify --package PACKAGE
```

Public build reruns the current layout-seal acceptance and consumes all accepted
board types and the current schematic-contract's manifest/expected sources.
Phase-resume authority remains with the coordinator. Internal `produce` is an
isolated test seam; its optional `schematics` argument is `{manifest: REL,
expected: REL}`. Omission produces a clearly limited PCB-only fixture, not a
complete public export or substitute stage acceptance.

Build validates local library coverage, copies—not links—sources, runs strict
all-severity DRC/refill in isolation, rejects any native change from refill, and
plots from those bytes. Replay inventories exact files, rejects symlinks and
modifications, regenerates plots/DRC in a temporary source copy, and compares
plot geometry and ZIP membership/bytes. Only existing plot/report timestamp
normalization applies. The archived sources are not mutated during replay.
PCB PDFs are compared as rendered pages using the existing native PDF checker,
not by unstable metadata. Layered PCB and top/bottom overlays use native geometry;
assembly views are not population-filtered, 3D mounted-body or fit evidence.
The bottom overlay retains the top-view coordinate registration (not mirrored).
Rendered-page equality does not establish readable labels: inspect actual PDFs
at release review and return overlaps or missing identifiers to their source owner.

Version 2 builds the copied schematic first and runs native DRC with explicit
`--schematic-parity --exit-code-violations` against its colocated copy. Each board's
`drc-execution.json` binds the actual command, source hashes and successful exit;
replay reruns and compares it. An empty parity field without execution is not proof.
Exact native net names and isolated no-connect identities come from regenerated
XML; intent aliases must not rename or merge native nets. Intended schematic
parts cannot be marked board-only, which native KiCad parity alone may not reject.
PCB-only fixtures omit schematic parity explicitly and cannot establish complete
fabrication acceptance. Historical version 1 packages use their archived verifier;
new output requires explicit downstream adoption, never refreshing old receipts.

The `design/` subtree retains original project-relative circuit paths. The
existing imported producer adapter rebuilds from copied declared inputs in a
temporary directory and rechecks native/intent/context bytes, complete membership,
pin facts/connectivity, all-severity ERC and rendered schematic PDF. Assembly
replay checks board instances and declared harness against retained expectations.
The joined checker also compares every physical intent reference, footprint,
ordering field and pad net/NC with the archived PCB; only footprint-library-identity-
free, board-only, unnumbered and entirely netless NPTH extras are structurally supported.
Population/position-file exclusions remain owned by assembly mapping, not inferred
from a raw parity pass. The comparator cannot judge engineering soundness or infer
independent membership from generated exports.

Only the already-supported **trusted local Python, flat imported producer** is
handled here. Read [imported tooling](../schematic/imported-tooling.md) before
executing unfamiliar authoring code. A temporary directory is not a security
sandbox; do not run an untrusted downloaded producer as if hashes made it safe.
Fresh package-local build provenance does not renew historical stage acceptance.

`bundle.json` binds the board set, KiCad version, file hashes and (for a live
export) upstream layout receipt/review hashes. It is not a cryptographic seal:
the later release owner must bind the complete reviewed archive to its source
and seal commits. A self-consistent rewritten package is not proof of provenance.
Replay requires the complete copied tool set and compares it with the running
verifier's toolchain. This supports checking with a separately trusted verifier;
executing a package's own modified verifier cannot establish its authenticity.

All output records remain unaccepted and DO-NOT-ORDER. Embedded external 3D model
references are listed as unbundled; successful 2D replay proves neither their
portability nor mechanical fit. Vendor BOM/CPL integration, population/stock/
process review and complete fabrication/assembly/release admission are still
required. Do not promote this
component into a complete release or hide an unresolved engineering obligation.
