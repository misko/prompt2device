subject: crow-audio-carrier-v1 1353d04766617721cf97ffbd80e7bf87c0055bdd
date: 2026-09-08
reviewer: fresh-context agent, schematic_render lens
context-given: exact-source-and-primary-documents, no prior reviews
source_commit: 1353d04766617721cf97ffbd80e7bf87c0055bdd
review_stage: pre-route
review_kind: schematic_render
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
netlist_sha256: ac2b772d357bf4c6e8e962a63fbc5cb5535e3770accaa3ce82a42b28520c227b
parts_sha256: da40483f53767ef34e8d0b561eea11d36e6bc6c10162dcae50a9078cf5373e0d
design_rules_sha256: 14603bc34e244ce702e97a3b14251090eeb88377107e26293fb6ace4d1d26fd9
schematic_pdf_sha256: 72fd0f97d190af75c5c26b06c39ce34b17433ba95afe7956f6700501f53bda3e

# Independent exact-PDF schematic-render witness

## Verdict and claim boundary

SOUND for this exact delivered schematic's human presentation. This is an affirmative integrated judgment after viewing every full page and every page at higher resolution, not acceptance inferred from passing checks or an absence of messages. The power entry/protection/regulation sequence, all eight complete analog paths, independent reference support, clock input, TDM return and reset sequence are drawn and understandable. I found no blocking foreign-net shared conductor, unexplained dangling connection, hidden active identity, omitted component reference or cropped circuit content in the inspected PDF.

Finding inventory: P0 = 0; P1 = 0; P2 = 1, a non-blocking small-print ergonomics observation below. No unresolved drawing ambiguity remains from this inspection. This witness does not certify complete electrical correctness or electrical equivalence, physical pin winding, PCB placement/routing, manufacture, allocation, release or an order. Canonical adoption belongs to the coordinator. DO-NOT-ORDER remains explicit.

## Freshness, scope and clocks

Repository: `/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901`.

Exact PDF: `projects/crow-audio-carrier-v1/03_tscircuit/build/schematic.pdf`, 786,013 bytes, PDF 1.7, 19 pages. Pages 1–3 and 5–19 are 900 × 607.5 points; page 4 is 607.5 × 900 points. This is 12.5 × 8.4375 inches, with the dimensions reversed for page 4.

Measured UTC clocks:

| Event | Actual clock |
|---|---|
| First clock recorded after task receipt | 2026-09-08 02:06:37 UTC |
| Before-work packet/census/subject verification completed | 2026-09-08T02:09:05.357153+00:00 |
| All 19 ordinary full-page views completed, clock sampled immediately afterward | 2026-09-08 02:10:46 UTC |
| All 19 higher-resolution page views completed, clock sampled afterward | 2026-09-08 02:12:15 UTC |
| After-view packet/census/subject verification | 2026-09-08T02:14:33.275517+00:00 |
| Final engineering-input verification before witness authoring | 2026-09-08T02:15:38.889288+00:00 |
| Post-authoring packet/census/subject verification | 2026-09-08T02:18:37.125068+00:00 |
| Commissioned hard deadline | 2026-09-08T02:23:32Z |

No TaskAttempt was created or claimed. No token telemetry was available or invented. These clocks are observed checkpoints, not an invented process-runner trace or continuous read-set log.

The complete TaskEnvelope and TASK were read. JSON decoding additionally rejected duplicate keys; the repository's closed-schema `TaskEnvelope.from_mapping` accepted the envelope. The repository's `envelope_sha256` produced `f9bcc762e049cc8d391951cab5118bbe872ac1565cfc96f2bfdd947a5f369084`. The canonical sorted-key, compact-JSON input-packet list hash was `083913028c758279429a524e3884a4972c0be522e30afad33f4f97a999b0015c`, matching both the supplied identity and `input_handoff_id`.

