# Independent 568-to-569 CJ E-FAULT semantic review

review_verdict: INCOMPLETE

efault_rebind: INCOMPLETE

digest_mutation: NOT_PERFORMED

## Scope and packet integrity

This is a fresh, READ_ONLY judgment of E-FAULT semantic eligibility only. It does not accept a schematic, native/PCB artifact, copper, placement, routing, sourcing, physical build, fault test, or release. It does not alter the `power_tree.yaml` binding. The narrow producer PASS is treated solely as a delivery receipt: it delivered the stated CJ and did not establish schematic or E-FAULT acceptance.

The schema-2 envelope is 4,261 bytes and its SHA-256 is exactly `4c573ec38d592d6225c766846eba3d99d922ec99b66d61b4a25e58736a73ca9e`. The detached manifest is 1,733 bytes and its SHA-256 is exactly `64b57cd3cb355ef9b66b9546ac29e445d3a36a7deef5acbe6d717bbe81816359`. I recomputed the SHA-256 and byte size of all **17/17** envelope inputs: zero hash or size mismatches. I separately recomputed all **18/18** manifest entries: zero hash mismatches.

The old raw CJ is 4,854,307 bytes, SHA-256 `2b9a33b6473029138362253c48a28406138221e2dbf28907fb1a6f5a3dfd5410`. The new raw CJ is 4,859,480 bytes, SHA-256 `1f01be73e0699cd62bc734aa189b25e9d66f1097b5ce6f52a8db30533ecc6448`. The supplied comparator source is 2,313 bytes, SHA-256 `1f2ca3cca95b1000e122a8dd7bb006040755af4247105c7a9de932251c1dc204`; its supplied result is SHA-256 `d40b780803bac8bf6cfd4a76b8ae0c06a9aea33e23199739b6799f8998ae622c`. Current `power_tree.yaml` is SHA-256 `d6c91cc46ac614695714f1dc70cb2f7f58a54379a8e1af6bc95f3de1259a55ac` and `route.yaml` is SHA-256 `3c3d8deae57f358ec91675d679299fa5ee209be61958459584c703bf8bb61415`.

## Comparator audit and independent raw-CJ comparison

The supplied comparator correctly reports its limited projection: 568 to 569 components, 1,788 to 1,790 ports, and 1,639 to 1,641 pin-to-net edges. It does include every component field except raw sequence/group/internal-port IDs, and its component signatures therefore include the raw component value, MPN, and supplier fields when present. That is useful, but it is **not** the required complete comparator. It does not compare source-net record fields, source-trace display/subcircuit/map fields or trace grouping, source-component internal connections, or source groups. It also keys components by name, so a duplicate name could collapse; footprint is not a CJ component field and is not independently checked by that script. These are comparator-method P2 defects, not evidence of a source change here, because I made the broader comparison below.

I independently normalized raw source records by resolving every port ID to component-name/pin/name and every net ID to net name, while retaining all non-sequence record fields and all endpoint relationships. Normalized coverage and differences are:

| Required source record | Old | New | Added | Removed | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| `source_component` | 568 | 569 | 1 | 0 | only specified capacitor |
| `source_port` | 1,788 | 1,790 | 2 | 0 | only its pins 1, 2 |
| `source_net` | 282 | 282 | 0 | 0 | exact normalized equality |
| `source_trace` | 1,639 | 1,641 | 2 | 0 | only its two traces |
| `source_component_internal_connection` | 7 | 7 | 0 | 0 | exact normalized equality |
| `source_group` | 5 | 5 | 0 | 0 | exact normalized equality |
| resolved pin-to-net edges | 1,639 | 1,641 | 2 | 0 | only the two stated edges |

The sole normalized component addition is `C_ADC_3V3X_OK_VDD`, a simple capacitor with `capacitance: 1e-07`, `display_capacitance: 100nF`, MPN `CL05B104KO5NNNC`, and JLC number `C1525`. The independently hash-verified capacitor dossier supplies its otherwise-absent CJ package property: 100 nF, 16 V X7R, 0402 `Capacitor_SMD:C_0402_1005Metric`, and C1525. Its entire raw-CJ connectivity is exactly one component, two ports, and two edges: pin 1 (`pin1`) to `N3V3_ADC`; pin 2 (`pin2`) to `GND`. There is no third port or trace, hence no terminal on SENSE, CT, MR, RESET, a 12-V net, USB, or XMOS.

`C_ADC_DIGITAL_OK` is byte/semantic unchanged (100 nF, `CL05B104KO5NNNC`/`C1525`, pin 1 `N3V3_ADC`, pin 2 GND). Both `U_ADC_1V8_OK` and `U_ADC_3V3X_OK` are unchanged `TPS389001DSER`/`C1509297` components with identical six ports and mappings: 1 to their respective SENSE net, 2 GND, 3 `N3V3_ADC`, 4 `N3V3_ADC`, 5 has no external trace, and 6 `ADC_DIGITAL_OK`. Thus the new bypass is on the latter supervisor's VDD pin 4; neither existing TPS389001 circuit was changed.

## Source/fault-path invariance

