# Incident packet: release readiness

## Scope and provenance

This packet supports the planned **Stable review and publication inputs** checkpoint family for retrospective incidents R02–R03, R18 and R21–R22. The retrospective is verified at `0dd098e2b58dc8750b19ab9305a78e46a9c92c5b` (2026-09-20). The compact historical publication record is `projects/crow-audio-carrier-v1/01_docs/journal/schematic.md` at verified revision `2f16225630637955b43f3446419cad2f8797e17b` (2026-09-16). Raw reviews, credentials and transcript bodies are excluded.

## Compact source excerpt (13 lines)

> Final publication census found a manifest member for an ignored, absent
> `.kicad_prl`; the atomic push stopped before remote mutation. A docs-only
> successor preserved source/fab/3d bytes and corrected README/MANIFEST.
>
> Combined publication passed locally, but GitHub rejected the atomic push:
> `pack exceeds maximum allowed size (2.00 GiB)`. Main and both tags were rejected.
>
> Recovery kept the rejected line, moved 15 packets over 100 MiB to explicit
> Git LFS objects, pushed 360 other packets in bounded batches, and required
> docs-only successors to bind identical board payloads to clean ancestry.
>
> The retrospective separately records stale review subjects, late metadata
> digest changes, omitted Git/manifest members and nested evidence archives.

The first three paragraphs compress the dated journal entry at `2f162256`; the last summarizes R02, R03, R21 and R22 from `0dd098e2`.

## Failure, cause and successful correction

Directly established failures include a release manifest naming an absent ignored file, review/metadata identity becoming stale, and an outgoing Git population too large for the remote transport limit despite local engineering/publication checks. The transport record confirms the push mutated neither remote main nor tags.

The direct transport cause was oversized outgoing history dominated by retained review material; recursive/nested archives are reported by the retrospective as a major contributor. The broader cause—release inputs were stabilized and transport-rehearsed too late—is an **inference** that motivates earlier preflight. Reviewer delivery failures and stale visible subjects are related readiness incidents, but they are not asserted to have caused the oversized pack.

Successful corrections added exact filesystem/Git membership checking, corrected the manifest through a docs-only successor, migrated large evidence to LFS, used bounded transport batches, rebound identical engineering payloads to transport-safe ancestry, and reverified remote state. Authoritative inputs and owners include:

- each candidate/release `MANIFEST.txt`, review subject headers and content hashes
- `projects/crow-audio-carrier-v1/07_releases/v0.1.8-2026-09-16/`
- `projects/crow-mic-pod-v3/07_releases/v0.2.7-2026-09-16/`
- `skills/pcb-design/scripts/pcb_publication_gate.py`
- `skills/pcb-design/scripts/publication_transport_gate.py`
- the recipient-visible Git index/tree and configured remote state

## Exact regression properties

The planned family must prove:

1. A review packet whose source/candidate identity or subject hash is stale is rejected; an exact-current control passes.
2. Required candidate and publishable-tree membership is checked against reopened hashes, filesystem census and recipient-visible Git tree. Missing, ignored-only, untracked-only or extra declared members fail.
3. Nested evidence archives or outgoing single/aggregate populations beyond existing transport limits fail before seal/push; a bounded control passes.
4. A plausible shortcut that edits only prose counts, drops evidence, or bypasses final publication checking fails.
5. The preflight records exact candidate/review identities while leaving unrelated protected artifacts unchanged. Final review, release rehearsal, seal admission, publication gate and remote verification still run.

These are **planned** additions from `update_and_test_pcb_design.md`; the packet does not claim they are all implemented. Existing publication/transport gates already cover parts of membership and transport behavior. Existing checkpoint `crow-release-evidence` is a different archived v1.0 reduction of ERC/BOM count contradictions and explicitly is not a complete release replay; it does not prove this family's Crow review identity, nested-archive and outgoing-tree properties.

## Retired approaches and reduction limits

Retired approaches: regenerating a review subject without invalidating its approval; editing metadata after the expensive final replay without dependency-scoped renewal; embedding prior evidence archives recursively; retrying the same oversized pack; force-pushing published history; and treating local engineering acceptance as successful publication. Reconsider a prior review only when its exact subject and dependency hashes remain unchanged; reconsider transport layout only with an independently checked, ancestry-safe population that preserves release payload identities.

A compact fixture cannot reproduce remote-provider behavior, all historical archives, GitHub service state, reviewer delivery timing or the full release graph. Local transport controls demonstrate rejection/admission of a bounded population; they do not prove a future remote push, reviewer verdict, engineering correctness, order readiness or first-article qualification. Historical elapsed time and aggregate token figures must not be assigned to this issue; per-issue spending is **UNKNOWN**.
