# Independent integrated schematic witness

subject: crow-audio-carrier-v1
source_commit: 7e6f751b0d25fd6aecfc00260c18fdac78c6a467
date: 2026-09-10
reviewer: independent judgment agent /root/carrier_rebuild_schematic_readability
context_mode: FRESH
review_stage: pre-route
review_kind: schematic_render
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
readability: EFFORTFUL
completed_at: 2026-09-10T19:24:08Z
commission_sha256: f255efff7e5e26531c1af1c85dc0e19e8a5e5ab9d3cc3ab455dd6be13145c1da
task_envelope_sha256: 8e9f6420f5b3f34902a40d339fb3892b2856730aa8e3b1483a3d28af405272e6
subject_packet_sha256: 9d38a20e80b717b41bf84ec363cf0eb8ac86d7f0cee33472aa3e2f20c0cfc9eb
circuit_json_sha256: e0f1275799fd2fa1529fb11e2275d26a2775a4e390987eedb7ea12dccdcaf55d
schematic_pdf_sha256: 4455fc6170799bc597bcf6348c25473f814133e5ffb4146266b97ed13a3537f7
native_schematic_sha256: b95cfca75a079b4b155a4fa24aa2c548fcaef779cd72271e5212a18529856674
netlist_raw_sha256: 3364e97284060bace699f887900baf1fc8fcc8090355f5f6b2c35332901bdb44
netlist_sha256: 471b96bf68be1fc3e5425b97cdace0f4a11cf929929011cf55170248f2129f9a
design_rules_sha256: 672f0b9be3b3f9b6c2a9c9c1b1ea0e12ff4d91f061ede29ac36d6ac71965b8a4
parts_sha256: 2f76a9ca1a8b2e3cf948d3b43fbbbc6ad101f1fccd58de1d7ecd05c556b2f38d

The verdict is limited to the commissioned integrated schematic readability and actual source/native consistency review. It is not full electrical-rating, physical-PCB, sourcing, stock, fabrication, or ordering approval. The drawing is usable, with the presentation limitations below; no blocking discrepancy was found. READABLE means readily interpretable; EFFORTFUL means reliable interpretation requires deliberate tracing; OPAQUE means interpretation cannot be trusted. No reviewed region was OPAQUE.

Context given was the commission, strict envelope, source-commit identifier, deadline, and permitted subject paths. I independently read the copied source, circuit JSON, PDF, native schematic, netlist, binding inputs, selected supplied primary datasheets, and method-only checker code. I read no prior review, commission, findings, root preflight/DELTA, STATUS, journal, disposition, conversation, or standalone checker verdict. No comparison packet or earlier judgment was used. This was one attempt, without delegation or replacement. Subject files were read-only; work used private scratch. No OS-level isolation is claimed.

All 257 envelope members matched their prescribed sizes and SHA-256 values before substantive review and again immediately before this witness. All 235 regular archive members matched the copied subject on both passes. Commission, envelope, packet, and all seven commissioned raw/owning bindings were independently recomputed. Rules bind 15 YAML files plus the prescribed route projection; parts bind 84 dossiers. No subject changed.

I independently ran `pdftoppm -r 120 -png` on the bound PDF: all 19 resulting PNG hashes exactly equal the supplied renders. I visually viewed every page individually, then viewed a 240-dpi buck detail. Text extraction supplemented visual review: all 333 references occur on their assigned pages and all 67 printed device MPNs are present. Passive MPNs are carried in source/native properties rather than printed beside the 266 engineering values; I do not claim visually reading unprinted identities.

I separately ran KiCad 10.0.4 `sch export netlist --format kicadsexpr` and `sch export svg` against the exact native file. An independent S-expression parser compared the actual export with the pinned netlist and a union-find reconstruction of source traces: 333 components, 937 physical source endpoints, 178 named nets/895 connected endpoints, and 42 intentional NC endpoints. The native export has 220 nets including those 42 NC singletons. There were zero pin/net, NC, or MPN differences; the fresh owning netlist hash equals the bound hash. The exporter emitted an annotation warning; all expected components and endpoints were nevertheless present. This is not an ERC-clean assertion.

A separate Bun JSX expansion of both exact TSX files, using a private intrinsic-element collector, yielded the same 333 references, 895 declared connections, 42 omitted NC pins, 333 identities/poses, and all 146 capacitance plus 120 resistance values. Values also matched the native netlist numerically.

The native is one large custom sheet with 19 functional regions. I rendered and visually inspected **all 19 regions/all 333 components**, including properties, pins, bodies, wires, and ground attachments; no representative-only or unchanged-geometry substitute was used. Native and PDF graphics are not identical. A per-region 12.7-mm/source-unit projection, anchored at the first component, found 24 center and 99 pin offsets, all at most 0.635 mm; therefore exact geometric equivalence is explicitly not asserted. The actual native views and connectivity export control the judgment. A supplementary scan transformed all 3,057 visible SVG text glyph bounds and checked all 2,106 wire segments, including diagonals: no wire entered a text bound or its 0.13-mm expansion. This scan supplements visual judgment, not a comprehensive geometric DRC.

