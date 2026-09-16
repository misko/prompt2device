# Crow audio carrier v1 — architecture

Status: FIRST-ARTICLE-ONLY / DO-NOT-ORDER. ADR0025 electrical source selected;
LT3041 local physical-source integration and 309 source regressions pass.
Native RJ45 schematics have been generated; corrected exact-subject review
and subsequent PCB generation remain owed. The existing PCB is stale and unrouted. This is not release acceptance.

## System boundary

This PCB is an analog receiver and synchronous ADC carrier. Eight roof pods arrive over eight factory RJ45 analog/power spokes. The carrier powers the pods, AC-couples and filters each balanced audio pair, digitizes all eight channels in one CS5308P, and presents one TDM8 stream to a short cable connected miniDSP MCHStreamer. Raspberry Pi 5, PoE/Ethernet, and USB data remain off-board COTS elements.

```text
PoE/Ethernet -> Raspberry Pi 5 -> short USB -> MCHStreamer
                                                |  clocks + TDM8
protected isolated 12 V -> carrier -> CS5308P --+
                               | eight 12 V + balanced-audio spokes
                               +-> roof microphone pods
```

## Power tree

```text
J9 protected isolated 12 V (11.4–13.2 V admitted)
  -> F_IN 2920L260/33 -> Q_IN reverse-hookup PFET + gate clamp -> 12V_PROTECTED
       -> D_IN shunt clamp
       -> F1..F8 -> 12V_POD1..12V_POD8, 0.10 A each continuous
       -> D_BUCK_IN US1B -> 12V_BUCK_IN + 3x10uF -> U_BUCK AP63205 -> 5V_BUCK
                      -> B340A -> 22 ohm precharge / AO3401A bypass
                         -> 5V_LDO_HOLD -> U_LDO LT3041 A-grade -> 3V3_ADC
                                   -> CS5308P VDD_A1/A2/VDD_IO
                                   -> 8 x OPA2320 dual amplifiers
                                   -> passive1k/1k external bias banks
                                   -> clocks + reset logic +200ohm rail bleed
```

ADR-0009 adds held-rail supervisors, delayed rail dump and eight TMUX2821
dual-channel isolation switches. Local steady 5 V allocation is 0.30 A;
150 mA ADC/reference reserve and1.0 A upstream limits are unchanged;
ADR0025 total shared3V3 allocation is230mA, local5V remains300mA. Startup and
partial-power behavior remain conditional source models, not qualifications.

ADR0022 adds local buck VIN reverse isolation. The shared spoke bus retains its
11.16V floor; a1.3V engineering input-diode drop leaves9.86V at the buck
and0.985346A total allocated input. The normal-removal versus preceding-
brownout distinction and conditional4.501285V shutdown reserve are governed
in[ADR0022](decisions/0022-buck-input-reverse-isolation.md). ADR0025 subsequently removes the independent OPA feed and buffered reference
energy domains; old held-input/OPA timing screens are not inherited.

The input source is already isolated and regulated; this PCB does not claim PoE isolation or lightning protection. F_IN is 2920L260/33 because its published hold current is 1.60 A at 70 °C and 1.27 A at 85 °C; the former 1812L110/33 candidate was only 0.63/0.50 A and could not support the total load. Q_IN is a 60 V P-channel MOSFET wired drain-to-input/source-to-load for static reverse-hookup blocking, with a 12 V gate-source zener. This is not reverse-current blocking from an energized downstream rail; pods are prohibited from sourcing power.

The carrier admits 11.4–13.2 V at J9 so the complete input PFET/PPTC plus per-port PTC/copper/contact budget can target at least 10.8 V at each carrier output header. J9 is the exact polarized/shrouded/positive-latch `43650-0200`/`43645-0200` pair with red `214761-2122` and black `214761-1122` 150 mm 18 AWG precrimps (`43030-0038`) and internal restraint `113-00022` after at least 12.70 mm free wire. Its tinned pigtails terminate at the protected COTS appliance output; there is no J9 gland and no PoE termination. The shared spoke cable contract then targets at least 10.5 V at the pod header at 0.10 A.

