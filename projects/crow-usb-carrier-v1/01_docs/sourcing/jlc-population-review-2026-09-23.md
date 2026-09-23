# JLC population backtrack — 2026-09-23

Dated research observations only; inventory may already be stale. M-IMPORT grade CITED direct JLC catalog results with manufacturer evidence linked in the retained reports. No PCBA allocation, substitution or engineering acceptance is claimed. D5 requires in-stock JLC population of all non-through-hole components; distributor coverage cannot close it.

## Current disposition

Terra audited native pad types:468/493instances require JLC population, including the mixed USB connector;25are pure through-hole. The immediate gap is seven SMD MPNs below actual build need plus the unqualified ADC. Five other SMD lines clear build demand but fail the existing150unit buffer. Through-hole population has not been changed.

SOL found direct-catalog candidates for all seven short SMD MPNs. The OPA reel variant is the smallest prospective change. Adjustable buck feedback, larger inductor lands, capacitor bias/ESL qualification and switch topology need substantive revalidation. The supervisor candidate has exactly10units for10needed; the proposed switch pair needs80against199stock and therefore misses the230buffer threshold. Neither is a stock-policy pass.

ADC options are not approved: AK5578EN has36units and is closer to the single-chip architecture/performance but misses the155buffer threshold. Two PCM1865DBTR parts draw10units against913stock but lower ADC SNR and alter full-scale range and synchronization requirements. Stock alone cannot justify adopting that performance change. Current CS5308P-DNR remains stock0.

Next bounded engineering work: independently qualify the OPA packaging change and crystal; evaluate ADC input/noise/clock contracts before selecting architecture; then close affected power/analog blocks. Keep source admission held until selections, population and stock-policy requirements reconcile. No silent buffer reduction or external SMD assembly.

## Retained research records

### population research — verbatim agent report
Report SHA256: `2881289f849776405db130f4ad2b6399c887f41d19a782da40c5c8df4ece7e8e`. Local raw evidence: `06_build/verification/d5-jlc-population/population/`.

# Crow USB carrier v1 — population audit, 2026-09-23

## Scope and method

This is a read-only reconciliation of the new requirement: **JLC is to
populate every non-through-hole component, using an in-stock exact selected
part.** It covers the 84 coded MPNs / 492 instances in
`06_build/sourcing/direct-check-20260923.csv`, plus the selected but excluded
`CS5308P-DNR` / `U_ADC`.  That is the requested 85 selected MPNs and 493 source
components.  It is a stock-and-population audit, not evidence that JLC will
accept an order or a particular assembly process.

Mounting technology was determined from the named native footprint's pad types,
not from package names.  `np_thru_hole` locating holes do not make an otherwise
SMD component through-hole; conversely, a connector with plated through-hole
electrical pads is not classified SMD merely because it has a surface-mount
body style.

## Population result

* 468/493 instances are non-through-hole and therefore must be on the JLC
  population set under the requirement.  This count includes `J_USB`:
  its native GCT footprint has 16 `smd` contact pads, four plated
  `thru_hole` shield stakes, and two `np_thru_hole` locating holes.  It is a
  mixed footprint and must be treated as an SMD placement for this rule,
  with the stake holes retained in the fabrication/assembly review.
* 25/493 instances are pure through-hole: `J_PWR` (one Molex 43650-0200),
  `J1`–`J8` (eight Wurth 615008160221), and `C_A1N/P` through `C_A8N/P`
  (sixteen R82DC4100CK60J).  The user has not chosen an assembly disposition
  for these.  They may be user-populated, but they are **not automatically
  excluded**, removed from the BOM, or removed from the CPL by this audit.

Native-footprint evidence:

| Component | Native footprint evidence | Classification / implication |
|---|---|---|
| `USB4105-GF-A-120` / `J_USB` | `GCT_USB4105_GF_A_120.kicad_mod`: 16 `smd` contacts; four `SH` `thru_hole` stakes; two `np_thru_hole` locators | Mixed; must receive JLC SMD placement under the requirement. |
| `CS5308P-DNR` / `U_ADC` | `Cirrus_CS5308P_QFN48_6x6_P0.4_EP4.6.kicad_mod`: pins 1–48 and EP 49 are `smd` (paste apertures are also SMD-only) | SMD; must be JLC-populated if the new rule is satisfied. |
| `615008160221` / `J1`–`J8` | `Wurth_615008160221_RJ45.kicad_mod`: electrical pads 1–10 are `thru_hole`; two locators are NPTH | Pure THT; no disposition selected. |
| `R82DC4100CK60J` / 16 coupling capacitors | `Capacitor_THT:C_Rect_L7.2mm_W5.0mm_P5.00mm`, corroborated by the source `FilmCap5mm` plated-hole footprint | Pure THT; no disposition selected. |
| `43650-0200` / `J_PWR` | `Molex_43650-0200.kicad_mod`: pins 1/2 are `thru_hole` (plus an NPTH locator) | Pure THT; no disposition selected. |

All remaining selected instances resolve to SMD native footprints/TSX SMD pads.

## Direct-check shortages reclassified

The direct checker measured 14 non-OK lines: nine fail current five-board
build demand and five fail only the configured 150-unit buffer.  The following
is the required reclassification.  "True build shortage" means the observed
JLC stock is below the five-board demand; it does not state that JLC cannot
allocate or assemble the part.

### True SMD build shortages — block the new rule

| MPN | Refs | Instances (5 boards) | JLC stock | Native technology |
|---|---|---:|---:|---|
| `744373240047` | `L_U_1V8,L_U_3V3X,L_U_CORE` | 15 | 0 | SMD, WE-LHMI footprint |
| `TPS389018DSER` | `U_1V8_OK,U_ADC_1V8_OK` | 10 | 0 | SMD WSON-6 |
| `CKG57KX7R1E476M335JH` | thirteen listed bulk capacitors | 65 | 0 | SMD J-lead capacitor |
| `FA-238 24.0000MD30X-W5` | `Y_XU` | 5 | 0 | SMD 3225 crystal |
| `OPA2320AID` | `U_AFE1`–`U_AFE8` | 40 | 13 | SMD SOIC-8 |
| `TPSM63603V5RDHR` | `U_BUCK` | 5 | 0 | SMD B0QFN-30 module |
| `TMUX2821DSGR` | `U_ISO1`–`U_ISO8` | 40 | 16 | SMD SON-8 |

These are 7 MPNs and 180 required pieces for the five-board build.  Their
combined measured shortfall is 151 pieces.  They are the material stock gap
for a JLC-populates-all-non-THT rule.

### SMD buffer-only shortages — build quantity is presently covered

| MPN | Refs | Build demand | JLC stock | Buffer threshold |
|---|---|---:|---:|---:|
| `ASFL1-24.576MHZ-EC-T` | `Y_AUDIO` | 5 | 86 | 155 |
| `TPS389030DSER` | `U_ADC_3V3X_OK,U_ADC_OK,U_XU_3V3_OK` | 15 | 58 | 165 |
| `TPS6282518DMQR` | `U_1V8` | 5 | 51 | 155 |
| `TPS6282533DMQR` | `U_3V3X` | 5 | 44 | 155 |
| `XU316-1024-TQ128-C24` | `U_XU` | 5 | 46 | 155 |

These five lines contain seven source instances.  They meet only immediate
build demand; whether the 150-unit buffer remains a release requirement needs
an explicit policy decision, not a silent threshold reduction.

### Pure-THT shortages — no automatic population decision

| MPN | Refs | Build demand | JLC stock | Current condition |
|---|---|---:|---:|---|
| `R82DC4100CK60J` | 16 `C_A*` coupling caps | 80 | 6 | True build shortage, but pure THT. |
| `615008160221` | `J1`–`J8` | 40 | 0 | True build shortage, but pure THT. |

They explain two of the nine direct build-demand failures.  They cannot be
relabelled as a JLC SMD shortage and cannot be excluded merely because their
stock is zero.

### Separate `U_ADC` gap — formerly excluded SMD, absent from the historical direct check

`CS5308P-DNR` / `U_ADC` is the 85th selected MPN and the remaining one source
instance.  It was formerly excluded by `assembly.yaml:not_assembled` and was
therefore intentionally absent from the historical 84-code direct check.  The
current source state removes that exemption, adds D5 and `COMMISSION_HOLD`, but
still has `jlc=""` for `U_ADC`: there is no exact JLC code.  The recorded exact
JLC/LCSC search has no qualifying Cirrus binding (only a stock-zero
placeholder), so the new rule is currently unsatisfied even if every
direct-check SMD shortage were resolved.  The 84-row receipt remains valid
only as historical coverage of those 84 coded lines; it is stale and
incomplete evidence for the current all-non-THT population request.  Calling
this a secondary-assembler exception would contradict the stated
JLC-populates-all-non-THT requirement.

## Required source / policy backtracks before this can become an order posture

1. Add a new ADR (after `0008`) that makes the rule explicit: all components
   having any SMD electrical placement lands, including mixed `J_USB`, are
   JLC-populated; pure-THT refs require an affirmative per-group disposition.
   Preserve the exact MPN selections unless a separately reviewed selection
   change is approved.
2. Retain the current removal of the `U_ADC` exemption and its D5 /
   `COMMISSION_HOLD` visibility.  Obtain an exact, in-stock JLC source, provide
   its code in the TSX source, and re-run direct stock checking over all 85
   selected MPNs.  Until then, the source must truthfully retain the gap and
   the project cannot claim compliance with the new rule.
3. For each of the seven true SMD shortages, obtain fresh exact-LCSC/JLC stock
   evidence sufficient for the selected build policy, then keep the exact
   selected MPN/code on the population source.  The five buffer-only rows also
   need either replenishment to the existing threshold or an ADR-backed change
   to that threshold; a distributor observation does not supply JLC stock.
4. Reconcile `crow_retained_analog.tsx`, the generated BOM/CPL policy, and
   `assembly.yaml` so that `jlc=""` is not a covert manual-population rule for
   a non-THT part.  In particular retain `J_USB` in the JLC population path;
   do not mistake its four PTH shield stakes for a reason to exclude it.
