subject: crow-mic-pod-v3 pre-route a44b769b
date: 2026-09-13
source_commit: abbae71edeab8d1addf9a8912d64c7c23c88ec7e
context-given: zero-context; exact native part-group dossiers and SHA-selected primary PDFs only
source_report_sha256: 62358161c20c53eef11eb614ac57ebfc923643e36c90c019b93299a75d0fd51b
source_evidence_archive: 01_docs/journal/00a00b04cd301851a7c06d4dce11be790b793e412fd4cb3691fa21f07540ad59.tar.gz

review_stage: pre-route
review_kind: pin
reviewer: /root/rj45_pin_pod_analog_approved (actual fresh independent agent)
context: FRESH
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: a44b769b1a5ad5fa959b476bd30f91a64aeaba9ad64d7868fa4e60ffbb62ee48
parts_sha256: adf3f7221a131e270f963fab153a2e2f56262932f1e272af9cbc0e4814d5c8a6
design_rules_sha256: 02c4ed58432368b92e3019a06bf20c137dbf90765af16c96c458790e88d54a9f
subject_raw_sha256: eb4c949e854392aeb4ed0f266bb5ed41f4742197118ea5a38815ec7fa91280ef
subject_semantic_sha256: 2e4c182741642c8439045f5dd58f178a439890fcc3ea7519bc17e5def8eb6588

Limited group coverage: U1 and U2 only, every commissioned instance checked. SOUND means these two parts pass the commissioned pin/function/net-kind review. No whole-board acceptance or permission to order. Board/parts/rules hashes above are immutable subject metadata, not independently reviewed conclusions.

## U1

VERDICT: PASS

Primary PDF: `projects/crow-mic-pod-v3/02_parts/OPA1679IDR/opa1679.pdf`; SHA-256 `4072daad4ebc4ec9a74ba6547d721b05db8d0cfc12924bda79e828271aeaec3b`.

Sources: PDF page 5 Figure 5-5 and Pin Functions: OPA1679; PDF pages 44/45 D0014A package outline/example board layout. PDF page 29 package option addendum maps OPA1679IDR to SOIC (D), 14 pins.

Expected D SOIC14: 7 leads per side, pin1 upper-left, CCW top view, no EP or fused pins. Observed 14 numbered native pad rows, 14 unique identities and centers; pins1..7 x=-2.48 and pins8..14 x=+2.48; pin1=(-2.48,-3.81); signed area -37.7952 mm2 in +y-down frame; CCW. No missing or duplicate pins or alias declarations.

Some dossier side labels say N/S because of directional sectors; actual coordinates establish two vertical lead rows and correct winding. Native pitch is 1.27 mm, agreeing with the package. The native 1.95 x 0.60 mm lands centered 4.96 mm apart span the manufacturer lead locations; no identity or mirror defect. D package has no thermal pad; QFN pad requirements are not applied to this SOIC.

- U1 pin 1 (OUTA): expected reference-drive output; observed `VREF` — PASS.
- U1 pin 2 (IN_A_NEG): expected reference-buffer feedback, same net as OUT A; observed `VREF` — PASS.
- U1 pin 3 (IN_A_POS): expected reference input; observed `VREF_RAW` — PASS.
- U1 pin 4 (V_PLUS): expected positive supply rail; observed `5V_QUIET` — PASS.
- U1 pin 5 (IN_B_POS): expected signal/reference input; observed `VREF` — PASS.
- U1 pin 6 (IN_B_NEG): expected feedback sense; observed `PRE_FB` — PASS.
- U1 pin 7 (OUTB): expected signal output; observed `PRE_OUT` — PASS.
- U1 pin 8 (OUTC): expected signal-drive output; observed `OUTP_DRV` — PASS.
- U1 pin 9 (IN_C_NEG): expected feedback sense; observed `OUTP_FB` — PASS.
- U1 pin 10 (IN_C_POS): expected signal/reference input; observed `VREF` — PASS.
- U1 pin 11 (V_MINUS): expected lowest supply rail; observed `GND` — PASS.
- U1 pin 12 (IN_D_POS): expected signal/reference input; observed `VREF` — PASS.
- U1 pin 13 (IN_D_NEG): expected buffer feedback, same net as OUT D; observed `SPARE_BUF` — PASS.
- U1 pin 14 (OUTD): expected buffer output; observed `SPARE_BUF` — PASS.

