# ADR-0004 — use bare analog ICs instead of modules

Status: accepted for first article
Date: 2026-09-01

## Decision

Use TPS7A4901DGNR and OPA1679IDR as bare ICs with their exact support networks.
Do not use a microphone preamp module, balanced-line module or regulator module.

## Why modules were rejected

- Common electret preamp modules expose single-ended output, unknown grounding,
  adjustable gain or undocumented noise, and do not preserve the fixed
  complementary 2.5 V common-mode interface.
- Balanced-audio modules generally assume bipolar or transformer interfaces,
  are physically larger, and obscure the exact output resistance and ESD path.
- Regulator modules duplicate input protection and do not expose a source- and
  layout-reviewable low-noise rail inside the pod enclosure.

The bare circuit is small, fully specified by primary datasheets, and keeps the
four-wire connector boundary directly auditable.

## Consequences

This choice transfers bypassing, stability, thermal and layout responsibility
to this board. Exact-part dossiers, schematic review and first-article tests are
therefore mandatory; this ADR is not a claim that the first article already passed.
