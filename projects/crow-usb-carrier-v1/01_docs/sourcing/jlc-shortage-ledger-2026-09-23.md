# Crow USB carrier — current D5/D7 shortage ledger

Audit point: source commit 500700a8; read-only, 2026-09-23. Dated stock observations may already be stale; M-IMPORT CITED from the retained reports/raw responses below, not fresh allocation evidence. Current
01_docs/sourcing/exact-parts.csv contains 490 references / 85 exact MPNs.
D5 requires JLC to stock and populate every non-through-hole component; D7
retains five boards plus 150 extra units per exact aggregated part/code.
Required quantity below is 5 × references-per-board + 150. Dated catalog
observations are not PCBA allocation, placement, or order acceptance.

## Current selection delta

The former 493-reference native-schematic headline and JLC population report
are historical, not a current whole-selection result. Their direct check remains
evidence only for unchanged exact identities:
- 06_build/sourcing/direct-check-20260923.json, generated
  2026-09-23T02:10:44.238329Z: 84 coded rows; explicitly does not predict JLC
  assembly allocation.
- 06_build/verification/stocked-source-composition/summary.json: 490 components,
  22 changed identities, removed C_U_1V8_OUT_2, C_U_3V3X_OUT_2 and
  C_U_CORE_OUT_2, no pin/net mismatches. Commission journal lines 540-542 says
  this is diagnostic source composition only, while native schematic and D5/D7
  admission remain held.

The 22 adopted changes are 8 OPA, 1 crystal, 10 capacitors and 3 inductors.
They replace four historical shortage identities:

| Adopted current exact part | Current aggregation / D7 requirement | Dated evidence | Current disposition |
|---|---:|---|---|
| OPA2320AIDR / C2863402 | 8/board; 190 | research/2026-09-23-opa-crystal-jlc-selection.md lines 8-18: 582 at 02:51 UTC | Replaces OPA2320AID; count clears D7. |
| X322524MOB4SI / C70590 | 1/board; 155 | Same record: 66,719 at 02:50 UTC | Replaces FA-238; count clears D7. |
| GRM32ER71A476KE15L / C84494 | 10/board; 200 | research/2026-09-23-grm32-bank-candidate.md lines 1-3: 56,478 on 2026-09-23 | Replaces 13 CKG parts, with three second outputs removed; source E-CAP screen accepted. |
| XFL4015-471MEC / C18221164 | 3/board; 165 | research/2026-09-23-coilcraft-inductor-source-candidate.md lines 1-7: 3,051 on 2026-09-23 | Replaces 744373240047; placement/loop/thermal and allocation still owed. |

These are adopted current CSV identities, not candidates. Their dated counts
do not close order-time allocation.

## Current unresolved exact-part ledger

Technology comes from the current exact footprint/pad class. D5 population
applies to each SMD row. THT means pure through-hole: D5 does not automatically
exclude it and D7 remains an every-part reserve constraint.

| Exact selected part / JLC code | Refs/board; D7 required | Technology / D5 | Latest dated evidence | Gap and next owner |
|---|---:|---|---|---|
| CS5308P-DNR / no selected code | 1; 155 once exact code exists | SMD QFN-48; JLC population required | TSX crow_retained_analog.tsx lines 210-212 has jlc empty. adc-d7-catalog/CS5308P-DNR.json, 2026-09-23T02:49:09Z: zero-stock shipping-only placeholder C9900305019, no qualifying binding. | D5/D7 blocker. Qualify exact stocked ADC architecture/source/footprint/interfaces; analog/electrical + sourcing. |
| TPS389018DSER / C2066910 | 2; 160 | SMD WSON-6 | Historic direct check: stock 0. Population review lines 227,434: Q1 C2066893 only 10. | Build and D7 shortage. Q1/adjustable replacements are unadopted; power/digital + sourcing. |
| TPSM63603V5RDHR / C5219330 | 1; 155 | SMD B0QFN-30 | Historic direct check: stock 0. Population review line 228 has unadopted adjustable C5219327 at 260. | Build and D7 shortage. Alternate is a power redesign; power + sourcing. |
| TMUX2821DSGR / C53283916 | 8; 190 | SMD SON-8 | Historic direct check: stock 16. Population review lines 231,447-451: unadopted two-per-cell TMUX2819 at 199 for 80 build / 230 D7. | Build and D7 shortage. Alternate changes topology/footprint; analog + sourcing. |
| ASFL1-24.576MHZ-EC-T / C17566269 | 1; 155 | SMD oscillator | Historic direct check: stock 86. Population review line 428 records unadopted alternatives. | Build covered; D7 shortage. Retain or qualify replacement; digital/clock + sourcing. |
| TPS389030DSER / C2066942 | 3; 165 | SMD WSON-6 | Historic direct check: stock 58. | Build covered; D7 shortage. Adjustable consolidation is unadopted; power/digital + sourcing. |
| TPS6282518DMQR / C2072356 | 1; 155 | SMD VSON-6 | Historic direct check: stock 51. Population review line 431 names adjustable C2650334 only as candidate. | Build covered; D7 shortage. Any change needs power requalification; power + sourcing. |
| TPS6282533DMQR / C3189971 | 1; 155 | SMD VSON-6 | Historic direct check: stock 44. Same candidate record at population review line 431. | Build covered; D7 shortage. Adjustable alternative needs divider/rail proof; power + sourcing. |
| XU316-1024-TQ128-C24 / C6362698 | 1; 155 | SMD TQFP-128 | stocked-source-composition/xmos-stock-recheck.json, 2026-09-23T03:50:20Z: stock 46. xu316-jlc-replenishment.md lines 1-15: 109-unit public gap, no approved exception. | Build covered; D7 shortage and USB-core blocker. D8 retains XMOS; systems + sourcing. |
| R82DC4100CK60J / C3778009 | 16; 230 | Pure THT | Historic direct check: stock 6; historical population audit classifies 16 coupling capacitors pure THT. | Build and D7 shortage. User/assembly must choose THT disposition; no automatic BOM/CPL removal. |
| 615008160221 / C6461980 | 8; 190 | Pure THT RJ45 | Historic direct check: stock 0; historical population audit classifies J1-J8 pure THT. | Build and D7 shortage. User/assembly must choose THT disposition; no automatic BOM/CPL removal. |

## Governing policy and handoff

- D5 and no automatic THT exclusion: BRIEF.md lines 144-147.
  assembly.yaml lines 129-132 and 150-151 has no active ADC/assembly exemption.
- D7 aggregation and 150 extra: BRIEF.md lines 154-157; assembly.yaml lines
  44-45.
- Current count and historical 493: BRIEF.md lines 58-61.
- findings.yaml lines 150-168 keeps sourcing ownership and requires every exact
  JLC-stocked non-through-hole part at build plus reserve, followed by source
  regeneration and independent review.

No fresh stock query was made. No research alternative is promoted. The current
shortage denominator is ten unchanged historic failing exact parts plus uncoded
U_ADC: nine SMD D5/D7 rows including U_ADC, and two pure-THT D7 rows awaiting
explicit assembly disposition.
