subject: crow_audio_carrier_v1 integrated schematic
date: 2026-09-10
reviewer: Codex independent judgment reviewer
context-given: continuation correction packet, original immutable packet, retained predecessor handback, and added connectivity proof
independence: CONTINUATION of the same reviewer; original visual judgment was fresh, while this correction uses the admitted predecessor and added proof without claiming a new fresh review
source_commit: bad6b2db7ad063a2955e8bb2b1f7741160ed29ff
review_stage: pre-route
review_kind: schematic_render
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
actualcompleted_at: 2026-09-11T04:26:44Z
actual_completed_at: 2026-09-11T15:34:00Z
correction_commission_sha256: 9832e76c193bd64ca1f04d160f03b0d13be942b4189649433babcfc97847e222
original_commission_sha256: a9ee13d67239c1c76e1fd1566bcf6985fb509a3af9b5339753f6451eb79f8222
original_subject_raw_sha256: 3f980283ac893b7d8987c818571a173d941a5a33f81b9be5e58d7e7edaeb1e0f
original_subject_semantic_sha256: bfac9f357d8a08e46088da7ab1624c4bb2731e46ecd640d3e791021328cac45b
commission_sha256: 9832e76c193bd64ca1f04d160f03b0d13be942b4189649433babcfc97847e222
subject_raw_sha256: f89b51abb7ac000aee5fb97e5148fe1d27698ba28a430de99e2f68bd9d9eb318
subject_semantic_sha256: 2834258f09076b57796cf20eabbdf0a58439ba53d7c45c9efd72f88c12a4bab7
schematic_pdf_sha256: 9782f93c076c61f536716c96b12ea0146b02a229da74545e2215edf7a8d75d3e
circuit_json_sha256: 8a93fcdd98a726981cf6002bcfb4c026fbcd427785d65299f1221133153a5a16
native_schematic_sha256: 5bdb143b8cfacc3da075f33df0a137c0e9b5f8a619ab685c37a16f4b69af93dc
netlist_raw_sha256: 2aa7bae438f88587df2965aecab9bbdb0558520eddebbf4dcfc996e301d0e860
netlist_sha256: 471b96bf68be1fc3e5425b97cdace0f4a11cf929929011cf55170248f2129f9a
parts_sha256: 2f76a9ca1a8b2e3cf948d3b43fbbbc6ad101f1fccd58de1d7ecd05c556b2f38d
design_rules_sha256: 672f0b9be3b3f9b6c2a9c9c1b1ea0e12ff4d91f061ede29ac36d6ac71965b8a4

# Independent schematic readability review

I find the commissioned schematic **SOUND for this pre-route schematic-render lens**. I visually inspected all 19 supplied PDF pages at their original dimensions: pages 4 and 15 are 1013 by 1500 pixels, while the other 17 are 1500 by 1013 pixels and, separately, all 19 regions of the independently exported native KiCad SVG in high-resolution region crops. The census covers 333/333 components. Every page and native region is READABLE: functional blocks are strongly separated, signal flow is generally left-to-right, power and ground attachments are visible, values and part identities are legible, and the repeated analog channels use a consistent arrangement that makes comparison straightforward. This verdict does not approve ordering; physical, routing, thermal, sourcing, assembly, and prototype qualification remain outside this review.

I first verified 265/265 envelope packet items by exact size and SHA-256, then verified all 236/236 regular `subject.tar.gz` members against both `subject-manifest.json` and their copied subject bytes. I independently rendered the exact PDF at 120 dpi. All 19 resulting PNGs matched the supplied render bytes exactly. I exported the exact native schematic to a KiCad s-expression netlist and SVG using bounded native commands. The source `circuit.json`, supplied netlist, and fresh native export each contain 333 components; source/native pin census is 937/937, and the supplied and fresh netlists each contain 937 nodes. Fresh and supplied netlists have the same normalized connectivity digest, `471b96…f9a`. That normalization establishes agreement under its documented projection; I do not claim that the raw-byte differences are limited to any enumerated metadata fields. Parsed reference, value, and manufacturer-part-number tuples are equal between native exports, and all 333 source reference/MPN pairs equal the native pairs. The native file contains 42 explicit no-connect markers; visual checks confirmed their unambiguous blue-X depiction. A separate endpoint proof now establishes that the exact same 42 source-isolated endpoints carry native no-connect flags.

The PDF is especially effective as a reading artifact. Pages 1–5 present protection and sequencing in dependency order. Pages 6–13 preserve polarity from AUDIO_P/N through input capacitors, OPA2320 differential paths, filter shunts, TMUX isolation, and ADC1–8 P/N labels. Page 14 makes the ADC supply groups, configuration straps, clocks, reset, TDM output, and unused ASP outputs easy to distinguish. Pages 15–16 separate the external VMID dividers from the independent reference-filter banks. Pages 17–19 then show clock direction, the TDM return gate, and reset pulse generation without requiring the reader to chase unlabeled page connectors. Decouplers are drawn locally with their rail and return, rather than collected in an unexplained bank.

The native one-sheet representation is also readable within each functional region, although it requires panning because the custom sheet is approximately 632 by 3000 mm. High-resolution crops of the actual exported vector confirmed property, pin, body, wire, junction, power, ground, and NC geometry independently of the PDF. The eight analog regions contain several long orthogonal traces, but named endpoints and junction dots prevent wire-crossing ambiguity. Region 17’s connector-to-clock-buffer paths cross visually at close spacing; the three distinct labels and lack/presence of junction dots remain clear at normal detail, so I grade it READABLE rather than EFFORTFUL.

