---
schema: 1
kind: pcb-human-report
report_id: 2026-09-16-first-article-order-readiness
title: Crow pod first-article order readiness
subtitle: Exact upload and assembly controls for the ten-board pod lot
project: crow-mic-pod-v3
date: 2026-09-16
status: REVIEWED
evidence_status: INCOMPLETE
---

## Executive conclusion

The immutable pod release is suitable for a supervised ten-board first-article
order after the live uploader checks pass. **MEASURED:** JLC places all 31
fitted SMD references on the top side. J1 and the off-board MK1 capsule remain
controlled manual operations; TP1–TP7 are intentionally bare pads.

## Question and scope

This report defines the order controls for immutable release
[`v0.2.5-2026-09-16`](../../07_releases/v0.2.5-2026-09-16/ORDER_README.md).
It covers fabrication selection, JLC assembly, manual fit and uploader review.
It does not claim physical cable, audio, thermal, enclosure or environmental
qualification.

## Evidence boundary

**MEASURED:** the release board SHA-256 is
`2685281fdb8dac636e16334c2d4eca679300bfa5322a368ac2685b59f48e3dd1`.

| Slot | Immutable file | SHA-256 |
| --- | --- | --- |
| PCB | [`crow_mic_pod_v3_gerbers.zip`](../../07_releases/v0.2.5-2026-09-16/fab/crow_mic_pod_v3_gerbers.zip) | `d8390720d661f35d3f504ae6eceb9231699bad743278d3667bba854aae99f79e` |
| BOM | [`bom.csv`](../../07_releases/v0.2.5-2026-09-16/fab/bom.csv) | `7dd5c9f9ae55591115be334a711bcb08bcf050dbcf880e8a1f44efa2bd737046` |
| CPL | [`cpl.csv`](../../07_releases/v0.2.5-2026-09-16/fab/cpl.csv) | `743a25d6065477efbb7b030d906a0d589419a67173e595f10f4e555862fad668` |

**OWED:** final allocation, price, resolved BOM and placement previews require
the live authenticated uploader session.

## Findings

**PROPOSED and accepted by ADR0010:** order ten Economic PCBA boards using
FR-4, two layers, 1.6 mm thickness, 1 oz copper, green solder mask, white
silkscreen, ENIG 1 microinch, the standard two-layer stack, no controlled
impedance and ordinary tented vias. Enable production-file confirmation.

**MEASURED:** [`assembly_coverage.txt`](../../07_releases/v0.2.5-2026-09-16/verification/assembly_coverage.txt)
reports 31 top-side CPL placements. The [manual-fit work order](assets/pod-manual-fit-work-order.csv)
requires ten exact Würth J1 jacks and ten exact AOM capsules for the lot.

**MEASURED:** the
[`rotation_human_gate.txt`](../../07_releases/v0.2.5-2026-09-16/fab/rotation_human_gate.txt)
requires final preview confirmation for U1 and U2. **OWED:** the resolved BOM
must match [`bom_echo_gate.txt`](../../07_releases/v0.2.5-2026-09-16/fab/bom_echo_gate.txt)
with no redirects or substitutions.

## Recommendations

1. Upload only the three hash-listed files and select the ADR0010 fabrication
   profile.
2. Confirm 31 top-side placements and U1/U2 orientation before payment.
3. Keep J1 and MK1 excluded from machine assembly; fit them from the exact
   manual work order and retain TP1–TP7 as bare pads.
4. Stop for any substituted part, bottom-side placement, altered outline or
   drill interpretation.

## Validation plan

Retain the final uploader selections, resolved BOM and placement previews, hash
them and bind them to this release in an order receipt. On delivery, inspect J1
and MK1 work and execute [`FIRST_ARTICLE_TEST_PLAN.md`](../FIRST_ARTICLE_TEST_PLAN.md).
Failure of any live uploader row or the absence of an exact manual part blocks
the corresponding assembly.

## Source register

- [Immutable pod manifest](../../07_releases/v0.2.5-2026-09-16/MANIFEST.txt)
- [Assembly population evidence](../../07_releases/v0.2.5-2026-09-16/verification/assembly_coverage.txt)
- [Order-profile authority](../decisions/0010-first-article-order-profile.md)
- [JLCPCB surface-finish guide](https://jlcpcb.com/help/article/jlcpcb-surface-finish)
- [JLCPCB assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