Each branch uses exact `1812L035/60MR`. Littelfuse publishes 0.20 A hold at 70 °C, 0.16 A at 85 °C, 0.70 A trip at 20 °C and 1.700 Ω `R1max`. The machine budget charges the 0.075 Ω input PPTC, 0.025 Ω PFET and 0.100 Ω common-copper allocation at the full rounded 1.0 A trunk current, then charges the 1.700 Ω branch PPTC, 0.400 Ω per-spoke copper/joint allocation and 0.100 Ω output-header allocation at 0.10 A. With the required 20% charge, the derived carrier-header floor is 10.896 V, 96 mV above 10.8 V. This closes the document-level selection, not hot-roof delivery: exact Kelvin-measured voltage drop, self-heating, all-eight loading and one-fault/seven-healthy behavior remain measured gates.

Protection is two-tier: carrier `1812L035/60MR` covers cable/pre-pod
faults; pod `0ZCJ0010FF2E` covers downstream-board faults. The carrier
0.70 A trip specification is a thermal PPTC characteristic, not a precision
current limit. Würth specifies 1.5 A per jack contact; the factory cord uses
26 AWG stranded conductors in three parallel positive/return pairs. Normal
0.10 A branch current would divide to about 33.3 mA per power contact with
equal paths. Neither equal sharing nor cable/plug fault ampacity is established
by those figures, and three contacts do not automatically triple the rating.
Do not inherit the former 22 AWG cable or Micro-Fit current ratings.
The COTS source's prospective short current must remain within the branch
PPTC's 10 A fault rating. Its 0.15 s trip point at 8 A does not authorize an
8 A installed-cord test. Hot resistance, source foldback, trip energy,
selectivity and one-fault/seven-healthy recovery remain first-article holds.

## Eight-channel analog path

Each spoke connector is Würth 615008160221: pins 1/3/7 `+12V_POD`,
2/6/8 `GND`, 5 `AUDIO+`, 4 `AUDIO−`, and shell pads 9/10 `CHASSIS`.
Physical nets are indexed per port (`12V_PODn`, `AUDIO_Pn`, `AUDIO_Nn`).

Each channel retains the Cirrus AN0556R1 Figure 2 filter cell, followed by
the ADR-0009 isolation stage:

- 1 µF series capacitor in each leg;
- 100 kΩ from each post-capacitor node to passive external VMID1 (channels 1–4) or VMID2 (channels 5–8);
- one OPA2320 dual in the unity-gain differential non-inverting topology;
- 10 kΩ current limiter between each bias tee and amplifier positive input;
- 300 Ω same-leg local feedback from each inverting node to its own filter-output branch, plus 680 pF C0G feedback per leg;
- 10 Ω series output resistors and two15nF C0G shunt capacitors per leg (30nF/leg) upstream of the isolation switch;
- TMUX2821 in both complete filter-output paths, then 10 kΩ and 1 nF C0G to ground at each ADC pin; no feedback bypass crosses the switch.

ADR0025 replaces the two reference followers with passive1k/1k external
bias banks using exact0.1percent RT0603BRD071KL resistors. Each retains
its10uF+1uF bypass and eight100k bias legs; all sixteen channel positive
inputs retain their10k current limiters. ADC_VMID1/2 remain independent
locally bypassed ADC outputs, not input-buffer references. The removed
U_AFE9/isolated4.7uF reservoir paths are not inherited protection obligations.
The shared-rail relative-pin argument and explicit engineering assumptions
are in [ADR0025](decisions/0025-shared-rail-protection-architecture.md).
The sixteen 1 µF signal-coupling parts are stable, nonpolar KEMET stacked-PET
film capacitors on exact 5 mm THT lands; their 10 mm installed height and manual
population are explicit placement/enclosure constraints.

