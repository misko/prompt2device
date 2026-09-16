subject: crow-audio-carrier-v1 owned physical-label/source/locator candidate review
date: 2026-09-11
reviewer: Codex independent judgment agent /root/carrier_owned_source_review
completed_at: 2026-09-12T05:11:34.639663+00:00
context-given: FRESH; immutable 278-input packet; READ_ONLY source; scratch-only exports and checks
source_commit: 57df15a2
board_sha256: ef72e6d2f5400b481f397532a58784644b82bc88d5fa527f4c46b7a3356c822b
current_board_sha256: 0ab5b6dae425074f2515dc3c3d737e56f2292d83140590dca592b7b964e73090
review_kind: noncanonical D-BACK focused source/physical-label/locator-candidate review
source_candidate_verdict: SOUND
physical_label_verdict: SOUND
locator_candidate_verdict: SOUND
engineering_verdict: SOUND-FOR-FOCUSED-CANDIDATE-SCOPE
order_verdict: DO-NOT-ORDER
design_rules_sha256: unavailable for this partial noncanonical packet; no digest guessed

# Focused judgment

## Scope

This noncanonical review judges only the proposed preferred-offset source entries, the exact generated native candidate, the two newly visible physical labels, and the proposed 25-exception locator candidate. It does not generate a board, edit live source, accept current placement, assess routing, or authorize release or ordering. The 306 unchanged visible labels and unchanged native regions inherit prior inspection only because exact native comparison established their identity; this review makes no expanded full-render claim.

## Source candidate — SOUND

The floorplan change adds exactly `R_DUMP_TIME1: [[1.1, -1.6]]` and `R_VMID2_TOP: [[1.5, 4.1]]` to the existing refdes policy and adds no priority list. The locator source retains the 25 ceiling and 22 exceptions byte-for-byte, removes `R_DUMP_TIME1`, `R_FILT2P`, and `R_VMID2_TOP`, and adds exact identities for `C_VDDA2_10N`, `R_FILT1P`, and `R_VMID2_BOT`.

Independent native comparison found only the two expected `Reference` field changes. The candidate has the supplied 340 footprints and 1002 native pads; its 25-ref hidden set removes exactly `R_DUMP_TIME1` and `R_VMID2_TOP` from the current 27. The supplied exact projection establishes unchanged footprints, pads, pad-net identity, zone connection modes, and the 380 unchanged inputs. Supplied owning evidence reports 0 DRC violations, 499 capped unrouted connections, 0 parity findings, and placement DRC PASS. No part, pad, net, zone, or other reference-field change is claimed.

## Physical labels — SOUND

`R_DUMP_TIME1` is legible at 0.55 mm / 0.1125 mm stroke, rotated 90 degrees. In the native F.Silk/F.Fab/pad crop, the label occupies a distinct gap immediately above-left of its own vertical 0402 and remains well separated from the adjacent identical `R_DUMP_TIME2`. Its owner distance is 1.94165 mm versus 3.42527 mm to the nearest other part. The local orientation and spacing make the physical association unambiguous and accessible for assembly lookup.

`R_VMID2_TOP` is legible at 0.55 mm / 0.1125 mm stroke, at 0 degrees. The native crop shows it below and to the right of the correct member of the adjacent VMID2 resistor pair, with the complete `_TOP` suffix readable. Its owner distance is 4.36578 mm, less than 4.87032 mm to `C_VMID2_EXT_10U`; it is also visibly displaced toward its own right-hand resistor rather than the left-hand `R_VMID2_BOT`. The combination of text identity, lateral alignment, and clear whitespace resolves the otherwise similar bodies. No collision, crowded-glyph, or wrong-body ambiguity is visible.

The rejected priority and phase-2 candidates remain rejected; this judgment applies only to board `ef72e6d2f5400b481f397532a58784644b82bc88d5fa527f4c46b7a3356c822b`.

## Locator candidate — SOUND

The independent exact checker passes 333/333 unique locator references, 995 assembled pad objects, 25 configured exceptions, and 25/25 page refs. Hidden, configured, and page-ref sets are the same 25 identities. Every omission matches ref, value, MPN, LCSC, X/Y, rotation, side, and all pad-number/net pairs. The 51 BOM rows expand to 300 unique fitted refs; the CPL contains the same 300 refs; the other 33 locator refs are the expected non-BOM set. The manifest binds the exact candidate board and all 28 unique locator members.

I visually inspected the full 25-page contact sheet and the full pages for all three additions: page 5 `C_VDDA2_10N`, page 17 `R_FILT1P`, and page 24 `R_VMID2_BOT`. Each has a readable title and identity, whole-board marker, enlarged exact body, unambiguous arrow/circle target, numbered pads, nets, coordinates, rotation, LCSC/MPN, board hash, and page denominator. No target ambiguity was found.

## Remaining work

Normal canonical renewal, full 337-source checks, current-pin validation, full render review, layout and route gates, and release gates remain owed. LAYOUT001 remains 3/3 spent. This report does not accept the current live placement and does not authorize fabrication.