One advisory finding remains. The native netlist exporter printed `Warning: schematic has annotation errors, please use the schematic editor to fix them`. This is reproducible in `native_netlist.log`. Descriptive references such as `F_IN` and `U_LDO` are present and may explain the warning, but that causal relationship is an inference; no separate annotation diagnosis was established. The export nevertheless completed and produced 333 unique component records. I therefore do not treat the generic warning as a present readability or connectivity defect under this lens. It should still be resolved or formally accepted before a later KiCad annotation/ERC gate, because a generic warning can conceal a future duplicate or malformed reference.

The admitted connectivity proof independently reconstructs the source graph by union-find over 1,395 `source_trace` endpoint/net references and does not import the converter or use its connectivity-map resolver. I reviewed its parser and alias method: the explicit alias file covers authored voltage-net names, and its fallback removes one leading `N` only before a digit, exactly reversing the owning TSX `N()` convention. Frozen replay against the retained reviewer export and canonical netlist passed both full comparisons: 333 components, 937/937 endpoints, 178 named nets, and 42/42 no-connect endpoints, with no missing, extra, wrong-net, component, partition, or NC differences. Three serialized controls were correctly rejected for swapped names, a missing endpoint, and a missing NC marker.

The exact unused-pin set is consistent with the owning TSX: 16 ESD NC pins, four package NC pins on the single-gate logic devices, ADC pins 26–28, LDO pins 4 and 6, seven unused J10 pins, and ten unused J11 pins. The logic and ESD dossiers explicitly identify their NC pins; ADC and connector unused status is established by TSX omissions and labeled schematic presentation. This confirms implementation consistency. It does not independently prove that every unused functional option is the desired system-level intent. The 42 connected graph endpoints whose presentation `is_connected` flag is false were not treated as NC; graph membership and native flags control this comparison.

No blocking or major visual defect was found. Cross-page continuity was checked through repeated named rails and signals: `12V_PROTECTED`, `5V_BUCK`, `5V_LDO_HOLD`, `3V3_ADC`, `AUDIO_EN`, ADC1–8 P/N, `FILT1P/FILT2P`, VMID1/2, the MCH clock trio, `ADC_TDM`, and `ADC_RESET_N`. Polarity and intentional NC meaning remain visible at every relevant endpoint. The correction evidence archive contains the added proof, correction scripts, command logs, runtime outcomes, comparison results, and final verification data. The original fresh exports, exact rerenders, native-region views, and visual-inspection records remain retained by exact SHA-256 reference to the predecessor delivery and its nested evidence archive.

| Page | Native region | Components | Representative inspected nets | PDF / native |
|---:|---|---:|---|---|
| 1 | input | 6 | 12V_IN, 12V_FUSED, Q_IN_GATE, 12V_PROTECTED | READABLE / READABLE |
| 2 | buck | 13 | 12V_BUCK_IN, BUCK_SW, 5V_BUCK, 3V3_ADC | READABLE / READABLE |
| 3 | held_ldo | 13 | 5V_LDO_FEED, PRE_GATE, LDO_EN, 3V3_ADC | READABLE / READABLE |
| 4 | supervisors | 14 | PWR_SENSE, PWR_EN, ADC_SENSE, AUDIO_EN | READABLE / READABLE |
| 5 | dump | 10 | DUMP_RC, DUMP_GATE, ADC_DUMP, LDO_EN | READABLE / READABLE |
| 6 | analog_1 | 27 | AUDIO_P1/N1, OPA_P1/N1, ADC1P/N | READABLE / READABLE |
| 7 | analog_2 | 27 | AUDIO_P2/N2, OPA_P2/N2, ADC2P/N | READABLE / READABLE |
| 8 | analog_3 | 27 | AUDIO_P3/N3, OPA_P3/N3, ADC3P/N | READABLE / READABLE |
| 9 | analog_4 | 27 | AUDIO_P4/N4, OPA_P4/N4, ADC4P/N | READABLE / READABLE |
| 10 | analog_5 | 27 | AUDIO_P5/N5, OPA_P5/N5, ADC5P/N | READABLE / READABLE |
| 11 | analog_6 | 27 | AUDIO_P6/N6, OPA_P6/N6, ADC6P/N | READABLE / READABLE |
| 12 | analog_7 | 27 | AUDIO_P7/N7, OPA_P7/N7, ADC7P/N | READABLE / READABLE |
| 13 | analog_8 | 27 | AUDIO_P8/N8, OPA_P8/N8, ADC8P/N | READABLE / READABLE |
| 14 | adc | 12 | ADC1–8 P/N, FILT1P/2P, ADC clocks/reset/TDM | READABLE / READABLE |
| 15 | vmid | 8 | 3V3_ADC, VMID1_EXT, VMID2_EXT, GND | READABLE / READABLE |
| 16 | references | 12 | FILT1P, FILT2P, VMID1, VMID2 | READABLE / READABLE |
| 17 | clocks | 9 | MCH_MCLK/BCLK/FSYNC, ADC_MCLK/BCLK/FSYNC | READABLE / READABLE |
| 18 | tdm | 11 | ADC_TDM, TDM_SENSE_G, TDM_OE_N, TDM_BUFFERED | READABLE / READABLE |
| 19 | reset | 9 | POR_N, RESET_C, RESET_RC, RESET_PULSE_H, ADC_RESET_N | READABLE / READABLE |

The full inspected reference lists and full visible named-net lists for every page/region are in `evidence.json`; the table above is a compact coverage index. The scope is schematic readability plus source/native identity, value, pin, connectivity, and NC consistency. It is not a second ratings/topology review and supplies no physical PCB or order approval.
