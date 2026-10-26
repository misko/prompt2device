# vNext PCB design and workflow orchestration

The domain skill defines what passes; the orchestrator defines how work proceeds,
recovers and stops. This package coexists with the reference skills in `../skills/`;
it does not replace them or silently migrate existing project receipts.

Start with [PCB design](skills/pcb-design/SKILL.md) and the sibling
[orchestrator](skills/workflow-orchestrator/SKILL.md). The
[domain graph](skills/pcb-design/workflow/graph.json) owns stage requirements.
Follow the [project binding](skills/pcb-design/bindings/project.md) to initialize
from a prompt and chronological decisions. Run documented `tools/...` commands
from this `vnext/` directory. Keep projects outside the skill package.

## Scope and dependencies

This is a coordinator-driven workflow, not an unattended scheduler or autorouter.
Explicitly adopt each stage adapter before use. Existing accepted projects retain
their frozen toolchain until a reviewed migration; copying this directory does
not upgrade an existing acceptance receipt.

The standalone route uses `bootstrap.py`, `task.py` and the adopted stage tools.
Historical `context.py`, `checkpoints.py`, `coverage.py` and the
`bindings/existing-tools.md` route require an external pinned legacy baseline and
`dependencies.json`; they are retained for history, not configured or supported
by this standalone package. Use the active stage contract rather than those old
schematic procedure wrappers. RF and hierarchical acceptance remain unsupported.

Portable control tests use Python 3.11+ and
[PyYAML](requirements-portable.txt) for source-snapshot handoff tests. Native CAD tests
require KiCad 10.0.4 (`kicad-cli` and its system-Python `pcbnew`) and Poppler.
Mechanical tests additionally require the versions in
[mechanical-requirements.txt](tools/mechanical-requirements.txt). Runtime libraries,
vendor documents, models and board artifacts are not bundled here.
Full release replay has additional host/isolation/rendering requirements; passing
portable CI is not evidence of full replay or engineering acceptance.

## Validation

From this directory:

```sh
python3 -m pip install -r requirements-portable.txt
sha256sum --check IMPORT-SHA256SUMS
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tools -p 'test_exploration.py'
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tools -p 'test_progress.py'
```

The [CI workflow](../.github/workflows/vnext-tests.yml) enumerates the portable
regression suites. Tests live beside their implementation in `tools/test_*.py`.
Some historical tests require `VNEXT_CROW_HISTORY`; without it they explicitly
skip. The normalized Crow fixture is test data, not a board design requirement
or independent reconstruction of the original history.

For the changed native adapters, run from `tools/` on the supported CAD host:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -m unittest \
  test_placement test_critical_routes test_fab_replay test_npth_revision
```

## Provenance

This import preserves 139 skill/tool files byte-for-byte. The frozen Crow v3
toolchain is the baseline; later tested lifecycle, stagnation and critical-route
improvements form the selected delta. The newer routing-tooling document is
deferred because it links to a separately unadopted native-authoring toolchain.
See [PROVENANCE.json](PROVENANCE.json) and [IMPORT-SHA256SUMS](IMPORT-SHA256SUMS).
The checksum file records the import, not a prohibition on future reviewed edits;
intentional changes must update provenance and validation together.

The original sealed Crow v3 archive remains separate and unchanged. This newer
package does not claim to be the exact toolchain that issued its seal.

Import validation (2026-10-25): 134 portable tests ran (118 passed, 16 optional
history tests skipped); 77 focused native tests passed on KiCad 10.0.4. Both
skill-entrypoint validators and all 139 import hashes passed. This is a focused
selection, not a claim that every native/mechanical/release suite was rerun.