All **42/42** `external_source_fuse.bound_refs` exist in both CJs with identical normalized component records; all **251/251** of their ports, all **241/241** resolved trace edges, and all **68/68** nets reached by those edges are identical. This includes `J_PWR`, `F_IN`, `Q_IN`, `R_QIN_G`, `D_QIN_GS`, `D_IN`, `U_BUCK`, `C_IN1..C_IN3`, `J1..J8`, `U_SPOKE1..U_SPOKE8`, `R_SPOKE_ILIM1..8`, and `C_SPOKE_DVDT1..8`. The raw path remains J_PWR.1 `N12V_IN` -> F_IN -> `N12V_FUSED` -> Q_IN -> `N12V_PROTECTED`; D_IN and C_IN1..3 remain across `N12V_PROTECTED`/GND, and U_BUCK VIN remains on `N12V_PROTECTED` with output `N5V_BUCK`.

The supplied, hash-verified `power_tree.yaml` still binds the historical old CJ only. Its `external_source_fuse` contract facts are present and agree with the unchanged source-path topology: `bound_refs` is the above 42-reference set; source topology is `N12V_IN` to `N12V_PROTECTED`; delivery is 2.185 A at 11.4 V minimum and 13.2 V maximum/recovery; instantaneous peak is 3.4 A; persistent maximum is 2.85 A; cumulative excess above 2.85 A is 10 ms; and rearm is prohibited until fault removal plus an input power cycle. Its stated episode scope includes capacitor discharge and retries. The fuse allocation is 2.85 A and 3.152 A2s; PFET assumptions are 50 mOhm, 123 C/W, 70 C ambient, and 150 C junction limit. Since all 42 relevant source identities and their endpoints are invariant, the CJ supplies no evidence of a topology, source-current, fuse, retry, or PFET-assumption alteration.

## Capacitor quantitative coverage judgment

The actual declared `N3V3_ADC` output range is 3.22--3.38 V; use its 3.38-V upper bound, not an assumed nominal 3.3 V. For C = 100 nF:

* At 3.38 V: Q = C*V = **0.338 uC** and E = 0.5*C*V^2 = **0.57122 uJ**. If, solely for comparison, the charge were spread uniformly over the entire 10-ms allowance, it would average 33.8 uA; that is not a peak-inrush or discharge bound.
* At the deliberately over-conservative 13.2-V external-source maximum: Q = **1.320 uC** and E = **8.712 uJ**. Spread over 10 ms it would average 132 uA, again without bounding the actual waveform. This voltage cannot be applied directly to the regulated 3.38-V rail; it is an energy/charge upper bound requested for source-side comparison.

`route.yaml` assigns `N3V3_ADC` to the 0.5-mm `quiet_power` routing class, but contains no inrush, stored-energy, source-current, or 10-ms discharge budget. `power_tree.yaml` gives `N3V3_ADC` a 0.25-A output allocation but likewise contains no minimum rail rise time, capacitor ESR/ESL, source/cable impedance, regulator current-limit/startup response, post-fuse capacitor inventory, or fault-discharge waveform/integral that includes this added capacitor. Its own `post_fuse_cap_discharge_status` is `first_article_owed`, and its qualification evidence explicitly owes source/output-capacitor discharge and repeated-fault waveforms.

Consequently the 3.4-A instantaneous, 2.85-A persistent, and 10-ms limits are requirements for a whole episode, not a demonstrated conservative coverage model for this additional local stored energy/load. C*dV/dt leaves the inrush/discharge peak indeterminate without the missing slew/impedance and protection-response data. The small computed energy alone cannot prove that the added event neither contributes to an over-limit instantaneous peak nor uses cumulative-excess time. It also cannot establish whether the 0.25-A regulated-rail allocation covers start-up. This is the controlling P1.

## Findings and decision

* **P0: none.** The raw-CJ source delta is exactly the specified two-terminal component and all named source/fault identities are invariant.
* **P1: unresolved whole-fault/inrush/discharge coverage.** No supplied model or waveform converts the new capacitor's charge/energy into a conservative bound against the 3.4-A peak, 2.85-A persistent, and 10-ms episode limits. Under the review instruction, this prevents `SOUND` and prevents a digest rebind.
* **P2: supplied-comparator incompleteness.** Its projection masks meaningful changes to source nets, trace metadata/grouping, internal connections, and groups; the independent comparison above checked those records for this packet. The absent raw-CJ footprint field was checked from the supplied matched-MPN capacitor dossier, not claimed as a CJ field.

Exact next source action: add a conservative, versioned E-FAULT calculation or measured qualification plan to `power_tree.yaml` that includes this 100-nF `N3V3_ADC` capacitor and all post-fuse/downstream capacitance. It must bound rail ramp/inrush and fault-discharge current versus source/cable impedance and regulator/protection behavior, integrate any current above 2.85 A over the entire episode (including retries), and show compliance with 3.4 A, 2.85 A, and 10 ms at the 13.2-V bound. Then regenerate and review a CJ bound to that evidence before proposing the exact digest mutation. Preserve all prior physical, first-article, schematic, placement, routing, sourcing, and DO-NOT-ORDER holds.