At the before and after checks, all 4/4 packet members matched both byte size and SHA-256. All 368/368 frozen census files matched both byte size and SHA-256, totaling 54,729,254 bytes each time. The subject normalization and design-rule digest were independently recomputed with `pre_route_review_check.py` functions, with the same sorted parts-byte concatenation used by that checker. All 77 part dossiers participated in the parts digest. All seven declared subject hashes matched:

| Identity | Measured SHA-256 |
|---|---|
| PDF | `72fd0f97d190af75c5c26b06c39ce34b17433ba95afe7956f6700501f53bda3e` |
| Normalized netlist | `ac2b772d357bf4c6e8e962a63fbc5cb5535e3770accaa3ce82a42b28520c227b` |
| Raw netlist | `c4ded19290cfcd88744a49fe4e9f5f380b755974937acf3d3d2474ee0fdd5b1a` |
| Native schematic | `044c0cea6504fc08b0115a60a30e4076d96ea8ae2c05e83159a40b936755acf6` |
| Circuit JSON | `99f3d38e3b471ad7eb0592c7f6fbe4d64f8f061003b7f2d7cc9f34e839be23bb` |
| Parts | `da40483f53767ef34e8d0b561eea11d36e6bc6c10162dcae50a9078cf5373e0d` |
| Adopted design rules | `14603bc34e244ce702e97a3b14251090eeb88377107e26293fb6ace4d1d26fd9` |

Administrative HEAD was `5efc042747f04f20d310d4f8c7b6df81570e839b` before and after. Git status already showed modifications to `01_docs/STATUS.md` and `01_docs/journal/schematic.md` at the first verification and showed the same two names afterward. They are outside this frozen census. I did not read their contents or alter them and do not claim a globally clean worktree. The frozen-census checks are identity observations, not a hermetic guarantee against transient writes elsewhere.

I read the complete PCB-design and KiCad skills, project `08_reviews/contracts.md`, execution graph, bounded-execution procedure, review/publication procedure, schematic-generation procedure, tscircuit folder procedure and pin-review protocol (including its render additions). The selected schematic-policy section S1–S12 was read completely. The task's narrower read-only schematic lens superseded generic instructions to rebuild, delegate or operate a board. Authored `ARCHITECTURE.md` and `DETAIL_DESIGN.md` supplied functional intent and the two limited math checks. Frozen part metadata and the exact netlist resolved drawing nomenclature. No previous project review, SOURCE-CORRECTION report, source-author review report, conductor, PCB/layout/route analysis, account, uploader, vendor communication or order was used. No delegation occurred.

## Rendering and measured coverage

Poppler `pdftoppm` 24.02.0 rasterized the exact PDF directly, without regenerating the schematic. Every page was actually opened with the image viewer at 96 dpi: 1200 × 810 pixels for landscape and 810 × 1200 for portrait. This was the ordinary full-page on-screen assessment. Each page was then actually opened at original resolution from a separate 180 dpi raster: 2250 × 1519 pixels for landscape and 1519 × 2250 for portrait. These second views supplied detail inspection; they did not replace the first full-page assessment. No physical print or calibrated monitor-PPI test is claimed.

Coverage denominators:

- Ordinary full-page visual inspection: 19/19.
- Higher-resolution visual/detail inspection: 19/19.
- Individually inspected audio-channel pages: 8/8, not a one-channel sample extrapolated to eight.
- Exact netlist component references found in extracted PDF text: 299/299; each appeared on exactly one page. The independent per-page count below agrees with the visible page-header counts and sums to 299. Circuit JSON separately contains 299 source components.
- Semiconductor/active references (`U_`, `Q_`, `D_`): 45/45 visible with human-readable MPN identities. Supplier-code netlist values resolve through frozen parts to those displayed names; supplier-code absence from the human PDF is not an identity defect.
- Named intentional NC pins: 40/40 present in the page inspections; the exact netlist identifies 40 NC nodes and the native schematic contains 40 `no_connect` records. This is an NC presentation cross-check, not a new independent datasheet pin audit.
- S5 limited arithmetic checks: 2/2, detailed below.

