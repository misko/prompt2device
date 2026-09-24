# XU VDDIO17 and PLL supply/return acceptance contract

## Scope and source record

This note defines the evidence boundary for `C_XU_VDDIO_17` at `U_XU.17`
(`VDDIOL`) and the adjacent PLL filter. It does not approve a placement,
route, first article, release, or order.

The retained primary source is XMOS **XM-014532-PC v2.0.0, xcore.ai
Datasheet XU316-1024-TQ128**, Sections 7.3 and 14, Appendix I §§I.2--I.3;
local file `02_parts/XU316-1024-TQ128-C24/XM-014532-PC-v2.0.0.pdf`,
SHA-256 `a2ce2dc835df06793a4e1aa6c5d226c6a01c25c979a63b09a2b57059c17321cf`.
Relevant printed-PDF locations are pp. 29--34 (integration), p. 31
(operating conditions), and pp. 94--97 (checklist/layout).

## Manufacturer facts

- `U_XU.17` is `VDDIOL`, the left digital-I/O supply. In the selected design
  it is `N1V8`; `LV_L_N` must be grounded when VDDIOL is at 1.8 V.
- VDDIO supplies require several low-inductance 100 nF MLCCs close to the
  chip; XMOS gives one 100 nF 0402 MLCC on each supply pin as an example.
  The ground side of every decoupler must have as short a path as possible
  to GND pins, and Appendix I says it needs a direct path to the device
  centre ground.
- A bulk capacitor of at least 10 uF is required on the VDD and VDDIO
  supplies.
- The manufacturer operating range for 1.8-V-nominal VDDIOL is **1.62 to
  1.98 V**. The project's 1.70--1.95 V record is a project derating; it is
  not a manufacturer limit.
- `PLL_AVDD` is specified at **0.855 to 0.945 V**. It must be separated
  from noisier board supplies. XMOS recommends a low-pass filter, for
  example a 1 uF MLCC and a 600-ohm-at-100-MHz, DCR-under-1-ohm ferrite;
  Appendix I requires the PLL filter capacitor close to `PLL_AVDD`.

XMOS does **not** publish a capacitor-to-pin maximum distance, a permitted
ground-via count, a loop-inductance limit, or a ripple limit for this
placement. None is introduced by this note.

## Project-owned acceptance contract

All geometry evidence below must come from a single exact-hash, saved native
board after zone refill. A placement-only artifact cannot close any row.

| Gate | Required evidence and pass condition |
|---|---|
| Identity | Netlist/schematic prove `C_XU_VDDIO_17` is a fitted 100 nF capacitor from `N1V8` to `GND`, `U_XU.17=VDDIOL=N1V8`, and `LV_L_N=GND`. |
| Bulk ownership | The `N1V8` VDDIO bulk capacitor(s) are named, connected to the same supply, and have retained value/effective-capacitance evidence showing the XMOS >=10 uF requirement is met. This is distinct from the local 100 nF requirement. |
| Supply path | Native-board extraction and render identify a continuous copper path from `C_XU_VDDIO_17.1` to `U_XU.17`; DRC has no relevant unconnected-item finding. Archive the complete segment/via/layer inventory and measured path length. |
| Ground return | Native-board extraction and render identify the return from `C_XU_VDDIO_17.2` to a U_XU centre-ground/ground-pin connection. Archive every segment, via, layer, filled-zone connection, and measured path length. A zone-presence sample alone does not pass. |
| Qualitative layout disposition | An independent reviewer examines the archived paths against XMOS's qualitative "close" and "direct/short to centre ground" requirements. The review records the measured geometry but does not convert it into an unsourced millimetre, via-count, or impedance threshold. |
| Reference integrity | Filled-board evidence shows continuous GND reference under the nearby TDM/fanout paths and no disconnected island or reference void relied on by the C17 supply/return path. |
| PLL companion | The exact board identifies `FB_PLL`, `C_PLL_1U`, `C_PLL_100N`, `U_XU.41=PLL_AVDD`, and `U_XU.42=PLL_AGND`; it archives their complete filter/supply/ground paths, a qualitative local/isolation review, and separate >=10-uF bulk ownership. |

## First-article validation after design release

Use a documented low-inductance probe method and preserve raw waveforms,
probe reference location, bandwidth setting, load/firmware state, temperature,
and supply conditions.

1. At `U_XU.17`, measure VDDIOL relative to a local U_XU ground reference
   during monotonic power-up, reset release, and the worst credible USB-audio
   / I/O switching workload. The observed extrema must remain within the
   XMOS 1.62--1.98 V operating range. A stricter 1.70--1.95 V result may be
   required only as an explicitly project-owned derating.
2. Verify VDDIOL is valid before reset release, as required for the boot-pin
   domain. Retain the reset and rail waveforms together.
3. At `U_XU.41`, measure PLL_AVDD relative to `U_XU.42` through the same
   applicable states. Observed extrema must remain within 0.855--0.945 V.
   Review the waveform for the effect of the actual PLL filter and noisy-board
   activity; no unsourced ripple number is asserted here.
4. Record any departure from the qualitative path review or waveform limits
   as a first-article/production acceptance blocker until corrected or
   governed by an explicitly project-owned disposition.

## SOL isolated-fanout probe disposition

`/tmp/crow-xu-fanouts-sol/04_kicad/crow_carrier.kicad_pcb`, SHA-256
`6f7c77fbf9a815f1596b6dd5285526df8adfd027f62f110af1c82f52b7a6ff34`, is not
admitted as a decoupler, power, ground-return, or PLL placement result.

The probe moves `C_XU_VDDIO_17` so its supply-pad centre to `U_XU.17` centre
is 3.9814 mm, versus 2.5162 mm before. That observation neither passes nor
fails an XMOS distance requirement because XMOS gives no such numerical
limit. More decisively, the native board contains zero `N1V8` tracks and zero
`PLL_0V9` tracks, so it supplies no copper-path proof for C17 or the PLL
filter. Its GND-zone sampling is not a demonstrated C17-pad-to-device-ground
return. `C_PLL_1U` at 6.1604 mm from `PLL_AVDD` likewise lacks filter and
return evidence.

The probe may be retained only as narrow, noncanonical diagnostic evidence:
three dangling TDM strips cleared native copper/width/courtyard checks, and
a separate MCLK strip left only a 0.040-mm lateral gap beside the moved C17.
That is not an assembly margin, a route, an endpoint allocation, a return
proof, or a basis for adopting any of its four component coordinates.