| PDF/native region | Components | PDF grade | Visually inspected functional anchors |
|---|---:|---|---|
| 01 input | 6 | READABLE | J9, F_IN, Q_IN, gate clamp, D_IN |
| 02 buck | 13 | EFFORTFUL | U_BUCK, D_BUCK_IN, L_BUCK, input/output banks, bleed |
| 03 held/LDO | 13 | READABLE | D_HOLD, Q_PRE/Q_PRE_EN, C_HOLD1/2, U_LDO |
| 04 supervisors | 14 | READABLE | U_PWR/U_AUDIO, sense dividers, CT, PWR_EN/AUDIO_EN |
| 05 dump | 10 | READABLE | U_DUMP/U_LDO_EN, DUMP_RC, Q_DUMP, R_DUMP |
| 06 channel 1 | 27 | EFFORTFUL | J1/F1/U_ESD1, U_AFE1, filters, U_ISO1, ADC1P/N |
| 07 channel 2 | 27 | EFFORTFUL | J2/F2/U_ESD2, U_AFE2, filters, U_ISO2, ADC2P/N |
| 08 channel 3 | 27 | EFFORTFUL | J3/F3/U_ESD3, U_AFE3, filters, U_ISO3, ADC3P/N |
| 09 channel 4 | 27 | EFFORTFUL | J4/F4/U_ESD4, U_AFE4, filters, U_ISO4, ADC4P/N |
| 10 channel 5 | 27 | EFFORTFUL | J5/F5/U_ESD5, U_AFE5, filters, U_ISO5, ADC5P/N |
| 11 channel 6 | 27 | EFFORTFUL | J6/F6/U_ESD6, U_AFE6, filters, U_ISO6, ADC6P/N |
| 12 channel 7 | 27 | EFFORTFUL | J7/F7/U_ESD7, U_AFE7, filters, U_ISO7, ADC7P/N |
| 13 channel 8 | 27 | EFFORTFUL | J8/F8/U_ESD8, U_AFE8, filters, U_ISO8, ADC8P/N |
| 14 ADC | 12 | READABLE | U_ADC, CFG1/2/4/5, LDO_A/D_FILT, local bypass |
| 15 external bias | 8 | READABLE | VMID1_EXT/VMID2_EXT dividers and shunts |
| 16 references | 12 | READABLE | FILT1P/FILT2P banks; separate VMID1/VMID2 |
| 17 clocks | 9 | EFFORTFUL | J10, U_CLK, MCLK/BCLK/FSYNC, source resistors |
| 18 TDM | 11 | READABLE | J11 sense, U_OE, U_TDM_SCH, U_TDM, R_TDM |
| 19 reset | 9 | EFFORTFUL | U_RST1/U_RST2, C_RST_T, Q_RST1, ADC_RESET_N |

Every corresponding native region is EFFORTFUL because its generic passive bodies require reference/value interpretation. Coverage totals are 19/19 PDF pages, 19/19 native regions, 333/333 components; no commissioned region is unviewed.

**F1 — folded routing, nonblocking.** On page 02, BUCK_SW from U_BUCK.5 to C_BUCK_BST.2/L_BUCK.1 folds beneath L_BUCK and crosses its 5V_BUCK output. The 240-dpi detail shows the crossing hop; native connectivity keeps the nets separate. On pages 06–13, U_AFE1–8 feedback through C_FB[n]P/N and R_X[n]P/N surrounds R_OUT and FILTER[n]P/N branches, requiring deliberate tracing. On page 17, J10.9/.10/.12 fanout to U_CLK.1/.3/.6 and the three R_MCH_*_PD resistors produces several crossings. Page 19 similarly folds RESET_C/RESET_RC around U_RST2.5/.6/.7 and C_RST_T. Named endpoints remain distinct and readable. Conventional amplifier symbols and simpler corridors would reduce effort.

**F2 — decoupler depiction, nonblocking.** PDF capacitor plates, local rail labels and ground bars make bypass/shunt function clear: C_OPA1–8 use 3V3_ADC, C_ISO1–8 use 5V_LDO_HOLD; ADC supply bypass is separated from LDO_A/D_FILT and VMID/reference banks. All power/ground attachments were visible and consistent. Native capacitors use rectangular bodies rather than plates, so capacitance units and C references carry the meaning. Native decoupler grade is EFFORTFUL; PDF decoupler grade is READABLE. C_HOLD1/2 and C_FILT1/2_470U show positive terminal 1 on the held/reference rail and terminal 2 at ground in both representations.

Actual device polarity is recoverable: diode K/A and MOSFET G/S/D labels are readable; supplied primary DMP6023LFG and AO3401A datasheets establish P-channel devices, AO3400A N-channel. Page 05 correctly identifies U_DUMP/U_LDO_EN as inverting; page 18 identifies U_OE as inverting and U_TDM_SCH as noninverting, agreeing with supplied Nexperia 1G14/1G17 primaries. These boxes require reading identities/headings rather than conventional polarity symbols. NC meaning is explicit at U_ESD1–8 pins1/2, U_LDO4/6, U_ADC26–28, unused J10/J11 pins, and the four Schmitt pin1 positions; native crosses and the 42 singleton exports agree. Same-name cross-page power, bias, ADC, clock, enable and reset continuity matches the actual 178-net graph.

Reproduction evidence is retained at `/tmp/independent-carrier-render-82v2y7bm`: `check.py`, `expand.ts`, `sourcecheck.py`, `geometry_full.py`, `native_projection.py`, fresh exports, per-page/per-region images, and JSON denominators/differences. `regions.json` lists every assigned reference and native crop rectangle. These are newly generated evidence, not prior reports.

All source-prototype boundaries remain: first-article physical qualification, exact sourcing/allocation, connector/cable/mating checks, routing/stackup/current paths, power-state and partial-power behavior, analog/reference behavior, reset and timing validation, and all fabrication/order gates remain separate required work. This witness grants no permission to fabricate or order.
