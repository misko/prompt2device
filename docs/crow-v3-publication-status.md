# Crow v3 publication checkpoint — 2026-10-25

Publication target: this existing `misko/prompt2device` repository. The isolated
publication branch imports reusable vNext first. No Crow archive, vendor documents,
runtime bundle or manufacturing files are published by that import.

## Exact preserved local release

Release: `crow-prototype-v3-first-run-5c10p`.
Carrier `rev-a-first-run-r3-d3` ×5; pod `rev-a-first-run` ×10.

- Source commit: `08bd3a485c23039bb1c27bdcfb8521bf454c935a`.
- Seal commit: `a74470eaee97effcfab69fb43fdf302f0cac1865`.
- `release/seal.json` SHA-256: `c2b89fdaf364b7538cd58bf0e52a150c8bde3b9cd1f2b52f2010adfafc398a50`.
- Archived `release.json` SHA-256: `97d98924da353325c3297f1886abdf5d305ede273d3100a5ce056f19ea15df56`.

These identities were rechecked against the clean local sealed repository.
The prior completion audit records full offline replay and independent acceptance
on October 23; publication preparation has not rerun that expensive full replay.
Its recorded verdict remains **SOUND / DO-NOT-ORDER**, with nine actual-job holds.
Publishing or downloading artifacts would not close those holds, establish current
stock, authorize purchases, or demonstrate firmware/physical qualification.

## Why the full bundle is held

The repository's [contribution policy](../CONTRIBUTING.md) requires recorded
redistribution rights and prohibits changing sealed artifacts to resolve an import.
The immutable archive contains third-party material, not only original board files:

| Material (paths relative to sealed repository) | Unresolved publication condition |
|---|---|
| `source/project/02_parts/P027/manufacturer.pdf`, `P035/manufacturer.pdf`, `P036/manufacturer.pdf` and repeated copies | Retained vendor terms require a rights review; public download availability is not a redistribution grant. |
| `source/project/03_src/recovery/first-run-d3-investigation/evidence/ti-slua566a.pdf`, `ti-spra953d.pdf` | Same restriction; linking upstream is distinct from redistributing the complete PDF. |
| Copied KiCad footprint/library collections | Preserve applicable library license, design exception and attribution; repository MIT does not relicense these files. |
| `source/project/03_src/release/ls47/runtime/site-packages.tar.gz` and `ls48/runtime/site-packages.tar.gz`, plus archive copies | Retained package notices alone do not demonstrate compliance for all bundled compiled libraries and corresponding-source obligations. |
| Other vendor PDFs, downloaded HTML and imported assets | Per-asset clearance remains incomplete; the examples above are not an exhaustive permissions inventory. |

This is a publication preflight, not a legal opinion or a claim that every vendor
asset is prohibited. Keep the original seal unchanged. No full Git bundle has
been uploaded, and no GitHub board release has been minted by this step.

## Ranked next approaches requiring a packaging decision

1. **Recommended: separately labeled public board package.** Select original
   native designs, PDFs, fab exports and verification records with verified rights;
   preserve required third-party notices and use upstream links/checksums for
   excluded dependencies. Bind every copied artifact to the sealed source hash.
   Explicitly state that this derivative is not the complete sealed offline replay.
   Review and verify dependency closure before publishing, without modifying the
   local original archive.
2. **Complete archive publication.** First establish redistribution permissions and
   satisfy binary/source/license obligations for the complete bundle; retain its
   exact original commits. This preserves the full offline replay transport but
   requires substantially more clearance work and may require external permission.

For either approach, add explicit verification for the selected vNext publication
layout. The existing legacy publication gate's zero-project result on the vNext
skill import is not acceptance of a future board package in a new folder layout.
After validation, publish on the review branch, merge/tag only the reviewed scope,
and verify a fresh remote download. No vendor contact or purchase is authorized
by this publication checkpoint.

## Repository regression checkpoint

The unchanged legacy locator suite passed 2 tests; publication gate passed 34;
transport suite passed 8. The selected legacy release-freshness test
(`--only='review coverage'`) failed: it expected `REVIEW-COVERAGE`, but the fixture
was rejected earlier with `CRITICAL-SELECTION RELEASE HOLD: cannot locate project
authority`. The legacy test and gate files are unchanged from the publication
base. Do not hide this failure or claim the complete repository CI is green;
diagnose the fixture/guard interaction separately before merging. No legacy gate
has been bypassed or weakened in this import.
