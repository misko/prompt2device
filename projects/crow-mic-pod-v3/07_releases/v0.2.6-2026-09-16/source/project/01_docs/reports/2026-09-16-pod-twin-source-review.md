---
schema: 1
kind: pcb-human-report
report_id: 2026-09-16-pod-twin-source-review
title: Pod native representation source review
subtitle: Diode contact evidence and exact manual/native model selection
project: crow-mic-pod-v3
date: 2026-09-16
status: REVIEWED
evidence_status: MIXED
---

## Executive conclusion

Independent source verdict SOUND; order verdict DO-NOT-ORDER. This admits only the exact representation-source delta, not a final twin or board release.

## Question and scope

Review D1/D2 terminal evidence, J1 manual-body declaration and U2 explicit native selection; electrical source and physical board geometry are unchanged.

## Evidence boundary

**MEASURED** delivery PASS and exact source identities are retained in the linked archive. **OWED** final twin/overlay, renewed source reviews and release gates.

## Findings

**CITED** manufacturer figures and **MEASURED** native terminal tests support the proposed source. The verbatim independent report follows; it distinguishes supplied measurements from direct inspection.

# Independent pod representation-source review

design_verdict: SOUND
order_verdict: DO-NOT-ORDER
reviewer: pod_twin_source_review
completed_at_utc: 2026-09-16T15:06:02Z
subject_raw_sha256: 329574f6bc79cb35e025e1d3e5fe8102d86874cef3d6348f2c0c2c6abecc532c
subject_semantic_sha256: e2e239547de6768fc9be48cee5b0c0a82de33859f3dc445a0446e906048b1698

## Scope and exact candidate identities

Fresh source-level review of the proposed D1/D2 land and terminal-envelope adjudications, D1 polarity/model-terminal semantics, J1 manual-body declaration, and U2 `native_representation.reason: vendor_model_absent` selection. Existing reviews were treated as context rather than acceptance. No physical geometry, electrical source, pin map, footprint/model transform, produced-twin acceptance, or release acceptance was reviewed or changed.

Exact proposed rule identities reviewed:

- `03_src/rules/assembly.yaml`: `f7db1baca39a8af7511173de67ff8c90aed1e3f2a06173e7a733bdb219866b07`
- `03_src/rules/twin_adjudications.yaml`: `3fc65e97c60047250f574c2f12bb5a124dea20672fe18b6e4da74bc11376f906`
- `03_src/rules/model_registration.yaml`: `c54b1068479a3cec655e8ea2233ac58dd68489188a908ca8a46b1556d92ad55f`
- Bound terminal helper `03_src/tests/check_native_terminal_envelope.py`: `6397be3580341914eba15e09da73d18dc9934cbc5ba1a5a1c6363533d9780835`

The candidate's `reviewer: pod_twin_source_review` and `reviewed_on: 2026-09-16` fields are accepted because this review is SOUND.

## Evidence and findings

### D1

I independently inspected Vishay document 88711 revision 07-May-2024 page 3, exact PDF SHA-256 `49c11fe1f333fda1bcdacc72754927dda4ee5bf977bf88d3c46eb1cd6ffe9277`. The figure states mounting-pad length at least 1.52 mm, width at least 1.68 mm, gap at most 1.88 mm, and marks the 5.28 mm mounting span as reference. The native 2.50 x 1.80 mm lands with 1.50 mm gap satisfy those requirements. The terminal dimensional union `0.945..2.640 mm` radially and `+/-0.825 mm` laterally is a sound conservative interpretation of the package limits and is contained by the actual rounded copper.

The supplied helper reproduced a minimum signed margin of `0.066561 mm` with exit 0. Its deliberately shrunken-pad hostile control returned `-1.274707 mm` with nonzero exit, so the predicate does not vacuously pass. Supplied mesh measurements place the metallic terminal projection within native copper with `0.250014 mm` minimum margin and its terminal centers within 4 nm of the native `+/-2.0 mm` land centers. The primary figure says the band denotes cathode; the supplied mesh places that band on negative X, corresponding to native pad 1 / `VIN_PROTECTED`. The raw 0.570 mm catalog numbered-pad residual remains explicitly preserved under `PAD-MISMATCH`; the adjudication does not erase it or claim process qualification.

### D2