5. Decide, explicitly, whether `J_PWR`, `J1`–`J8`, and the sixteen R82 parts
   are user-fitted, a separately qualified THT assembly operation, or another
   named process.  Record the refs, BOM/CPL treatment, and evidence in
   `assembly.yaml`/the ADR.  No auto-exclusion is authorized by the present
   requirement.

The present tree remains **not ready to assert the new population posture**:
seven direct SMD build shortages and the excluded, stock-zero SMD ADC remain.
This conclusion deliberately does not infer live JLC process availability,
allocation, consignment acceptance, preview correctness, or THT service from
the stock observations.

## Inputs examined

* `06_build/sourcing/direct-check-20260923.csv` and its dated JSON receipt
  (`2026-09-23T02:10:44Z`; 84 coded MPNs, 492 instances): historical evidence
  that excluded `U_ADC`, not current 85-MPN population evidence.
* Current source state at main `4be37a80`: `U_ADC` exemption removed, with D5
  and `COMMISSION_HOLD` added; no exact JLC code exists for `U_ADC`.
* `03_tscircuit/src/crow_retained_analog.tsx`,
  `03_tscircuit/src/usb_receptacle.tsx`, and exact project footprints under
  `03_src/lib/*.pretty`.
* Part dossiers for USB4105, CS5308P, Wurth RJ45, R82 film capacitor, and
  Molex 43650-0200.


### adc research — verbatim agent report
Report SHA256: `dc4991a46b86d6d95c3646e9466088c71105a0e825a5a8f517ac4e067056b2d0`. Local raw evidence: `06_build/verification/d5-jlc-population/adc/`.

# Crow onboard ADC: JLC population and stock investigation

UTC observations: 2026-09-23 02:49–02:53. This is a bounded candidate screen, **not** an accepted replacement, JLC placement commitment, order allocation, or change to the source. The new user rule requires JLC to populate every non-through-hole device from in-stock parts; the existing U_ADC secondary-assembly exclusion cannot satisfy it.

## Project contract

The [Crow USB carrier brief](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/01_docs/BRIEF.md) binds eight synchronous analog channels, 48 kHz, 24-bit, eight 32-bit TDM slots and an onboard XU316 USB device. The [CS5308P-DNR dossier](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/02_parts/CS5308P-DNR/part.yaml) records 2 Vrms differential full scale and 123 dB typical dynamic range. The selected circuit uses a 24.576 MHz MCLK, 12.288 MHz BCLK and 48 kHz FSYNC. The [assembly rule](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/03_src/rules/assembly.yaml) specifies five boards plus 150 public catalog units of surplus for each BOM line. Existing analog buffers, ADC reference/VMID network, QFN48 footprint, source pin contracts, TDM/clock wiring and layout constraints bind specifically to CS5308P. No candidate is a drop-in.

## Direct JLC catalog observations

I used the repository's unofficial JLC SMT catalog endpoint, POST `https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`, serially with at least 1.2 seconds between requests. Every JSON under [raw](/tmp/crow-jlc-adc-20260923/raw) retains the query keyword, UTC time, HTTP result and complete response. This is public catalog stock, not BOM matcher acceptance or reserved PCBA inventory.

| Exact JLC code | Catalog brand and MPN | Stock | Five-board requirement under 150-surplus rule | Finding |
|---|---|---:|---:|---|
| C9900305019 | JLCPCB Assembly, CS5308P-DNR | 0 | 155 | Exact text appears but no stock; brand does not itself establish Cirrus manufacturer identity. |
| C42457798 | Cirrus Logic, suffixless CS5308P | 0 | 155 | Not the DNR ordering MPN; no stock. |
| C42442015 | Cirrus Logic, CS5308P-CN | 0 | 155 | Earlier revision/suffix and no stock. |
| C2655448 | Asahi Kasei Microdevices, AK5558VN | 32 | 155 | Genuine named part and stocked, but below current buffer. |
| C2651626 | Asahi Kasei Microdevices, AK5578EN | 36 | 155 | Genuine named part and stocked, but below current buffer. |
| C181312 | Texas Instruments, PCM1865DBTR | 913 | 160 (two per board) | Genuine named part and stock clears current catalog arithmetic. Placement still unproven. |

