# PCB-RELEASE-SEAL — immutable, reproducible release

Local Git-backed seal pilot; read [seal tooling](../../procedures/release/seal-tooling.md).
Requires current
`release_reviewed`; successful layout, export or archive hashes alone are not a
release. Minting applies to both board types and the system manifest linking
their versions/quantities. Publication, ordering and first article are separate.

Before execution, adopt one project-local release contract and its tested
sole seal owner. Preserve the reference process's provenance and integrity:
exact committed source plus a complete standalone archive. Do not replace the
release with pointers, an unreviewed draft zip or a checksum-only ceremony.

The intended sequence is: finish mutable staging and standalone replay; commit
all actual project/tool inputs as source commit S; stamp S and a complete file
hash inventory; recheck exact staged acceptance; make a seal commit containing
the accepted release and release record; refresh the live status to name it.
Keep mutable status outside the archive. The seal must check Git provenance and
scoped cleanliness, not merely trust authored SHA/clean fields. A non-Git working
directory needs explicit local source-versioning setup before seal, not a fake S.

Immutability begins at the seal commit. Reopen the final committed archive and
verify file inventory/hashes, source provenance, per-board completeness and
owning acceptance independently. Future corrections create new versions; never
refresh a sealed board or its evidence. An explicit supersession pointer is the
only allowed addition to a prior release and must not alter its original bytes.

Tests must prove current valid fixtures can seal while stale source, dirty
inputs, modified/missing/extra archive files, absent reviews, mixed board
versions and post-seal edits fail. No automatic publication or order follows.
Record phase reflection and report exact release paths/source/seal identities,
design/order verdicts and all first-article/deployment holds. Only then does
`sealed_release` exist and the user's release goal become eligible for audit.
