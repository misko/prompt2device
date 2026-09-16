# Crow audio carrier v1 — canonical pre-route physical-pin continuity review

subject: crow-audio-carrier-v1; raw_sha256 83d753dcadb0eb31dda7a0e8f30121568f3c055a148d78f099cb182969357eb7; semantic_sha256 5372a3dac8b654ca45aa2b338ce471161987df9125cd85a4a1fc34a78bba0cd7
date: 2026-09-12
reviewer: Codex independent judgment agent /root/carrier_owned_pin_review
context-given: FRESH; immutable prior canonical manufacturer-pin aggregate; exact previous/current native boards; all current/previous part.yaml dossiers; accepted ADR0027 and channel-map authority; READ_ONLY packet
source_commit: b9d77ca73ac2b7eff4111e07bd8a8a0d6376d22e
review_stage: pre-route
review_kind: pin
board_sha256: ef72e6d2f5400b481f397532a58784644b82bc88d5fa527f4c46b7a3356c822b
parts_sha256: bd5dc4f2092cbf0b4a56d07eeff8d7a6ce9d727eaaaef7d40be68318a88bb285
design_rules_sha256: 53529b7c990d7a8313be7515483aaff9d5b92f2bf8f4b8b34c4153b39aac9b23
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
completed_at: 2026-09-12T06:26:30Z
actualcompleted_at: 2026-09-12T06:26:30Z
task_identity: task_id=owned-pin-review; run_id=owned-pin-review; input_handoff_id=owned-pin-review; stage_id=KICAD-PLACEMENT
envelope_sha256: 44b89368d51579c5b9ebb0b46ade368776ef6744169989149deb7089b6400eb6
reviewer_id: /root/carrier_owned_pin_review
reviewer_provenance: independent judgment; FRESH context; no child agents; read-only exact-board/source continuity review
raw_subject_sha256: 83d753dcadb0eb31dda7a0e8f30121568f3c055a148d78f099cb182969357eb7
semantic_subject_sha256: 5372a3dac8b654ca45aa2b338ce471161987df9125cd85a4a1fc34a78bba0cd7
prior_pin_witness_sha256: 79a8bafd73f9422f09959cd709338d48c0657dd6d4ec1dd7e572cc2735a2c769
previous_board_sha256: 0ab5b6dae425074f2515dc3c3d737e56f2292d83140590dca592b7b964e73090
native_pin_projection_sha256: a913246f18d9ea856430b3d767dfd3840d819de1870755ead2083dfc2cbc24bb
native_full_projection_sha256: a8a5c2261ea1ef587097a6b127b4ed40eb427ad20ea2c97a72181fac47d1dff4
manufacturer_identity_projection_sha256: ceac9e4411c0d0817e9bd97c1842679ee5ddbb931a766de7c15783c4a92f122e
channel_map_sha256: 1640e8993f47658a46b2d1c90f9f8082c5a04c5339ca063b6a9efceeb1f41c23
locator_manifest_sha256: 503e9326edf22ccd65e05d7aa23d50aba9fb261d81556937bc00100066fbcacd
locator_reviewed_refs: ["C_AUDIO_CT2","C_FILT1_10U","C_FILT2_10U","C_PWR_CT","C_VDDA2_10N","C_VMID1_470N","C_VMID1_4U7","C_VMID2_470N","C_VMID2_4U7","R_ADC_BOT","R_ADC_PD1P","R_ADC_PD6N","R_ADC_TOP","R_AUDIO_PD","R_AUDIO_PU","R_DUMP_TIME2","R_FILT1P","R_IN6N","R_PRE_G","R_PWR_BOT","R_PWR_TOP","R_VMID1_BOT","R_VMID1_TOP","R_VMID2_BOT","R_X6N"]

## Judgment

The exact current board is **SOUND** for the pre-route physical-pin lens. Coverage is complete for 333/333 assembled references. All 333 manufacturer judgments are inherited from the prior canonical aggregate under fresh proof that every current electrical pin/source fact is unchanged. This review performed no fresh manufacturer-drawing inspection and does not enlarge the prior inspection scope. The prior aggregate's original 324 inherited plus nine then-fresh attribution remains exactly as written, including its U_ADC manufacturer-only **QUESTION** and its design-context resolution under ADR0027.

The inherited authority is `supporting-witnesses/2026-09-12_0ab5b6da_aggregate_pin.md`, SHA-256 `79a8bafd73f9422f09959cd709338d48c0657dd6d4ec1dd7e572cc2735a2c769`, bound to previous board `0ab5b6dae425074f2515dc3c3d737e56f2292d83140590dca592b7b964e73090`. Its manufacturer evidence covers the complete 333-reference assembled population and retains its original report lineage and limitations.