The netlist parser returned 165 named connected nets and 828 connected nodes, plus 40 NC nodes. Those are inventory counts; I do not claim a pin-by-pin electrical audit over all 828 nodes.

## Complete page-by-page witness

Every row below means both the ordinary full page and its higher-resolution page were actually viewed. Common checks on each page were heading/occupancy, references and values, active names and pin labels, polarity/NCs where applicable, wire ends and junctions, foreign wire/symbol/text collisions, and page-edge clipping.

| Page | Components | Observed subject and specific evidence |
|---:|---:|---|
| 1 | 9 | J9 → F_IN → Q_IN → protected rail is an explicit wired story. Q_IN gate pull-down and D_QIN_GS clamp are distinct; D_IN and three input capacitors shunt to GND. Source/drain/common-drain and diode A/K labels remain legible. No cropped right-hand capacitor annotation. |
| 2 | 9 | AP63205 U_BUCK, C_BUCK_BST, L_BUCK, output capacitors, C_RAW_HOLD and FB_OPA are identifiable. Switch and bootstrap wiring are distinct from output/feedback. The 5V_OPA bead branch and polarized raw reservoir are visible. |
| 3 | 17 | D_HOLD/R_PRE/Q_PRE precharge/bypass network flows to held capacitors and TPS7A9201 U_LDO. NR filter bank, FB divider, SS_CTRL/GND/EP returns, two IN and two OUT pins, and PG_NC are visible. Crossings of NR and held rail use hop-over ink, not false junction dots. |
| 4 | 14 | Portrait page keeps U_PWR raw-rail supervision above U_AUDIO ADC-rail supervision. PWR_EN visibly reaches U_AUDIO MR_N; the ADC sense path crosses it without a connection. Each supervisor's divider, timing capacitance, pull-up and bypass is associated with its own block. |
| 5 | 10 | Parallel R_DUMP_TIME1/2, C_DUMP_TIME, the two named Schmitt inverter parts, LDO_EN and Q_DUMP/R_DUMP are understandable. Both inverter NC pins are named. Gate pull-down and local 100 nF bypasses are visible. |
| 6 | 22 | Complete channel 1: F1/J1 and U_ESD1 → two nonpolar 1 uF coupling capacitors and VMID1 bias → OPA1656 U_AFE1 feedback/filter → TMUX2821 U_ISO1 → ADC1P/N shunts. Feedback branches stay upstream of isolation. Dense crossings were zoom-checked. |
| 7 | 22 | Complete channel 2 independently inspected. F2/J2/U_ESD2, both bias and feedback legs, R_OUT2P/N/C_DIFF2, U_ISO2 and ADC2P/N support are visible. Top feedback routing differs from page 6 but remains traceable, with distinct FILTER2P and OPA_P2. |
| 8 | 22 | Complete channel 3 independently inspected. Indexed connector, ESD, bias, feedback, isolation and ADC3P/N identities are consistent in the drawing. Feedback/input crossings have hop-over separation; no missing local bypass seen. |
| 9 | 22 | Complete channel 4 independently inspected. VMID1_BUF ownership is visible; positive and negative paths and their 300 Ω/680 pF feedback are separate from the post-isolation ADC4 shunts. |
| 10 | 22 | Complete channel 5 independently inspected. Bias ownership changes to VMID2_BUF. J5/U_AFE5/U_ISO5 and ADC5P/N are individually readable; 15 nF differential capacitor remains before isolation. |
| 11 | 22 | Complete channel 6 independently inspected. Indexed passives and active identities, ESD NC1/NC2, both TMUX control pins and EP/GND returns, and held-rail bypass are present. |
| 12 | 22 | Complete channel 7 independently inspected. VMID2 bias, upstream feedback/filter, two isolated ADC outputs and per-output 100 kΩ/1 nF shunts are visible and unoccluded. |
| 13 | 22 | Complete channel 8 independently inspected with the same full chain and local support checks. ADC8P/N and all channel-8 references are visible; no page-edge or lower bypass cropping. |
| 14 | 12 | CS5308P-DN U_ADC has all eight P/N input pairs, ASP clock/data/reset identities, configuration resistors, local LDO filters and supply bypass row. ASP_DOUT2_NC/3_NC/4_NC are visible. Ground, FILT negative returns, EP and SPI/config straps at the lower edge were detail-checked. Smallest-text observation below applies. |
| 15 | 14 | Two external half-supply dividers, their 10 uF + 1 uF support, OPA1656 U_AFE9 followers, 100 Ω isolation resistors and explicitly polarized 4.7 uF outputs are drawn. Raw follower feedback closes before the output resistors. VMID1_EXT/VMID2_EXT are not mistaken for ADC VMID bypass-only nodes. |
| 16 | 12 | Two independent FILT banks visibly use 1 Ω positive-feed resistors and 470 uF/10 uF/1 uF capacitors with direct ground returns. Separate VMID1 and VMID2 4.7 uF/470 nF bypass pairs are named. No ground-leg series resistor is drawn. |
| 17 | 9 | J10 clocks to SN74LVC3G34 U_CLK and three 22 Ω output resistors are wired left-to-right. Three 10 kΩ input pull-downs and local bypass are visible. J10 unused pins are explicitly NC; FSYNC/BCLK crossing was detail-checked. |
| 18 | 8 | J11 3.3 V sense → 300 Ω/10 kΩ divider → Schmitt U_OE → U_TDM OE_N is wired. TDM_RAW → SN74LVC1G125 → 33 Ω → ADC_TDM return is distinct. J11 unused pins and U_OE NC are explicit; output, OE and GND wires are separate. |
| 19 | 9 | TPS3839 U_RST1 → CLR_N of SN74LVC1G123 U_RST2 → Q_RST1 reset pull-down is wired. Q, CEXT and REXT_CEXT routes cross using visible hops and remain distinct. 100 kΩ/220 nF timing, both local bypasses and reset pull-up/pull-down are present. |

