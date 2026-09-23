# Crow USB carrier architecture — commissioning draft

Status: hardware source under commissioning. The current source composes the
XU316-1024-TQ128-C24, its power/clock/memory support, retained eight-channel
analog circuitry, and USB front end. Nominal USB cross-section is adopted in
`03_src/rules/rf.yaml`. Schematic presentation/review, power bounds and physical
qualification remain open. Firmware stays separately scoped; the commissioning
hold remains active.

## Block diagram

```text
8 existing Crow analog/power spokes
    -> eight protected differential receive/filter paths
    -> one synchronous 8-channel ADC
    -> short onboard synchronous digital audio link
    -> onboard USB-audio interface IC + required clock/memory/power support
    -> protected USB device receptacle
    -> USB cable -> Raspberry Pi host

External carrier supply -> protected spoke power + analog rails + digital rails
Pi USB VBUS -> presence/detach sensing; no intentional carrier-to-host power path
```

The old external MCHStreamer and its board-to-board TDM/presence cables are
removed from the new product boundary. This does not automatically retain or
remove any individual safety component: each power-state dependency is to be
rechecked from its owner and pin limits.

## Power tree

The provisional policy retains the external carrier supply and eight powered
spokes. The USB bridge is provisionally carrier-powered, so its audio clocks,
ADC and control logic can share a controlled local startup/shutdown sequence.
The digital source uses 0.9 V core, nominal 1.860 V on the net named 1V8 for every XU316 I/O bank, and
nominal 3.318 V on 3V3X for USB/audio support. The adjustable-divider DC screens are 1.822–1.899 V and 3.243–3.394 V respectively; executable feedback bounds are in power_tree.yaml. Boot memory is exact W25Q128JWSIQ,
a 1.8 V, 128-Mbit (16-MiB), fixed-QE QSPI NOR selected for the XU316 ROM EBh path.
The repaired 5 V input supply candidate
is TPSM63603V5RDHR; its land pattern and thermal implementation remain under
review. Retained analog quiet-start, hold-up and disconnect source has been
compared with the donor topology; this does not confer new-board acceptance.

| Carrier power | Pi VBUS | Required behavior |
|---|---|---|
| absent | absent | De-energized; stored energy discharged through the designed path. |
| absent | present | No back-power into carrier rails or spoke wiring through USB or logic pins. |
| present | absent | Spokes and analog circuitry remain within their supported state; USB device stays detached. |
| present | present | Enumerate and stream only after valid rails and stable audio clocks. |
| falling/brownout | either | Stop invalid samples/clocks and protect analog inputs before uncontrolled rail decay. |
| stable | VBUS removed/reapplied | Detach/reattach without a false clock edge, latch-up or host backfeed. |

Each row needs exact pin-level circuit evidence, an independently reviewed
state argument and eventual first-article measurements. This table is a design
requirement, not evidence that these behaviors already work.

## Net domains

- Eight analog receive paths: preserve channel ordering, common sampling clock
  and supported source/load boundary.
- ADC common-mode/reference and supply paths: solve with the ADC pin neighborhood.
- Onboard serial audio: select the IC pair and clock master together. Existing
  operating intent is 48 kHz, eight 32-bit time slots, 12.288 MHz serial bit clock
  and 24.576 MHz master clock; alternate clock modes need explicit evidence.
- USB device link: USB 2.0 high-speed UAC2 through the onboard XU316 and
  protected USB4105 receptacle. The 8-channel payload exceeds one full-speed
  isochronous transaction; high-speed operation is required.
- Power/protection/control: source rules will replace the scaffold examples once
  the input envelope and part selection are admitted.

## Data and clock budget

The retained audio payload is 8 × 48,000 × 24 = 9,216,000 bits/s before USB
protocol overhead. With four-byte sample containers it is 12,288,000 bits/s.
The synchronous TDM link is 8 × 32 × 48,000 = 12.288 MHz. Matching those rates
alone is insufficient: exact frame-sync polarity/width, data alignment, launch
edge, receiver setup/hold and master-clock relationship must match both ICs.
The digital source adds a hardware frame-sync pulse extender to accommodate
the documented lib_xua pulse and ADC minimum width. Component timing has been
screened; the ADC supply-domain interface is being repaired before adoption.
Routed timing and eventual USB capture remain separate evidence boundaries.

