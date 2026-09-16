# Frozen schematic-render review witness

subject: crow-audio-carrier-v1 77d25f0dd1a44ca5139be80310e65417c17a2ec6  
date: 2026-09-07  
reviewer: fresh-context agent, schematic_render lens  
context-given: exact-source-and-primary-documents, no prior reviews  
source_commit: 77d25f0dd1a44ca5139be80310e65417c17a2ec6  
review_stage: pre-route  
review_kind: schematic_render  
design_verdict: DEFECTIVE  
order_verdict: DO-NOT-ORDER  
netlist_sha256: 32353f2259a5b903725e25bf54d192f9b2b5bc3a290e89d145a90e65400aba70  
parts_sha256: da40483f53767ef34e8d0b561eea11d36e6bc6c10162dcae50a9078cf5373e0d  
design_rules_sha256: 14603bc34e244ce702e97a3b14251090eeb88377107e26293fb6ace4d1d26fd9  
schematic_pdf_sha256: 9bd63701177f611b0822e30d6b8438e2c515522539007fa2502708e682ad7e89

## Verdict and boundary

The delivered PDF has understandable page partitioning, wired functional paths, and generally readable component identities and values. Nevertheless, it cannot receive the human-schematic acceptance: several distinct electrical nets are drawn through ground symbols, ground text, or another net’s ground downleg. The strongest case is the ADC configuration circuit on page 14, where the CFG4 conductor is visually superimposed on R_CFG1’s grounded connection.

These are confirmed presentation defects, not a claim that the exact electrical netlist shorts those nets. Consulting the netlist resolves the ambiguity for this reviewer; it does not make the delivered drawing unambiguous for its reader.

No placement, routing, release, or order permission is conveyed.

## Clocks and frozen-input verification

- First captured preparation clock: **2026-09-07T23:55:13Z**. Instruction reading began before this sample; an earlier exact launch timestamp was not captured.
- Artifact-review start and preflight: **2026-09-07T23:56:15.266479Z**.
- Evidence completion and final verification: **2026-09-08T00:02:49.424564Z**.
- Commissioned deadline: **2026-09-08T00:11:41Z**. The review reached a judgeable conclusion and finished before it.
- Strict `TaskEnvelope.from_json` parsing succeeded. `pipeline_execution.verify_input_packet` passed **4/4 packet items before and after**, with no reported failures.
- The frozen census passed **368/368 files before and after**, comparing both byte length and SHA-256.
- Independently recomputed subject identities matched **7/7 before and after**: normalized netlist, raw netlist, delivered PDF, native schematic, Circuit JSON, aggregate parts, and adopted design rules.
- Parts hashing covered **77/77 dossiers**, using the path-and-byte framing implemented by `pre_route_review_check.py`. Netlist and rule normalization used that module’s functions directly.
- Canonical envelope SHA-256: `b96468c308aab89332ad28126455e06e89765e88c2ee7b391ce0f36c51ee8b31`.
- Observed HEAD before and after was `7b823202f81db2d81ea73811947cd6b184e8a544`, not the named source commit. This witness binds the frozen source subject through the verified packet and exact artifact identities; it does not claim HEAD equaled the source commit.

No repository source, generated artifact, review, receipt, or status file was written. Temporary PDF rasterizations were written only under `/tmp`. No canonical TaskAttempt or token telemetry was fabricated.

## Measured visual coverage

The exact delivered PDF was rasterized and **all 19/19 pages were actually viewed individually**, including their complete boundaries, at 96 dpi. Landscape pages were viewed as 1200 × 810 images; page 4 used the corresponding portrait format. Detail inspection used 192-dpi crops and full-page rendering, plus 288-dpi crops where the ADC configuration collision required closer discrimination.

The full-page survey, rather than successful zooming or font/count tests, established the generally usable page structure. No physical print was examined.

Circuit JSON independently contained **299 source components, 299 schematic components, and 299 unique source references**. The 19 printed page counts sum to 299. These counts establish the population inspected, not pin-by-pin electrical acceptance.

