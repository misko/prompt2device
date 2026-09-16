# contract: placement-backtrack-20260910/

**Purpose** — durable historical evidence for the 2026-09-10 placement source
backtrack and its evidence-governance repair. This directory is project-local;
it does not authorize canonical regeneration, checkpoint resume, board review,
routing, release, or order.

**Mutability** — archive, original source-author receipt and manifests are
immutable historical witnesses. New corrections append a separately dated
record; never rewrite their original path bindings or failed verdicts.
The current governance result and its actual validation receipts are finalized
at this source boundary. No archive member is executable source authority.

## Allowed

| File | What | Rule |
|---|---|---|
| `f451678d0ca60990de947a7898cbaea952f79f3deb5bb081fed2ab0ddf5a6883.tar.gz` | hash-addressed gzip/tar of exact historical regular file bytes | archive SHA and every regular member must match archive-manifest.json; no symbolic/hard links or duplicate names |
| `archive-manifest.json` | complete member names, original paths, sizes, SHA256, source commits and exactly two symlink facts | preserve original preimage manifest and all original reports/envelopes unchanged inside archive |
| `diagnostic-disposition.json` | all 47 original C-ALLOW paths and durable member mapping | removing an original from index requires durable member byte verification; retain ignored local originals |
| `protected-generated.json` | launch hashes for generated/checkpoint/sourcing paths | compare current paths at handback; never treat stale checkpoints as valid |
| `placement-source-author-result.md` | verbatim original failed source-author receipt | historical execution evidence, not current board acceptance |
| `placement-governance-result.md` | actual current source-boundary result, test evidence, provenance and limitations | distinguish source-test PASS from unregenerated/unaccepted PCB |
| `PROVENANCE.md` | relocation, reconstruction and template audit explanation | no silent promotion of historical witnesses |
| `source-suite.log` `source-suite-result.json` | complete bounded final 325-test source execution output and measured telemetry | retain raw return code and actual duration |
| `contracts-before.log` `contracts-staged.log` `contracts-staged-result.json` | actual governance diagnosis and staged-index validation | no debt or auditor relaxation; preserve raw outcomes |
| `archive-verification.json` | actual reopened archive/member and original-preimage verification counts and hashes | nonzero complete denominators |
| `handoff-validation.log` | actual pcb_flow generation and validation result | no fabricated DRC or checkpoint restamp |
| `contracts.md` | this exact contract | no wildcard evidence namespace |

## Validate

Run `/usr/bin/python3 scripts/contracts_audit.py --projects` and
`/usr/bin/python3 tests/t1_contracts.py` after staging the intended index.
Independently open the gzip/tar, refuse links, duplicates or unexpected members,
and hash every extracted regular member against `archive-manifest.json`.
Require 463 preimages / 94,665,796 bytes and all 47 diagnostic members.
Reopen `protected-generated.json` against the current filesystem.

## Forbidden

- Deleting original diagnostic bytes before their durable archive is verified.
- Rewriting a historical TaskEnvelope/report to point at its new member.
- Treating the two absolute symlink target strings as portable source content.
- Adding unrelated archives, arbitrary logs, waived audit debt or release claims.
