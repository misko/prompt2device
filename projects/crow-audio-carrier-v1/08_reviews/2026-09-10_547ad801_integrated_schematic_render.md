subject: crow-audio-carrier-v1  
source_commit: 547ad801f45f0ddd9e04315a83794c5775a4a728  
date: 2026-09-10  
reviewer: /root/carrier_final_schematic_readability, independent judgment agent  
context-given: FRESH; complete immutable commission, copied project/ and external_hardware/, supplied page renders, repository method instructions  
independence: No live project, subject prior reviews, journals, STATUS, or prior verdicts opened; no authoring or repair performed; exports and independent parsers written only in private scratch  
review_stage: pre-route  
review_kind: schematic_render  
commission_sha256: 554e96ba0ef5ee467492633f9c17290b811d31cdbb4cc65b1c34d7481d13ccfa  
subject_packet_sha256: da8278e829329f20a0c4ee9a9b6464d691c8fd1e202b3cd812066f6d6d2e3bd0  
netlist_sha256: 7190f3ba8b20280b81e39430fcbd5d5f06d182af30c5ac0ef87383dd98d19e29  
parts_sha256: 2f76a9ca1a8b2e3cf948d3b43fbbbc6ad101f1fccd58de1d7ecd05c556b2f38d  
design_rules_sha256: 672f0b9be3b3f9b6c2a9c9c1b1ea0e12ff4d91f061ede29ac36d6ac71965b8a4  
schematic_pdf_sha256: b0cf9ca3e127dccc59efed4c0accd9371464a6ac55e06de3784eaefb6bb06123  
circuit_json_sha256: b318c3c143930f68eeb6c54fdbb80ba700efcce9a10ec5cf06cc6eb73443f5c7  
native_schematic_sha256: ecf583f25fb015b232a59c1dd5c5b1ff171b3dfad9cf14b3370367370ea7fbf1  
raw_netlist_sha256: e6b6544e06f29d5bbfb7e0fbc3068fe16f0313c0ba15ff09e3235d34ff82d1ad  
design_verdict: DEFECTIVE  
order_verdict: DO-NOT-ORDER  
completed_at: 2026-09-10T15:53:56Z

The integrated readability review is complete and defective on native geometry. The 19-page human PDF is READABLE: the main circuits can be followed, identities and values remain legible, and no misleading electrical connection was found. The separately exported native schematic has reproducible reference/pin collisions and detached clock-pin graphics. Clear PDF spacing does not dispose of these native findings.

I read CLAUDE.md, the KiCad PCB skill, the render-review additions in pin-review-protocol.md, and relevant schematic canon. All 235 tar members matched their copied bytes before and after review. All raw and owning hashes above were independently recalculated both times; 84 part dossiers contribute to the owning parts hash. The permitted method file supplied only hash semantics, not a design verdict. Independent Poppler rendering of the bound PDF reproduced all 19 supplied 120 dpi PNGs byte-for-byte.

All pages were visually inspected at ordinary whole-page size, including wire crossings and small pin text; native clock/TDM sections additionally received 150 and 300 dpi detail inspection. Coverage below refers to the unedited `render/page-NN.png` files under `/tmp/carrier-final-schematic-review-20260910.m5kamgmm/`.

| Page | Actual visual coverage |
|---|---|
| 01 | J9, fuse, reverse PFET, gate zener and TVS |
| 02 | Input diode, buck, bootstrap, inductor, input/output banks and bleed |
| 03 | Hold diode, precharge/bypass, held capacitors and ADC LDO |
| 04 | Raw/ADC supervisors, sense dividers, CT, reset and enable paths |
| 05 | Delayed dump, two inverting Schmitt devices, dump FET/resistor |
| 06 | Channel 1: J1, ESD, coupling, AFE/filter, isolation and ADC1P/N |
| 07 | Channel 2: corresponding complete path to ADC2P/N |
| 08 | Channel 3: corresponding complete path to ADC3P/N |
| 09 | Channel 4: corresponding complete path to ADC4P/N |
| 10 | Channel 5: corresponding complete path to ADC5P/N |
| 11 | Channel 6: corresponding complete path to ADC6P/N |
| 12 | Channel 7: corresponding complete path to ADC7P/N |
| 13 | Channel 8: corresponding complete path to ADC8P/N |
| 14 | All ADC analog, clock, reset, configuration, supply and unused pins |
| 15 | Both independent external half-supply bias dividers and capacitors |
| 16 | Both FILTP banks and separate ADC VMID bypass networks |
| 17 | J10 clock/data interface, U_CLK, pulldowns and series resistors |
| 18 | J11 presence sense, U_OE, Schmitt TDM stage, U_TDM and R_TDM |
| 19 | Supervisor/monostable reset sequence, timing RC and pull-down FET |

