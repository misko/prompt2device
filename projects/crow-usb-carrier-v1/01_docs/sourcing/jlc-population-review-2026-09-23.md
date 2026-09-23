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

