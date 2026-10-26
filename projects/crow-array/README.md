# Crow carrier and microphone pod

[Open the public v3 design package](releases/crow-prototype-v3-first-run-5c10p-public-v1/README.md).
It contains **5 carrier / 10 pod** design quantities, native KiCad files, PDFs,
Gerbers, BOM/CPL, population policy and retained verification records.

This is a redistribution-reviewed subset, not the full original sealed offline
replay. The original design verdict is SOUND; the ordering verdict remains
**DO-NOT-ORDER**. No firmware or manufactured-hardware qualification is supplied.
The package index exposes all nine exact-job holds and its excluded dependencies.

For the current assembly split, sourcing worksheets and browser-based ordering
continuation, start with the [MacBook handoff](order-readiness/MACBOOK-HANDOFF.md).
These mutable preparation records do not change the immutable release verdict.

`publication.py verify` checks the actual file census, trusted source hashes,
both board roles, local native libraries, license/handoff policy and Gerber ZIPs.
`test_publication.py` corrupts isolated copies to prove that the checker refuses
missing boards, altered/rehashed payloads, added assets and misleading claims.
This verification is separate from the repository's legacy release-format gate.

Validation on 2026-10-25: 15 public-package regression tests passed; independent
[publication review](checks/publication-review-20261025.json) passed. The
[isolated native replot check](checks/native-20261025.json) regenerated all 26
Gerber/drill members and all eight PDFs with matching geometry/rendered pages.
Both boards passed strict DRC, connectivity and explicit schematic parity with
zero findings; refilling zones did not change native geometry. The check used
only this public package and vNext tools, not the original sealed archive.
This does not replay the excluded mechanical/runtime/engineering evidence.

To repeat the native check on the supported KiCad 10.0.4/Poppler host:

```sh
/usr/bin/python3 -B projects/crow-array/native_smoke.py --output /absolute/absent-result.json
```

Portable CI verifies the package and its negative controls, not this native run.

The exporter refuses an existing destination. Rebuild in an absent temporary
directory using explicit paths to the original sealed repository and its parent
project (for post-seal evidence):

```sh
python3 -B projects/crow-array/publication.py build \
  --sealed /absolute/path/to/original-sealed-repository \
  --post-seal-project /absolute/path/to/original-project \
  --package /absolute/path/to/absent-public-candidate
```

The trusted `publication-policy.json` freezes this derivative's generated notices,
external-dependency inventory and handoff. Changes require explicit review of
that policy and a separately identified package; never rewrite the original seal.
