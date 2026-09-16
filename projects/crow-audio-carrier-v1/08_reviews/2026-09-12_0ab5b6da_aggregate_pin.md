# Crow audio carrier v1 — canonical pre-route physical-pin aggregate

subject: crow-audio-carrier-v1; raw_sha256 acfc655fa49db5bb741c215180e0186fcf059fe1f79918874e5c9e5ce71291bd; semantic_sha256 976140177102d395e2abfe2c0967eb5082588cc7ab01ee526ed0980823a951e3
date: 2026-09-12
reviewer: fresh-context channel-pin-aggregate judgment agent
context-given: immutable blind manufacturer reports for U_ADC and eight C_ADC_CM references; accepted ADR0027 and channel-map source/review; exact previous/current native boards; current dossier subject bindings; previous canonical pin aggregate
source_commit: 24263dead13543e76c096ee2b3df6c94c9379cee
review_stage: pre-route
review_kind: pin
board_sha256: 0ab5b6dae425074f2515dc3c3d737e56f2292d83140590dca592b7b964e73090
parts_sha256: bd5dc4f2092cbf0b4a56d07eeff8d7a6ce9d727eaaaef7d40be68318a88bb285
design_rules_sha256: 5891d8028d9864ea0503dc3f63c7520efca45ece640c9db65423680f85b88712
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
completed_at: 2026-09-12T04:24:21.807294+00:00

## Judgment

The exact current board is SOUND in the pre-route physical-pin lens. Coverage is complete for all 333 assembled references: 324 inherit unchanged prior judgments and nine references receive fresh manufacturer/context adjudication here. This verdict is limited to physical pin identity, winding, polarity, electrical-kind suitability and the intentional logical-channel association. It does not admit routing or ordering.

The inherited authority is `current/08_reviews/pre-route_pin.md`, SHA-256 `55af9b469d500d58e70b8e9c70adc8b7cb8502277af430cd6430530b29b63358`, on previous board `9aa1c2c821a31129176a8b519b9a211d78dfc011adb997a64470c03d0726891f`. That canonical transfer report in turn binds the complete previous aggregate `2026-09-11_9aa1c2c8_aggregate_pin.md`, SHA-256 `775f26c79fcde976ed82a51c13fb7537d9eb7567445c457f1b48a2f3041eb225`, and its original manufacturer groups and corrections. This aggregation preserves those inspection attributions and does not enlarge their scope.

## Exact native-board and part transfer

An independent packet-relative `pcbnew` comparison keyed every footprint and physical pad field across the previous and current native boards. It covered 340/340 footprints and 1002/1002 physical pad objects, including footprint origin, angle, layer, value, FPID and assembly attributes, plus pad number, position, size, net, angle, shape, corner radius, drill, type, layer set, solder-mask/paste overrides and local-zone connection. Exactly nine footprint pin projections differ: `U_ADC` and `C_ADC_CM1P/N`, `C_ADC_CM2P/N`, `C_ADC_CM3P/N`, `C_ADC_CM4P/N`. The other 331 footprints are exactly equal; seven of those are board-only (`FID1`–`FID3`, `H1`–`H4`), leaving 324 unchanged assembled references.

The nine changed projections equal the prior records only after the explicit ADR0027 transform: logical nets `ADC1P/N` exchange with `ADC4P/N`, `ADC2P/N` exchange with `ADC3P/N`, and the eight capacitor reference identities exchange 1↔4 and 2↔3 for each P/N leg. The untransformed projections are unequal. Thus the eight capacitor positions retain their physical pad/ground construction while their logical references follow the new association.

All 87 current and previous `part.yaml` records were compared. Only `02_parts/CS5308P-DN/part.yaml` differs, and removing its `layout` field makes the documents exactly equal. Manufacturer identity, package, pin, winding, polarity and electrical facts therefore remain unchanged. `parts_sha256` above is the owning 87-file digest; `design_rules_sha256` was computed with the supplied `design_rules_digest(current)` API.

## Fresh manufacturer groups and exact disposition

The immutable U_ADC blind report is `channel-adc-pin/report.md`, SHA-256 `e25fe802633973ef78f28486e0dfda946f0dfc9084ca0a13ce14094ea8cc928d`. Its original engineering verdict remains **QUESTION**: 49/49 manufacturer electrical identities, pin-1 corner, counterclockwise top-view winding, 12 pins per side, 48 numbered pads and one ground paddle all pass, but isolated manufacturer evidence cannot decide whether IN1..4 intentionally use ADC4..1 logical net names. This aggregate does not rewrite that original verdict.

The added design-owned context resolves that specific QUESTION. Accepted ADR0027 (`current/01_docs/decisions/0027-fixed-north-adc-channel-map.md`, SHA-256 `3f7fc0dcbda74d882172d5d0ae270cf515c8980326a9dba4269027895373311d`) states that north pod order 1–4 is physically reversed relative to CS5308P channels 4–1 and explicitly adopts the fixed permutation while preserving physical channel slots. Its machine-readable authority is `current/03_src/adc_channel_map.json`, identity `crow-carrier-channel-map-20260912`, SHA-256 `1640e8993f47658a46b2d1c90f9f8082c5a04c5339ca063b6a9efceeb1f41c23`. The accepted independent schematic review is `current/08_reviews/2026-09-12_channel-map_131e0dda_topology.md`, SHA-256 `f1bf59afe6dc980700634ae97ff939ab83a36cc0c781853ba70dd133e8a5491c`.