## Fresh exact native and source continuity proof

An independent bounded `pcbnew` comparison loaded hash-verified scratch copies of the previous and current boards. It keyed 340/340 footprints and 1,002/1,002 physical pad objects. The compared footprint projection includes reference, value, Manufacturer Part Number/property map, schematic path, origin, rotation, side/layer, package/FPID and attributes. The pad projection includes pad number, shape, size, absolute location, layers, net, orientation, drill, pad attribute, electrical pin function/type, mask/paste overrides, local zone connection and thermal parameters.

The electrical/native pin projection has zero differences and the same SHA-256 on both boards: `a913246f18d9ea856430b3d767dfd3840d819de1870755ead2083dfc2cbc24bb`. Exactly two display-field differences exist, both expected: `R_DUMP_TIME1` and `R_VMID2_TOP` change only their `Reference` text position/orientation/visibility. No Value field, footprint property, footprint geometry, pad property, pad net or local-zone-connection value changed. The current full projection, including these display fields, is `a8a5c2261ea1ef587097a6b127b4ed40eb427ad20ea2c97a72181fac47d1dff4`. The seven board-only references are `FID1`–`FID3` and `H1`–`H4`; the other 333 are assembled.

All 87 previous/current `02_parts/*/part.yaml` paths were compared byte-for-byte and semantically. There are zero byte, semantic or manufacturer-identity differences. The explicitly recomputed identity projection covers MPN, manufacturer, type, value, status, datasheet binding, package, footprint, escape, pins, limits, gotchas and verified fields and hashes to `ceac9e4411c0d0817e9bd97c1842679ee5ddbb931a766de7c15783c4a92f122e`. This is direct source equality, not an inference from the file count. The owning 87-file digest is `bd5dc4f2092cbf0b4a56d07eeff8d7a6ce9d727eaaaef7d40be68318a88bb285`.

The current semantic design-rule digest was independently computed with the owning `pre_route_review_check.design_rules_digest(project)` API as `53529b7c990d7a8313be7515483aaff9d5b92f2bf8f4b8b34c4153b39aac9b23`. It correctly differs from the prior report because the locator identities changed; no prior digest metadata was restamped.

## Channel identity continuity

The current `adc_channel_map.json` remains SHA-256 `1640e8993f47658a46b2d1c90f9f8082c5a04c5339ca063b6a9efceeb1f41c23`, ID `crow-carrier-channel-map-20260912`. Fresh native extraction proves all eight P/N identities:

| Logical pod | Physical ADC channel | U_ADC pins | Exact current nets | Disposition |
|---:|---:|---|---|---|
| 1 | 4 | 48 / 47 | ADC1P / ADC1N | PASS |
| 2 | 3 | 46 / 45 | ADC2P / ADC2N | PASS |
| 3 | 2 | 42 / 41 | ADC3P / ADC3N | PASS |
| 4 | 1 | 40 / 39 | ADC4P / ADC4N | PASS |
| 5 | 5 | 14 / 13 | ADC5P / ADC5N | PASS |
| 6 | 6 | 16 / 15 | ADC6P / ADC6N | PASS |
| 7 | 7 | 20 / 19 | ADC7P / ADC7N | PASS |
| 8 | 8 | 22 / 21 | ADC8P / ADC8N | PASS |

This preserves the prior manufacturer's 49/49 CS5308P physical identities and the earlier 16/16 common-mode capacitor terminal judgments without claiming either was freshly inspected here. The original ADC blind report's channel-name QUESTION remains a truthful manufacturer-only result; accepted design-owned mapping context resolves the association for this aggregate.

## Visual inspection and limits

I inspected the exact-current native top render and populated twin top at their supplied full resolution. The central ADC, eight repeated north/south analog chains, connector ordering, and current two moved visible references are coherent with the extracted native identities. These images corroborate current-board identity and physical organization; pixels do not replace the complete keyed pin comparison.

This review does not judge generation, route feasibility or realized copper, DRC, return-plane continuity, matching, thermal or analog performance, render completeness, physical mating, fabrication, assembly, release or first article. Physical eight-channel capture and its map/digest/serial/coordinate/epoch evidence remain owed. Locator and physical-assembly limitations remain governed by their own reviews. The order verdict is therefore **DO-NOT-ORDER**.
