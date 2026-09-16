review_stage: pre-route
review_kind: topology
revieweridentity: carrier_rj45_native_pod_topology_s1m1
context: FRESH
date: 2026-09-13
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
netlist_sha256: b4edc879929e85fb35953e06f24ca6f8ade42b14d777b7751cbda47bc84aadff
parts_sha256: d0d0026dd67cbfaa98176799ea34ea3bfde384675d74d58d8cf8f0c88e41fd89
design_rules_sha256: 474e5d0a81baf576aefac32e9c60bce37704bb138961c16bf92573843b6409c4
schematic_pdf_sha256: a85a9a1e79dac95aa48a639bc7738986848ed8c14e8673441967dfe62ed6bb13
exact_netlist_sha256: 26f5b5819dda308da4d7f6df3e8a06f88c5b806c1e71f25cf600b6a56b78ee02
circuit_json_sha256: 9a1871284a29fa2fd63d58acdd6c6411bdc49797288b949161f49a24caa957b7
kicad_schematic_sha256: 1182894e471c6d7c2b86060359a02ce95288c647542b90ca9d2e5a8fe63e12b4

The exact frozen crow-mic-pod-v3 schematic is SOUND for the commissioned pre-route topology lens after the S1M-E3/61T renewal. No electrical-topology defect was found. This does not accept placement, copper, mechanical mating, fabrication, stock allocation, release, or ordering. FIRST-ARTICLE-ONLY / DO-NOT-ORDER remains in force.

Independent measured coverage

- Verified all 297/297 frozen envelope inputs by declared size and SHA-256 before analysis and again immediately before packaging. The owning frozen pre_route_review_check.py independently reproduced all seven expected subject hashes.
- Parsed the current CircuitJSON and native KiCad netlist directly: 40/40 components, 103/103 physical pins, 99 connected endpoints, 20 connected source nets, and four explicit NC pins. Native representation contains 24 nets and 103 nodes because U2.3, U2.7, U3.1 and U3.2 each have a one-pin unconnected net. The maintained electrical invariants grade 39/39 PASS.
- Compared 118 paths common to the supplied current and preceding subsets: 111 are byte-identical and seven differ. Forty current files have no preceding counterpart because the preceding snapshot is intentionally partial; the D1 renewal itself adds the Vishay dossier/PDF and footprint. No preceding file was removed from the current packet.
- CircuitJSON remains 1,188 records. Its substantive changes are D1 manufacturer/supplier identity and its rendered value text. Fifteen unrelated supplier-footprint warning rows reorder/regenerate IDs and source metadata changes. Port, trace, net, schematic wire and PCB geometry records are unchanged. The native netlist changes D1 value/MPN/supplier/footprint plus exporter timestamps/UUIDs; every net and node is unchanged.

Current component and population inventory

The 40 schematic identities comprise 11 capacitors, 14 resistors, three ICs, two diodes, one fuse, J1, MK1 and seven test pads. The exact first-power list contains 33 refs: 31 fitted SMD, manually fitted J1, and MK1 as the off-board capsule represented by its two-wire board landing. Board-mounted fitted population is therefore 32; the machine SMD population is 31. TP1–TP7 are bare copper pads and are excluded from BOM/CPL. The source tree contains 35 part.yaml dossiers because the preceding JKSEMI dossier remains present as unused source evidence while the Vishay dossier is added; it is not a second D1.

Exact S1M source delta and electrical judgment

D1 changes from Shenzhen Jinkaisheng 1N4007(M7)SMA / C2972759 / crow_mic_pod_v3:JKSEMI_1N4007_M7_SMA to Vishay General Semiconductor S1M-E3/61T / C144860 / crow_mic_pod_v3:Vishay_S1M_SMA. The current four-page Vishay document 88711 is hash-bound in the new dossier. Its pages were inspected as images: page 1 explicitly states that the color band denotes the cathode end and rates S1M at 1 kV, 1 A, 1.1 V maximum forward drop at 1 A and 30 A for the specified 8.3 ms surge; page 2 gives 5 uA maximum reverse current at 25 C and 50 uA at 125 C; page 3 identifies the cathode band on the package outline.

The D1 footprint keeps the preceding 2.50 x 1.80 mm pads at 4.00 mm centers and all geometric primitives; only identity/description/value text changes. Pad 1 is the left pad beside the cathode-side silk line and is K/VIN_PROTECTED. Pad 2 is A/12V_FUSED. TSX, CircuitJSON, native schematic and exact netlist all agree. Thus correct-polarity current flows 12V_POD -> F1 -> 12V_FUSED -> D1 anode/pad 2 -> D1 cathode/pad 1 -> VIN_PROTECTED. D2 cathode, C1/C2, R14, TP2 and U2 IN/EN remain on VIN_PROTECTED; D2 anode and R14 return to GND.