| U_ADC pins | Manufacturer identity | Exact board/dossier net | Design-owned association | Aggregate disposition |
|---|---|---|---|---|
| 39 / 40 | IN1N / IN1P | ADC4N / ADC4P | logical pod 4 → physical ADC channel 1, slot 0 | PASS; original QUESTION resolved as intentional |
| 41 / 42 | IN2N / IN2P | ADC3N / ADC3P | logical pod 3 → physical ADC channel 2, slot 1 | PASS; original QUESTION resolved as intentional |
| 45 / 46 | IN3N / IN3P | ADC2N / ADC2P | logical pod 2 → physical ADC channel 3, slot 2 | PASS; original QUESTION resolved as intentional |
| 47 / 48 | IN4N / IN4P | ADC1N / ADC1P | logical pod 1 → physical ADC channel 4, slot 3 | PASS; original QUESTION resolved as intentional |
| 13 / 14 | IN5N / IN5P | ADC5N / ADC5P | logical pod 5 → physical ADC channel 5, slot 4 | PASS; unchanged south association |
| 15 / 16 | IN6N / IN6P | ADC6N / ADC6P | logical pod 6 → physical ADC channel 6, slot 5 | PASS; unchanged south association |
| 19 / 20 | IN7N / IN7P | ADC7N / ADC7P | logical pod 7 → physical ADC channel 7, slot 6 | PASS; unchanged south association |
| 21 / 22 | IN8N / IN8P | ADC8N / ADC8P | logical pod 8 → physical ADC channel 8, slot 7 | PASS; unchanged south association |

The immutable common-mode capacitor blind report is `channel-cm-pin/report.md`, SHA-256 `53b1a15551555fbe48a82aae65f28f9c83dcf8b1dfc749201f10c8d4916c6bbf`. It passes all eight current dossiers and all 16/16 physical terminals: each Murata GRM1555C1H102JA01D is a nonpolar two-terminal 1005M/0402 capacitor with interchangeable end electrodes and no exposed pad. Each instance has one channel-net end and one GND end; no manufacturer winding or pin-1 convention applies.

`current-dossiers/subject.json`, SHA-256 `1420b8671ddfde036d34054949c84cd3b86fa0c9a847d28e410f814cd7a449d0`, binds the exact current board, pin BOM SHA-256 `6efb39c2f5af6df50aef6f48e0de777aff910c25fc80dd06193e95a8b1b7361f`, U_ADC dossier SHA-256 `2d0bb1d64a46023b01d05eaf233c45c4cd2b7417d07c159c0ff330376c86b5e6`, and capacitor dossier SHA-256 values: `C_ADC_CM1P ed273c9f94cc18dd0eb83c186fd5f1616aa0d2054c33ef8e19752be32a3ce595`, `C_ADC_CM1N c054134eac03bfa400834b535c17c9c5a43aa2bb59bcf4ee3a5aaae212842c32`, `C_ADC_CM2P 58074d98992e32f34d252311a8ae1ec540705bf48c5673ecf197027b55d064b8`, `C_ADC_CM2N 63360d0d8d1941b1f406edb0688cd905c9f0b672e2d34a1bf7da3142b58a115d`, `C_ADC_CM3P ce88eb2c64af1f75eca7e1b6ad3f8d76431076f3249fb76e292485520aa797ca`, `C_ADC_CM3N b7cd136a1b3ab39b595823d48591e715d755ed0e92bba4ad4a8d0cf4718e8225`, `C_ADC_CM4P 1f4d3013c2bfb6fca1405471cff54bfaabb9cf7bb3f042a79c1c6b6574893db4`, and `C_ADC_CM4N 064b9c36ff485d5982e9cb4b79d1b06fa88c0ccf548c16106f4ddb5fbc238735`.

The manufacturer-group denominators (49 U_ADC identities and 16 capacitor terminals) are evidence scopes inside the nine fresh references. They are distinct from the complete 1002-board-pad-object transfer denominator.

## Limits and order disposition

The accepted mapping is source intent, not physical capture evidence. Eight-channel impulse capture, map/digest metadata, serialized pod and cable identities, surveyed coordinates, stream epoch and rejection of missing, duplicate, swapped, inverted or unstable channels remain owed. Cable manufacture, crimp quality, installed polarity/continuity/keying, component body and silkscreen/render clearance, physical assembly, analog performance and first-article validation are outside this pin judgment.

The current board remains blocked by 27 hidden assembly locators, and `LAYOUT-001` retains its exhausted 3/3 routing-investigation spend. Simultaneous north-pad clearance, legal routing/vias, <=1 mm P/N spread, matching, quiet returns, filled inner-layer continuity, DRC, fabrication and release acceptance remain unproven. The SOUND pin verdict does not reopen routing, create a board candidate or authorize an order; `DO-NOT-ORDER` is mandatory.
