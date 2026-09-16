# Crow audio carrier v1 — v0.1.3 assembly-policy successor review

subject: crow-audio-carrier-v1 v0.1.3 assembly-policy successor release
project: crow-audio-carrier-v1
release: v0.1.3-2026-09-16
date: 2026-09-16
reviewer: integrated assembly-policy release review
context: FRESH
source_commit: 726bccf5f7600d1d3c434ceb856086bbb92fc6ed
board_sha256: 0776f364424282a7924266450f899ce69bf28cf95a602ca74d92b86fd91c164d
design_verdict: SOUND
order_verdict: BLOCKED-SOURCING

## Integrated delta judgment

PASS. The v0.1.3 archive is an assembly-policy successor to v0.1.2. Its
fabrication, native board, STEP, schematic, BOM, CPL, PDFs, connector renders,
and physical verification payload remain byte-identical. The source delta is
confined to the authoritative assembly policy and archive-local project
documentation. `verification/assembly.yaml` is byte-identical to that source
authority.

The policy sets `public_stock_surplus: 150`. Fresh public catalog evidence was
measured on 2026-09-16 against the five-board build: C7452883 measures 0 units
against a 155-unit threshold, and C53283916 measures 16 against 190. Both are
explicitly classified in the sourcing plan; the remaining 49 coded BOM rows
clear their configured thresholds.

Exact assembly-policy release rehearsal passes all three seal-required gates.
The public catalog check remains advisory and the authenticated JLCPCB PCBA
receipt remains invalid or stale, so ordering is blocked. All first-article,
physical connector, cable, thermal, analog, EMC, enclosure, CAM and uploader
checks remain mandatory. No copper, component, placement, routing or
fabrication acceptance is created by this policy successor.
