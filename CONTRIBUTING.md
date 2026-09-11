# Contributing

By submitting a contribution, you agree that your original contributions are
licensed under the repository's [MIT License](LICENSE). Submit only content
you have the right to contribute under those terms. Third-party materials
retain their existing copyright and license terms.

For new original source files, add `SPDX-License-Identifier: MIT` in the
language's comment syntax when convenient. Keep `"license": "MIT"` in project
`package.json` files. Preserve existing third-party notices; do not apply an
MIT identifier to someone else's material unless it is MIT-licensed.

For third-party imports, record the author or supplier, upstream URL, version
or revision, and applicable license or redistribution permission in the
local provenance record, and update [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
Keep any required upstream copyright and license files with the material.
For vendor datasheets or models without clear redistribution permission,
link to the upstream file instead of committing a copy. Downloads needed for
local work can remain in an untracked cache; record the URL, revision, and
checksum so the same file can be retrieved again.

Follow the repository's project contracts and the relevant workflow in the
[README](README.md). If a workflow requires a committed vendor file whose
redistribution permission is unclear, resolve that conflict before submitting
it. Do not rewrite sealed release artifacts to update licensing metadata.