The new S1M limits are numerically identical to the preceding rectifier limits relevant here. At the published 50 uA hot reverse-leakage maximum and R14's +1% value of 4.747 kohm, the protected node can reach -0.23735 V. The current TI U2 dossier now records the primary-source -0.3 V IN-to-GND absolute minimum, visibly confirmed on TI PDF page 5, leaving 62.65 mV margin. R14 worst-resistance dissipation is 37.45 mW at 13.2 V and 127.95 mW at the retained 24.4 V clamp boundary, below 250 mW. The 1 kV/1 A diode ratings remain above the 24.4 V protected boundary and 100 mA spoke maximum.

Retained topology and ratings

J1's complete map is unchanged and independently found in all generated domains: pins 1/3/7 = 12V_POD, 2/6/8 = GND, 5 = AUDIO_P, 4 = AUDIO_N, and shell pins 9/10 = POD_SHIELD. POD_SHIELD has exactly J1.9 and J1.10 and no GND node. This is custom analog/DC on a factory Cat6A cable, not Ethernet or PoE, and mating remains power-off.

U2 pins 8/5 remain on VIN_PROTECTED, pin 1 on 5V_QUIET, pins 4/9 on GND, pin 6 on LDO_NR, and pins 3 NC / 7 DNC remain open. The 324 kohm / 100 kohm feedback network and 10 nF feed-forward path are unchanged; independently recalculated worst corners are 4.792587–5.229513 V. Microphone bias/coupling, VREF buffer, 18k/22k inverting preamp, equal 10k polarity restore, private spare follower and the two 100-ohm audio legs remain unchanged. U3 pins 3/5 clamp AUDIO_P/AUDIO_N, pin 4 returns to GND, and pins 1/2 remain open.

Rendered review and equality

All 4/4 current PDF pages were rendered at 144 dpi to 1800 x 1215 RGB images and visually inspected, covering 7 + 11 + 10 + 12 = 40 components. Connector labels and wires, D1/D2 polarity, shield isolation, U2 NC/DNC/PowerPAD, capsule polarity, signal paths, U3 NCs and all page headers are legible. The current header carries CircuitJSON prefix 9a1871284a29fa2f and correct page/component counts.

All four images were pixel-compared with the preceding accepted PDF render. Pages 2–4 are exactly equal below y=125: 5,886,000/5,886,000 body pixels. Page 1 has exactly 784 changed body pixels, confined to [1001,332,1105,345), the changed D1 value text. The generated hash identity line differs only within [349,100,797,117) on every page. Excluding that identity line and the D1-value rectangle gives 8,491,375/8,491,375 equal pixels. Fresh visual review, rather than equality alone, covers the changed D1 drawing and every page.

Warnings, observation and remaining limits

ERC is 0 errors and 158 classified warnings: 64 lib_symbol_issues and 94 endpoint_off_grid. Zero errors is not an all-severity-clean claim. CircuitJSON retains 15 supplier footprint mismatch warnings unrelated to D1.

One nonblocking source-documentation observation remains: unchanged electrical_invariants.yaml rationale text for D1.1/D1.2 still says “1N4007” although the executable assertions address ref D1 and correctly pass for S1M. The stale noun does not alter a pin, net, rating, hash, or the topology verdict, but should be renamed to the current rectifier in a later source cleanup.

The connector SOURCE gate is PASS while FULL is authentically INCOMPLETE with nine physical obligations. Routing/return/ESD geometry, the current conditional 23-locator exception's atlas/render acceptance, physical cable/capsule mating, solder-fillet validation for the retained land, stock allocation, first-article rail/noise/gain/polarity/EMC/thermal tests, and release acceptance remain owed at their owning gates. No board claim is made from this schematic evidence.

Evidence integrity

Every engineering and image-analysis subprocess was launched with finite direct argv through pipeline_runtime.run_stage, explicit cwd/environment, raw log, duration and runtime receipt in allocated scratch. One initial direct netlist parser attempt failed on a tuple-unpack assumption; its log and runtime receipt are retained, the parser was corrected, and the complete census then passed. Host image viewing covered the four schematic pages, all four Vishay PDF pages, and TI page 5. The evidence archive reopens every regular member and rejects symlinks, traversal, duplicates and embedded archives. The supplied preflight is run after packaging. Delivery PASS establishes complete exact-subject evidence, not engineering adoption.
