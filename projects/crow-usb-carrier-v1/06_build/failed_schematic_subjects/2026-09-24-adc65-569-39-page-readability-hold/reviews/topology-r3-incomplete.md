review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
circuit_json_sha256: 1f01be73e0699cd62bc734aa189b25e9d66f1097b5ce6f52a8db30533ecc6448
netlist_sha256: 7ab8c90f46ff4f25a9af50f43659a6b304e3c15932875519fa916fd018b1d8cc
parts_sha256: 833913d1c3d68cec43ab53f34e63b48cbf0e38bd3ec5a5115abfbaa5e23c2a0e
design_rules_sha256: 8211187b0a0bb0ab38799ade9459944f0226cdf0180a75bcfdb94ca385a1a0c1
helper_path: review/pre_route_review_check.py
helper_sha256: b02a6d97feef2436ba71053e676d87e04c726b1ceec92cd92cf8a4b5d25c6b4e
packet_manifest_sha256: 1cadb2895230a120e927cc0ebfc57783b31bd57b9e990276e085b0ed256a9e88

# Independent frozen-packet topology review

Scope was the complete frozen subject in `/tmp/crow-39-formal-review-terra-vDNAHk`, not a delta-only review. I recomputed every one of the 839 manifest-file SHA-256 and size entries: 839/839 match, with no missing or extra manifest discrepancy. The packet manifest itself recomputes to the front-matter value. Its declared scope is 100 topology-bearing source/policy files, 21 frozen current artifact/evidence files, 289 local parts dossier/evidence files, 415 context files, 3 protocol/helper files, and 11 immutable historical-only files. The latter and prior review verdicts were not used as a current witness. `pdfinfo` confirms that the separately bound rendered PDF is 39 pages, unencrypted; readability was not judged here.

The designated project freeze receipt also reopens at its recorded SHA-256 `6498e96a512ab6bee141f76b230fb5b92849f56096793f4554e54970e4313233`; it binds raw and semantic subject SHA-256s, both `4841591b695cd4b64a8d5e8cda729f1e0de703cecfff580128369481583e6aeb`. The named fresh topology probe receipt, output, and result reopen at `d415ff72a74fc956d08800f7a5f4beb633668b63b9b345ce9ca5f0286d54a981`, `cd91ea35b80b65df16d995a8c8096faf90055154b2f203b96f91ebac682f6a06`, and `bcc7bb208f9765fc74f374783f7be27584af41396bded61814cdc2a237fbba47`. It is schema-2, READ_ONLY, terminal PASS, has the packet nonce and the same raw/semantic subject binding. This report is a new review, not a copied probe or former review verdict.

## Recomputations and cross-artifact census

Raw Circuit JSON is `1f01be73e0699cd62bc734aa189b25e9d66f1097b5ce6f52a8db30533ecc6448`. Its 10,551 elements contain 569 source components and the same 569 schematic components, 1,790 source ports, 1,641 source pin-to-net traces, 282 source nets, 39 schematic sheets, and 7 explicit component-internal connection records. No PCB elements exist in this pre-route Circuit JSON. The native KiCad schematic is separately bound as `74a9edc982039843bb2938ad3664a0fd67a442fb09068fcb1039dbfd47a989d4`.

The raw KiCad netlist is `8a1ad62eeb9da4b9e8574269c07d613aaf3c956e09096ee4d2adc11595b9e502`; applying the packet helper's presentation-metadata normalization gives the front-matter digest `7ab8c90f46ff4f25a9af50f43659a6b304e3c15932875519fa916fd018b1d8cc`. Its full native census is 569 components, 428 nets, and 1,787 net nodes. This agrees with the 569-component source census. The source graph has 1,641 pin-net edges, 282/282 source nets have at least one port, and no port is placed on more than one source net.

There are 149 untraced source ports. They are not silently treated as opens: 29 are represented by seven internal-connection records (15+2+2+2+2 on U_XU, 2 on Y_XU, and 4 on J_USB), and the exported netlist has 146 intentional `unconnected-*` nets. The remaining exposed untraced port names are documented NC, unused, PG, CT, fault, or intentionally unused signal functions (including the XU unused I/O population, USB SBU, eFuse FLT, regulator PG/NC, supervisor CT, and ESD NC pins). The three J_USB internal pins do not carry a public source pin number and are within the four-contact internal J_USB grouping. This source/native representation difference is recorded as debt below, rather than inferred to be a short or an accidental connection.

The complete-parts digest was recomputed from all 112 sorted `02_parts/*/part.yaml` path/NUL/bytes/NUL records: `833913d1c3d68cec43ab53f34e63b48cbf0e38bd3ec5a5115abfbaa5e23c2a0e`. All 569 components have an MPN; their 90 unique normalized MPNs all resolve to a packet part dossier. All 569 native footprint assignments are nonempty and match the referenced `part.yaml` footprint declaration; 46 unique footprints appear. The most populated are R_0402 (152), C_0402 (131), C_0805 (72), GRM32E 1210 (42), and the 16 each of the stated THT and Panasonic bulk-cap footprints. Values are nonempty (79 unique). I parsed all 60 executable electrical-invariant assertions: 27 value and 33 pin-on-net assertions; 60/60 match after normalizing the netlist's ohm glyph presentation.

