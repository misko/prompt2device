# Crow USB modular placement plan adoption

The authored plan is [modular_plan.json](../../03_src/modular_plan.json).
The independent checker confirms422/422componentownershipand53/53crossingnets
against current electrical Circuit JSON. It is an architecture-stage plan;
all16workitems remain placement-stage tasks, with no completed observations.
No child is admitted until the parent lifecycle and engineering prerequisites pass.

## Functional ownership

| Block | Components |
|---|---:|
| adc_reference | 41 |
| analog_ch1 | 27 |
| analog_ch2 | 27 |
| analog_ch3 | 27 |
| analog_ch4 | 27 |
| analog_ch5 | 27 |
| analog_ch6 | 27 |
| analog_ch7 | 27 |
| analog_ch8 | 27 |
| audio_clock_tdm | 33 |
| clock_flash_debug | 8 |
| debug_connector | 1 |
| digital_power | 27 |
| input_buck | 17 |
| quiet_power | 40 |
| usb_frontend | 6 |
| usb_vbus_sense | 4 |
| xmos_core | 29 |

## Work sequence

```mermaid
flowchart LR
  P1["P1: floorplan and corridors"] --> P2["P2: coupled block placement"]
  P2 --> P3["P3: critical local route proofs"]
  P3 --> P4["P4: analog, USB/digital and power-return joint proofs"]
  P4 --> P5["P5: integrated independent placement review"]
  P3 -. local failure .-> P2
  P4 -. return-path or corridor conflict .-> P1
  P5 -. failed coupled proof .-> P4
```

The graph above summarizes the exact dependencies in the JSON. P2 contains
seven scopes; P3 has power-loop, analog-handoff, timing/boot and USB-pair scopes.
The eight channel blocks remain electrically separate, while analog joint
proof includes the shared ADC/reference owner and quiet supply. USB routing
shares one proof corridor with the XMOS core and protection, and the USB/digital
joint proof also depends on the local power-loop proof. Ground crossings do
not merge these ownership blocks.

The coordinator corrected the trial path to the contract-owned JSON filename,
removed a stray BGA reference for the TQFP part, and added floorplan/ADC/digital
power backtrack targets for global return-path failures. All rows allow at most
two attempts before their recorded backward targets must be used. Work delivery
and this coverage pass never establish physical placement or routing success.