| Page | Components | Actual full-page observation |
|---:|---:|---|
| 1 | 9 | Input → fuse → reverse-polarity stage → clamp/bulk path is visible. Clamp reference collision noted below. |
| 2 | 9 | Buck, bootstrap, output capacitors, raw hold-up and analog bead form a readable wired circuit. |
| 3 | 17 | Precharge, held capacitors, LDO, feedback and noise-reduction bank are locally understandable. Output-capacitor reference touches its rail. |
| 4 | 14 | Portrait partition makes both supervisors readable, but both CT conductors collide with ground graphics. |
| 5 | 10 | RC delay → Schmitt stages → discharge FET and LDO enable is understandable; local bypass ownership is visible. |
| 6 | 22 | Channel 1 connector → input capacitors → amplifier/filter → isolation → ADC labels is traceable. Switch ground-text collision present. |
| 7 | 22 | Channel 2 individually viewed; same functional sequence and switch collision. |
| 8 | 22 | Channel 3 individually viewed; same functional sequence and switch collision. |
| 9 | 22 | Channel 4 individually viewed; same functional sequence and switch collision. |
| 10 | 22 | Channel 5 individually viewed; VMID2 bias identification visible; same switch collision. |
| 11 | 22 | Channel 6 individually viewed; same functional sequence and switch collision. |
| 12 | 22 | Channel 7 individually viewed; same functional sequence and switch collision. |
| 13 | 22 | Channel 8 individually viewed; same functional sequence and switch collision. |
| 14 | 12 | ADC inputs, clocks, TDM, configuration and local bypass are identifiable, but configuration/ground drawing ambiguity is blocking. |
| 15 | 14 | Two external VMID divider/filter/follower paths and output isolation are clearly partitioned. |
| 16 | 12 | Two reference-filter banks and separate ADC VMID bypass banks are readable. |
| 17 | 9 | Interface clocks → buffer → source resistors is readable. An unexplained FSYNC_BUF wire tail remains. |
| 18 | 8 | Presence detection, Schmitt enable and TDM return are understandable, but OE_N crosses the buffer’s ground graphic. |
| 19 | 9 | Reset supervisor, monostable, timing network and FET path are traceable; output-net label overlaps the monostable ground symbol. |

No component body or substantive circuit was observed cropped by a delivered page boundary. Important active-part MPNs were generally readable. Explicit NC names and exposed pin stubs were visible for the unused LDO status output, unused logic pins, ESD pins, unused ADC data outputs, and unused interface-header positions. This is a presentation observation, not an independent audit of every sanctioned float.

## Findings

### SR77-01 — P0 — Distinct nets collide with ground graphics and imply false connections

This blocks the human-schematic gate. The following locations were observed in the delivered PDF; the exact netlist establishes that the colliding objects belong to different electrical nets.

| Page/ref | Rendered collision | Exact ownership resolving the ambiguity |
|---|---|---|
| 4, U_PWR | The CT downleg intersects the right edge of the local ground bar and passes through its GND text before reaching C_PWR_CT. | U_PWR.5 and C_PWR_CT.1 are **PWR_CT**; U_PWR.2 is **GND**. |
| 4, U_AUDIO | The same collision occurs below the second supervisor, beside the AUDIO_CT label. | U_AUDIO.5 and the timing-capacitor top nodes are **AUDIO_CT**; U_AUDIO.2 is **GND**. |
| 6–13, U_ISO1–U_ISO8 | The VDD-to-bypass conductor descends through the GND lettering immediately below each switch. The ground bar and supply conductor are closely stacked, making the apparent bypass ownership misleading. | U_ISOn.8 and C_ISOn.1 are **5V_LDO_HOLD**; U_ISOn.4/.9 and C_ISOn.2 are **GND**. All eight pages were individually viewed. |
| 14, R_CFG1/R_CFG4/U_ADC | The CFG4 vertical conductor occupies the same horizontal position as R_CFG1’s ground downleg. Between the CFG4 label and ground symbol, the distinct conductors are visually superimposed; CFG4 also passes through the ground bar and lettering. | U_ADC.10 and R_CFG4.1 are **CFG4**. R_CFG1.2 is **GND**. R_CFG4.2 is **3V3_ADC**. This is not merely a small-text issue: even the enlarged drawing suggests a connection absent from the netlist. |
| 14, U_ADC SPI pins | The SPI_CS supply route crosses the GND lettering beneath the grouped SPI pins. | U_ADC.38 is **3V3_ADC**; U_ADC.35/.36/.37 are **GND**. |
| 18, U_TDM | OE_N’s vertical conductor crosses the ground bar/text beneath the buffer. | U_TDM.1 and U_OE.4 are **TDM_OE_N**; U_TDM.3 is **GND**. |
| 19, U_RST2 | The left edge/bottom of the RESET_PULSE_H label plate overlaps the right portion of the local ground bar. | **RESET_PULSE_H** is the U_RST2.5 output net; U_RST2.4 is **GND**. |