## Integrated criteria and resolved ambiguities

S6 readability: READABLE. The power story is explicit through pages 1–3 with separately titled supervision/discharge on 4–5. A representative complete audio path is J1 AUDIO_P → C_A1P → U_AFE1 A_POS, followed by the visibly drawn output/filter and U_ISO1 to ADC1P; the matching negative leg is also drawn. All eight corresponding channel pages were examined. Labels are used chiefly at sheet boundaries and for rails/bias/control reuse, not as a substitute for every segment of the primary chain.

S7 decoupling adjacency: functionally grouped and attributable. Each analog channel shows its own C_OPAn under the amplifier and C_ISOn beside the switch; logic and regulators show their own support. The ADC bypass row is immediately below U_ADC, with C_LDO_A/D at its right. The large reference banks occupy a separately titled ADC-support page. The buck input bank is on preceding protection page 1, not duplicated beside U_BUCK on page 2; its `C_BUCK_IN*` names and common `12V_PROTECTED` rail make the ownership apparent. This is schematic attribution, never proof of physical PCB proximity.

The denser crossing sites were not accepted merely because the netlist passed. I saw actual hop-over ink in the high-resolution PDF and checked the relevant exact-netlist separation:

- Page 3: LDO_NR contains U_LDO.8 and C_LDO_NR1–5; it is separate from held-rail IN pins 9/10, Q_PRE.3 and C_HOLD1/2. The drawn NR vertical crosses the held rail without a junction.
- Page 6: BIAS_P1 contains C_A1P.2/R_B1P.1/U_AFE1.3, while FB_P1 contains C_FB1P.1/R_X1P.1/U_AFE1.2. Their crossing is not a connection. OPA_P1 reaches U_AFE1.1, C_FB1P.2 and R_OUT1P.1; FILTER1P reaches R_OUT1P.2/R_X1P.2/C_DIFF1.1/U_ISO1.1. The output resistor is not bypassed by the drawing.
- Page 17: MCH_BCLK is J10.10/R_MCH_BCLK_PD.1/U_CLK.3, while MCH_FSYNC is J10.12/R_MCH_FSYNC_PD.1/U_CLK.6. The crossing does not join these clocks.
- Page 19: RESET_C is C_RST_T.1/U_RST2.6; RESET_RC is C_RST_T.2/R_RST_T.2/U_RST2.7; RESET_PULSE_H is U_RST2.5/Q_RST1.1/R_RESET_GPD.1. Visible hops distinguish the timing nodes from the Q-output path. No pin-5-to-pin-6 short is implied after inspection.

