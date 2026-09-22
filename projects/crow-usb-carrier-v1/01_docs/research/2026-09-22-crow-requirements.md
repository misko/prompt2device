# Crow USB carrier: requirements and architecture delta

## Scope and authority

This is a read-only requirements handoff. It does not select a USB IC, approve firmware, adopt the old board layout, or transfer any release/order approval. The sole new hard product directive is a **new Crow carrier with an onboard USB interface IC and a direct USB cable to the Raspberry Pi**, replacing the external MCHStreamer boundary ([new brief, lines 17–33](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/01_docs/BRIEF.md#L17); [ADR 0001, lines 8–30](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/01_docs/decisions/0001-onboard-usb-boundary.md#L8)). Everything else below is classified as inherited precedent, provisional assumption, or owed decision.

The new commission remains open. Q1 has not confirmed retention of the eight Crow spokes/external 12 V supply, and Q2 has not authorized project firmware ([new brief, lines 77–97](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/01_docs/BRIEF.md#L77)). The seeded architecture/rule files are examples and must not be treated as product facts while `COMMISSIONING-HOLD.md` exists ([commission hold, lines 1–16](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/01_docs/COMMISSIONING-HOLD.md#L1)).

## Requirements matrix

| ID | Requirement / precedent | Classification for new board | Architecture consequence / acceptance evidence |
|---|---|---|---|
| U1 | Onboard USB interface IC; direct USB cable to Raspberry Pi; no external MCHStreamer | **HARD — user directive** | Remove MCH module/cable boundary. Freeze exact USB IC only after host support, clocking, power, firmware/image and sourcing evidence close. USB receptacle, ESD, impedance/length, VBUS sense and self-powered-device backfeed behavior become native board responsibilities. |
| U2 | Pi is host, carrier is USB device; USB transports audio and does not replace spoke power | **PROVISIONAL A2**, pending Q1 | Treat bridge as carrier-powered/self-powered and VBUS as attach/sense only. Never join VBUS to `5V_BUCK`/`3V3_ADC` without a new power-role decision. Grade carrier-only, VBUS-only, both-on, brownout, attach and detach. Source: [new brief, lines 48–61](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/01_docs/BRIEF.md#L48). |
| A1 | Eight simultaneous, phase-coherent channels at 48 kHz, 24-bit samples | **PROVISIONAL inherited product requirement**, pending Q1 | Keep one synchronous ADC clock domain and prove eight channels at the Pi capture endpoint. Existing TDM framing is eight 32-bit slots, 12.288 MHz BCLK and 24.576 MHz MCLK, but those exact internal clocks are retained only if compatible with the selected bridge ([prior architecture, lines 124–132](/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/crow_requirements/inputs/prior_architecture.md#L124)). |
| A2 | USB transport capacity for eight packed 24-bit channels | **DERIVED hard gate if A1 is adopted** | Payload is `8 × 48,000 × 24 = 9.216 Mbit/s` before USB framing; per 1 ms frame it is 1,152 bytes (or 1,536 bytes if padded to 32 bits). A candidate must evidence a high-speed-capable USB/audio path; do not accept nominal USB Full Speed bandwidth as proof. Confirm Linux/Raspberry Pi enumeration, endpoint packetization, channel count, sample format and sustained capture without loss. |
| A3 | Logical pods 1–8 map to physical ADC 4,3,2,1,5,6,7,8; stream slots 0–7 carry pods 4,3,2,1,5,6,7,8 | **INHERITED candidate identity**, explicitly re-adopt or replace | Preserve `crow-carrier-channel-map-20260912` only if the new USB bridge exports that order. Capture record must bind map digest, pod/cable identities and an eight-channel impulse test ([prior architecture, lines 176–185](/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/crow_requirements/inputs/prior_architecture.md#L176); [map source](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-audio-carrier-v1/03_src/adc_channel_map.json#L1)). |
| S1 | Eight exact shielded RJ45 Crow spokes, all concurrent; pins 1/3/7 +12 V, 2/6/8 GND, 5 AUDIO+, 4 AUDIO−, shell 9/10 CHASSIS; not Ethernet/PoE; mate powered off | **PROVISIONAL inherited interface**, pending Q1 and explicit adoption | Candidate reuse: J1–J8 Würth `615008160221`, factory Weidmüller `8909650150` 15 m cords, pin/net identity and labels. Keep CHASSIS separate from circuit GND. Do not infer Ethernet/PoE from connector form ([prior architecture, lines 153–174](/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/crow_requirements/inputs/prior_architecture.md#L153)). |
| S2 | Each pod: 12.0 V nominal, 10.8–13.2 V at carrier jack, >=10.5 V at pod after qualified cable drop, 0.10 A continuous; all eight loaded | **PROVISIONAL inherited load lock**, pending Q1 | If adopted, retain eight independent branch protections and the measurement-plane distinction. Current source claims 10.896 V carrier floor and 10.58875 V conditional pod result; both remain first-article measurements, not transferred proof ([prior detail, lines 68–90](/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/crow_requirements/inputs/prior_detail.md#L68); [prior detail, lines 96–122](/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/crow_requirements/inputs/prior_detail.md#L96)). |
| S3 | Active-balanced input, 2.5 V nominal common mode, 1.2 Vrms differential maximum; carrier unity gain and AC coupling | **PROVISIONAL inherited analog lock**, pending Q1 | Candidate reuse of each analog cell and its 1.2 Vrms admitted envelope. The ADC's 2.0 Vrms full scale is context, not permission to raise the interface limit ([prior architecture, lines 69–122](/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/crow_requirements/inputs/prior_architecture.md#L69)). |
| P1 | External isolated regulated 12 V at J9, 11.4–13.2 V; disconnect J9 for off; no on-board safety isolation/lightning claim | **PROVISIONAL inherited power boundary**, pending Q1 | Candidate retain J9 and input PPTC/PFET/clamp, spoke distribution, local buck/quiet rail. Recalculate trunk current and all rail margins after adding USB core/clock/memory loads. Prior local limits were 0.30 A at 5 V and 0.23 A at 3V3; shared 3V3 used 222.374 mA already, so the USB block cannot simply be added to `3V3_ADC` ([prior detail, lines 68–94](/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/crow_requirements/inputs/prior_detail.md#L68)). |
| P2 | Input protection and per-spoke PPTCs; one faulted spoke must not reset the other seven | **PROVISIONAL inherited safety/function lock** | Candidate retain `F_IN`, `Q_IN`, `D_IN`, `F1..F8` and branch nets `12V_POD1..8`; redo prospective-short, foldback, hot-drop, energy/selectivity and one-fault/seven-healthy tests with the selected source ([prior architecture, lines 49–67](/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/crow_requirements/inputs/prior_architecture.md#L49)). |
| P3 | Quiet ADC startup/shutdown: held rail, supervisors, dump, analog isolation and high-delay-low-high ADC reset | **INHERITED candidate function; fresh validation required** | These functions protect/quiet the ADC and analog path, not merely the MCH boundary. Retain the intent and likely `U_PWR`, precharge/hold, `U_AUDIO`, `U_DUMP`, `U_LDO_EN`, `U_ISO1..8`, ADC-side bleeds, and `U_RST1/U_RST2/Q_RST1`; rerun sequencing with USB bridge load and clocks. Prior switch topology is after the complete filter and keeps the OPA loop closed ([ADR 0009, lines 41–83](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-audio-carrier-v1/01_docs/decisions/0009-held-power-and-analog-isolation.md#L41)). |
| P4 | MCHStreamer independent-power four-state boundary | **SUPERSEDED** | Do not carry the old external-module state machine forward. An onboard bridge powered by the carrier has no separately powered MCH rail/cable. Replace it with USB VBUS-present versus carrier-power states and the bridge vendor's unpowered-I/O/VBUS rules. |
| M1 | Prior 154 × 100 mm outline / x16..170, y20..120 and mounting centers | **PROPOSED precedent, not a hard envelope** | Re-floorplan around USB receptacle and bridge; old east MCH area is only available space, not an accepted placement. Exact connector service, enclosure and bend scenes remain owed ([prior architecture, lines 144–146, 187](/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/crow_requirements/inputs/prior_architecture.md#L144)). |
| M2 | All fitted SMD on F.Cu and all carrier SMD placed by JLCPCB; THT may be local | **PRIOR explicit manufacturing directive; requires explicit adoption into new commission** | Treat as a strong default, then re-lock. Do not place USB bridge/support on B.Cu to recover area without user reversal. Prior record: [prior brief, lines 270 onward](/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/crow_requirements/inputs/prior_brief.md#L270). |
| R1 | Four layers, In1 continuous ground, no signal over plane splits; switching cell away from ADC inputs/references | **INHERITED design precedent, fresh architecture decision** | Likely minimum starting stack. USB differential routing, clock return and the USB/core power islands must be added to the stack/return analysis; layer count/fab tier can change if the bridge escape requires it ([prior architecture, lines 140–142](/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/crow_requirements/inputs/prior_architecture.md#L140)). |
| F1 | No project firmware | **NOT a current hard requirement** | The prior board used hardware-mode ADC and COTS MCH firmware, but the new brief explicitly leaves firmware authorization unanswered. Research is allowed; authoring/build/release is not. Exact USB IC cannot be frozen until Q2 or a documented immutable vendor image/configuration path closes ([new brief, lines 35–41, 82–85](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/01_docs/BRIEF.md#L35)). |
| L1 | Old release/order/placement/routing approvals | **DO NOT INHERIT** | New schematic, population, power budget, placement, USB SI, routing, DRC/parity, sourcing and first-article evidence are required. No fabrication/order is authorized ([new brief, lines 19–24](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/01_docs/BRIEF.md#L19)). |

## Source adoption and replacement plan

The existing source is useful as a component/net-level donor only. Do not copy the solved placement, `route.yaml`, `final_chain.kicad_pcb`, generated KiCad board, or old gate receipts.

| Prior source slice | New-board disposition | Concrete refs / nets |
|---|---|---|
| Eight physical spoke entries | **Candidate retain after Q1** | `J1..J8`, `U_ESD1..8`, `F1..F8`; `AUDIO_Pn`, `AUDIO_Nn`, `12V_PODn`, `CHASSIS`, GND. Exact authored pin map appears at [TSX lines 334–350](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-audio-carrier-v1/03_tscircuit/src/crow_audio_carrier_v1.tsx#L334). |
| Eight receive cells | **Candidate retain electrically; place afresh** | `C_AnP/N`, `R_BnP/N`, `R_INnP/N`, `U_AFEn`, `R_XnP/N`, `C_FBnP/N`, `R_OUTnP/N`, `C_FILTERnP1/P2/N1/N2`, `U_ISOn`, `C_ISOn`, `C_OPAn`; nets through `FILTERnP/N` ([TSX lines 368–405](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-audio-carrier-v1/03_tscircuit/src/crow_audio_carrier_v1.tsx#L368)). |
| ADC-side input terminations | **Retain with ADC neighborhood, not channel geographic ownership** | `R_ADC_PDnP/N` and `C_ADC_CMnP/N` on `ADCnP/N`. They occur after `U_ISOn` and directly load ADC pins ([TSX lines 394–403](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-audio-carrier-v1/03_tscircuit/src/crow_audio_carrier_v1.tsx#L394)); assign their placement to the ADC joint neighborhood. |
| CS5308P and reference/mode network | **Candidate retain, conditional on selected bridge's exact serial mode** | `U_ADC`, `R_CFG1/2/4/5`, `R_FILT1P/2P`, `C_FILT*`, `C_VMID*`, `C_LDO_A/D`, `C_VDDA*`, `C_VDDIO`, passive `VMID1_EXT/VMID2_EXT` banks, channel-map JSON. Preserve local returns and effective-capacitance requirements; do not freeze TDM straps until bridge clock/frame capability is proven ([TSX lines 532–576](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-audio-carrier-v1/03_tscircuit/src/crow_audio_carrier_v1.tsx#L532)). |
| Input/spoke and quiet analog power | **Candidate retain topology, recalculate/re-source as needed** | `J9`, `F_IN`, `Q_IN`, `R_QIN_G`, `D_QIN_GS`, `D_IN`, `D_BUCK_IN`, buck/hold/precharge/LT3041/supervisor/dump circuits; nets `12V_IN`, `12V_FUSED`, `12V_PROTECTED`, `12V_BUCK_IN`, `5V_BUCK`, `5V_LDO_HOLD`, `3V3_ADC`. Add a separately budgeted USB digital/core rail if required. |
| ADC reset | **Candidate retain** | `U_RST1`, `C_RST1`, `U_RST2`, `C_RST2`, `R_RST_T`, `C_RST_T`, `Q_RST1`, `R_RESET_PU`, `R_RESET_GPD`, `POR_N`, `RESET_PULSE_H`, `ADC_RESET_N`. Required sequence is initial high, wait >=2 ms, low >=1 ms, final high; measured qualification remains owed ([prior architecture, lines 134–138](/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/crow_requirements/inputs/prior_architecture.md#L134)). Firmware control may supplement but must not silently replace this behavior while Q2 is open. |
| MCH physical boundary | **Remove** | `J10`, `J11`, both Samtec cables, their MCH mating facts/models/footprints and MCH labels. Nets `MCH_MCLK`, `MCH_BCLK`, `MCH_FSYNC`, `MCH_3V3_SENSE` retire. |
| MCH input/presence conditioning | **Remove, not transplant** | `R_MCH_MCLK_PD`, `R_MCH_BCLK_PD`, `R_MCH_FSYNC_PD`, `R_MCH_SENSE`, `R_MCH_SENSE_PD`, `U_OE`, `C_OE`. Their purpose was an independently powered cable-connected module ([TSX lines 578–618](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-audio-carrier-v1/03_tscircuit/src/crow_audio_carrier_v1.tsx#L578)). New bridge needs a vendor-defined VBUS sense/detach circuit instead. |
| MCH-return DOUT conditioning | **Remove or redesign as local bridge interface** | `R_TDM_PD`, `U_TDM_SCH`, `C_TDM_SCH`, `U_TDM`, `C_TDM`, `R_TDM`; retire `TDM_RAW`, `TDM_CLEAN`, `TDM_OE_N`, `TDM_BUFFERED`, `ADC_TDM` unless deliberately reused with new meanings. Direct local `ASP_DOUT1` to bridge receive input normally eliminates the old cable/off-domain tri-state chain; validate voltage, loading, edge and setup/hold from both datasheets. |
| Clock fan-in | **Redesign** | `U_CLK`, `C_CLK`, `R_MCLK`, `R_BCLK`, `R_FSYNC`; old buffered nets and exact 22 ohm values were driven by the MCH cable boundary. The onboard bridge may be TDM master, ADC-clock slave, or share an oscillator. Choose one clock owner and derive source damping from exact driver/package/trace; retain `ADC_MCLK`, `ADC_BCLK`, `ADC_FSYNC` only as ADC-side semantic nets. |
| USB block | **New** | Exact high-speed USB IC, USB connector, D+/D− ESD, any common-mode/series elements justified by vendor reference, VBUS sense/protection, oscillator/crystal, flash/EEPROM, programming/recovery access, core/I/O rails and decoupling. Assign unique refs/nets only after architecture/part selection. |

### Power-state simplification

Assuming the onboard USB bridge runs from the carrier supply and USB VBUS is sense-only, the old external-MCH four-state circuit is eliminated. The new state table is still mandatory but narrower:

| Carrier 12 V | Pi VBUS | Required behavior |
|---|---|---|
| off | off | Entire board off/discharged within declared limits. |
| off | on | USB D+/D− and VBUS sense must not back-power carrier/core/ADC; device must remain electrically compliant and detached. |
| on | off | Carrier/ADC may complete quiet startup, but USB device remains detached; no uncontrolled data/clock activity into an unready bridge. |
| on | on | Enumerate and stream eight channels; deterministic reset, clock and channel order. |

Also test attach/detach during streaming, carrier brownout with VBUS present, Pi reset/reboot, cable removal, ordinary J9 removal, prior-dropout removal and rapid correlated restart. Bridge clocks must be gated/reset so they cannot defeat the retained ADC reset/mute sequence. This is a fresh state analysis; old ADR0005 approval does not transfer.

## Modular ownership and joint placement groups

Use functional ownership for schematic/source work, then create joint physical groups wherever locality crosses those functions. Each component has one owner; joint groups own checks and corridor decisions, not duplicate components.

1. **Spoke mechanical/power owner:** J1–J8 connector bodies, shields, service/bend envelopes, `F1..F8`, `U_ESD1..8`, power-contact fanout and CHASSIS. Boundary: `AUDIO_P/N`, `12V_PODn`, GND/CHASSIS.
2. **Repeated AFE owners (eight):** coupling/bias/OPA/feedback/filter components through the source side of `U_ISOn`. These may repeat schematically, but their positions derive from connector escape, ADC reach and shared VMID routing; do not force eight identical geographic islands.
3. **ADC analog joint group:** `U_ADC`, `U_ISO1..8` ADC-side pads, **all `R_ADC_PD*` and `C_ADC_CM*`**, ADC bypass/reference/FILT/VMID parts and the first segment of all sixteen `ADCnP/N` routes. This group overrides the tempting functional assignment of termination capacitors to distant channel blocks.
4. **Quiet-power/analog-state group:** buck exclusion boundary, precharge/hold, LT3041 local loops, supervisors/dump and `AUDIO_EN`. Joint proof with the ADC group covers supply-return geometry, startup/discharge and switch control.
5. **USB/core group:** USB receptacle, ESD, differential pair, bridge IC, local clock, memory/configuration and core rails. It owns the USB escape and edge keepout, not the TDM/ADC endpoints.
6. **Digital clock/data joint group:** bridge serial pins, source damping, ADC MCLK/BCLK/FSYNC/DOUT1 pins, reset interaction and the complete bridge-to-ADC route. Prove this jointly with the ADC group before global routing.
7. **Board-level integration owner:** outline/holes, continuous reference plane, 12 V trunks, USB/clock/analog corridor reservations, thermal/assembly access and whole-board coupling checks.

This grouping follows the prior failed modular replay: the coarse candidate failed 54/62 adjacency and 268/353 pair checks, and the bounded repair explicitly joined `U_ADC`, `C_FILT1_1U`, and `C_ADC_CM1P/N` with the receive-chain neighborhood ([trial provenance, lines 142–187](/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/tests/checkpoints/evidence/crow-modular-20260921/PROVENANCE.md#L142)). Functional sheets are inputs to grouping, not geographic placement templates.

## Architecture and gate checklist

### Commission closure before IC freeze

- Obtain Q1: confirm eight existing Crow RJ45 analog/power spokes, their exact 12 V/load envelope, and external carrier power are retained.
- Obtain Q2: authorize project firmware, or constrain selection to an exact vendor-programmed/class-compliant image with a reproducible acquisition, digest, programming and readback path.
- Lock supported Raspberry Pi model/OS/kernel, USB Audio class/version, capture API, eight-channel sample packing, channel names/order, acceptable latency and sustained-record duration. Prior 120 s identity language is precedent, not yet adopted into this new brief.
- Decide whether 48 kHz/24-bit is the only required mode or a minimum/default; do not silently add sample rates.
- Re-adopt or change the top-only/JLC assembly constraint, outline/enclosure and connector placement limits.

### USB/clock architecture gate

- Candidate proves high-speed USB operation and eight-channel 48 kHz/24-bit input on Raspberry Pi/Linux; record enumeration descriptors and endpoint bandwidth calculation.
- Candidate proves exact TDM/I2S receive capability: eight slots, slot width, data width/alignment, FSYNC polarity/width, BCLK edge, master/slave role, MCLK need/frequency, channel order and voltage domain.
- Exactly one clock owner; frequency tolerance/jitter budget covers bridge, oscillator/PLL and CS5308P. Recalculate source terms after placement.
- Firmware/configuration boot source and recovery path are explicit. Blank/unprogrammed behavior is safe and cannot energize or connect audio unpredictably.

### Power/protection gate

- Recompute 12 V trunk, 5 V and every low-voltage rail with bridge/core/clock/memory peak and inrush currents. Do not fit the USB block into the prior 7.626 mA 3V3 headroom.
- Prove VBUS sense thresholds and current, USB attach/detach, no backfeed in VBUS-only/carrier-only states, and D+/D− behavior when the bridge is unpowered.
- Revalidate quiet-start/hold/dump/TMUX/reset timing with bridge clocks and load; preserve ADC relative-pin and negative-excursion limits.
- Keep USB return-current paths and digital regulator noise away from ADC input/reference neighborhoods; establish conducted/radiated noise and spur acceptance at 48 kHz capture.

### Schematic/source gate

- Adopt selected old subcircuits by enumerated ref/net mappings, with new ADRs and current dossiers; do not copy old placement/copper/check receipts.
- Remove every MCH-only ref/net/assertion from schematic, requirements, integration rules, floorplan, route config, BOM, models, silkscreen and tests. A stale `J10/J11`, `MCH_*` net or old independent-power checker is a failure.
- Add exact USB pin map, connector orientation, ESD topology, clock/memory straps, decoupling and power-on defaults with hostile fixtures.
- Independently review generated native netlist and human schematic; pin 1/orientation and USB D+/D− polarity require primary-source evidence.

### Placement/routing gate

- Begin from fresh board anchors. Reserve USB edge/service envelope, differential escape, crystal loop, digital/ADC clock corridor, ADC analog fanout, buck exclusion and all connector bend/service space before detailed placement.
- Pass detailed proximity checks before routing. Run local copper probes for (a) USB connector–ESD–bridge, (b) bridge clock/data–ADC, (c) ADC input/termination/reference neighborhood, and (d) regulator critical loops.
- Grade joint groups together; local block success does not prove combined feasibility. Any repeated boundary conflict reopens grouping/floorplan.
- Final native checks: DRC 0 violations, 0 unconnected, 0 schematic parity; USB differential impedance/spacing/length/reference continuity, clock topology, all 16 analog inputs, eight spoke-current paths, return continuity, top-side population and model/connector service review.

### Bench/first-article gate

- Enumerate on target Pi and capture eight simultaneous 48 kHz, true 24-bit channels continuously; record packet/drop/xrun evidence and 120 s identity stability if that duration is re-adopted.
- Logic-analyzer proof of MCLK/BCLK/FSYNC/DOUT edge, slot and 24-bit extraction; eight-channel impulse proof binds USB channel to physical pod and polarity.
- Exercise all carrier/VBUS power states, brownout, rapid restart, attach/detach and Pi reboot while measuring backfeed, reset, mute, rails and ADC pins.
- Repeat prior analog/power qualifications: gain/phase/noise/THD/crosstalk, full-level all-channel behavior, hot all-eight load/drop, inrush, one-fault/seven-healthy, thermal and cord/service limits. Old prototype results, if any, are not evidence for the new USB population.

## Principal risks and unresolved decisions

1. **Firmware authorization is the architecture fork.** A capable high-speed multichannel USB bridge commonly needs firmware/configuration; Q2 is unanswered. No exact IC should be presented as selected until this closes.
2. **USB throughput/host compatibility can invalidate a part before schematic work.** Require an exact eight-input endpoint demonstration or vendor-supported configuration, not a headline USB speed.
3. **Power margin is already nearly consumed.** The old 3V3 rail used 222.374 mA of 230 mA; a new digital bridge likely forces a separate rail or upstream redesign.
4. **Clock ownership changes the ADC interface.** The old MCH was a fixed TDM master. A different bridge may require a new oscillator/PLL, different framing or firmware; existing straps and 22/33 ohm terms are not automatically valid.
5. **USB VBUS creates a new partial-power path even when the bridge shares carrier power.** Removing MCH Ioff circuitry is justified only after the new bridge's VBUS/D+/D− unpowered rules are proven.
6. **Mechanical size is open.** The prior 154 × 100 mm layout and holes are proposals. USB edge access, cable shell, ESD/bridge locality and all-top assembly may require enlargement or a different outline.
7. **The source donor is not release authority.** Its current board was documented as stale/unrouted at the architecture snapshot, and later approvals belong to a different subject. Every changed path needs fresh evidence.

## Conditional USB candidate update from parallel research

The current preferred candidate is **XMOS XU316-1024-TQ128-C24**, carrier-powered, using high-speed USB Audio Class 2. This is a research preference, not a frozen part or an inherited approval. `XU208` was excluded by that review because of a documented TDM-master reliability problem; `CM6637` was excluded because an exact image/programming path was unavailable. Preserve those rejection reasons in the architecture ADR and sourcing record rather than reopening them without new evidence.

For the XU316 path, hardware work may proceed conditionally on exact primary material: open the part dossier, reference-design adoption record, package/pin audit, USB/clock/boot-memory/power tree, TDM pin assignment and preliminary floorplan. The bridge remains powered from new carrier digital rails and VBUS remains sense-only, so the MCH presence/OE/Ioff chain stays removed. Do not connect XU316 loads to the nearly full `3V3_ADC` budget; derive and screen every required XU316 rail and sequence separately, then join only the intended logic ground/reference domain.

The XU316 choice strengthens rather than closes Q2: a board-specific firmware image is required. Firmware source/build/release remains unauthorized until the user answers Q2, but hardware dossier and reference-design pin-assignment work can continue as reversible design research. Part freeze additionally requires an evidenced Raspberry Pi/Linux UAC2 enumeration and sustained eight-channel 48 kHz/24-bit capture path, exact boot/program/recovery method, image identity/readback plan, and proof that the selected TDM master/slave arrangement satisfies both XU316 and CS5308P timing.
