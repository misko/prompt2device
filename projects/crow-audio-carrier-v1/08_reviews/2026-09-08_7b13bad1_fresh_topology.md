subject: crow-audio-carrier-v1 schematic admission before placement
date: 2026-09-08
reviewer: fresh independent topology reviewer /root/carrier_schematic_topology_7b13bad1
context-given: FRESH; assigned TASK, strict task envelope, commission, bound source/netlist/dossiers/manufacturer documents; no prior conversations or review witnesses consumed
source_commit: 7b13bad1c03badcd040c48e38bf32f44c0dadce3
review_stage: pre-route
review_kind: topology
design_verdict: DEFECTIVE
order_verdict: DO-NOT-ORDER
netlist_sha256: 8db05581656333deca457b2ff21828dd5aedc32067446407a393344aae354076
parts_sha256: f7c7a547aa9f4e3f4c3403d37b44fbc72909c4ac5d35183c18c46bd289eb62f4
design_rules_sha256: 78bcdad0b6380aefca514461f356f4d33134af36ec07e12d617b130789fe0ab1
schematic_pdf_sha256: a01f739910edaefb4f2e524b4a92d0a190680d379e140927bc7d21601b54f968
subject_raw_sha256: e6428d2ef69dddab64c3896d76247507e9ede12bfc6a892886b7bb9210b95f4d
subject_semantic_sha256: e873064a0bdc8c7e4c8ae075cc9211f9beb4a84a73267aea4f128dee58743eb4
commission_id: CARRIER-TOPOLOGY-20260908
input_handoff_id: sha256:ffc15d0fadf78b40c6aee3140dec01cd63f14de3f9a70a86343f171f3f9d8f9f
completed_at: 2026-09-08T14:37:59Z

## Integrity and scope

`pipeline_execution.verify_input_packet(envelope, ROOT)` passed all 458 files before review at 14:24:21.977456Z and after review at 14:37:59.344295Z. The commission’s 456 artifacts exactly match their envelope entries; the envelope additionally binds TASK.md and commission.json.

An independent balanced-S-expression reading of the native netlist found 299 components, 165 functional nets plus 40 intentional NC singleton nets, and 868 pin entries. The generated source-component inventory contains 58 selected MPNs; all 58 resolve to exact dossier-bound primary PDF bytes, with no selected supplier-code/dossier mismatch.

This is an unqualified laboratory-prototype schematic review, not physical qualification, PCB acceptance, assembly allocation, or order authorization. No project or review artifacts were edited. Machine records were not substituted for electrical judgment.

## Checklist

checklist: requirements_and_scope PASS

BRIEF, requirements, power tree, shared spoke interface and accepted ADR-0007 establish eight simultaneous 0.10 A spokes, 11.4–13.2 V isolated input, at least 10.8 V at carrier output headers, 1.2 Vrms maximum balanced input, one hardware-controlled ADC, and an independently powered external MCHStreamer. Pi, PoE, Ethernet and USB remain off-board. The source implements this partition. Prototype measurements, outdoor qualification and purchasing remain separate gates; none are claimed here.

checklist: eight_analog_signal_paths PASS

Independently traced every channel from Jn.3/.4 through two 1 µF film coupling capacitors, two 100 kΩ bias resistors, the OPA1656 pair, same-leg 300 Ω feedback and 680 pF feedback capacitors, 10 Ω outputs and the 15 nF differential filter. These connections match the actual AN0556R1 Figure 2, visually inspected on p4.

Each TMUX2821 follows the complete filter. Its source pins 1/5 connect FILTERnP/N; drain pins 2/6 connect ADCnP/N. Neither feedback leg bypasses isolation. All sixteen ADC-side inputs have 100 kΩ and 1 nF to ground.

| Channel / header | ADC P pin | ADC N pin | Intended TDM slot |
|---|---:|---:|---:|
| 1 / J1 | 40 | 39 | 0 |
| 2 / J2 | 42 | 41 | 1 |
| 3 / J3 | 46 | 45 | 2 |
| 4 / J4 | 48 | 47 | 3 |
| 5 / J5 | 14 | 13 | 4 |
| 6 / J6 | 16 | 15 | 5 |
| 7 / J7 | 20 | 19 | 6 |
| 8 / J8 | 22 | 21 | 7 |

