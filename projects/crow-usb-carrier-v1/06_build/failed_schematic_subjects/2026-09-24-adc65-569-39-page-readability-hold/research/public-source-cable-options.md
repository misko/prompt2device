# Crow public-record external-source/cable screen

**Scope/date.** Public-record-only research, 2026-09-23. No vendor contact,
purchase, order, project-file change, or claim of qualification. This is a
candidate screen, not a released supply selection.

## Governing board boundary

The authoritative contract is an **isolated external 12 V source** delivering
**11.4--13.2 V at J_PWR at 2.185 A continuously**, including the stated static
branch-limited fault, without foldback or hiccup.  In an aggregate/TVS fault,
the entire J_PWR episode, including source-output and cable capacitance
discharge, must stay at or below **3.4 A instantaneous**; the cumulative time
above **2.85 A** is at most **10 ms**; it must then be <=2.85 A or off while the
fault remains. An autonomous retry cannot receive a new above-2.85-A allowance.
Fault removal plus a deliberate input power cycle is the only rearm. Recovery is
also <=13.2 V. The addendum explicitly includes every fitted downstream
capacitor in that board-level waveform obligation.

`J_PWR` is Molex **43650-0200**, Micro-Fit 3.0 single-row 1x2 right-angle
header. The part dossier assigns **pin 1 = +12V_IN** and **pin 2 = GND**. The
nominal mating receptacle is **43645-0200** with **43030-0038** tin 18-AWG
female crimp contacts. This fixes mechanical mating but does *not* establish
polarity of a cable connected to a supply: verify the source-side wire mapping
and a completed assembly before energizing.

## Shared detachable board cable candidate

**Molex 226429-1022** is the best public-record fit for a bench-source
lead-in: an off-the-shelf single-row, two-circuit Micro-Fit 3.0
female-to-pigtail assembly, 150 mm, 18 AWG UL 1061, tin contacts. Its official
drawing names the fitted housing as 43645-0200 and contacts as 43030-0038,
calls for 150 +/-4 mm length, and says the free ends are stripped, twisted and
tinned 5 +/-1 mm. It is therefore physically mateable to fitted J_PWR; its free
end can be landed in a source's binding posts or a separately qualified terminal
block. The source and cable are detachable at J_PWR. The drawing demands 100%
continuity/polarity testing but does not state a cable resistance, inductance,
current rating of the completed path, or a source-side polarity assignment.

For all combinations below, make the **verified** end-view mapping `J_PWR pin
1 -> source +` and `J_PWR pin 2 -> source -`. The black-on-black two-conductor
cable makes a label/continuity check essential. Do not infer polarity from wire
color. The official board material already says installed run, strain relief,
far-end support, contact resistance, and physical fit require first-article
qualification.

## Candidate combinations

| Combination | Publicly documented positives | Contract gaps / disposition |
|---|---|---|
| **B&K Precision 1550 + Molex 226429-1022** | B&K specifies a main **isolated** output, 1--36 V and 0--3 A, with constant-voltage/constant-current operation; the manual calls it a floating-ground design. Its datasheet specifies 10--100% load regulation +/-50 mV and line regulation +/-20 mV. Set 12.0 V nominal and a conservative current limit no higher than 2.80 A; B&K says the unit crosses into CC once load equals/exceeds the preset limit, so it is not a hiccup mode by the published operating description. 2.80 A is above the required 2.185 A normal delivery and below both 2.85 A persistent and 3.4 A instantaneous ceilings. | **Plausible bench-qualification candidate only; not qualified.** Published current-regulation is +/-20 mA and the unit has adjustable preset, but no published J_PWR short transient peak, CC-entry delay/overshoot, source-capacitance discharge, cable RL, exact power-cycle rearm behavior, or recovery-voltage waveform. Setting 2.80 A leaves only 50 mA before the persistent ceiling. Its pigtail/binding-post transition is a completed custom lead, so that transition needs a documented construction and qualification. The published regulation supports choosing a nominal voltage but does not prove 11.4--13.2 V at the board after all lead/contact losses. |
| **Rohde & Schwarz HMP2030 + Molex 226429-1022** | Manufacturer material describes the HMP channels as galvanically isolated/floating; HMP2030 has three 0--32 V, 0--5 A channels. It has constant-voltage/constant-current modes plus an electronic fuse/OCP. The public manual describes an adjustable fuse delay including 0 ms, and states an activated fuse link switches linked channels off when current exceeds the limit. Configure one channel at a conservatively controlled 12 V and OCP below 2.85 A; this architecture is closer to the required latched-off fault behavior than a hiccup adapter. | **Plausible bench-qualification candidate only; no PASS.** The available public material does not bound the output-current overshoot or source/cable-capacitor discharge at J_PWR to 3.4 A, nor demonstrate an actual 10 ms whole-episode excess bound, no autonomous retry, or <=13.2 V recovery with Crow fitted. The manual's displayed delay options do not certify trip propagation/current waveform. The exact HMP output-to-226429 termination, its polarity, resistance/inductance and strain relief are also unqualified. Its 5 A capacity is not an admissible fault limit; only a verified programmed OCP plus waveform evidence could make it relevant. |
| **Mean Well GST36E12-P1J + a custom barrel-to-226429-1022 lead** | This is a common compact external 12 V/3 A class-II desktop adaptor candidate. The official sheet lists 12 V, 3 A and 85--264 Vac input. It is useful as a negative control for a familiar ready adapter. | **Reject from published data.** The sheet gives 12 V tolerance +/-3% plus load regulation +/-3%, so its stated output envelope alone can reach 11.28 V before cable loss and 12.72 V before line regulation; the lower bound cannot establish 11.4 V at J_PWR. More decisively, overload is 110--150% of rated output power and protection is automatic-recovery hiccup. That is 3.3--4.5 A equivalent at 12 V before considering dynamics, and automatic recovery conflicts with the no-autonomous-new-allowance requirement. The P1J barrel connector is not J_PWR; no exact off-the-shelf barrel-to-single-row Micro-Fit cable/polarity/rating evidence was identified. Do not adapt or procure this as a compliant package. |

