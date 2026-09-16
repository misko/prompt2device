# Independent pre-route rendered-schematic witness

review_kind: schematic_render
review_stage: pre-route
design_verdict: DEFECTIVE
order_verdict: DO-NOT-ORDER
date: 2026-09-07
reviewer: Codex independent agent /root/carrier_schematic_corrected
fresh_context: yes; no previous reviews or parent transcript were read
review_started_utc: 2026-09-07 19:35:28 UTC
review_deadline_utc: 2026-09-07 19:45:28 UTC
witness_written_utc: 2026-09-07 19:45:48 UTC
budget_note: visual work and hash recheck finished by 19:41:23 UTC; witness persistence exceeded the deadline by 20 seconds
pages_reviewed: 6/6
components_accounted: 206/206
native_component_count: 206
native_node_count: 601
native_net_count_including_no_connects: 171
parts_dossier_count: 62
schematic_pdf_sha256: dc23165096141171ee5a33ec711b4515613def66e9ed53d3204dbe29edab9470
circuit_json_sha256: 4abfd28e0ee7ed4149d78aa5d44850962704b794ec99f612ce5db27d374a5470
netlist_sha256: 01abbcf8345dafff98b76cd53b3c75b5c86661a4d0b2e2be642bc6d78fd5a265
parts_sha256: 82a2b2853eaa520252dc67e53371bf8559f161146c49a4068026e4e62ed00ebb
design_rules_sha256: 3c66fafe15df75ae062c19a6e92dc6e1f708689a88fcb3808b9d2453a62a6fc9

## Subject and method

The human subject is exactly `03_tscircuit/build/schematic.pdf`, six pages,
from the bound `03_tscircuit/build/circuit.json`. The independent native
cross-check is `06_build/netlists/crow_audio_carrier_v1.net`. Project-relative
paths in this witness refer to
`/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1`.

I read the PCB-design and KiCad skills, the complete review-and-publication
procedure, execution graph, relevant schematic-generation review boundary,
BRIEF and ADR-0007. This is a public-information, physically unqualified
prototype design review. Physical fit, reset timing, analog, power/fault and
MCH image/operation qualification remain first-article/COTS obligations. Their
absence is not the reason for this DEFECTIVE verdict. No tested hardware or
purchase authorization is inferred.

Every page was freshly rasterized with `pdftoppm -png -r 160` into
`/tmp/carrier-schematic-fresh-Rp4aU7/` and individually opened with
`view_image`. Additional direct PDF crops at 300, 360, 480, 600 and 720 dpi
were opened, including enlarged views of all eight analog rows. The verdict
is pixel-based, not text-only. PDF text extraction only supplemented inventory:
all expected references occur on their circuit-JSON-owned page. Native and
source sets each contain exactly 206 components, with no missing/extra refs.

Hashes use the actual `pre_route_review_check.netlist_digest` and
`design_rules_digest` functions. The parts hash uses the exact checker
algorithm: sort `02_parts/*/part.yaml`, concatenate each project-relative POSIX
path, NUL, exact file bytes, NUL, then SHA-256. All five subject hashes were
rechecked at 19:41:23 UTC and remained unchanged. No source, PDF, netlist or
board was modified by this reviewer; only this requested witness was written.

## Actionable findings

The six functional blocks are intelligible and complete, but the current PDF
has actual annotation/geometry collisions. Zoom does not remove them. The
following are pre-route readability blockers requiring source/renderer repair,
regeneration and fresh exact-subject review. They are not claims that the
native netlist contains the apparent graphic shorts.

### SR-1 — Boxed labels and resistor values collide with their own graphics

Across all six pages, the upper outline of inspected boxed net labels runs
through glyph bodies instead of enclosing the text. Examples: page 4 CFG1,
ADC4P and ADC_RESET_N; page 6 MCH_MCLK, TDM_OE_N and RESET_PULSE_H.
Resistor values overlap the lower resistor stroke: page 6 R_MCH_MCLK_PD/10kΩ,
R_MCH_SENSE/300Ω and R_TDM/33Ω; the same treatment occurs in analog rows.

Every boxed-label exemplar inspected has this defect, including left/right
outlines and the rotated U_BUCK power label. It is NOT literally every label
shape: stem-style VMID/VMID_BUF labels lack the enclosing-edge defect. The JSON
contains 387 schematic-net-label records; I do not claim individual pixel
grading of all 387. Repeated affected examples on all six pages establish the
defect. Correct text baseline/outline alignment and passive value clearance.

