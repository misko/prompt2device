# Integrated schematic render and native readability witness

subject: crow-audio-carrier-v1
source_commit: 2378791ff6398e31ab41a506958b94deaae05166
date: 2026-09-10
reviewer: /root/carrier_identity_native_readability (independent judgment agent)
agent-role: judgment
context_mode: FRESH
context-given: Immutable source packet, integrated-render commission, permitted method-only hash source, BRIEF, selected ADR intent, and packet primary references; no earlier conversation or reviewer findings.
independence: Read-only subject; private exports, parsers, and renders; root remained sole live writer. No prior reviews, dispositions, STATUS, journals, standalone checker verdicts, or ARCHITECTURE were consulted. Author/checker assertions embedded in ADRs were excluded from acceptance evidence.
review_stage: pre-route
review_kind: schematic_render
commission_sha256: 4b28eb1d9fd36fc41a5710226428c084e1f49c0f2af074c39b9f6062281ce61f
subject_packet_sha256: 3843576c988e23cfb2d66c058b474aac21e16b0d8418f509c76eeb01e7e91392
netlist_sha256: 471b96bf68be1fc3e5425b97cdace0f4a11cf929929011cf55170248f2129f9a
parts_sha256: 2f76a9ca1a8b2e3cf948d3b43fbbbc6ad101f1fccd58de1d7ecd05c556b2f38d
design_rules_sha256: 672f0b9be3b3f9b6c2a9c9c1b1ea0e12ff4d91f061ede29ac36d6ac71965b8a4
circuit_json_sha256: 78c7ffbf7defc297dfa6ca88d5b24e2ae9bd4e2de96931c0f8cb91ba1488bb3f
schematic_pdf_sha256: 194529d5a49eda59bfeeb7f028acda030c8916f670518ca241c12e440a282a8e
native_schematic_sha256: 43eaaa45fb16a68ee45f910765976f443a4070aafd86d67c9039f3b02bf9a0ef
archived_netlist_raw_sha256: 6eddbc460ce1a05e34df68e37bf955adbca8ef8dba7982609d7b1f79adf36980
fresh_native_netlist_raw_sha256: 5a98c884b6cc7c892247e7943ae24c3b1bddbeac6dea8d41816a3526537fcc2d
fresh_native_netlist_owning_sha256: 471b96bf68be1fc3e5425b97cdace0f4a11cf929929011cf55170248f2129f9a
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
completed_at: 2026-09-10T17:43:34Z

## Scope, identity, and method

SOUND applies to the commissioned integrated schematic readability, functional topology, and source/native consistency lens. This is a completed review of the exact subject, with no missing page or native-region coverage. It is not a full component-rating calculation, PCB acceptance, sourcing approval, or hardware qualification.

Before inspection I independently recalculated the commission and packet hashes and compared all 235 tar members against the copied subject; all members are regular files and all matched. Final verification repeated that comparison, checked for extra/missing subject files, and again found none. Every listed raw/owning digest was independently recalculated. The permitted method file supplied only owning-hash normalization; it supplied no circuit verdict.

I inspected each supplied 120 dpi page at ordinary page-fit size, then examined necessary native details at larger scale. A fresh Poppler 24.02.0 rendering of the exact PDF proved pixel-identical to all 19 supplied images. KiCad 10.0.4 independently exported the actual native schematic to a netlist and SVG. I visually examined 19 bounded SVG regions covering all 333 component instances, including every native property, pin/body relationship and local wire arrangement. The native page is one large custom sheet; its region spacing was inspected directly, not inferred from the PDF.

My own source-trace union parser reconstructed 178 named electrical nets and 42 isolated pins from circuit.json. These agree with all 220 exported native net groups and all 937 component pins. Source identifiers beginning N12, N5 and N3 map to their displayed rail names; no electrical membership change is hidden by that spelling normalization. Fresh and archived native pin memberships agree exactly. KiCad emitted a generic annotation warning during netlist export; all 333 source references survived uniquely, so that warning did not conceal missing exported circuitry. These comparisons support, rather than substitute for, the visual judgment below.

## Complete page and native coverage

PDF evidence base: `/tmp/carrier-identity-complete-review-20260910.uhy2hdo3/render/`.
Each row means the unedited `page-NN.png` and independently exported `native-region-NN.png` in `/tmp/carrier-native-readable.xGoDuNmS/` were actually examined.