Bounded upstream correction: change source-owned ground-label positions, pin arrangement or trace waypoints so unrelated conductors and label plates cannot intersect ground-symbol ink or lettering. On page 14, give the CFG4 route a genuinely separate corridor from R_CFG1’s grounded downleg. Preserve the electrical net assignments; do not “fix” the drawing by joining the nets.

The principal source owner is the `Ground` helper and associated chip arrangements, component poses and presentation paths in [schematic_presentation.tsx](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/03_tscircuit/src/schematic_presentation.tsx:164). The observed pattern is consistent with insufficient clearance around ground graphics; this causal attribution is an inference from the source and rendered ink, not a producer-internals proof.

### SR77-02 — P2 — Component references collide with nearby rail ink

These references remain decipherable, so they are recorded separately from the false-ground-connection blocker.

- **Page 1, D_QIN_GS:** the `12V_PROTECTED` horizontal conductor crosses the upper portion of the reference text. Its MPN remains readable below.
- **Page 3, C_LDO_OUT:** the `3V3_ADC` horizontal conductor touches/overlays the upper edge of the capacitor’s reference lettering.
- **Page 14, U_ADC:** the upper supply route crosses the `U_ADC` reference; the adjacent MPN remains readable.

Correction: move the reference/property rows or the nearby conductors in the source-owned presentation so the complete rendered text has visible clearance. Do not enlarge the whole page merely to preserve the same collision at another scale.

### SR77-03 — P2 — Unexplained dangling FSYNC_BUF wire tail

On **page 17**, the **FSYNC_BUF** connection between U_CLK.2 and R_FSYNC.1 has a vertical downward wire tail terminating in a short leftward segment without a component or functional annotation.

It does not prevent tracing the clock path, but visually suggests an unfinished connection. Remove the unused presentation tail, or explicitly identify its purpose if it represents intended document content. No electrical change is requested.

## Source and primary-document checks

Drawing ambiguities were resolved against the exact [netlist](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/netlists/crow_audio_carrier_v1.net) and the authored [electrical TSX](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/03_tscircuit/src/crow_audio_carrier_v1.tsx).

The local primary-document pin tables were also reopened for the two most direct control-versus-ground examples:

- TI SLVSD65A, PDF page 3: TPS3890 CT is pin 5; GND is pin 2. [Exact local PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/TPS389001DSER/TPS3890_SLVSD65A.pdf).
- TI SCES223U, PDF page 3: SN74LVC1G125 DBV OE is pin 1; GND is pin 3. [Exact local PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/SN74LVC1G125DBVR/SN74LVC1G125_SCES223U.pdf).

These limited primary checks support identity interpretation only. No second full electrical calculation review was performed.

## Temporary visual evidence

All images were rasterized directly from the exact delivered PDF, not generated from the native KiCad schematic.

Full-page images: `/tmp/carrier-render-77d25f0d-TkyKCG/page-01.png` through `/tmp/carrier-render-77d25f0d-TkyKCG/page-19.png`.

Principal collision evidence:

- `/tmp/carrier-render-77d25f0d-TkyKCG/p14-config.png`
- `/tmp/carrier-render-77d25f0d-TkyKCG/p14-detail.png`
- `/tmp/carrier-render-77d25f0d-TkyKCG/p4-supervisor.png`
- `/tmp/carrier-render-77d25f0d-TkyKCG/p4-audio.png`
- `/tmp/carrier-render-77d25f0d-TkyKCG/p6-iso.png`
- `/tmp/carrier-render-77d25f0d-TkyKCG/p18-tdm.png`
- `/tmp/carrier-render-77d25f0d-TkyKCG/p19-reset.png`
- `/tmp/carrier-render-77d25f0d-TkyKCG/p1-clamp.png`
- `/tmp/carrier-render-77d25f0d-TkyKCG/p3-ldo.png`
- `/tmp/carrier-render-77d25f0d-TkyKCG/p17-stub.png`

Additional inspected details: `/tmp/carrier-render-77d25f0d-TkyKCG/p5-nc.png` and `/tmp/carrier-render-77d25f0d-TkyKCG/p6-differential.png`.

Temporary images are not immutable archived evidence.

## Exclusions and unresolved work

No earlier review verdicts, root source-correction reports or earlier review reasoning were read. No PCB/layout/render, routing, thermal, fabrication, stock allocation, order-readiness, account, uploader or physical-test assessment was performed. No delegation occurred.

The unresolved work is upstream presentation repair of SR77-01, disposition of SR77-02/SR77-03, regeneration by the authorized source owner, and a new exact-PDF readability review. Recheck the complete delivered document after regeneration, including ordinary full-page appearance and the affected detail regions. Netlist consistency and successful generation alone cannot close these findings.