## Stackup

Use the vendor-supported four-layer JLC04161H-7628G nominal-1.6-mm stack,
1 oz outer / 0.5 oz inner copper, with F.Cu USB routing over continuous In1.Cu.
The source RF rule carries the vendor-solved nominal width/gap; exact primary
responses and plated-copper/mask assumptions are retained in
[impedance evidence](research/2026-09-22-usb-impedance-evidence.md).
This establishes a design cross-section, not routed-board or production
qualification. The 1 oz thermal design must be proven separately. No old
outline, hole positions or learned via/copper arrangements are hard constraints.

## Ground strategy

Use continuous ground/reference paths as the baseline. Separate analog and USB
placement/current-return regions by floorplanning rather than assuming a split
plane is beneficial. USB protection/shield currents need an explicit short
return strategy and must not traverse the ADC input/reference neighborhood.

## Critical geometries

1. Solve each receive AFE/filter/isolator pin group together, preserving both
   signal legs and actual part-body clearances.
2. Treat receive-owned ADC termination parts and ADC-owned reference/decoupling
   parts as a joint physical task. Logical ownership does not force colocation
   with the distant connector/AFE group.
3. Place the USB interface, its high-speed pair, clock source and core supply
   support as a coupled group with exact datasheet/reference-layout evidence.
4. Keep switching-power hot loops and USB/shield returns away from the analog
   reference/input neighborhoods while preserving continuous return paths.
5. Prove connector mate/cable/service access before fixing board dimensions.

## Admission and verification

Commission -> architecture -> sourcing -> fresh schematic review -> placement
P1/P2 -> local P3 route probes -> P4 joint proofs -> P5 independent integrated
placement review -> full routing -> layout verification/seal. Sol owns bounded
engineering tasks; the coordinator reopens actual output evidence. Research,
a completed agent report and successful tool qualification do not close any
board engineering gate.

Hardware freeze requires the documented software capability, flash protocol,
port mapping and programming interface described in BRIEF D2. Firmware
authoring remains forbidden; a future board-specific image is explicitly owed.
Hardware design may continue, but neither a working USB capture path nor a
programmed board is claimed.

## Research disposition

[USB IC research](research/2026-09-22-usb-ic-research.md) favors XU316 over the
older XU208 and the less-accessible CM6637 production path. The
[requirements delta](research/2026-09-22-crow-requirements.md) identifies which
MCH-specific circuits disappear and which analog sequencing functions remain.
[Coordinator disposition](research/2026-09-22-research-disposition.md) records
claim limits and corrections. Source adoption is now being prepared; none of
these reports supplies a completed schematic or board.

## Digital power-state repair candidate (2026-09-22)

This source candidate makes the six required power states explicit at pins. It is a
reviewable circuit delta, not a routed-board, firmware, USB-compliance, or first-article
acceptance result.

| State | Hardware path and resulting state |
|---|---|
| carrier absent, VBUS absent | 1V8/0V9/3V3X and 3V3_ADC are absent. The rail-less USB protectors do not provide a carrier supply path. `R_USB_VBUS_BLEED` discharges connector VBUS. |
| carrier absent, VBUS present | VBUS reaches only rail-less `U_USB_VBUS_ESD`, `C_USB_VBUS`, the 47k bleeder, and the 100k/1M gate divider of AO3400A `Q_VBUS`; the insulated gate cannot source the unpowered 1V8 rail. No intentional VBUS-to-carrier power path exists. |
| carrier present, VBUS absent | `Q_VBUS` is off and `R_VBUS_PU` reports `VBUS_PRESENT_N=1` in the 1V8 domain. Board firmware must interpret this inversion and keep the USB D+/D- pullups detached. |
| carrier and VBUS present | `Q_VBUS` reports `VBUS_PRESENT_N=0`. Firmware may attach only after XU and ADC startup sequencing completes; hardware alone does not claim enumeration. |
| digital brownout while 3V3_ADC is held | `U_ADC_1V8_OK` and `U_ADC_3V3X_OK` form wired-open-drain `ADC_DIGITAL_OK`. Either rail loss disables held-domain `U_ADC_CLOCK_OK`; its output pulldown turns off the two AO3400A open-drain enable sinks, so the local 1V8/3V3X pullups disable TDM/MCLK drive. `U_ADC_DIGITAL_BAD` plus `Q_ADC_DIG_RST` holds `ADC_RESET_N` low. The held `U_ADC_OUT` inputs are defined by 100k pulls at `ADC_MCLK_RAW`, `ADC_BCLK_RAW`, and the actual post-OR `ADC_FSYNC_EXT` pin. |
| VBUS removed/reapplied with carrier stable | The 47k bleeder discharges the required connector-side capacitor. Firmware must treat low-to-high `VBUS_PRESENT_N` as detach immediately and may reattach only on the opposite transition after its debounce/validity policy. |