The ADC reference bank deliberately uses higher nominal X7R values than the
typical-connection labels so every fitted part clears the Cirrus effective
minimum after one common conservative charge: 10% initial tolerance, 50% DC
bias, 15% temperature and 10% lifecycle loss. Each LDO filter and raw-VMID
bulk position uses exact Murata GRM188Z71C475KE21D/C389010 4.7 µF; each
raw-VMID high-frequency position uses exact Samsung
CL10B474KA8NFNC/C318640 470 nF; each `ADC_FILT` support position uses exact
KEMET C0603C105K4RACTU/C2167386 1 µF and active KEMET
C0805C106K8RACTU/C2167576 10 µF. The resulting conservative effective
values are 1.618, 0.1618, 0.3443 and 3.4425 µF respectively, above the
0.8, 0.1, 0.22 and 2.2 µF minima. Increased nominal capacitance is not a
production stability claim. Both 470 µF FILT reservoirs are retained;
their negative terminals and ADC_FILT1N/2N return directly to GND without
ground-leg resistors. ADR0025 replaces TPS7A92 with reverse-protected LT3041 and shares its
rail with the eight OPA2320 duals. Local source geometry is now screened;
filled native return/routing and prototype qualification remain OWED.
Native topology checks do not establish
power-state validity, reference-ripple or THD performance.

The resulting nominal high-pass corner is 1.59 Hz and the reference circuit's
low-pass corner is 640 kHz. Carrier gain is unity. The CS5308P's nominal
2.0 Vrms differential full scale is silicon context, not the admitted carrier
input envelope: the shared interface remains capped at 1.2 Vrms differential.
ADR0025 retains sufficient3V3 amplifier headroom without raising this requirement. Actual
filter/noise/distortion and correlated all-state protection remain owed.

## ADC and clocks

One CS5308P-DN is the only sampling clock domain. MCHStreamer is master at 48 kHz: MCLK 24.576 MHz, BCLK 12.288 MHz (256 Fs), one-BCLK FSYNC, eight 32-bit slots. CS5308P hardware straps select secondary ASP, 44.1/48 kHz family, TDM minimum-slot mode, default channel order, linear-phase fast rolloff, and the 1 Hz HPF. Only DOUT1 is used; DOUT2–4 float as instructed.

MCHStreamer J1 usage is fixed to pin 2 TDM input, 9 MCLK output, 10 BCLK output, 11 ground, and 12 FSYNC output. Pins 1 and 3–8 are intentional no-connects. J11 connects to official J3 pin 1 ground and pin 2 3.3 V only; its 3.3 V is sensed at about 0.320 mA through 300 Ω / 10 kΩ and never supplies the carrier rail. The other J11 pins are no-connects.

SN74LVC3G34 buffers the three incoming clocks and provides Ioff protection when carrier power is absent. Three corrected 10 kΩ input pull-downs give a valid disconnected-input leakage budget. DOUT1 passes through an Ioff-capable SN74LVC1G125. J3 sense drives the 74LVC1G14 Schmitt inverter U_OE: its push-pull output holds active-low OE high when the sensed module rail is absent and enables DOUT when it is present. The former NMOS interlock and OE pull-up were removed. The 33 Ω resistor is output damping after that buffer, not a back-power barrier. ADR-0005 records the four-state contract, explicit leakage/driver-load allocations and the choice not to carrier-power MCH J2. Module driver limits, actual interlock levels over temperature and power transitions remain first-article evidence, not a guaranteed hot-plug claim.

The MCHStreamer always treats TDM input as 24-bit. Retention of the intended 24 MSBs, clock edge, channel order, slot mapping, all four independent-power states, and split-cable behavior are mandatory logic-analyzer/current first-article tests.

## Reset

CS5308P requires RESET high after initial power, a delay of at least 2 ms, RESET low for at least 1 ms, then high. TPS3839K33 holds the monostable clear low during rail ramp and releases it only after its 120–350 ms delay. CLR rising triggers SN74LVC1G123; Q drives a 2N7002 that pulls ADC_RESET_N low, then releases it to a 10 kΩ pull-up.

The candidate uses 100 kΩ ±1% and 220 nF X7R ±10% for a nominal 22 ms pulse. TI specifies the 10 kΩ/0.1 µF reference point as 1.0 ms typical, 1.1 ms maximum and does not publish a guaranteed minimum pulse duration. The deliberately large ratio provides screening margin, but oscilloscope proof over supply and temperature remains an first-article qualification hold.

