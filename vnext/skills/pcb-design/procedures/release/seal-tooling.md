# Local immutable release seal

Read the release-seal stage. This pilot seals the accepted flat non-RF prototype
design archive; it does not authorize ordering, publication, firmware or physical
qualification. It needs Git with an existing user identity and the accepted
archive's Linux isolation/KiCad runtime. No remote or signing service is used.

Adopt `01_docs/release-seal-contract.json`: version1, authority path/hash,
archive path and archive_record_sha256, independent review path/review_sha256,
release_reviewed_sha256, new repository path, release_id, boards (exact accepted
versions/quantities), and seal_tool_sha256. All paths are project-relative. Pin the
accepted archive rather than updating its historical tools to today's versions.
The archive record binds its original source manifest. Participating live project
inputs must still match the archive; legitimate changes return to their owner.

For a version2 reviewed archive, the same seal contract retains its runtime
capsule and candidate index. The preserved checker replays with the inventoried
runtime in guarded scratch; allow up to 2400 seconds for the nested owning check
and adequate space for nested extracted runtimes. No upstream accepted tool is
modified to select that interpreter. `construct` derives `CURRENT-STATUS.json`,
its human-readable counterpart and root `INDEX.md` from the accepted review.
They bind the candidate and review hashes, expose all holds, link native designs
and artifact roles directly, and point to `seal.json` for source provenance.
Reconstruction verifies these files as well as the archive; a self-rehashed
contradictory status cannot pass. The historical UNREVIEWED candidate is preserved,
not rewritten into a self-certifying SOUND archive.

Freeze the owner, tests and guidance before `prepare`. Use an absent isolated
repository path, never initialize Git over unrelated project history. Commands:

```
python3 -B tools/release_seal.py prepare --project ABS
python3 -B tools/release_seal.py stage --repo ABS
python3 -B tools/release_seal.py commit --repo ABS
python3 -B tools/release_seal.py check --repo ABS
python3 -B tools/release_seal.py issue --project ABS --review REL
python3 -B tools/release_seal.py check-receipt --project ABS
```

`prepare` checks adoption/identities and creates actual source commit S: accepted source/toolchain, archive
reconstruction inputs, independent design review/receipt, adoption authority,
current seal tools/skills and full inventory. `stage` reconstructs the exact
accepted archive without adding files inside it, places its review alongside,
and writes a seal record binding S and complete release inventory after full
owning replay. `commit` rechecks exact staged reconstruction/inventory without
redundantly regenerating identical PCB outputs, and creates T, a direct child of
S adding only the release. Neither commit issues acceptance. `check` independently compares actual Git blobs,
ancestry and working-tree census, reconstructs the archive from S, and invokes
the preserved owning acceptance chain in read-only offline scratch. The tool
reads raw parent headers with replacement objects disabled (not graft-sensitive
history views), and propagates bytecode-disabled execution through children; no cache/extra-file
ignore list applies to the release. Unsupported isolation fails closed.

The sealed repository is self-contained: run its
`seal-tools/tools/release_seal.py check --repo ABS` after relocation. Source,
acceptance and replay inputs are committed, not pointers into development.
The working checkout must exactly match T, including ignored/untracked files;
regular non-executable files only are supported. Git history is not a digital
signature or a defense against replacing both the trusted verifier and identity.

Independent seal review is one JSON block with schema1, stage PCB-RELEASE-SEAL,
distinct author/reviewer, verdict PASS and `result` exactly equal to full `check`.
Checks provenance/completeness/replay/integrity/handoff each need PASS and a
substantive rationale. The result binds both commit IDs, board scope, full census
and seal-record hash. Review actual committed content and run tests/checks;
do not approve an author's summary. Design engineering was graded by the upstream
release review; this review proves its preservation and committed replay.
Only root may `issue` the separate project receipt after this review passes.

Keep mutable logs/status and the post-commit seal review outside the sealed repo.
This avoids a self-hash cycle: T contains the prior independent design review,
while the final independent seal review binds actual T. Retain it with the
project receipt as post-seal evidence. Corrections require a new release version,
not amendments or hash refreshes to a sealed release. Stop for reflection and
audit the user's complete objective before declaring completion. Report both
commit IDs, board versions/quantities and the unchanged order/qualification holds.