Evidence in the fresh raster directory: `p4-adc-4.png`, `p6-clocks-6.png`,
`p6-enable-6.png`, `p6-pulse-6.png`. Reproduce the ADC detail with
`pdftoppm -f 4 -l 4 -png -r 360 -x 1000 -y 420 -W 1000 -H 2090`
and clock detail with
`-f 6 -l 6 -png -r 300 -x 175 -y 520 -W 1620 -H 460`.
Coordinates are raster pixels from upper-left at the specified dpi.

### SR-2 — Power-entry graphics falsely suggest fuse/PFET continuity

Page 1's green 12V_PROTECTED route lies along F_IN's top body border. At its
right end, the source-pin interconnection reaches the graphic location of the
pointed tip of F_IN's 12V_FUSED output label beside Q_IN.S2. This appears to
join the fuse output to the PFET source group despite their differing labels.
It is a route/body and route/label collision, not an ordinary open-space
crossing. Nearby, C_BUCK_IN's protected-input label occupies D_IN's anode/GND
routing region, further weakening the protection story.

Native distinction: J9.1 and F_IN.1 are 12V_IN; F_IN.2 and Q_IN.5/D are
12V_FUSED; Q_IN.1/.2/.3 are 12V_PROTECTED. D_IN.1/K is protected and .2/A
is GND; C_BUCK_IN.1 is protected and .2 is GND. These nets remain distinct in
the native netlist. Move the protected route and labels clear of foreign
bodies/pin wires/label polygons. Make J9 → fuse → PFET drain → protected
source rail traceable without implying a bypass or reversal.

Evidence: `p1-fuse-1.png`, page 1 at 600 dpi, crop
`x=1710,y=1140,W=1030,H=275`; `p1-fuse-tight-1.png`, 720 dpi,
`x=2730,y=1450,W=1400,H=450`; broader context `p1-power-1.png`.

### SR-3 — F7 output identity is overprinted by another net label

Page 1 F7's 12V_POD7 output label and C_BUCK_IN3's 12V_PROTECTED label
occupy the same region. Their text and outlines overprint, hiding the distinct
bank-7 output name even at high zoom and suggesting a protected-rail connection
at its output. Native connectivity is correct: F7.1=12V_PROTECTED,
F7.2=12V_POD7, C_BUCK_IN3.1=12V_PROTECTED.

Evidence: `p1-fuses-top-1.png`, page 1 at 300 dpi, crop
`x=2530,y=270,W=710,H=1140`, near local pixels `x=375..465,y=350..380`.
Separate the capacitor/label from the fuse output and inspect all eight output
labels again after regeneration.

## Coverage and design-intent observations

| Page | Accounted / expected | Observations |
|---|---:|---|
| 1 — power | 28/28 | Input protection, reverse-hookup stage, buck, OPA ferrite rail, 3.3 V LDO and F1–F8 present; SR-2/SR-3 block clear power/bank storytelling. |
| 2 — channels 1–4 | 60/60 | Four distinct cells with connector pin polarity, ESD, AC coupling, VMID1_BUF bias, OPA feedback/output networks and differential capacitors. All rows enlarged. |
| 3 — channels 5–8 | 60/60 | Four distinct cells use VMID2_BUF; numbering and polarity retained. All rows enlarged. |
| 4 — ADC | 12/12 | All 49 U_ADC physical pin numbers exposed; eight P/N input pairs, configuration and bypass parts present. DOUT2–4 have NC pin names and visible open ends; serial configuration pins visibly tied to GND. |
| 5 — references | 20/20 | Separate VMID1/VMID2 followers and isolated buffered outputs; distinct FILT1/FILT2 banks. The two 470 µF capacitors retain polarized curved-plate symbols. |
| 6 — digital/reset | 26/26 | Separate clock/TDM and presence connectors; clock buffers, terminations, output enable and supervisor/monostable/NMOS reset chain present. |
| Total | 206/206 | 6/6 pages opened and every expected reference reconciled on its correct PDF page and in native netlist. |

The native spoke checks passed 80/80 assertions: Jn pins 1/2/3/4 are
12V_PODn/GND/AUDIO_Pn/AUDIO_Nn; Fn connects the protected input only to its
numbered branch; both AC capacitors preserve numbered polarity; bias returns
select VMID1_BUF for channels 1–4 and VMID2_BUF for 5–8; C_DIFFn spans
ADCnP/ADCnN. These establish bank identity, not measured performance.