All 11 semantic rule YAMLs plus the helper's `route.yaml#design-v1` projection produce `8211187b0a0bb0ab38799ade9459944f0226cdf0180a75bcfdb94ca385a1a0c1`. This binds requirements, integration, nets/RF rules, power tree/stages, protection paths, connector/assembly rules, and electrical invariants. It does not prove physical placement, routing, fabrication, or first article behavior.

## Electrical-topology audit

Input ownership is unambiguous in the extracted graph: J_PWR.1 and F_IN.1 are N12V_IN; F_IN.2 and Q_IN.5 are N12V_FUSED; Q_IN source pads 1/2/3, D_IN, D_QIN_GS, input capacitors, U_BUCK VIN/EN, and all eight U_SPOKEn IN/SHDN inputs are N12V_PROTECTED. This is the stated fuse-before-PFET reverse-polarity path. The protection contract binds SMBJ15A at the input with 15 V standoff and 24.4 V maximum 10/1000-us clamp screen, and checks the exposed PFET, buck, eFuses, and 50 V input capacitors against that screen. It expressly does not claim broader surge or pod survival.

U_BUCK's output lands, its output bank, the three digital-converter inputs, and the held-rail feed are N5V_BUCK. U_3V3X, U_1V8, and U_CORE have their required EN/FB/GND/SW/VIN pin-net assignments; the three digital switching rails are kept as distinct named nets. The selected N3V3_ADC owner is U_LDO (LT3045): its OUT/OUTS plus 68 observed nodes feed the ADC, analog front end, reset/supervisor, bias, decoupling, and quiet-rail loads. The rules set N3V3_ADC to 3.22--3.38 V, 0.25 A maximum, with N5V_BUCK as its parent.

The USB boundary is electrically coherent in the frozen graph. Reversible receptacle contacts J_USB.4/J_USB.12 and J_USB.5/J_USB.13, the shunt ESD pads, and U_XU.60/.59 are respectively the four-node USB_DP and USB_DN trees. VBUS_USB terminates in receptacle VBUS contacts, local capacitance/bleed, the VBUS ESD device and sensing divider; it is not connected to an on-board power-source rail. RF policy identifies the XU316 USB PHY as the device endpoint, 90-ohm intent, ESD branch, no-via intent, and required later impedance/return/skew proof. J_PWR, J1--J8, USB, and JTAG remain interface boundaries; no external supply, cable, pod, or attached appliance is asserted as qualified by this review.

The eight distribution paths each leave N12V_PROTECTED through a TPS26625 to its own N12V_PODn rail. The rule uses 44.2 kOhm ILIM and 10 nF dV/dt per channel, nominal 0.10 A per spoke, 0.145--0.159 A current-limit screen, and a 2.12 A eight-spoke normal allocation. The stated faults are not converted into a claimed result: source/cable load line, cap-discharge episode, eFuse hiccup/retry, pod startup/capacitance and thermal behavior remain open.

Capacitor/rating audit found the new factual change and no raw net contradiction. The frozen delta is exactly one added component, `C_ADC_3V3X_OK_VDD`, 100 nF Samsung CL05B104KO5NNNC (16 V X7R, 0402), from N3V3_ADC to GND; it adds exactly its two pins and exactly two edges, with no removals or other component/pin/edge changes from the recorded 568-component predecessor. Its 16 V rating exceeds the declared 3.38 V N3V3_ADC maximum. The power-tree engineering banks identify input/output effective-capacitance calculations, dielectric/rating assumptions, and per-bank residual qualification. No capacitor bank is treated here as production-qualified simply because its calculated screening number exceeds its declared minimum.

## ERC evidence

The bound error-only report `de8543b69a7f7f0d8cf426483971fbc2765e7193a5447221daf20b0ec68b6e71` states 0 errors and 0 warnings in the error-only view. The bound raw full report `227e24f82f4684a45803116aa0111cec07138a55f35ca93c21616ea2c12a8f38` contains 4,173 warning markers and no error-severity message. Its available raw category breakdown is: `endpoint_off_grid` 2,625, `lib_symbol_issues` 979, and `footprint_link_issues` 569. This preserves, rather than waives, the warning population.

The historical baseline is 4,216 warnings, with no usable category breakdown. The current raw count is therefore 43 lower, but the packet supplies no category-by-category historical population to determine why. This is an unresolved warning-delta/debt; it is not evidence that all current warnings are harmless. It does not expose an error-level topological contradiction in the frozen net graph.

## Findings, holds, and verdict basis

No source/net/pin conflict, unexpected multi-net port, missing component MPN/footprint, value-invariant failure, raw ERC error, or changed-net regression was found in the complete frozen topology. That evidence supports the `SOUND` pre-route topology verdict only. It is not a promotion, PR-REVIEW gate pass, placement/routing approval, fabrication release, or order authorization.

Open debt remains: (1) reconcile and disposition the 4,173 versus historical 4,216 warning baseline despite the missing historical breakdown; (2) map the 149 source-untraced ports to the 146 native unconnected nets plus seven internal records in an explicit machine-readable parity statement; (3) qualify the exact external isolated supply/cable, source and local capacitor discharge, repeated-fault waveforms, and fuse/PFET thermal coordination; (4) perform real-copper/thermal/IR/return/escape/USB impedance and physical connector/mate review; and (5) verify capacitor effective values, startup/load-step/stability, sourcing/allocation, firmware/integration, and first-article measurements. The packet's own contracts retain these holds. `order_verdict: DO-NOT-ORDER` remains mandatory.
