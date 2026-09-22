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
The digital source candidate uses 0.9 V core, 1.8 V on every XU316 I/O bank, and
separate 3.3 V USB/audio support power. The repaired 5 V input supply candidate
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