Channels 1–4 use VMID1_BUF; channels 5–8 use VMID2_BUF. Loaded distortion, isolation feedthrough and realized matching remain unmeasured.

checklist: adc_configuration_and_references PASS

Native straps are CONFIG1/2 = 4.7 kΩ to ground, CONFIG2/3 = 0 Ω to VDD_A, CONFIG3/4 directly grounded, CONFIG4/10 = 4.7 kΩ to VDD_A, and CONFIG5/11 = 100 kΩ to ground. DS1314F1 pp19–20 therefore selects secondary 44.1/48 kHz operation, minimum-slot TDM, normal channel order and linear-phase fast-rolloff filtering with HPF.

VDD_A1/5, VDD_A2/9 and VDD_IO/31 share 3V3_ADC. VDD_D/33 connects LDO_D_FILT/32, not 3V3_ADC. SPI pins 35–37 are grounded; SPI_CS/38 is high; unused DOUT2–4 have NC treatment.

Both external 10 kΩ/10 kΩ VMID dividers feed U_AFE9 followers, with feedback before each 100 Ω output isolator and 4.7 µF reservoir. ADC_VMID1/2 remain separately bypassed and do not supply those followers, satisfying DS1314F1 §4.5.6/p31. FILT positive pins 43/18 retain separate 1 Ω feeds and 470 µF banks; negative pins 44/17 and capacitor returns are grounded directly.

checklist: component_identity_and_ratings PASS

All 299 source components have selected identities spanning 58 MPNs with matching bound primary PDFs. Signal capacitors use the declared stable film/C0G parts; polarized reservoirs have positive terminals on their named positive rails. Control parts operate within their steady supply ranges; the OPA supply is 4.85–5.15 V, TMUX/held controls remain below 5.5 V, and the ADC rail screen lies within its 3.13–3.47 V analog recommendation.

At the declared VMID acceptance ceiling of 1.70 V, a balanced 1.2 Vrms input reaches 2.5485 V per positive leg, below the OPA1656’s 2.60 V common-mode ceiling at 4.85 V. This is a conditional headroom calculation, not measured distortion.

Hot resistance, capacitor bias/lifetime behavior, switch partial-supply behavior, and pulse/thermal capability remain explicitly conditional. Published typical quantities have not been promoted to guaranteed minima or maxima.

checklist: power_entry_protection PASS

Native topology is J9.1 → F_IN → Q_IN drain/common pin 5 → source pins 1–3 → 12V_PROTECTED. Q_IN’s gate has the 100 kΩ pull-down and correctly oriented gate-source zener. D_IN’s cathode is on the protected positive rail. This provides reversed-J9-hookup blocking, not downstream reverse-current blocking or sustained overvoltage cutoff.

The bound Littelfuse tables support 1.27 A input-PPTC hold and 0.16 A branch-PPTC hold at 85°C as reference rerating data. Recalculation of the declared resistance budgets yields 10.896 V at each header and approximately 0.9639 A upstream demand. These are document-level screens, not hot four-wire or fault-selectivity results.

The SMBJ15A’s cited 24.4 V clamp with the declared 20% voltage allowance gives 29.28 V, below the selected buck’s 32 V operating ceiling, input capacitors’ 50 V rating, input PPTC’s 33 V rating and PFET’s 60 V rating. Its published pulse ratings are not blanket hot-board immunity. The audio TVS arrays have appropriate normal-voltage headroom; downstream transient survival remains expressly unqualified.

checklist: regulators_and_capacitor_corners PASS

U_BUCK has fixed-output FB on 5V_BUCK, EN/VIN on the protected input, the bootstrap capacitor between BST/SW, and XGL4020-332MEC between SW/output. The selected inductance lies in the AP63205’s permitted range. U_LDO’s IN, OUT, FB, EN, SS_CTRL and NR/SS connections agree with SBVS318B.