## Result

No ready external adapter/cable package found in this bounded public search
clearly qualifies. The Mean Well adapter is affirmatively unsuitable on its
published protection/tolerance data. The two isolated programmable bench
supplies are candidates for a controlled first-article qualification only; they
are not production-source recommendations and their documents leave the
whole-episode terminal waveform unbounded. Their regulated current limit may be
set below 2.85 A, but that is not evidence that output/cable capacitance,
overshoot, protection transition, or rearm meets the board contract.

## Required qualification before procurement/release

1. Fix the exact supply configuration, exact 226429 length and every
   source-side termination/adapter; record pin-1-plus/pin-2-return continuity.
2. At J_PWR, record calibrated voltage/current with the complete fitted board at
   normal maximum and the specified static branch fault. Prove 11.4--13.2 V at
   2.185 A with the actual cable/contact temperature and its complete path.
3. Apply aggregate/TVS and branch-fault cases and capture the **entire** episode:
   supply/cable/output-capacitor discharge, Crow's fitted downstream capacitors,
   current peak, time integral above 2.85 A, CC/OCP transition, all retries, and
   recovery. Demonstrate <=3.4 A peak, <=10 ms cumulative excess, then <=2.85 A
   or off; demonstrate no autonomous renewed allowance and <=13.2 V recovery.
4. Also perform the contract's separate local post-fuse discharge, hot
   F_IN/Q_IN/gate/thermal, all-pod start-up/cable, and repeated-fault tests.

## Source ledger (direct URLs and SHA-256)

### Project authority inspected

| Item | Direct project path | SHA-256 |
|---|---|---|
| Power contract | `03_src/rules/power_tree.yaml` | `8a15377a61f37c4bc1f204f55170e50c2227fd779dacc6ab05fe4d39cd975ba0` |
| Protection contract | `03_src/rules/protection_paths.yaml` | `8bdb701d2d84f192f2b074cac4ac5814b4995029797d02d5f6f5ebe1ee81fd32` |
| J_PWR assembly dossier | `03_src/rules/connector_assemblies.yaml` | `af77d53db29565b29ac945310e75f603fd89d2f3ad88e5c20446fa5f809da228` |
| Conditional-source contract | `01_docs/research/2026-09-23-external-source-fault-contract.md` | `ff46fe9537b82f9f20cde37daae4f0fb0d96462ac6148d48cd3b721765ad8e83` |
| E-FAULT capacitor addendum | `01_docs/research/2026-09-24-adc65-efault-addendum-review-terra.md` | `4105480acc0277d6674e48b4f06a95745988f29e67b8676cb2b17f9831ae6c30` |

### Public manufacturer records consulted

| Record | Direct URL | SHA-256 of retrieved byte copy / status |
|---|---|---|
| Molex 226429-1022 product customer drawing, rev A1 | https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/226/226429/2264291022_sd.pdf | Direct byte retrieval timed out in this session; no byte SHA asserted. Search backend extracted the exact drawing table and notes. |
| Molex 226429 series chart | https://www.molex.com/en-us/products/series-chart/226429 | Dynamic page; no stable downloadable byte capture/SHA asserted. |
| B&K 1550 datasheet | https://bkpmedia.s3.us-west-1.amazonaws.com/downloads/datasheets/en-us/1550_datasheet.pdf | Not locally byte-captured; evidence read through the public PDF. |
| B&K 1550 manual | https://bkpmedia.s3.us-west-1.amazonaws.com/downloads/manuals/en-us/1550_manual.pdf | Not locally byte-captured; evidence read through the public PDF. |
| R&S HMP series fact sheet | https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/pdm/cl_brochures_and_datasheets/fact_sheet/5214_9344_32/HMP_Fact_sheet_en_5214-9344-32_v2.10.pdf | `86ed8f633066d21895cc0ab0a94b00c9d30c51087750e2d98a784b06d7244ac6` |
| R&S HMP series manual | https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/pdm/cl_manuals/user_manual/1178_6833_01/HMPSeries_UserManual_en_04.pdf | Public record consulted via indexed official PDF; direct byte capture was not retained after URL retrieval failure, so no SHA asserted. |
| Mean Well GST36E series sheet | https://www.meanwell.com/Upload/PDF/GST36E/GST36E-SPEC.PDF | `2b7230946dae854581de8507508b39d0aeb7985914a4484631800b942ea7a4b5` |

`SHA-256` values name only the exact local byte capture at research time; absent
values deliberately are not substituted with a content claim or a page hash.