`U_XU_3V3_OK` adds 3V3X to the wired-open-drain `XU_RESET_N` qualification.
The existing 1V8 supervisor delays `CORE_EN`; therefore core-valid reset release occurs
after 1V8 and flash power are established. With the 10nF CT capacitor screened at
7.65nF (nominal 10nF, -10% tolerance, -15% X7R temperature allocation), TPS3890
`VCT(min)=1.17V` and `ICT(max)=1.35uA` give 6.63ms minimum before core enable,
which exceeds the XU316 flash-readiness requirement of 300us by 22.1x before adding
core ramp and the TPS3808 reset delay. The added 3V3X supervisor's exact 1nF C0G
part gives at least 0.823ms from its 5% low capacitor corner using the same TPS3890
limits. These are component-bound source calculations; rail ramps still require a saved
PCB and first-article measurement.

The CS5308 sequence remains hardware-owned. `U_ADC_READY` qualifies the push-pull
120-350ms `POR_N` result with wired-open-drain `ADC_DIGITAL_OK` in the held domain.
On readiness, the invalid-state clamp releases `ADC_RESET_N` high. A 100k/470nF
Schmitt-input delay then triggers `U_RST2`, and `Q_RST1` produces the required second
active-low interval. Conservative selected-part corners give 9.1ms for the initial-high
interval: fastest -1% R/-10% C, an actively discharged 0V start, the 0.8V guaranteed-low
boundary as the earliest possible trigger, 3.6V supply, and 5uA leakage toward the input.
The 100k/220nF pulse network has a 19.6ms engineering lower bound by scaling TI's
guaranteed 1.0ms minimum at 10k/0.1uF by the selected -1%/-10% RC product; TI's
log-log curves show proportional pulse duration over the selected range. These are
documented engineering bounds rather than manufacturer guarantees for arbitrary RC.

`C_USB_VBUS` is exact GCM21BR71C475KA73L, 4.7uF +/-10%, 16V X7R, 0805. Its Murata
typical curves are conservatively screened at 36% combined DC/AC retention, then
charged the full -10% tolerance, -15% temperature and a separate -10% lifecycle
reserve. The resulting 1.165uF low estimate and 5.946uF no-bias high corner remain
within the XU316 self-powered reference's 1-10uF interval. At the high corner and +1% 47k bleeder,
the conservative VBUS discharge time constant is 282ms; decay from 5.25V to 0.8V is
530ms. The AO3400A sense remains intentionally inverted. Its 100k/1M divider gives at
least 4.32V gate drive at the 4.75V USB valid floor and the exact device guarantees
48mohm maximum at 2.5V gate drive. Host-source impedance and the actual detach threshold must be captured
on first article; no USB compliance conclusion is inferred from the calculation.

The JTAG header VREF is 1V8. Only a probe that senses 1.8V VREF, level-adapts TCK/TMS/TDI,
does not source an unpowered target, and treats `XU_RESET_N` as an open-drain target
reset is supported. Firmware remains separately owned: it must configure X0D14/pin 8
for the active-low VBUS indication and configure `lib_xud` to remove D+/D- pullups whenever
VBUS is absent. No firmware image is created or implied here.