Independent recalculation gives approximately 3.235–3.332 V for the declared prototype divider corners and 308.6 mW/102.56°C for the LDO’s reference-board thermal screen at 85°C. This does not establish achieved PCB thermal resistance.

Declared capacitor deratings yield 13.77 µF buck input, 64.719 µF buck output, and 16.180 µF for each local LDO 47 µF capacitor including the additional lifecycle factor. ADC-bank minima are 1.618, 0.1618, 0.34425 and 3.4425 µF, exceeding the applicable Cirrus guideline minima.

The independently inventoried ADC charging groups total 1060.98 µF nominal; both 470 µF reference reservoirs are retained. AP63205’s 4 ms soft start and complete NR/SS ramp behavior are not guaranteed timing bounds. Large-bank stability, complete rise/fall behavior, restart and pulse heating remain qualification obligations.

checklist: mch_clock_and_tdm_interface FAIL

The clock/frame configuration itself is consistent: 48 kHz × 8 × 32 = 12.288 MHz BCLK; MCLK is 24.576 MHz. J10 pins 2/9/10/11/12 agree with miniDSP’s TDM8 table; J11 uses J3 ground/presence only. The manual’s actual p14 timing diagram was inspected. Three 10 kΩ clock pull-downs, Ioff-capable buffers, series damping and Schmitt presence-to-OE conversion are present.

However, TDM_RAW has no defined bias when the ADC output tri-states. See CARRIER-TOPO-001.

checklist: sequencing_partial_power FAIL

The held analog-power topology is coherent at the stated conditional-prototype boundary: D_HOLD isolates stored input energy; R_PRE/Q_PRE provide delayed precharge/bypass; U_AUDIO opens the sixteen analog paths; delayed U_DUMP and U_LDO_EN then discharge/disable the ADC rail. The minimum declared supervisor charge delays are approximately 298 ms and 597 ms. The reset chain correctly uses CLR rising on SN74LVC1G123 to produce Q high and pull ADC_RESET_N low, following an initially high interval. TPS3839’s 120 ms minimum delay exceeds 2 ms; the selected pulse network has substantial nominal margin but no manufacturer-guaranteed minimum pulse duration.

Cold-start below valid logic supplies, detector/dump delay allocations, reverse margin, full ramp endpoints and rapid restart remain the named physical obligations. Independently of those acknowledged holds, the powered TDM buffer lacks a defined input during ADC reset/non-transmission, so complete default-state closure fails under CARRIER-TOPO-001.

## Finding

### CARRIER-TOPO-001 — P2 — Define TDM_RAW when the ADC is not transmitting

Location: [crow_audio_carrier_v1.tsx, U_TDM connections](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/03_tscircuit/src/crow_audio_carrier_v1.tsx:550), U_ADC.25 → U_TDM.2; confirmed in the [native netlist](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/netlists/crow_audio_carrier_v1.net:30282).

The complete TDM_RAW node census is only `U_ADC.25` and `U_TDM.2`: there is no pull resistor or keeper. Cirrus DS1314F1 p36 explicitly makes ASP_DOUT high impedance when not transmitting. TI SCES223U p5 specifies valid CMOS input conditions and a 10 ns/V input-transition ceiling at 3.3 V. Consequently the powered buffer’s A input is undriven during non-transmitting intervals, including ADC reset. Its OE follows remote presence alone, so it can also be enabled while that input is undefined. OE disable protects the external output but does not provide a defined A-input state.

This is a schematic omission, not a claim that excess current or spurious transitions were measured.

Recommended correction: provide a defined TDM_RAW state through a suitably bounded bias/keeper or appropriate input-stage choice; check leakage, ADC drive/loading and transition behavior. Extend the source invariants to cover ADC reset/non-transmission as well as remote-presence states, regenerate, and re-review the changed exact subject.

## Disposition

Eight checklist rows completed: six PASS, two FAIL, zero INCOMPLETE. One P2 source finding; no P0/P1 finding identified. Correct the TDM default-state omission before claiming a sound schematic. All previously declared prototype qualification and order holds remain open.
