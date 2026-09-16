# Crow daughter-pod release deficiencies

Candidate: v0.2.0 (mutable, not released). Updated 2026-09-16.

## Fix before release

- Refresh source/checkpoint and review evidence for representation-only policy changes; run layout, fabrication, review, rehearsal and publication gates on final sources.

## Deferred to next release

| ID | Issue / impact | Evidence and current disposition | Owner | Revisit / closure test |
|---|---|---|---|---|
| POD-D001 | D1 invariant rationale still names 1N4007 instead of S1M; misleading prose | Current pre-route topology review identifies this as documentation-only; executable pin assertions and actual S1M part identity are correct. | PCB maintainer | Next source revision: correct rationale and verify it matches D1 BOM/dossier without changing topology. |

## Resolved on current candidate

- U2 native-representation coverage: independently accepted explicit selection; signed front fraction 0.893637 against 0.85 floor; twin bodies 32/32 and top overlay 7/7 resolvable bodies, zero resolvable-but-unmeasured. Bottom overlay is inapplicable because there are no bottom component bodies/courtyards. Final archive binding remains part of release admission.
- Regenerated J1 connector views explicitly confirmed by user; owning orientation gate machine 1/1 and human 1/1 accepted subject ee066f412899580aff6d669d2dafa1adacd3b8479eb226cbe631b0e65d045c62.

## Separate holds

Exact JLC allocation, manual RJ45/capsule assembly, physical cable fit, rail/noise/gain/clipping, thermal and environmental measurements remain first-article/order holds under ADR0005 and assembly.yaml. No production or order-ready claim follows from design release.