| Required checklist row | Completed judgment |
|---|---|
| Functional flow and continuous primary paths | PDF READABLE (S6): pages 1–3 carry protection through conversion and held regulation; pages 6–13 show continuous coupling→AFE/filter→switch paths. Native clock body continuity fails F2. |
| Power/protection polarity | Consistent: Q_IN drain faces fused input; sources face protected output; zener cathode faces source, anode gate; TVS cathode faces positive rail. D_BUCK_IN and D_HOLD cathodes face downstream banks. Polarized reservoir positives face their rails. Manufacturer DMP6023, US1B and B340 primary figures were consulted. |
| Readable identities/values | PDF values and 333 component identities are legible, including 10 kΩ ADC bleeds and 22 Ω clock resistors. Native references fail F1; native active-device Value rows use catalog identifiers, while the PDF prints MPNs. |
| Power/ground attachment geometry | PDF rail/ground ends visibly attach to the intended pins; ADC supply and ground groups are explicit. Native exports retain the correct connected pins, but VCC pin ink overlaps references in F1. |
| Intentional NC meaning | All 42 unconnected ports geometrically match 42 native no-connect markers: J10 7, J11 10, ADC 3, ESD devices 16, LDO 2, and four single-gate NC pins. PDF NC text/end markers distinguish these from active paths. |
| Wire/text/plate/body clarity | No confirmed PDF occlusion or false joining found. Native F1/F2 fail this row. C_TDM_SCH reference sits close above its supply wire but retains visible clearance in the 300 dpi view; it is not a reported collision. |
| Same-net/cross-page continuity | Channel numbering remains distinct into ADC pins; VMID1_EXT serves channels 1–4 and VMID2_EXT 5–8, separately from ADC VMID1/2. Clock, TDM, reset and enable labels retain their respective endpoints. |
| Consistency with native topology | Fresh KiCad export agrees with the frozen netlist on all 220 nets, including 42 unconnected nets. Independent source-trace union reproduces all 178 connected net partitions and 895 connected pins, with zero node differences. Sixteen numeric rail names drop the source-only leading N; each rename was verified by identical node sets. |

F1 — **P2, native reference/pin overlap; PDF pages 17–18; net 3V3_ADC.** Native U_CLK Reference anchor (132.715,2651.465 mm) lies on VCC pin 8 at x132.715, y2648.585–2653.665. U_TDM_SCH (147.320,2777.830), U_TDM (210.820,2845.712), and U_OE (160.020,2866.095) similarly intersect their VCC pin-5 graphics; their vertical pin spans are respectively y2774.315–2780.030, y2842.260–2847.911, and y2863.850–2868.295. Pin numbers overprint reference glyphs. Move the property rows clear of native pin lines and pin-number text, then re-export. Evidence: `/tmp/carrier-native-render-judgment.E20yXtYd/native-clock-detail.png`, `native-tdm-sch-detail.png`, `native-tdm-out-detail.png`, and `native-tdm-oe-detail.png` in that same directory.

F2 — **P2, detached native clock pins; PDF page 17; U_CLK pins 1/6/7/2.** The native body occupies x123.825–141.605, y2653.665–2701.925 mm. Pins 1/6 at x118.745 and pins 7/2 at x146.685 are vertical 1.270 mm stubs, leaving a 5.080 mm horizontal gap to the body. Their endpoints are at y2662.555 or 2693.035. Thus MCH_MCLK/MCH_FSYNC and MCLK_BUF/FSYNC_BUF visibly terminate outside the device while the middle BCLK pair attaches normally. Restore body-facing pin geometry without changing net endpoints. Evidence: the same unedited `native-clock-detail.png`; native PDF page 1. This is drawn disconnection, not an exported electrical open.

Concrete connectivity traces independently checked include J10.9→U_CLK.1, U_CLK.7→R_MCLK.1 and R_MCLK.2→U_ADC.34; corresponding BCLK/FSYNC chains reach U_ADC pins 29/24. U_ADC.25→U_TDM_SCH.2→its output4→U_TDM.2→output4→R_TDM→J10.2 is preserved. The miniDSP manual Table12 supports these interface directions and pin roles. KiCad emitted an annotation-warning line; I used explicit node comparison, not exporter success, as connectivity evidence.

S7 adjacency is adequate in the PDF: channel bypasses accompany their AFE/switch, with ADC bypass/reference banks on adjacent dedicated pages. The limited S5 nominal spot-check used TPS3890 primary Equation2 (PDF p13): 1.15×(1+30.9/10)=4.7035 V and 1.15×(1+17.4/10)=3.151 V for page4. ADR0009 records these divider choices; no DETAIL_DESIGN.md was included. This verifies nominal arithmetic only.

No full rating, transient, timing-margin, physical PCB, thermal, sourcing, allocation, fabrication, order, or first-article acceptance is asserted. The complete eight-row review does not close those separate obligations. Scratch exports, connectivity results and raster authentication are bound by `scratch-evidence-manifest.json` beside this report; the coordinator alone archives evidence and performs any repair.