Related search hits: CS5368/CQZ/DQZ variants are all stock 0; AK5538VN C2667106 has stock 1; ADAU1978WBCPZ C443873 stock 61; PCM1864DBTR C544855 stock 97. These do not improve the stock-buffer case. Search responses are retained. Both AKM rows and the TI row are JLC `expand` library type. JLC page links for independent lookup: [AK5578EN](https://jlcpcb.com/parts/componentSearch?searchTxt=C2651626), [AK5558VN](https://jlcpcb.com/parts/componentSearch?searchTxt=C2655448), [PCM1865DBTR](https://jlcpcb.com/parts/componentSearch?searchTxt=C181312).

## Engineering fit and costs

**AK5578EN, one IC.** The [AKM product page](https://www.akm.com/us/en/products/audio/audio-adc/ak5578en/) and [manufacturer datasheet](https://www.akm.com/content/dam/documents/products/audio/audio-adc/ak5578en/ak5578en-en-datasheet.pdf) specify eight differential 32-bit ADC channels, 24/32-bit TDM256, 48 kHz normal speed and 256fs BICK, so the existing 12.288 MHz BCLK and 24.576 MHz MCLK are frequency-compatible in TDM256 slave mode (datasheet Table 9 modes 32–35). Eight samples remain on one serial output and one frame clock. It requires a new 64-pin 9×9 mm exposed-pad footprint, 4.75–5.25 V analog rail (not CS's 3.3 V), altered power/reset/config straps, and reworked analog gain and filter. Typical differential full scale is **2.8 Vpp = 0.99 Vrms** versus CS's 2 Vrms; typical dynamic range is **121 dB** versus CS's 123 dB. The ADC input resistance is 3.6 kΩ typical. Those differences can materially affect Crow microphone level, loading and noise. The datasheet says 24-bit data on falling BICK in slave normal-speed mode, but exact FSYNC polarity, launch/sample timing, and XU316 peripheral/firmware mapping still require a specific timing proof. Stock 36 gives only 31 spare units after five boards and fails the current 150-unit buffer. AKM lists it as mass production; the JLC quantity is still volatile.

**AK5558VN, one IC.** [AKM's product page](https://www.akm.com/us/en/products/audio/audio-adc/ak5558vn/) states it is pin/register compatible with AK5578EN and supports the same eight differential channels and TDM. Its [manufacturer datasheet](https://www.akm.com/content/dam/documents/products/audio/audio-adc/ak5558vn/ak5558vn-en-datasheet.pdf) requires a 4.5–5.5 V analog rail; typical dynamic range is **115 dB**, a larger reduction against CS. It has only 32 catalog units and also fails the buffer. It could be evaluated as an AK5578 footprint alternate, but neither identity can silently substitute for the other in a frozen BOM.

**Two PCM1865DBTR ICs.** The [TI datasheet](https://www.ti.com/lit/ds/symlink/pcm1865.pdf) §10.1.4 and Fig. 59 explicitly show two software-controlled PCM186x devices producing one **eight-channel TDM stream**: first outputs slots 1–4, second outputs 5–8. §9.3.16.4 specifies a 256-BCK frame and, in 32-bit slots, 24 data bits plus eight zero-padding bits. At 48 kHz that is 12.288 MHz, the existing framing. The devices support four differential analog channels each, 3.3 V supply, shared LRCK/BCK and two I²C addresses; TI's illustrated second device uses a BCK-derived internal PLL. A common LRCK defines sample timing, but inter-device group-delay/channel alignment and clock/start sequencing must be proven for Crow's *synchronous* requirement. Analog full scale is **4.2 Vrms differential** and typical SNR is about **110 dB** (datasheet pp. 1, 13, 31, 73), both substantial changes from CS. Existing Crow gain/noise performance cannot be presumed. Two 30-pin TSSOPs, new analog input networks, power/reference, two-address control, reset sequencing, and clock integrity replace essentially the entire ADC cell. Although stock 913 exceeds the 160-unit threshold, it is **not an engineering-approved option** without a quantified analog-performance and sample-coherence review. Firmware source remains outside the present authorized scope.

## Disposition and next bounded candidate

No direct stocked CS5308P-DNR path was found. **Do not retain the secondary-assembler workaround or mark U_ADC/JLC population accepted.** Preserve the source-admission hold while evaluating **AK5578EN first for closest single-IC audio architecture and dynamic range** and **PCM1865DBTR as the stock-robust architecture comparator**. The next bounded engineering proof should calculate Crow's actual peak differential ADC drive/noise budget against AK5578EN's 0.99 Vrms full scale and 3.6 kΩ input, then derive its exact 24.576/12.288/48 kHz TDM slave timing and 5 V power/footprint/placement impact. In parallel, calculate PCM1865's two-device frame alignment, analog gain/noise loss and required XU316 control/peripheral resources. If neither preserves the existing Crow analog-performance envelope, the requirement remains blocked by catalog sourcing; stock alone cannot justify a functional downgrade. Recheck current JLC stock and exact BOM matcher/placement capability at the eventual order stage.

Local manufacturer PDF SHA-256: AK5578EN `e1f3f8c94c17b61ad8107fecca66e47d94c6b679bc2f0df5f2d5ab50971e4bd1`; AK5558VN `47adbccfbc1278d2acbf618ae95783f335aa97c84c959ef1698eb991b6835ff3`; PCM1865 `c42b9dfac5d8a4f684edc45edc8a3b2b82d3e26ea352f1e019044ed8aad4ab50`. Copies and extracted text reside in [raw](/tmp/crow-jlc-adc-20260923/raw).


### smd research — verbatim agent report
Report SHA256: `cf5a0f50780ce76ae770d3d7aa84788a1e673236598a4ebf83f915c6065b8ec7`. Local raw evidence: `06_build/verification/d5-jlc-population/smd/`.

# Crow USB carrier: JLCPCB SMD shortage alternatives

Research cut: 2026-09-23 02:52 UTC. The user requires **JLCPCB to populate every non-THT part from in-stock inventory**. These are candidate MPNs, not approved BOM changes. No project files were edited. Quantities are for five boards; stock counts can change before upload. Inventory below comes from the serialized **direct JLCPCB component endpoint**, queried by the ADC agent and retained at `/tmp/crow-jlc-adc-20260923/raw/C<number>.json`; the independent jlcsearch queries used `CircuitsJlcsearchReport/1.0` and are logged in `/tmp/crow-jlc-smd-20260923/search.log`. Direct JLC observations take precedence over jlcsearch stock. Public TI/manufacturer pages and local exact part dossiers support the engineering screen. All seven shortages have at least a candidate, but the capacitor, inductor, module, and switch require design change or qualification before placement.

| Short part (five-board need) | Direct-JLC-stock candidate | Qty / direct stock | Electrical and package assessment | Required change/hold |
|---|---|---:|---|---|
| FA-238 24.0000MD30X-W5 (5) | **YXC X322524MOB4SI, C70590** | 5 / **66,719** | 24 MHz, 12 pF, 60 Ω ESR max, 3225 4-pad crystal, pads 1/3 crystal and 2/4 case ground. A previous Crow project [part dossier](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/archived_projects/crow-recorder-central/02_parts/X322524MOB4SI/part.yaml) and [decision](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/archived_projects/crow-recorder-central/01_docs/decisions/0014-fa238-crystal-substitute.md) validated this part for the FA-238 function. Tighter ±10 ppm initial / ±20 ppm temperature than the named Epson. | Compare **exact present Epson native pad centers/size** against YXC recommended land, verify case-pad netting and CL using present 22 pF load caps plus board stray. First-article oscillator start and frequency. Do not assume prior board's 18 pF caps apply here. |
| OPA2320AID (40) | **TI OPA2320AIDR, C2863402** | 40 / **582** | Same OPA2320 device and **D SOIC-8** pinout, with R tape/reel packaging suffix; the current AID dossier has the 8-pin D footprint. [TI ordering/product page](https://www.ti.com/product/OPA2320/part-details/OPA2320AIDR) and [TI package table](https://www.ti.com/ods/sysadd/pm/symlink/opa320_pm.pdf) identify D/SOIC-8. | Best near drop-in candidate: update exact MPN and LCSC binding, run native pin/footprint check and BOM uploader allocation. No circuit retune anticipated from packaging suffix. |
| TPS389018DSER (10) | **TI TPS389018QDSERQ1, C2066893** | 10 / **10** | Automotive Q1 variant retains the 1.73 V falling / 1.740 V rising threshold, open-drain active-low reset, CT timing, and DSE WSON-6. [TI Q1 datasheet](https://www.ti.com/lit/ds/symlink/tps3890-q1.pdf) pin map is 1 SENSE, 2 GND, 3 MR, 4 VDD, 5 CT, 6 RESET, matching current part. | Exact-stock count equals five-board need, so **zero allocation margin**. Recheck in uploader immediately before order and revalidate actual CT delay/reset sequencing. No alternate 1.8 V part with comfortable stock identified. |
| TPSM63603V5RDHR (5) | **TI TPSM63603RDHR, C5219327** | 5 / **260** | Same 30-pin RDH 4 × 6 mm family/pin geometry, 3–36 V input and 3 A output, but **adjustable output**, not the fixed-5 V V5 option. [TI family datasheet](https://www.ti.com/lit/ds/symlink/tpsm63603.pdf) identifies the versions and shows the external FB divider. | Redesign FB network: TI equation with bottom 10 kΩ to AGND and top **40.2 kΩ** from 5 V VOUT to FB (verify exact recommended 5 V table and tolerance); ensure existing fixed-version FB connection is removed/changed. Re-run output setpoint, startup, compensation/stability, thermal and layout; update source, native footprint/pin check and power-tree contract. Same copper land does **not** make it a drop-in. Spread-spectrum adjustable `TPSM63603SRDHR` C5219328 also had 174 in jlcsearch, but no direct stock check and changes EMI mode, so not ranked. |
| 744373240047 (15) | **Chilisin MHCI05030-R47M-R8, C329374** | 15 / **2,619** | 0.47 µH ±20%, shielded, max DCR **8 mΩ** (versus Würth 14 mΩ), typical Irms 10 A at ΔT40 and Isat 14 A at **30%** L drop. [Chilisin-authored series specification](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/MHCI05030_2D00_4R7M_2D00_R8.pdf) row is explicit. Current design peak screen is 1.79 A. | **New land and placement:** candidate 5.7 × 5.4 mm, larger than Würth 4.45 × 4.06 mm body; verify height, exact land/courtyard and switch-loop geometry. Do not compare its 14 A/30%-drop Isat directly to Würth 10.4 A/10%-drop rating. Recalculate L(I,T) at worst peak, SRF at 2.2 MHz, loss/thermal with actual copper, and TPS62825 startup/stability. |
| CKG57KX7R1E476M335JH (65) | **Murata GRM32ER71A476KE15L, C84494** | 65 / **56,478** | 47 µF ±10%, 10 V X7R 1210; current project already has [exact Murata dossier](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/02_parts/GRM32ER71A476KE15L/part.yaml). Every named CKG bank is at no more than 5.05 V, but confirm rail overshoot and voltage margin. The CKG is a 25 V **J-lead metal-frame**; this is a **different package and construction**, not a footprint replacement. | Preserve current **13 positions per board** unless bank redesign is independently approved: 3 TPSM output, two per each of three TPS62825 outputs, 1 LT3045 input, 2 LT3045 output, 1 advisory OPA reservoir. At the existing 40%/35% bias-retention proxies, 15% temperature and 12.5% lifecycle reserves, and improved 10% tolerance, arithmetic is 37.753 µF TPSM output vs 25 minimum; 22.022 µF each doubled TPS62825 and LT3045 output vs 10 minimum; 11.011 µF LT3045 input vs 4.7 minimum. **These are cross-part engineering estimates, not measured Murata effective-C guarantees.** Rebuild 1210 lands and loop placement; validate exact DC-bias/AC-bias curves and load steps. Crucially, ADI LT3045 requires assembled COUT ESR <20 mΩ and ESL **strictly <2 nH**. No exact Murata ESL or routed-network proof was found. The CKG pair's prior 1.0 nH ideal/less-than-1.0 nH interconnect budget cannot be transferred; extract or measure assembled network and Kelvin OUTS before approval. Current project's [CKG bank rationale](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/01_docs/research/2026-09-22-ckg57-bank-candidate.md) explains the requirement. |
| TMUX2821DSGR (40) | **TI TMUX2819DSGR, C53283915** | **80** / **199** | Same TMUX28xx silicon family, DSG 2 × 2 mm 8-pin WSON and ±5.5 V beyond-supply/powered-off protection. However it is **one SPDT channel with an EN pin**, whereas TMUX2821 is two independent SPST channels. [TI family datasheet](https://www.ti.com/lit/ds/symlink/tmux2821.pdf) Table 7-2 confirms EN=0 makes all channels Hi-Z; EN=1, SEL=0 selects SA→D. | Use **two TMUX2819 per existing TMUX2821**: one per audio leg (80 total). Tie each SEL pin low, route each original SELx control to corresponding EN, signal via SA (pin 1) and D (pin 6), connect VDD/GND/EP and bypass each new package; pin 2 N.C. to GND per TI. Handle unused SB pin 5 per TI guidance/board test. Existing footprint is **not pin-compatible** despite same package: TMUX2821 pin 3=SEL2, pin 7=SEL1, pin 1=S1, pin 2=D1, pin 5=S2, pin 6=D2. Redesign all eight cells and placement/capacitors, revalidate positive/negative signal limits, break/make, partial-power behavior, leakage, filter response and THD. Two-channel stock need 80 leaves 119 observed. |

Direct inventory provenance: [JLC C70590](https://jlcpcb.com/parts/componentSearch?searchTxt=C70590), [C2863402](https://jlcpcb.com/parts/componentSearch?searchTxt=C2863402), [C2066893](https://jlcpcb.com/parts/componentSearch?searchTxt=C2066893), [C5219327](https://jlcpcb.com/parts/componentSearch?searchTxt=C5219327), [C329374](https://jlcpcb.com/parts/componentSearch?searchTxt=C329374), [C84494](https://jlcpcb.com/parts/componentSearch?searchTxt=C84494), [C53283915](https://jlcpcb.com/parts/componentSearch?searchTxt=C53283915). Raw JSON is timestamped 2026-09-23 02:50–02:52 UTC and contains exact code/MPN/manufacturer/stock. These observations confirm catalog stock, **not uploader allocation, PCBA eligibility, or assembled-board electrical signoff**. Distributor stock was not counted. The zero-margin supervisor is the immediate purchasing risk; the capacitor ESL and switch topology are the main engineering holds.



## ADC architecture follow-up — research only

The following bounded SOL proof advances AK5578EN for qualification, not source adoption. The current 150-unit catalog reserve remains unchanged. D5 remains binding; no low-stock exception or distributor substitution is accepted by this report.

# Crow ADC architecture decision proof (bounded, 2026-09-23)

This is a design recommendation, not a source edit, PCBA acceptance, firmware implementation or measured performance result. Current source HEAD `b896673d` remains held for ADC sourcing. The new user requirement is that JLCPCB place every non-through-hole component from in-stock inventory; the old secondary reflow exclusion is superseded. The prior 150-unit surplus in `03_src/rules/assembly.yaml` is an engineering policy, not a stated user minimum. It must be explicitly revised, with a defensible order-stage threshold and assembly acceptance, before either AKM part can be admitted. Public catalog stock is not allocation.

## Governing audio envelope

The new carrier `01_docs/BRIEF.md` G2 and A1 bind eight simultaneous channels, 48 kHz, 24-bit payload in eight 32-bit slots; XU316 is onboard and firmware authoring remains out of scope. The retained Crow audio carrier `01_docs/BRIEF.md` T4 and `01_docs/DETAIL_DESIGN.md` cap the active-balanced pod output at **1.2 Vrms differential**. The latter retains 1 uF coupling, 100 kohm bias, 10 kohm input limiting, OPA2320 unity/filter feedback, TMUX2821 isolation and 3.3 V quiet rail. Pod ADR0003 and `2026-09-01-design-math.md` estimate 0.653 Vrms differential at 110 dB SPL nominal, 0.923 Vrms at +3 dB capsule corner and 0.952 Vrms at the modeled resistor corner. The pod capsule is about 80 dB SNR; none of these are measured first-article numbers. Thus the system needs the 1.2 Vrms unclipped interface and materially less than capsule-referred electronic noise, not a minimum 123 dB ADC headline DR. Prior CS5308P 2 Vrms/123 dB A-weighted typical implies 1.42 uVrms ADC noise at its pins and 118.56 dB ADC-only SNR for a 1.2 Vrms signal, assuming unity transfer and comparable conditions.

| Candidate | JLC public stock (02:49–02:53 UTC) | Differential full scale | Typical ADC noise from stated DR/SNR | At retained 1.2 Vrms interface |
|---|---:|---:|---:|---|
| CS5308P-DNR, current | 0 | 2.00 Vrms | ~1.42 uVrms (123 dB) | Reference only; cannot meet in-stock JLC population. |
| AK5578EN C2651626 | 36 | 2.8 Vpp / (2 sqrt 2) = 0.990 Vrms typ; 2.7 Vpp = 0.955 Vrms min | ~0.88 uVrms (121 dB, A weighted) | Direct drive clips 1.2 Vrms. With ~0.70 calibrated analog transfer, 1.2 -> 0.84 Vrms; ~1.12 dB below min full scale. Typical ADC noise referred to connector ~1.26 uVrms and ADC-only SNR ~119.6 dB. The transfer and actual front-end noise must be proven. |
| AK5558VN C2655448 | 32 | Same 0.990 Vrms typ | ~1.76 uVrms (115 dB) | Same attenuation gives ~2.51 uVrms input-referred. Weaker than CS and AK5578; no reason to prefer except package-compatible fallback after a performance decision. |
| 2 x PCM1865DBTR C181312 | 913 | 4.2 Vrms at 0 dB PGA | ~13.3 uVrms (110 dB, A weighted) | Direct drive uses only 28.6% FS: ~99.1 dB ADC-only SNR. +10 dB PGA would approximately map 1.2 Vrms to 90.4% FS, but the 110 dB specification is at **0 dB gain**; one may not carry that noise number across gain settings. Two ADCs complicate continuous cross-device phase. |

Noise calculations are mathematical translations of typical manufacturer specifications, not complete system-noise predictions. Datasheet weighting, gain, source impedance and filters must be aligned for a final comparison. Existing OPA/filter/cable noise, the actual capsule noise, 5 V reference ripple and attenuation resistor noise need a measured or bounded budget. For AK5578, the 3.0–4.2 kohm specified input resistance means the existing buffer/filter cannot simply be moved across; the attenuation must be designed using that range, OPA2320 output load, input common-mode, antialias corner and 10 kohm/1 nF pin network. A nominal 0.70 is a target, not a frozen resistor set. Preserve the connector-level 1.2 Vrms capability and pod gain.

## Serial timing and coherence

At 48,000 frames/s, 8 x 32 = 256 BCLK/frame; BCLK = 12.288 MHz (81.380 ns period), frame = 20.833 us. Existing 24.576 MHz MCLK = 512 fs = 2 BCLK. AK5578 manufacturer datasheet Table 5 explicitly permits CKS3:0 = `0110`, MCLK = 512 fs, normal speed in slave mode. Table 9 mode **33** is TDM256, 24-bit I2S-compatible, slave: TDM1:0=`10`, MSN=`0`, DIF1:0=`01`, LRCK identified by its falling edge, one SDTO1 line carrying channels 1–8 in 32-BICK slots (Figures 47 and 57). Its parallel pin mode can strap these values: no new ADC control firmware is intrinsically needed. DP=0 (PCM), PSN=1/I2C=1 (parallel), LDOE=1 uses internal 1.8 V core regulator from TVDD=3.3 V. AKM says MCLK, BICK and LRCK must be frequency-synchronous but MCLK phase need not match, and the single die's channels share its timing/decimation. This is stronger cross-channel coherence evidence than two independent chips.

The electrical edge proof is **not yet closed**. AKM requires each LRCK transition at least 14 ns from a BICK rising edge; TDM output is specified 5–30 ns after a BICK rising edge in slave TDM256 (Figure 21), so XU316 sampling edge/setup margin and the existing level translator must be checked at worst clock duty/propagation/skew. The retained XU `lib_i2s` plan specifies an offset-one, one-BCLK-wide FSYNC and 32-bit slots, but the exact generated FSYNC polarity and phase relative to BICK at the AK pins must be shown by official XU timing and eventually a waveform. AK mode 33 places a one-bit delay from LRCK falling edge, and the receiver must pack 24 valid bits per 32-bit slot with channel 1–8 identity. A transition coincident with rising BICK would violate AKM's 14 ns minimum. Program/configuration of the already-selected XU316 audio stack remains the existing hardware/software interface contract, not authorized firmware authoring.

PCM1865's TI datasheet §9.3.16.4 fixes 256 BCK/frame and describes 24 valid bits + 8 padding bits in each 32-bit slot. §10.1.4/Figure 59 explicitly shows two ICs on one shared data line, first slots 1–4 and second slots 5–8; two I2C addresses and register setup are required. That proves data multiplexing, **not** invariant analog sample-phase equality. Separate ADC modulators/decimators and TI's illustrated BCK-PLL second chip introduce possible startup phase and group-delay differences; the common LRCK is necessary but insufficient to prove continuous inter-device phase alignment. Independent timing data or measured simultaneous-impulse/skew across repeated reset/power cycles would be needed. This path also consumes an I2C control interface and board-specific ADC initialization path beyond the current hardware-only scope.

## Power and physical backtrack

AK5578 requires AVDD/VREFH 4.75–5.25 V, TVDD 3.0–3.6 V with LDOE=1; datasheet maximum operating currents are 125 mA from AVDD/VREFH and 22 mA TVDD at 48 kHz. The retained 3V3_ADC LT3045 rail powers OPA2320 and cannot become AK AVDD. A separate **quiet regulated 5 V** rail, reference bypass and power/reset sequencing must be engineered and JLC sourced. Simply tying AVDD to the noisy 5V_BUCK or adjusting the OPA rail would discard the inherited noise/headroom contract. Direct 12 V-to-5 V LDO dissipation could approach 0.9 W at 125 mA and needs thermal proof; alternate preregulation may be needed. AKM's PDN reset and stable-clock startup (datasheet §12/Figure 59) replace CS-specific hardware mode/filter/VMID circuitry. Rebuild the AK 64-pin 9x9 mm EP footprint and pin contracts, filter/bias/attenuation network, decoupling, clock routing, schematics, BOM, placement and DRC. Recheck every added SMD's JLC stock and placement capability. None is a drop-in or a live-source correction.

AK5558 is pin/register compatible but shares the same 5 V/attenuation/footprint backtrack and has 6 dB worse typical DR. PCM1865 uses 3.3 V but needs two 30-pin TSSOP ADC cells, signal/gain and filter redesign, I2C straps/control and phase proof. Its high catalog stock does not compensate for those functional uncertainties.

## Decision

**Advance AK5578EN as the engineering choice for a new ADC cell**, contingent on an explicit revision of the project's 150-surplus rule, order-time JLC stock/BOM-matcher and placement acceptance, bounded full-path noise and clipping proof, quiet 5 V regulator/thermal proof, and measured/configured XU316-to-AK frame timing. The user requires *in stock* and JLC population; the public count 36 is in stock and covers five boards in arithmetic, but does not meet the current local 155-unit policy. A reasonable proposed policy would be minimum five-board BOM quantity plus documented JLC setup/attrition reserve and order-time inventory allocation, rather than a fixed 150 surplus; choose the actual reserve only with vendor order information. Do not silently revise it. Do not advance AK5558 or two PCM1865 merely because of stock count. If AK5578 cannot clear the power, attenuation or JLC/order gates, there is currently no proven in-stock, JLC-populated ADC replacement preserving this Crow architecture; keep release held and seek another part or replenish/obtain CS5308 stock.

Manufacturer primary PDFs retained in `/tmp/crow-jlc-adc-20260923/raw`: `ak5578.pdf` (AKM 015016736-E-03, pp. 8–9, 20, 31–36, 41–43, 55), `ak5558.pdf` (AKM), `pcm1865.pdf` (TI SLAS831D, pp. 13, 58–59, 73). CS5308 source: `projects/crow-usb-carrier-v1/02_parts/CS5308P-DNR/CS5308P_Datasheet_DS1314F2.pdf`. JLC raw exact-part response JSON and query times: `/tmp/crow-jlc-adc-20260923/raw/{C2651626,C2655448,C181312,C9900305019}.json`. Project primary requirement sources above are relative to `/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/`.


## D7 superseding stock-policy decision

The user explicitly retained 150 extra units per part beyond the five-board build. The preceding AK5578EN architecture recommendation was conditional on revising that policy; that condition is now rejected. Preserve AK feasibility work as research only. AK5578EN, AK5558VN and the two-per-channel TMUX2819 proposal fail the confirmed stock criterion at the retained observations. Continue stocked alternatives; do not reduce the buffer.

### JLC attrition policy evidence (proposal below not adopted)

# JLC PCBA reserve / attrition evidence — 2026-09-23

Accessed official JLCPCB pages at **2026-09-23T03:19:22Z**.  This is a
read-only evidence review; it does not alter the project's sourcing policy or
authorize an order.

## What JLCPCB publicly says

1. JLC's current [Global Sourcing Parts Service help page](https://jlcpcb.com/help/article/how-to-use-jlcpcb-global-sourcing-parts-service)
   says customers must consider the *minimum assembly quantity* and *attrition
   quantity* during PCBA assembly.  It does **not** publish a numeric formula,
   table, package class, value class, or per-board example for either number.
   It also says global-sourced parts cannot be used for assembly until they
   arrive at JLC's warehouse, and a reviewed part may be cancelled if it does
   not support assembly.
2. The official [parts page](https://jlcpcb.com/parts) presents real-time
   inventory and tells the customer to upload/match the BOM, review stock, and
   confirm the PCBA order.  It separately advertises the Private Component
   Library as a way to pre-order/reserve critical parts.  Therefore the public
   catalog quantity is an observation, not proof that a given order's
   components are allocated.
3. The official [PCBA FAQ](https://jlcpcb.com/help/article/common-pcba-after-sales-issues-and-faq)
   says production normally assembles only parts explicitly selected by the
   customer, and requires review of the Selected Parts List before order
   submission.  It also says a BOM C-code is prioritized for matching.  This
   makes the resolved order selection, rather than an off-line stock count, the
   operative placement evidence.
4. JLC's official [MOQ/attrition Q&A page](https://jlcpcb.com/help/answers/detail/92-What%20are%20the%20MOQ%20and%20attrition%3F)
   currently exposes the question “5 PCBs … 6 pcs” but supplies no visible
   vendor answer or general numerical rule.  It cannot support a 150-part
   reserve, a one-part reserve, or a percentage rule.

## Interpretation limits

The official material establishes that attrition and a minimum assembly
quantity exist, but not their numeric values.  It supplies no defensible basis
to calculate a fixed reserve from:

* five boards versus any other order size;
* package type, pin count, reel/cut-tape status, or component value;
* cheap R/C lines versus expensive ICs; or
* aggregate usage count of the same MPN on a board.

Thus no public evidence supports changing `+150` to another fixed number,
including a superficially modest percentage.  The old Q&A's 5-to-6 example is
only the user's question, not a JLC policy statement.

## Project history / present meaning

`03_src/rules/assembly.yaml:44-45` sets `build_quantity: 5` and
`public_stock_surplus: 150`, described as an “absolute catalog buffer per
aggregated LCSC line.”  Git history shows that exact field and value were
introduced in the project-creation commit
`3ec8c72537222a95ef2706e5cd36bf5822279fe6` (2026-09-21), with no rationale or
vendor citation in the field or subsequent history.  It is an internal
engineering screening rule, not an identified JLC requirement.

The project itself records this limitation:

* `01_docs/sourcing/jlc-population-review-2026-09-23.md:243` calls the prior
  150-unit surplus an engineering policy rather than a user minimum and says
  public catalog stock is not allocation.
* The same document at `:274` proposes “five-board BOM quantity plus documented
  JLC setup/attrition reserve and order-time inventory allocation,” with the
  actual reserve chosen only from vendor order information.

## Concrete policy proposal

Replace the flat catalog-surplus test only through a documented source-policy
change with these two separate gates:

| Gate | Required proof | Quantity rule |
|---|---|---|
| **Pre-order source screen** | Dated exact-C-code public catalog observation, exact MPN/package match, and current BOM quantity | `catalog_stock >= boards × placements_per_board` for every JLC-populated non-THT MPN.  This answers “in stock” only at observation time. |
| **Order-stage assembly gate** | Saved JLC quote/uploader Selected Parts List and its displayed minimum-assembly/attrition requirement for each resolved line; exact BOM/CPL match | `JLC-resolved/reserved quantity >= JLC-displayed required quantity` for each line.  If the order UI does not expose a sufficient number, obtain a vendor order-screen/support response or keep the gate HOLD. |

For **expensive or scarce ICs**, use the same source-screen arithmetic but
require order-stage allocation/Private Library reservation before calling the
line ready; do not demand an arbitrary 150 public units.  For **cheap R/Cs**,
the same two gates apply: their high public quantity does not replace the
uploader's actual attrition/minimum number.  If the project wants a
future-build continuity reserve, make it a distinct, per-MPN procurement
forecast (e.g., planned additional board count), held/reserved at JLC; do not
fold it into a universal public-catalog availability threshold.

This proposal works for any package/count because it relies on JLC's resolved
per-line requirement rather than inventing a QFN/SOIC/0402 or expensive/cheap
formula.  It preserves the D5 requirement that every non-through-hole part be
in stock and JLC-populated, while not misrepresenting public inventory as
allocation or assembly acceptance.

## Evidence boundary

No page reviewed proves that the currently selected parts can be assembled,
that a code is allocated to this project, that JLC will accept a given package,
or what attrition quantity the eventual quote will show.  Those are
order-stage, exact-BOM/CPL, and resolved-uploader facts.


### AK front-end follow-up (not selected under D7)

# AK5578EN front-end feasibility proof (bounded, 2026-09-23)

**Result:** The retained OPA2320/TMUX/filter architecture can plausibly support AK5578EN with a small *signal-path* change, but it cannot use the old 1.65 V bias or 3.3 V OPA supply. Do not adopt or release this as a completed schematic. The actual network below provides a concrete design starting point and testable corner limits. All eight channels, pod connectors, 1.2 Vrms differential connector ceiling, and XU316 hardware boundary remain in scope. JLC stock/placement and the current 150-unit surplus rule remain open.

## Primary facts and existing nodes

The exact retained `crow_retained_analog.tsx` path per leg is pod 100 Ω source → 1 µF coupling film → BIAS node, 100 kΩ from BIAS to one of two 1.65 V external-VMID banks → 10 kΩ R_IN → OPA2320 noninverting input. OPA output closes feedback through the R_OUT 10 Ω / FILTER node and R_X 300 Ω / C_FB 680 pF loop; two 15 nF shunts at FILTER are before the TMUX2821, then an ADC pin has 10 kΩ to ground and 1 nF to ground. OPA runs on `3V3_ADC`; TMUX runs on `5V_LDO_HOLD`. This is a low-impedance unity/filter buffer, not just a passive cable filter. The current 100 kΩ bias and 10 kΩ R_IN do **not** attenuate an essentially open OPA input.

AKM AK5578EN 015016736-E-03 pp. 8–9 and 68–69 says 3.0–4.2 kΩ input resistance, 2.7–2.9 Vpp differential full scale at nominal 5 V, AVDD/VREFH 4.75–5.25 V, and **new H-datecode products need ADC-pin DC bias 0.502–0.522 × AVDD** for optimal S/(N+D). AKM explicitly says the old 2.5 V bias costs about 6 dB S/(N+D) on those products. Existing 1.65 V is far outside this interval. The ADC's VREFH/AVDD ratio also scales input full scale: conservatively using the 2.7 Vpp minimum at 5 V and 4.75/5 rail ratio yields `2.7×0.95/(2√2)=0.9069 Vrms` minimum full scale. AKM's Figure 76 drives each ADC input through only 10 Ω after a low-impedance buffer; using the AK input resistance itself as an attenuator would make gain and DC bias poorly controlled.

TI OPA2320 SBOS513F §6.5–6.7 rates supply 1.8–5.5 V, input common mode V−−0.1 to V++0.1, 45 mV maximum output swing from either rail at 2 kΩ over −40..125°C, 1.7 mA/channel maximum quiescent, and 8.5 nV/√Hz typical voltage noise at 1 kHz. TI TMUX2821 SCDS488 gives ≤0.225 Ω RON to 85°C, ≤0.3 Ω to 125°C and ≤0.09 Ω RON flatness to 125°C. The 5 V-powered OPA is an allowed component use, but different from the admitted shared-3.3 V source.

## Proposed analog change and calculations

1. Retain each OPA2320, R_IN=10 kΩ, R_OUT=10 Ω, R_X/C_FB/filter, TMUX and ADC-pin protection/isolation. Add **18 kΩ, 1% from each OPA noninverting input to the local new VCM bank**. This makes a divider before the buffer. Supply all eight OPAs from the new quiet 5 V rail. Move the two external bias banks from 3.3 V to the same 5 V rail and set `VCM ≈ 0.512×AVDD`, for example top 1.00 kΩ/bottom 1.05 kΩ in 0.1% tolerance; exact stocked MPN and loading remain to be chosen. Keep each channel's pod input AC-coupled, so its DC bias settles at VCM. Retain separate bank decoupling; the VCM branch carries only op-amp input bias at DC rather than the 3–4.2 kΩ ADC load. AKM VREFH1–4 need their own 20 Ω/0.1 µF/100 µF filtering and VREFL-to-AVSS per datasheet; do not conflate these with signal VCM.
2. Assuming each pod leg's retained 100 Ω source and a low-impedance VCM AC return, the AC source load is `100k || (10k+18k) = 21.875 kΩ`. Divider transfer to the OPA positive input is `18/(10+18) × 21875/(21875+100) = 0.63993`. Independent ±1% corners of R_IN, 18 kΩ and 100 kΩ give approximately 0.6353–0.6445. Max connector input 1.2 Vrms becomes **0.762–0.773 Vrms differential** before the ADC-pin load. Against the rail-scaled minimum ADC full scale 0.9069 Vrms, the maximum gain corner leaves **1.38 dB nominal arithmetic clipping margin**. The 110 dB SPL pod estimate 0.653 Vrms maps to about 0.418 Vrms; its modeled 0.952 Vrms corner maps to about 0.609 Vrms. No per-pod gain reduction is needed.
3. At the ADC pins, treat AK's 3.0–4.2 kΩ as an adverse **per-leg load to ground** until its internal impedance topology is validated. In parallel with the retained 10 kΩ pulldown, this is 2.308–2.958 kΩ. The 10 Ω R_OUT plus worst 0.3 Ω TMUX RON drops only ~0.35–0.45% if no feedback compensation; the actual R_X/C_FB loop senses FILTER ahead of TMUX and may compensate part of R_OUT loss at audio frequencies. Because the ADC resistance may mean differential input resistance rather than two independent ground returns, that bound is deliberately pessimistic and must be checked against an AKM input model/bench impedance. It cannot produce the >30% gain spread a series attenuator at the ADC pins would. With 5 V VCM=2.56 V, 0.45% DC loading shifts ADC-pin VCM to ~2.549 V, or 0.510×AVDD, inside AKM's 0.502–0.522 target if the 5 V rail/reference track. This must be checked with actual 4.75/5.25 V rail corners, VREFH drops, switch state and input bias currents.
4. At 1.2 Vrms differential, each balanced OPA leg swings `0.6445×1.2×√2/2 = 0.547 Vpeak`. Around VCM≈2.56 V the output range is 2.013–3.107 V, well inside a 4.75 V minimum OPA supply, leaving >1.6 V high-side swing margin. At 20 kHz, the two 15 nF shunts per leg draw about `2π×20k×30nF×0.547≈2.06 mApeak` reactive current; a grounded 3 kΩ ADC resistance would add ~0.85 mA DC plus ~0.18 mA signal current per leg; the retained 10 kΩ pulldown adds ~0.26 mA DC. OPA's 2 kΩ rated output-swing load is a useful screen, but the capacitive filter/feedback loop and full-range THD remain unproven. TMUX RON and flatness are small relative to 2.3–3 kΩ, but vendor THD numbers are typical, not a guarantee for this filter/load.
5. The extra 18 kΩ lowers the pod input resistance and moves the 1 µF coupling high-pass from roughly 1.6 Hz to `1/(2π×1µF×(21.875k+100))=7.24 Hz`, about **−0.53 dB at 20 Hz** per differential signal. A **2.2 µF film** per leg would give 3.29 Hz and −0.116 dB at 20 Hz; 4.7 µF gives 1.54 Hz and −0.026 dB. Thus retaining the old 1 µF capacitor exactly changes low-frequency response. Choose the required 20 Hz tolerance and an exact JLC-compatible/through-hole assembly path before source edits. The existing 10 Ω with 30 nF shunt has a simple RC pole near 530 kHz; R_X/C_FB ~780 kHz and 1 nF pin shunt are not simple isolated poles because of closed-loop feedback and AK input loading. Recompute/simulate the entire loop, check peaking and high-frequency alias attenuation, then measure gain/phase/THD across 20 Hz–20 kHz.
6. A white-noise scale check at 300 K over an ideal 20 kHz flat band: `10k||18k=6.43kΩ` at each OPA input contributes ~10.3 nV/√Hz per leg or **3.23 µVrms differential referred to the pod connector** after 0.64 gain. OPA2320's typical 8.5 nV/√Hz at 1 kHz adds ~2.66 µVrms connector-referred for two uncorrelated legs; AK5578's typical A-weighted `0.990 Vrms/10^(121/20)` adds ~1.38 µVrms connector-referred. Naive RSS is ~4.4 µVrms / 108.7 dB relative to the 1.2 Vrms ceiling. These use incompatible spectral weighting and omit 1/f noise, source resistors, reference/buck noise, capacitor behavior and actual analog gain response; they demonstrate that the 18 kΩ does not obviously squander the ~80 dB capsule SNR, **not** that the finished system meets a guaranteed noise specification. An unfiltered VCM rail, channel-to-channel reference coupling, and added divider resistor excess noise could dominate. Full-path measurements remain mandatory.

## Quiet 5 V rail and sequencing

AK AVDD/VREFH max current is 125 mA at 48 kHz; sixteen OPA channels add up to 27.2 mA quiescent maximum, two 1k/1.05k VCM dividers draw ~4.88 mA, and an adverse ADC input DC-to-ground interpretation plus the existing 10 kΩ pulldowns can require roughly another 18 mA of OPA output current across sixteen legs. Plan **at least ~0.18 A continuous** before regulator ground current and design margin; TVDD separately draws up to 22 mA at 3.3 V with LDOE=1. Existing fixed TPSM63603V5 5 V buck is 4.95–5.05 V at source and the Schottky/22 Ω `5V_LDO_HOLD` path is lower still, so neither provides dropout headroom for a regulated quiet 5 V LT3045 output. Retargeting that fixed buck would overvoltage the current 5 V-domain hardware and is not a local change.

Minimum credible regulated topology: take `12V_PROTECTED` into a **separate ~6.0–6.4 V switching preregulator**, then a low-noise 5.0 V LDO with ≥0.2 A rated continuous load and the manufacturer's required input/output, reference and thermal layout. Feed AK AVDD/VREFH and OPA V+ from its quiet 5 V output; TVDD may use the retained 3.3 V quiet/digital boundary only after level and sequencing review. At prereg maximum 6.4 V and 0.18–0.20 A, pass-device loss is ~0.25–0.28 W plus LDO ground-current loss, far below a direct 12 V LDO. ADI LT3045 Rev D Table 3 gives ~34–36°C/W only on its specific four-layer 1 oz/2 oz thermal test boards; the Crow native footprint, copper and filled-via process must be requalified. A single direct 13.2-to-5 V LDO at 0.19 A loses ~1.56 W **before** ground current; 35°C/W would raise junction ~55°C above a 70°C board ambient, leaving essentially no margin to the E-grade 125°C limit, so this is not an admitted minimum. No preregulator MPN or JLC stock is selected here.

The new rail must participate in existing PWR_EN, AUDIO_EN, ADC_RESET_N, TMUX power-off protection and held-energy discharge: neither an energized OPA output into an unpowered AK input nor an energized AK pin into an unpowered OPA/TMUX is acceptable. AKM limits analog input pin current to 10 mA and pin voltage to AVSS−0.3..AVDD+0.3 V. Prove ramp/down state ordering and resistor-limited injection across all independently powered states. The existing 10 kΩ ADC-pin pulldown helps discharge but is not a substitute for this analysis.

**Decision:** One OPA-input shunt per leg plus two VCM changes, 2.2 µF coupling if the 20 Hz response is preserved, and a separate quiet 5 V supply are a feasible engineering backtrack. The change is larger than a passive ADC swap and requires new control, power, filter, thermal, layout and measurement evidence. AK's low input resistance is manageable behind the OPA; its DC bias requirement is the hard constraint. There is no basis yet for release/admission or a claim that JLC stock and the local reserve policy are satisfied.

Local primary PDFs: `/tmp/crow-jlc-adc-20260923/raw/ak5578.pdf`, `projects/crow-usb-carrier-v1/02_parts/OPA2320AID/OPA2320_SBOS513F.pdf`, `projects/crow-usb-carrier-v1/02_parts/TMUX2821DSGR/TMUX28xx_SCDS488.pdf`, `projects/crow-usb-carrier-v1/02_parts/LT3045EDD-PBF/LT3045_RevD.pdf`. Project paths are under `/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/`.


## D7 buffer-shortage alternatives — research only

# D7 exact JLC catalog alternatives — 2026-09-23 03:24–03:26 UTC

Dated design-stage observations only. Five-board quantities retain **150 extra catalog units per aggregate code**. Direct JLC results are from serialized POST requests to `https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`. Search terms, UTC times, response SHA256 and unmodified raw JSON are retained under `/tmp/crow-active-sourcing-20260922/alternates/` (`exact_search.jsonl`, `broad_search.jsonl`, `variant_search.jsonl`). Search results are candidate identity/stock evidence, never PCBA uploader allocation or a part substitution. No selected source or BOM was changed.

| Selected code and MPN | Five-board qty +150 | Exact-MPN JLC result | Candidate with direct JLC stock | Disposition |
|---|---:|---|---|---|
| C17566269 ASFL1-24.576MHZ-EC-T | 5+150=155 | Sole exact code, 86 | C1987425 ASFL1-24.576MHZ-EK-T, 84: same Abracon ASFL1 series and tighter ±30ppm, but also below155. **C2901534 SX5M24.576M20F30TNN, 1,071**, or C252361 SJK 7N24576G33YC, 268: other manufacturers, SMD5032 four-pad oscillators. | SX5M is a real catalog candidate, not an approved replacement. Its manufacturer's signed datasheet shows 24.576MHz, 1.62–3.63V, ±30ppm across -40 to85°C, 15pF CMOS, OE/GND/OUT/VDD on pads1–4. Compare exact pad geometry, clock jitter/edge/load and source qualification before adoption. Retaining the selected Abracon part with exact distributor sourcing is less circuit change. |
| C2066942 TPS389030DSER | 15+150=165 | Sole exact code, 56 (earlier screen 58; stock moved) | **C1509297 TPS389001DSER, 591**, same TPS3890 WSON-6 family, adjustable sense threshold. Selected fixed 3.0V version trips at 2.89V falling. | Already selected for U_AUDIO/U_PWR; sharing it would bring total to 5 devices per board, 25+150=175, still below observed 591. Requires external sense divider, tolerance/rail/reset timing review, new resistor BOM/placement and sourcing. C702227 TPS389033DSER 97 and C2066922 030QDSERQ1 10 fail165; 033 has wrong nominal threshold. |
| C2072356 TPS6282518DMQR | 5+150=155 | Sole exact code, 51; DMQT ordering variant C2072289=0 | **C2650334 TPS62825DMQR, 5,819**, same TPS62825 VSON-6 adjustable-output family. | Already selected for U_CORE. Reusing for U_1V8 would take aggregate to 2 devices/board, 10+150=160, still below 5,819. Current fixed 1.8V FB-to-output tie must become an external divider for 0.6V reference; TI specifies R2<=100kΩ. Requalify feedback accuracy/noise, compensation, power sequencing and layout. |
| C3189971 TPS6282533DMQR | 5+150=155 | Sole exact code, 44 | **C2650334 TPS62825DMQR, 5,819** as above. | Reusing for both U_1V8 and U_3V3X plus existing U_CORE gives 3 devices/board, 15+150=165, still below 5,819. The 3.3V fixed FB tie must become a different external divider; 5V-input dropout, accuracy, noise, thermal/inductor and sequencing need review. The adjustable candidate is a circuit redesign, not a drop-in BOM change. |
| C6362698 XU316-1024-TQ128-C24 | 5+150=155 | Exact C6362698=46; extra exact-code C9900032908=0 (catalog calls it LQFP) | C6938291 XU316-1024-TQ128-I24=0. | No stocked same-package XMOS alternative found. XMOS's current TQ128 ordering table lists only C24 and I24 at 600MHz/2400MIPS; faster C32/I32 are in QF60 or FB265, not the current TQ128 footprint. Keep exact part and pursue exact distributor sourcing or obtain manufacturer/JLC procurement evidence. No firmware- or layout-compatible replacement is established. |

Additional zero-stock fixed supervisor: **C2066910 TPS389018DSER**, 10+150=160, sole exact code=0; C2066893 TPS389018QDSERQ1=10 also fails160. The same C1509297 adjustable TPS389001DSER=591 can nominally set a 1.8V rail sense threshold with an external divider, but the selected fixed 1.8V variant trips at 1.73V falling. If both fixed supervisor MPNs moved to adjustable, the existing 2 plus 2 plus 3 devices/board total 7, requiring 35+150=185; observed 591 clears that aggregate. The divider, threshold tolerance, delay, rail sequencing and exact source changes remain design work.

Primary specification support: [Abracon ASFL1 ordering and electrical tables](https://abracon.com/Oscillators/ASFL1.pdf), [SCTF SX5M specification](https://static.chipdip.ru/lib/727/DOC043727753.pdf), [SJK 7N specification](https://datasheet.lcsc.com/datasheet/pdf/404d9ade0ee48598cc94231394d91d47.pdf?productCode=C252361), [TI TPS3890 datasheet](https://www.ti.com/lit/ds/symlink/tps3890.pdf), [TI TPS62825 datasheet](https://www.ti.com/lit/ds/symlink/tps62825.pdf), [XMOS TQ128 ordering table](https://www.xmos.com/documentation/XM-014532-PC/html/rst/XU316-1024-TQ128.html), and [XMOS part-number list](https://www.xmos.com/file/xmos-part-numbers-and-part-markings/?version=latest). The TI buck datasheet says adjustable output uses an external divider with `R1=R2*(VOUT/0.6V-1)` and R2 no higher than 100kΩ. The TI supervisor datasheet gives falling thresholds 1.73V (018), 2.89V (030), and 1.15V (001 adjustable base).

The least-disruptive next step is retain exact selected MPNs and apply the established exact-distributor public-stock path where it clears 150 extra units. If an all-JLC-source requirement supersedes that path, the adjustable TI parts and SCTF oscillator are engineering candidates needing new dossiers and full electrical/layout/footprint/sourcing requalification; the XU316 remains unsolved in JLC catalog stock.


## Rejected two-SPDT switch proposal under D7

# Crow TMUX shortage: bounded source proof and D5 disposition

Research cut: 2026-09-23 UTC. **Do not adopt TMUX2819DSGR now.**
User-confirmed policy keeps **150 extra of every part**. Two TMUX2819DSGRs
per original TMUX2821DSGR require 16 per board, **80 for five boards and 230
including the buffer**. Direct JLC C53283915 recorded 199 in stock at
2026-09-23 02:51:42 UTC, 31 short of that threshold; its `canPresaleNumber`
was 156, also below 230. These are catalog observations, not allocation.
The original TMUX2821DSGR/C53283916 had 16 in the project JLC census for
40 needed, and a separate jlcsearch observation showed 4. Neither clears
five-board demand. No exact JLC-stocked, requirement-preserving dual-SPST
replacement with >=190 observed units was proven in this bounded search.
The candidate remains a *topology proof*, not a source selection.

## Current circuit and exact single-package substitution

Current TSX `crow_retained_analog.tsx` instantiates U_ISO1..8, each a
TMUX2821DSGR with two independent SPST legs. P uses pin1 S1 from
FILTERnP and pin2 D1 to ADCnP, controlled by pin7 SEL1=`AUDIO_EN`.
N uses pin5 S2 from FILTERnN and pin6 D2 to ADCnN, controlled by pin3
SEL2=`AUDIO_EN`. Pins4/9 ground; pin8 is **5V_LDO_HOLD**. The amplifiers
and ADC use 3V3_ADC; the present switch does not. Each ADC output side
has its own 10k pulldown and 1nF shunt; one 100nF C_ISOn bypasses each
original package. The inherited pod ceiling is 1.2 Vrms *differential*;
this is not a per-leg 1.2 Vrms specification.

[TI SCDS488 primary datasheet](https://www.ti.com/lit/ds/symlink/tmux2821.pdf)
pp3, 6, 19-20 gives these top-view functions and truth tables:

| Device | Pin 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | EP9 |
|---|---|---|---|---|---|---|---|---|---|
| TMUX2821 | S1 | D1 | SEL2 | GND | S2 | D2 | SEL1 | VDD | GND |
| TMUX2819 | SA | N.C. | EN | GND | SB | D | SEL | VDD | GND |

2821: VDD=0 isolates both channels; with VDD valid each channel is OFF
at its SELx=0, ON at SELx=1. 2819: VDD=0 isolates; EN=0 isolates both
throws; EN=1/SEL=0 connects SA-D; EN=1/SEL=1 connects SB-D. Thus one
2819 for each **single** P or N leg reproduces the intended logic if
SEL7 is hard tied low and EN3 receives `AUDIO_EN`. One package per leg:
SA1=FILTERnP or FILTERnN, D6=ADCnP or ADCnN, VDD8=5V_LDO_HOLD,
GND4/EP9=GND. TI specifically says pin2 N.C. should connect to GND
for a known state. SB5 is unused and should be a native no-connect; no
signal should be routed through it. Do not join P and N on one 2819:
its SA/SB throws share one D, so that would short or select audio legs.
Existing 2821 and 2819 share the DSG 2x2-mm package outline but **not pad
functions**; the eight existing footprints/net assignments cannot be
reused unchanged. There would be 16 packages, 16 local 100nF bypasses
(+8 versus the current source), and 16 SEL-to-ground ties. The original
16 total SEL input pins become 16 total EN inputs, so AUDIO_EN input
count is unchanged. Pin5 SB N.C. and pin2 grounded N.C. must be represented
explicitly in source/native NC handling.

## Electrical screen and owed proof

The TI family sheet applies to both chips: recommended VDD 1.8..5.5V,
signal terminals -5.5..+5.5V, logic 0..5.5V; VIL <=0.6V and VIH
>=1.1V at 3.3V supply. The current held 5V logic pull-up can drive EN
within the 5.5V limit. TI specifies fail-safe logic up to 5.5V even if
VDD=0 and powered-off switch-path isolation to +/-5.5V at VDD=0.
These bounds accommodate a balanced 1.2Vrms differential sine (1.697V
peak differential, about +/-0.849V peak per opposite leg), including
the present 3.3V-biased AFE output, and ordinary near-rail excursion.
They do **not** establish survival of a >5.5V switch-terminal fault,
or switch behavior while held VDD traverses 0..1.8V. Retain the current
first-article partial-power and fault-injection tests; review actual
pod/coupling/protection fault transients before release.

At VDD=3.3V, TI specifies RON <=0.225ohm through +85C and <=0.3ohm
through +125C under its -5..+5V/100mA test. Each signal still crosses
one switch, so no series switch is added. Against the source's 10k ADC
pulldown, 0.3ohm is a <=30ppm ideal resistive gain term, but ADC dynamic
loading/filter behavior is not captured by that estimate. The 2821
within-package channel-match number cannot be carried to P/N channels
in separate 2819 packages. TI's +/-0.1uA off leakage to +85C gives up
to 1mV per 10k pulldown per leg and 2mV differential worst opposed;
at +125C the +/-1uA off-leakage bound gives 10mV per leg / 20mV
differential. The VDD=0 powered-off leakage reaches +/-2uA at +125C,
which gives 20mV per leg against 10k if that test condition applies.
These are conservative resistor-only bounds, not measured ADC offsets.

TI's THD+N is -105dB at 600ohm, 0.5Vpp, 20Hz..20kHz over -40..125C;
this test amplitude/load is not Crow's 1.2Vrms differential operating
point. Off capacitance 70pF, charge injection 5pC, and isolation/crosstalk
figures are typical. Recheck analog-filter loading, audio THD+N and
P/N gain/phase on a first article. Revalidate held-rail start/brownout,
`AUDIO_EN` timing, ADC backdrive isolation, and break/make transitions
with both packages at every one of eight channels. No claim of measured
performance or layout clearance follows from the family match.

## Sourcing comparator and next source action

The bounded catalog search found no verified stocked dual-SPST preserving
independent SEL gating, negative/beyond-supply signal range, VDD=0
isolation, low Ron/audio behavior, and the confirmed buffer. A standard
4066 or ordinary single-supply dual switch cannot be accepted solely
because it has two SPST channels: negative/beyond-supply and VDD=0
backfeed behavior require primary evidence. TI TMUX4827 is a dual SPDT
with a common SEL and no active EN, so it cannot reproduce both OFF
states under `AUDIO_EN` without an additional disconnect; no JLC stock
qualification was established. [TI TMUX4827 primary datasheet](https://www.ti.com/lit/ds/symlink/tmux4827.pdf).

Requery direct JLC stock and PCBA availability for exact dual-SPST and
TMUX2819 codes. A candidate can advance only when exact catalog stock
is >= five-board need +150 (>=190 for one dual package per board, >=230
for two single packages per board), and exact primary evidence closes
negative signal, power-off and control truth table. If 2819 reaches
>=230, implement the 16-package mapping above in TSX, an exact
TMUX2819 dossier/native pin/land, 16 local bypasses, placement/adjacency
and assembly rules, then regenerate and independently regrade netlist,
filter/loading and fault/timing behavior. Do not waive the buffer,
change the rail, or count distributor stock as JLC population.

Evidence: retained project `02_parts/TMUX2821DSGR/TMUX28xx_SCDS488.pdf`
(SHA256 493e5c0d4eb5ca55dea82dbcce59b1be9c353577e256c161821662c38bb9ac55);
`/tmp/crow-jlc-adc-20260923/raw/C53283915.json`; source
`projects/crow-usb-carrier-v1/03_tscircuit/src/crow_retained_analog.tsx`
lines 127-135; project dated `01_docs/sourcing/jlc-population-review-2026-09-23.md`.


## Stocked capacitor-bank feasibility — source candidate under preparation

# C84494 Murata replacement for Crow CKG57K bank — bounded primary-evidence screen

Date: 2026-09-23 UTC. Scope: replace the 13-per-board TDK CKG57KX7R1E476M335JH/C2171626 bank, observed JLC stock zero, with **Murata GRM32ER71A476KE15L/C84494**. Serialized direct JLC check retained at `/tmp/crow-jlc-adc-20260923/raw/C84494.json` returned exact Murata MPN and stock **56,478**, enough for the proposed 50 units/5 boards. No source/BOM/board edit was made.

## Result

A **10-part-per-board engineering candidate** follows from exact Murata model data and avoids a TPS62825 capacitor combination outside TI's validated table. It is **not yet an electrical/PCBA signoff**: Murata's characteristic curves and SPICE coefficients are *typical simulation data*, not a production worst-case capacitance, ESR, or ESL guarantee. In particular, ADI's **assembled** LT3045 COUT ESL <2 nH needs extracted or measured loop proof. No defensible paper-only claim can close that physical requirement before board placement.

| Bank | Present CKG references | Proposed C84494 refs | Worst exact-model C per unit at -55 °C / max rail, µF | Screen after ×0.90 tolerance ×0.875 lifecycle, µF | Requirement / disposition |
|---|---|---|---:|---:|---|
| TPSM63603 N5V_BUCK output | C_OUT1/2/3 | same 3 × Murata | 14.7 at 5.05 V | **34.73** | 25 effective min: model screen passes 1.39×. TI permits more output C; 141 µF nominal is beyond its two-47-µF example, so startup/load-step check remains. |
| TPS62825 N3V3X output | C_U_3V3X_OUT_1/2 | **OUT_1 only**, remove OUT_2 | 16.9 at 3.38 V | **13.31** | 10 effective min: model screen passes 1.33×; **47 µF nominal with 0.47 µH is explicitly marked in TI Table 8-3**, while 100 µF nominal is blank for TPS62825. |
| TPS62825 N1V8 output | C_U_1V8_OUT_1/2 | **OUT_1 only**, remove OUT_2 | 18.4 at 1.818 V | **14.49** | 10 min, passes 1.45×; same TI nominal LC row. |
| TPS62825 N0V9/Core output | C_U_CORE_OUT_1/2 | **OUT_1 only**, remove OUT_2 | 18.7 at 0.92 V | **14.73** | 10 min, passes 1.47×; same TI nominal LC row. |
| LT3045 input | C_LDO_IN | same 1 × Murata | 14.7 at 5.05 V | **11.58** | 4.7 min, passes 2.46×; input ripple/loop remains physical check. |
| LT3045 N3V3_ADC output | C_LDO_OUT_1/2 | same symmetric 2 × Murata | 16.9 at 3.38 V | **26.62** | 10 min, passes 2.66× by model; ESR/ESL below. Kelvin OUTS and SET capacitor ground. |
| Downstream OPA reservoir | C_OPA_BULK | same 1 × Murata | 16.9 at 3.38 V | **13.31** | Advisory only, no invented regulator minimum. Analog load-step check. |

Total: **10 C84494 per board; 50 per five boards**. Source mutation would need exact `part.yaml`, integration/exact-parts population, schematic/PCB footprint, power-tree rows, E-CAP gate, TSX source, and BOM alignment. All present TDK J-lead lands need replacement with exact Murata 1210 geometry and re-placement; the CKG footprint is **not compatible**.

## Primary evidence and arithmetic

- [Murata exact product page](https://www.murata.com/en-eu/products/productdetail?partno=GRM32ER71A476KE15L) and [Murata reference sheet](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM32ER71A476KE15-04CA.pdf) establish GRM32ER71A476KE15**L** as 47 µF ±10%, 10 Vdc, X7R, -55…125 °C, 1210/3225M; the trailing L is 180-mm reel packaging. Project's exact [local dossier](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/02_parts/GRM32ER71A476KE15L/part.yaml) retains the June 2026 sheet. All five relevant bank rail maxima are ≤5.05 V in `03_src/rules/power_tree.yaml`; output overshoot still must remain within the 10 V rating. Reference sheet states 47 µF at 120 Hz, 0.5 Vrms, 25 °C and the 10 V rating with AC peak included; it **does not guarantee DC-biased effective C, ESR or ESL**.
- Murata's live [SimSurfing exact-part viewer](https://ds.murata.com/simsurfing/mlcc.html?oripartnumbers=%5B%22GRM32ER71A476KE15L%22%5D&partnumbers=%5B%22GRM32ER71A476KE15%22%5D) served numerical `C-DC bias`, `C-AC Voltage`, temperature, impedance, resistance and reactance data for base MPN `GRM32ER71A476KE15`. Exact JSON responses are retained in `/tmp/crow-capbank-evidence-20260923/` (DC-bias SHA-256 `cd00cda39b1ad340ce1f85070c9758677b99361812dc6a33dbef68bb80c64abd`, AC-voltage SHA-256 `7afa43163efee7ac879db8b2f80ee15eeaf77a69af5d827f9faab233ad483599`). The DC curve is labeled **25 °C / 0.5 Vrms**; AC curve **0 V DC / 25 °C**, so directly multiplying their percentages would mix reference conditions. The combined-condition simple netlists below are the cleaner screen.
- Murata's **own exact-part simple SPICE netlists**, queried from SimSurfing for specified DC voltage and temperature, are retained under the same evidence directory. They identify 2018 model-generation date, small-signal operation, 100 Hz–6 GHz and manufacturer. Values (per part): at **-55 °C**, 5.05 V `C=14.7 µF, L=0.591 nH, R=2.18 mΩ`; 3.38 V `16.9 µF, 0.588 nH, 2.23 mΩ`; 1.818 V `18.4 µF, 0.587 nH, 2.25 mΩ`; 0.92 V `18.7 µF, 0.588 nH, 2.25 mΩ`. At **125 °C / 3.38 V**, `C=28.8 µF, L=0.657 nH, R=2.13 mΩ`; **125 °C / 5.05 V**, `23.8 µF, 0.661 nH, 2.04 mΩ`. The colder models are the smaller-C case in this bounded sample. 25 °C models give 22.0 µF at 5.05 V and 26.2 µF at 3.38 V. These are exact-part *typical model parameters*, with packaging L/K sharing the base die; they are not guaranteed minima/maxima. The ×0.90 tolerance and ×0.875 lifecycle reserve in the table are **engineering allowances** applied to the model C. Temperature and DC/AC behavior are already represented by the model, so the prior separate 15% temperature and 65% bias factors must not be stacked again.
- [ADI LT3045 datasheet Rev. D](https://www.analog.com/media/en/technical-documentation/data-sheets/lt3045.pdf), pp. 12–13 and 16, requires COUT ≥10 µF, **ESR <20 mΩ and ESL <2 nH**; Kelvin OUTS directly to output capacitor/load and tie output-cap ground to SET-cap ground. For the two symmetric Murata 1210 parts at 3.38 V, the simple 125 °C coefficients imply an ideal parallel **0.329 nH** and **1.065 mΩ**. This leaves **<1.671 nH** for all common pads, vias, copper, return and sensing interconnect if treating the model as representative. The complete network has not been placed, extracted or measured. The model is not a worst-case guarantee, so even a layout calculation below the number is a screen, with first-article measurement still required. More C may lower LT3045 bandwidth; ADI says larger-than-minimum values only marginally improve PSRR/noise, so validate the resulting 94 µF nominal pair at startup/load steps.
- [TI TPS62825 family datasheet SLVSEF9I](https://www.ti.com/lit/ds/symlink/tps62825.pdf), Table 8-3, marks **0.47 µH + 47 µF** as a supported nominal combination for TPS62825; its **100 µF** column is blank for TPS62825 (the separate TPS62827 Table 8-4 does mark 100 µF). The current 2×47 µF=94 µF output bank is thus not table-certified. TI section 8.2.2.5 requires 10 µF effective output. Retaining one 47 µF at each TPS62825 stage is a cleaner nominal match, but qualified transients/loop stability are still required with the replacement inductor, distributed load capacitance, bias and actual copper.
- [TI TPSM63603 datasheet SLVSFS5A](https://www.ti.com/lit/ds/symlink/tpsm63603.pdf), section 8.2.2.2.5, requires 25 µF effective output, permits additional capacitance, and describes two 47 µF/10 V/1210 ceramics giving ~48 µF effective at 5 V in its example. The three Murata pieces estimate ≥34.73 µF by the model/reserve screen even at -55 °C. Keep three because two would screen at **23.15 µF**, below 25 µF. Verify the module's output startup/loop and ripple with the actual 141 µF nominal bank.

## Required blocker resolution

This is a **concrete preferred topology for the stocked part**, but cannot be called qualified production substitution from public primary data alone. The decisive unmet evidence is LT3045 **assembled COUT network ESL strictly below 2 nH**, plus actual production lot/temperature/bias effective capacitance and regulator startup/load-step response. Obtain Murata approval/characteristic data or measure representative lot C at **-55 °C** and each stated rail maximum under small-signal conditions, and extract/measure the placed LDO pair including common return and OUTS connection. The model screen has a 1.33× margin at the tightest TPS62825 bank, so an adverse lot shift beyond the chosen allowances could defeat it. Verify all three TPS62825s with the 47 µF/0.47 µH pair and all downstream capacitance; verify TPSM module with 3×47 µF. JLC uploader allocation should be checked at order time. No substitute is automatically approved by the stock observation.