| Page | Components | Inspected region |
|---|---:|---|
| 01 | 6 | J9, fuse, reverse PFET, TVS, gate clamp |
| 02 | 13 | Buck, reverse-input diode, bootstrap, output/bleed leaves |
| 03 | 13 | Hold diode, precharge, held capacitors, LT3041 |
| 04 | 14 | Raw/ADC supervisors, dividers, CT, audio enable |
| 05 | 10 | Delay, Schmitt pair, LDO enable, switched discharge |
| 06 | 27 | Complete channel 1, J1 through ADC1P/N |
| 07 | 27 | Complete channel 2, J2 through ADC2P/N |
| 08 | 27 | Complete channel 3, J3 through ADC3P/N |
| 09 | 27 | Complete channel 4, J4 through ADC4P/N |
| 10 | 27 | Complete channel 5, J5 through ADC5P/N |
| 11 | 27 | Complete channel 6, J6 through ADC6P/N |
| 12 | 27 | Complete channel 7, J7 through ADC7P/N |
| 13 | 27 | Complete channel 8, J8 through ADC8P/N |
| 14 | 12 | ADC, mode straps, internal LDO nodes, local bypass |
| 15 | 8 | Two passive external bias banks |
| 16 | 12 | Separate FILT banks and internal VMID bypass |
| 17 | 9 | J10, three incoming clocks, buffer and terminations |
| 18 | 11 | J11 presence, raw-data Schmitt, OE, TDM return |
| 19 | 9 | Supervisor, monostable, timing network, reset NMOS |

## Integrated judgment

The primary power path is continuously readable from J9 through F_IN and Q_IN to the protected bus, then through D_BUCK_IN to the buck and through D_HOLD/precharge to the held LDO input. PFET source/drain names, the input clamp cathode, gate-zener cathode and polarized reservoir positives are explicit. Actual pins put the buck feedback on 5V_BUCK, bootstrap across BST/SW, LT3041 OUTS with OUT, SET through 33 kΩ to ground, PGFB at held input, and its intentional PG/VIOC outputs unconnected. This agrees with the relevant DMP6023LFG, AP63205 and LT3041 primary pin/application descriptions. Both presentations make power and ground attachments distinguishable from unrelated crossings.

Every channel is traceable from connector pins 3/4 through coupling, bias and positive-input limiting to its OPA2320, feedback/filter network, TMUX and matching ADC pair. I checked polarity and numbering across all eight instances. Actual feedback has 680 pF from each amplifier output to its inverting input and 300 Ω from that input to its corresponding post-10 Ω filter node. AN0556R1 Figure 2 supports this feedback structure. The drawing clearly exposes the ADR0025 modifications: common 3V3_ADC amplifier/ADC power, added input resistors, passive external bias and two grounded 15 nF capacitors per leg. It does not visually disguise those changes as the unmodified vendor circuit. VMID1_EXT feeds channels 1–4 and VMID2_EXT feeds 5–8; neither is confused with the ADC's internal VMID1/2. Independent FILT returns and bypasses remain identifiable.

ADC pin numbers and straps agree with DS1314F1 Tables 1-1 and 4-1 through 4-4: secondary 48 kHz family, minimum-slot TDM, default channel order and linear-phase fast filter with HPF. J10's data input/clock/ground assignments agree with the packet miniDSP manual Tables 3/12. Three clocks remain distinct through U_CLK and their 22 Ω resistors. DOUT1 reaches the biased noninverting Schmitt, tri-state buffer, 33 Ω resistor and J10. J11 presence controls active-low OE through the inverting Schmitt. The page headings explicitly state inversion/noninversion despite rectangular chip glyphs.

Reset is readable as supervisor release into the monostable clear trigger, with A low/B high, separate CEXT and REXT/CEXT nodes, and Q driving the reset NMOS. TI SCES586E's pin/function description supports this trigger arrangement; Cirrus Table 4-5 establishes the high-delay-low-high requirement. This review establishes the intended path and polarity, not guaranteed pulse duration or bench timing.

## Findings and limits

RND-01, minor/nonblocking: native passive symbols are generic rectangular bodies rather than conventional resistor/capacitor glyphs. Examples are page 02 C_BUCK_IN2 on 12V_BUCK_IN, native center (76.200, 198.755) mm, and page 19 C_RST_T on RESET_C/RESET_RC, center (485.140, 75.565) mm. `native-region-02.png` and `native-region-19.png` reproduce the observation. Standard passive glyphs would improve immediate recognition. References, units, values and terminal attachments remain legible, so this does not obstruct interpretation or justify a blocking verdict.

No blocking identity, text/body collision, misleading junction, polarity, NC, continuity or native-consistency finding remains. PDF capacitor plates and polarized markings are clear. Native detail inspection resolved close property/wire spacing without an unreadable value. All 42 isolated pins carry meaningful NC treatment: unused connector pins, ESD NCs, ADC DOUT2–4, four logic NCs, and LT3041 PG/VIOC.

Retain every existing physical, sourcing and order boundary: routing/stack/return geometry, effective capacitance and LDO stability, analog headroom/distortion, reset timing, power-state and transient behavior, TDM timing, connector/cable fit, hot load/drop/fault selectivity, outdoor qualification, exact assembly availability, final fabrication/upload checks and separate purchase authorization. No hardware test or procurement acceptance is claimed.