## Ground and stack

Four layers: F.Cu components/signals, In1.Cu continuous ground reference, In2.Cu quiet power islands, B.Cu secondary signals/ground fill. ADC paddle, GND_A, and GND_D join the common ground plane with local returns following the Cirrus layout guide. No signal crosses a plane split. The buck/input protection cell stays away from ADC inputs and VMID/reference components.

## Physical layout intent

The proposed 154 × 100 mm first-article board puts four spoke headers on each long edge, analog cells directly behind their connectors, ADC and reference network centrally, MCH clock header at the east edge, and the 12 V/buck cell at the west edge. This is a source floorplan, not a fit proof. Connector bodies, cable bends, enclosure/chassis drain termination, and MCH cable keying require independent physical evidence.

## Release boundary

No generated artifact is order authority. ADR-0006 permits its explicit public-catalog-only prototype prelayout path without claiming exact JLC allocation. Release staging still requires source acceptance, schematic and placement reviews, DRC/parity, spoke-copper 8/8 proof, both red-team lenses and the applicable sourcing gate. Per ADR-0007, a prototype order additionally requires separate user authorization, exact sealed upload review and current JLC allocation/economics; it does not require measurements on the yet-unbuilt first article. First-power checks, measured first-article qualification and production/outdoor authorization remain separate later boundaries. Neither public catalog data nor a design release closes those physical tests.


## Adopted factory RJ45 spoke — 2026-09-12

The adopted source uses Würth 615008160221 nonmagnetic shielded 8P8C
jacks and complete Weidmüller 8909650150 factory 15 m Cat6A S/FTP PUR cords.
Pins 1/3/7 carry +12 V, 2/6/8 return, 5 AUDIO+ and 4 AUDIO−. Shell pads
9/10 join carrier CHASSIS or pod POD_SHIELD; neither net connects to circuit
GND. The pod shield island is isolated from circuit ground, not disconnected
from the cord shield. These ports carry custom analog audio and power;
label them “POD AUDIO +12V / NOT ETHERNET OR POE” and mate with power off.
No field crimps, splices or pigtails belong to this spoke assembly.

Exact manufacturer STEP establishes a nominal complete plug end of
57.98 × 13.70 × 18.456687 mm and a 22.986 mm nominal grip diameter.
These are nominal CAD envelopes, not manufacturing or installed-service
limits. Cable OD is 6.1–6.5 mm; retain the 67 mm bend planning floor.
The three parallel power pairs give the conditional hot-loop screen
`290 Ω/km × 0.015 km / 3 × 1.25 + 0.300 Ω = 2.1125 Ω`, hence
10.58875 V at 0.10 A from 10.8 V. Contact allowance, finished-loop resistance,
power sharing, fault behavior, mating/service and environmental performance
remain measured obligations. UV is unestablished; PUR alone is not evidence.
The source adoption is recorded in the carrier schematic journal at
2026-09-12 20:08 UTC. Native review, routing and release are separate gates.

## Fixed logical pod and physical ADC association — ADR0027

`03_src/adc_channel_map.json` freezes logical pods1..8 to physical
ADC4,3,2,1,5,6,7,8. Hardware-default TDM slots0..7 therefore carry
pods4,3,2,1,5,6,7,8. ADCnP/N names the logical pod, not the physical
ADC ordinal. All north receive paths remain in the same reference domain;
all connector, AFE, ISO, clock/configuration and south identities are unchanged.
Capture records must bind map ID `crow-carrier-channel-map-20260912`, its digest,
and surveyed pod identities. Source ordering is distinct from the owed
eight-channel impulse/USB slot proof.

ADR0030 proposes outline x16..170/y20..120 mm with west mounting centers x21 mm (east x165, y25/115). The J9 physical mouth at x19.08 is set back3.08 mm from the new west edge. Direction-only edge_faces does not establish mouth exposure, mate/latch/tool clearance, pigtail/restraint routing or enclosure fit; these existing service holds require renewed exact scenes. All fitted SMD, including manual/consigned, is on F.Cu. This source batch remains proposed pending exact-source/native review.