I independently inspected Littelfuse SMBJ revision JC.07/04/25 v4 page 5, exact PDF SHA-256 `d7df155be4b1f612085401e8c946f065e284d65a0e7de22b9225a7b73946e51b`. The figure supports J/L at least 2.160 mm, I at least 2.260 mm, K at most 2.740 mm, and package dimensions G `5.210..5.590 mm`, E `0.760..1.520 mm`, A `1.930..2.200 mm`. The native 2.50 x 2.30 mm lands with 1.80 mm gap satisfy the stated land requirements. The resulting contact union `1.085..2.795 mm` radially and `+/-1.100 mm` laterally is contained by the rounded copper.

The helper reproduced a minimum signed margin of `0.039703 mm` with exit 0. Supplied cached metallic-mesh measurements independently report `0.099964 mm` minimum native-copper margin. The adjudication is limited to land/contact geometry and does not claim solder-process qualification.

### J1 manual body

The assembly declaration keeps J1 in `not_assembled`, `reason: user_supplied`, and `on_bom: false`, while declaring `twin_body.source: board`. The board resolves the Wurth model, whose exact SHA-256 is `3f902b89d4bd756b121be056782deff312efb127c9c48f2c798ebd6db0e59f49`; this matches the declared `j1_wurth_615008160221_official_step` registration group. The declaration describes only the exact manually installed part and preserves soldering, cable-fit, continuity, shell-isolation, assembly, and first-article holds. This is a sound representation declaration and does not place J1 into machine assembly.

### U2 native representation

The declaration uses the supported closed schema implemented by `native_representation.py` and passes its declaration, source-file, fetched-vendor-footprint, and zero-vendor-model checks. The exact fetched C16430 footprint SHA-256 is `89faf406a20a9a9b03fd6a033706c01ae2ab0d41ecb758fba627e04767dc31c3`; it has nine pads and no model clause. The native footprint SHA-256 is `91eb6873b082e819ce587a0ac0ddb3bf22cd8d5844fffe590110cb3907873fa4`.

TI datasheet SBVS121E pages 33-35, exact SHA-256 `0a5e198966ab05ebb39f4512355352c0946af5f52e1fbd2e9ec554041123a126`, show the DGN0008D 3 x 3 mm PowerPAD VSSOP package and its 0.65 mm pitch, eight signal lands, and 1.57 x 1.89 mm exposed pad. The unmodified TI WEBENCH file identifies itself as `DGN0008G_ASM`; its exact SHA-256 is `9751a8fa8744b8d50553223b504f942a373396d134eccee1f86c69b545fffc10`, matching the declaration, provenance, and registration group. Treating the official DGN0008G STEP as the nominal visual package representation for the exact DGN0008D land pattern is supported for the declaration's limited purpose.

The signed registration receipt binds the board, footprint datum, model, transform, contract, and tool. It reports center delta 0.000 mm, 13/13 attachment centers inside, minimum pad margin 0.303 mm, zero courtyard outward extent, and 0.903 mm beyond the 3 x 3 mm F.Fab body due to the gull-wing leads. I inspected the supplied top overlay and both orthogonal side renders. They are consistent with a front-mounted package and the report's measured front-side fraction `0.893637`, which exceeds the explicit conservative `0.85` pixel-side threshold. This threshold is representation evidence only; it does not establish full-volume exclusion, electrical correctness, thermal performance, solder-joint quality, assembly-process fitness, or first-article performance.

## Deficiencies and blockers

There is no blocker to adopting these exact source declarations and adjudications.

Nonblocking next-release work remains mandatory: regenerate the relocatable twin from the adopted exact rules; rerun native-representation delivery/relocation and hostile-input controls; regrade P-MODEL-REG, P-MATE-REG where applicable, mounted-body coverage, polarity, catalog pad/rotation correspondence, and same-camera A-RENDER on the produced twin; renew stale rule-bound checkpoints and continued-context review records through their owners; and inspect the uploader/order preview and all existing first-article holds. The 0.85 signed-side threshold and the diode positive margins must not be promoted into soldering, thermal, enclosure, process, or production qualification.

This review accepts only the exact representation-source delta above. It makes no final digital-twin, PCB-release, procurement, or order acceptance claim. `DO-NOT-ORDER` remains in force.


## Recommendations

Adopt the exact reviewed YAML, produce a new twin, and rerun all affected owners. Keep minor prose cleanup in DEFICIENCIES.md.

## Validation plan

Require U2 native-representation receipt, signed model registration, both same-camera overlays, positive body denominator, complete release review and rehearsal. Retain physical first-article and sourcing holds.

## Source register

- [Exact packet, review and delivery closure](../journal/b7195e483182ee04df672dda06ef5e2c8852322b7da70654e723f947d11a054b.tar.gz).
- Primary PDF and model hashes, page numbers and exact source hashes are listed in the verbatim report above.
