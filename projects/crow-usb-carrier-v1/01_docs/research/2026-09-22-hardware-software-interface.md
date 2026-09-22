# Crow USB hardware/software interface

Hardware contract reviewed against the corrected authored source on 2026-09-22.
This supersedes the provisional 3.3 V I/O and obsolete flash proposals in the
early XU316 research report. It is not firmware, a tested image, or a native
schematic acceptance record. BRIEF D2 governs the hardware-only scope.

## Host and stream

The Raspberry Pi is the USB host; the independently powered carrier is a
USB 2.0 high-speed device using XU316-1024-TQ128-C24. Intended software is an
eight-input, zero-output UAC2 interface at 48 kHz, with 24 meaningful bits per
sample. The implementation path is XMOS lib_xua/lib_i2s and the Pi Linux
snd-usb-audio class driver. No board-specific executable image exists yet.

USB D- and D+ connect to physical XU pins 59 and 60. VBUS supplies sensing
only through an insulated-gate AO3400A open-drain detector; X0D14/pin 8 receives
active-low `VBUS_PRESENT_N`. Future firmware must configure the sense polarity
and lib_xud attachment behavior: powered local rails alone must not cause
attachment when VBUS is absent.

## Current signal allocation

All XU GPIO supply banks are 1.8 V; selectors 40, 43 and 52 are grounded.
The USB PHY has separate 3V3X and 1V8 supplies. Level translation separates
the XU audio pins from the ADC-side 3.3 V logic.

| Function | XU physical pin | Port identity | XU-side net/direction |
|---|---:|---|---|
| Audio master clock | 23 | X1D11 / tile 1 P1D0 | AUDIO_MCLK_1V8, input |
| Frame sync | 20 | X1D01 / tile 1 P1B0 | TDM_FSYNC_1V8, output |
| Bit clock | 22 | X1D10 / tile 1 P1C0 | TDM_BCLK_1V8, output |
| ADC data | 107 | X1D24 / tile 1 P1I0 | TDM_DATA_1V8, input |

The local 24.576 MHz oscillator is the audio reference. Eight 32-bit slots
at 48 kHz require a 12.288 MHz BCLK. The future TDM configuration must match
CS5308P hardware-mode channel/slot selection and its one-bit frame offset.
The source extends the raw FSYNC trailing edge through two flip-flops and
an OR gate; therefore the actual ADC pin pulse is not the raw one-BCLK
firmware pulse. Validate the realized frame edge, pulse width, setup/hold,
slot order and all 24 meaningful sample bits before functional acceptance.

Hardware qualifies the clock-output enables with ADC quiet-power validity and
1V8/3V3X digital-rail validity. Firmware must treat clock availability and USB
attachment as separate conditions. On initial power and any qualified restart,
hardware gives the CS5308P at least a 9.1 ms engineering-bounded high interval,
then at least a 19.6 ms engineering-bounded low pulse before final reset release.

## Boot and programming

The selected flash is W25Q128JWSIQ, a 128-Mbit (16-MiB) fixed-QE device
powered from 1V8. Its 24-bit address range is 0x000000-0xFFFFFF and matches the
XU316 ROM boot range. ROM-fixed QSPI connections are CS_N=X0D01/pin 2, CLK=X0D10/pin 4, D0=X0D04/pin 127,
D1=X0D05/pin 128, D2=X0D06/pin 1 and D3=X0D07/pin 3. Preserve normal
power-on QSPI boot compatibility and flash readiness before reset release;
do not leave the flash in a mode the ROM cannot read.

`J_JTAG` uses the keyed FTSH-105-01-L-DV-K header. Its pins are 1=1V8 VREF,
2=TMS, 3=GND, 4=TCK, 5=GND, 6=TDO, 7=NC/key, 8=TDI, 9=GND,
10=XU_RESET_N. XU pins are TDI=36, TDO=37, TMS=44, TCK=51, reset=38.
A programming probe/adapter must explicitly match this pinout, sense VREF,
adapt to 1.8 V, avoid driving an unpowered target, and use open-drain reset.
The connector shape alone does not establish XTAG cable compatibility.

The later authorized firmware work must supply the board XN/resource map,
USB identity/descriptors, port and clock bindings, TDM format, active-low
VBUS handling, reset/power recovery behavior, image and programming recipe.
Programming/recovery must work through this header without a previously
working USB image. Firmware authoring/build, enumeration and capture have
not been performed.

## Evidence boundary

Pin/net assignments and power-state behavior were read from the corrected
authored TSX. Primary pin/boot authority is the retained XU316 XM-014532-PC
v2.0.0 PDF; audio format authority is CS5308P DS1314F1 and the retained XMOS
library research. Native schematic parity and actual USB/audio behavior remain
separate verification steps.
