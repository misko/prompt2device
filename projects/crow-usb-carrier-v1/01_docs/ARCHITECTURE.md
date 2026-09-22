# Crow USB carrier architecture — commissioning draft

Status: candidate architecture. No IC, pin map, rail setpoint, stackup or source
rule has been frozen. The commissioning hold remains active.

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
Exact bridge core/I/O rails and power-up requirements depend on IC selection.
Existing analog quiet-start, hold-up and disconnect circuits are evidence to
review, not a preapproved circuit copied into this board.

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
- USB device link: exact electrical implementation and USB speed/class are under
  research; no GPIO bit-banging or external converter is an accepted substitute.
- Power/protection/control: source rules will replace the scaffold examples once
  the input envelope and part selection are admitted.

## Data and clock budget

The retained audio payload is 8 × 48,000 × 24 = 9,216,000 bits/s before USB
protocol overhead. With four-byte sample containers it is 12,288,000 bits/s.
The synchronous TDM link is 8 × 32 × 48,000 = 12.288 MHz. Matching those rates
alone is insufficient: exact frame-sync polarity/width, data alignment, launch
edge, receiver setup/hold and master-clock relationship must match both ICs.
The USB research task must verify endpoint capacity and clock-domain handling.

## Stackup

A continuous-reference multilayer board is the starting point. Layer count is
not frozen; prove exact package escape and controlled-impedance manufacture
before committing to it. No old PCB outline, hole position, layer choice or
learned via/copper arrangement has been imported as a hard constraint.

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

Firmware, USB identity/configuration and host compatibility must be resolved
before freezing the interface IC. Existing firmware authoring remains forbidden
pending the user's answer; the hardware design cannot claim a working USB path
while an indispensable software dependency is unowned.