All 40 intentional NCs are accounted for by visible names and unconnected pin ends: U_LDO.5 (1); U_DUMP.1/U_LDO_EN.1 (2); U_ESD1–8 pins 1/2 (16); U_ADC pins 26–28 (3); J10 pins 1,3–8 (7); J11 pins 3–12 (10); U_OE.1 (1). This PDF uses named NC pins and terminal marks rather than relying on prose elsewhere. The native flags were counted independently but not substituted for this visual check.

S5 design-math spot-check: 2/2 reproduced from `DETAIL_DESIGN.md` and compared with drawn values. Page 19's 100 kΩ × 220 nF gives 22.0 ms nominal RC; 99 kΩ × 198 nF gives 19.602 ms component-only low corner. These are not guaranteed monostable pulse widths. Page 15's 10 kΩ/10 kΩ divider gives the documented independent ±1%/rail-window bounds: 3.23 × 9.9/(10.1+9.9) = 1.59885 V and 3.34 × 10.1/(9.9+10.1) = 1.68670 V. Its 5 kΩ Thevenin resistance and 11 uF nominal bypass give 55 ms. Broader timing/headroom/ratings qualification was not repeated.

## Non-blocking observation

SR-P2-01 — Small print margin on dense pages. Page 14's U_ADC pin-function/number bank, and pins on pages 3, 4 and 6–13, use approximately 6-point text according to Poppler's integer-rounded font metadata at unity scale; many references/values on the channel and ADC pages are approximately 7 points. I could distinguish the names and primary paths in the ordinary 96-dpi full-page views and resolved detailed pin/crossing inspection at 180 dpi. There is no text-over-symbol/foreign-wire collision at these inspected locations. This is not a requirement to deep-zoom the whole circuit to understand it, but further fit-to-smaller-paper reduction would be undesirable. Retain the delivered-size print scale or enlarge these pin groups in a future presentation revision. This is an ergonomics note, not a blocking electrical or schematic-connectivity finding. No physical printer test was performed.

## Exclusions, limits and handoff

Not reviewed or authorized: PCB source as a layout, placement, clearance, routing, power copper, thermal realization, footprint winding, fabrication outputs, JLC allocation, assembly readiness, connector physical qualification, order permission, first article, outdoor/production authorization, or all-corner electrical ratings. I did not independently rederive every pin from manufacturer package figures, rerun ERC/conductors, or assert full PDF/netlist electrical equivalence over every connected node. The exact normalized netlist and parts were used to resolve observed drawing ambiguity and nomenclature only.

No physical schematic print was produced. No machine-perfect exhaustive intersection proof is claimed for all PDF primitives. Visual coverage is the complete integrated 19-page presentation plus all 19 higher-resolution page views, backed by the stated component and NC censuses. Frozen hashes do not certify the engineering truth of their contents.

All task-created files are confined to `/tmp/carrier-render-1353d047-ilzWlI/`: direct PDF rasters, extracted text/XML, temporary verification/coverage scripts, and this witness. No repository file was written by this reviewer. The exact witness bytes must be archived unchanged by the coordinator; this temporary report is not canonical adoption and does not permit layout or ordering by itself.