ADC labels match native mapping: channel P/N pins are 40/39, 42/41, 46/45,
48/47, 14/13, 16/15, 20/19 and 22/21 for channels 1–8 respectively.
VMID1/2 are pins 1/12; FILT1 P/N 43/44; FILT2 P/N 18/17. The long 3V3
route snakes around several left-side labels and crosses other wires; native
mapping distinguishes its intended supply connections. Not every crossing was
individually graded geometrically.

MCH connectivity matches the displayed design intent: J10.9/.10/.12 supply
MCLK/BCLK/FSYNC to U_CLK inputs 1/3/6; outputs 7/5/2 feed 22 Ω resistors
to ADC clocks. ADC DOUT1/pin 25 feeds U_TDM.2; U_TDM.4 returns through
33 Ω R_TDM to J10.2. J11.2 is presence sense only, through 300 Ω
R_MCH_SENSE to Q_TDM_EN gate, with 10 kΩ gate pulldown and OE pullup.
J11.1 is GND. The separate presence-dependent output-enable story is visible;
J11 is not a carrier supply input. The declared Ioff-capable part identities
are shown, but this review does not prove power-sequence/hot-plug behavior.

Reset design intent is traceable: U_RST1 POR_N feeds U_RST2.CLR_N;
U_RST2 A is low and B high, with external 100 kΩ/220 nF timing and
RESET_PULSE_H driving Q_RST1. The 10 kΩ ADC_RESET_N pullup and
100 kΩ gate pulldown support the documented high–low–high story. Actual
minimum delay/pulse width is a first-article obligation under ADR-0007, not
established by this visual review.

## Complete component denominator

Page 1: C_BUCK_BST, C_BUCK_IN, C_BUCK_IN2, C_BUCK_IN3, C_BUCK_O1,
C_BUCK_O2, C_BUCK_O3, C_LDO_IN, C_LDO_OUT, C_OPA_BULK, D_IN, D_QIN_GS,
F1, F2, F3, F4, F5, F6, F7, F8, FB_OPA, F_IN, J9, L_BUCK, Q_IN,
R_QIN_G, U_BUCK, U_LDO.

Page 2: for each n=1,2,3,4, exactly these 15 references:
Jn, U_ESDn, U_AFEn, C_AnP, C_AnN, R_BnP, R_BnN, R_XnP, R_XnN,
C_FBnP, C_FBnN, R_OUTnP, R_OUTnN, C_DIFFn, C_OPAn.

Page 3: the same exact 15-reference expansion for n=5,6,7,8.

Page 4: C_LDO_A, C_LDO_D, C_VDDA1_10N, C_VDDA1_4U7, C_VDDA2_10N,
C_VDDA2_4U7, C_VDDIO, R_CFG1, R_CFG2, R_CFG4, R_CFG5, U_ADC.

Page 5: C_FILT1_10U, C_FILT1_1U, C_FILT1_470U, C_FILT2_10U,
C_FILT2_1U, C_FILT2_470U, C_OPA9, C_VMID1_470N, C_VMID1_4U7,
C_VMID1_BUF, C_VMID2_470N, C_VMID2_4U7, C_VMID2_BUF, R_FILT1N,
R_FILT1P, R_FILT2N, R_FILT2P, R_VMID1_ISO, R_VMID2_ISO, U_AFE9.

Page 6: C_CLK, C_RST1, C_RST2, C_RST_T, C_TDM, J10, J11, Q_RST1,
Q_TDM_EN, R_BCLK, R_FSYNC, R_MCH_BCLK_PD, R_MCH_FSYNC_PD,
R_MCH_MCLK_PD, R_MCH_SENSE, R_MCH_SENSE_PD, R_MCLK, R_RESET_GPD,
R_RESET_PU, R_RST_T, R_TDM, R_TDM_OE_PU, U_CLK, U_RST1, U_RST2, U_TDM.

## Limitations and handoff

This is not a datasheet-by-datasheet electrical/ratings signoff, footprint/pad
orientation review, placement/routing review, ERC rerun, full 601-node parity
proof, or exhaustive 387-label pixel audit. All pages/components are accounted,
but known collisions preclude unobscured-annotation signoff. A follow-up must
visually inspect the corrected complete PDF; text extraction/native netlist
cannot substitute for the human document. Raster evidence is temporary under
the stated fresh directory and reproducible from the bound PDF and commands.
No order, physical qualification, outdoor or production claim is supported.