## U2

VERDICT: PASS

Primary PDF: `projects/crow-mic-pod-v3/02_parts/TPS7A4901DGNR/tps7a49.pdf`; SHA-256 `0a5e198966ab05ebb39f4512355352c0946af5f52e1fbd2e9ec554041123a126`.

Sources: PDF page 4 Section 5 DGN top-view pin drawing and Pin Functions; PDF pages 33/34 DGN0008D package outline/example board layout. PDF page 24 package option addendum maps TPS7A4901DGNR to HVSSOP (DGN), 8 leads.

Expected DGN: 8 leads plus separate PowerPAD9; 4 leads per side, pin1 upper-left, CCW top view. Observed 9 numbered native pad rows, 9 unique identities and centers; pins1..4 x=-2.15, pins5..8 x=+2.15; pin1=(-2.15,-0.97); peripheral signed area -8.342 mm2 in +y-down frame; CCW. Center pad9 GND. No missing or duplicate pins or alias declarations. Four unnumbered paste/mechanical pads reported omitted: 13 total pad objects reported, but 9 electrical identities independently counted.

The native 90-degree placement rotation is undone in the dossier and does not mirror the package. On PDF page 33, the upper package drawing has pin1 upper-left; lower drawing shows underside exposed pad with pin1 lower-left. Board top-view numbering uses the upper drawing and PDF page34 land pattern. Native center pad9 is 1.57 x 1.89 mm, consistent with the DGN0008D exposed-pad land, and connected to GND as permitted. Rounded lead coordinates agree with 0.65 mm pitch. Physical PowerPAD identity9 is retained separately from GND pin4.

- U2 pin 1 (OUT): expected regulated output rail; observed `5V_QUIET` — PASS.
- U2 pin 2 (FB): expected feedback divider/sense node; observed `LDO_FB` — PASS.
- U2 pin 3 (NC): expected open or ground; observed `unconnected-(U2-NC-Pad3)` — PASS.
- U2 pin 4 (GND): expected ground; observed `GND` — PASS.
- U2 pin 5 (EN): expected enable logic; may connect to IN; observed `VIN_PROTECTED` — PASS.
- U2 pin 6 (NR_SS): expected noise-reduction capacitor node; observed `LDO_NR` — PASS.
- U2 pin 7 (DNC): expected no electrical connection; observed `unconnected-(U2-DNC-Pad7)` — PASS.
- U2 pin 8 (IN): expected input supply rail; observed `VIN_PROTECTED` — PASS.
- U2 pin 9 (POWERPAD): expected open or ground thermal pad; observed `GND` — PASS.

## Scope and retained evidence

Exactly one instance of each part is commissioned; same-part cross-instance symmetry is not applicable. U1 channels A/D have matching output/inverting-input buffer nets; B/C have corresponding output and feedback net kinds. All 23 physical electrical identities are individually retained.

U2 NC pin3 and DNC pin7 carry native `unconnected-(...)` markers, consistent with no-connect intent. These markers are not evidence of a routed external connection. This review accepts per-pin net kinds and does not establish hidden topology, required output/NR capacitor presence or values, rail magnitudes, or analog loop behavior. No pin/function mismatch or required pin-review QUESTION was identified.

Independent pin derivation was recorded from source images before dossier content was read. All six inspected PNGs, extracted primary text, native dossier copies, exact input digests, derivation, measured rows, methods, finite subprocess commands/raw logs/runtime, report and evidence JSON are retained in evidence.tar.gz. Whole PDFs remain in the digest-bound frozen input packet. Every envelope input is size/hash verified before and after review. The three checks in result.json describe complete honest handback, not whole-board engineering acceptance.
