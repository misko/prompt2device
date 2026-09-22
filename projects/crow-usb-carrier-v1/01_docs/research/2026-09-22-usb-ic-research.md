# Crow USB audio bridge architecture research

Retrieved 2026-09-22 UTC. Scope is architecture and sourcing evidence only; no firmware was authored and no schematic or PCB source was changed.

## Recommendation

Use a bare **XMOS XU316-1024-TQ128-C24** as a self-powered USB 2.0 high-speed UAC2 capture device, with the XU316 as TDM controller (clock master) and the existing CS5308P as TDM target (secondary). Preserve one synchronous eight-channel stream, 48 kHz, 24 meaningful bits carried in eight 32-bit TDM slots. The concrete clock topology is:

```text
24 MHz system reference -> XU316 system clock
24.576 MHz low-jitter audio oscillator -> buffer -> CS5308P MCLK
                                        +--------> XU316 1-bit MCLK input
XU316 1-bit output -> buffered BCLK 12.288 MHz -> CS5308P ASP_BCLK
XU316 1-bit output -> buffered FSYNC 48 kHz -----> CS5308P ASP_FSYNC
CS5308P DOUT1 -> Ioff-capable buffer -> XU316 1-bit TDM data input
XU316 HS USB PHY D+/D- <-> USB-C device receptacle <-> Raspberry Pi 5 host
```

This recommendation has one explicit dependency: **a board-specific XMOS firmware build must be authorized before the schematic pinout can be frozen**. XMOS supplies current source and build-time configuration, but its precompiled images target XMOS boards. Crow needs its own XN port map, input-only 8-channel UAC2 descriptors, 48 kHz restriction, TDM settings, VID/PID, and hardware hooks. That is configuration plus a custom build and verification, even if application code changes stay small. It is not a no-firmware IC.

The XU316 choice is preferable because XMOS documents a current, source-available UAC2 stack, XU316 multichannel reference hardware, TDM controller support, Linux class compatibility, and a currently sourceable exact package. The alternative CM6637 has a plausible electrical datapath but does not remove the firmware dependency and lacks an evidenced public production supply/tooling path.

## Why high-speed USB is required

Eight channels at 48,000 samples/s and three payload bytes/sample require `8 * 48,000 * 3 = 1,152,000 bytes/s`, or **1,152 bytes per 1 ms USB full-speed frame**. If UAC2 exposes the normal four-byte subslot for 24 valid bits, it is `1,536 bytes/ms`. A full-speed isochronous transaction is limited to 1,023 payload bytes, so one ordinary audio-streaming IN endpoint cannot carry this stream at full speed. USB 2.0 high-speed divides time into 125 us microframes: the corresponding payload is 144 bytes/microframe packed or 192 bytes/microframe with four-byte subslots, comfortably below the 1,024-byte high-speed transaction size. The asynchronous feedback endpoint is additional but small.

Therefore the design requirement is **USB 2.0 high-speed UAC2**, not merely “USB 2.0 compatible.” The current [USB 2.0 specification landing page](https://www.usb.org/document-library/usb-20-specification) is the governing primary source; XMOS also states that UAC2 supports high-speed USB and documents the 1,024-byte HS packet constraint in [lib_xua channel-count guidance](https://www.xmos.com/documentation/XM-012296-UG/html/doc/rst/opt_channels.html). The 1,023-byte full-speed ceiling is from USB 2.0 endpoint rules; the arithmetic above is derived.

## Audio timing and CS5308P fit

At 48 kHz, eight 32-bit slots require `48,000 * 8 * 32 = 12.288 MHz` BCLK, exactly 256 Fs. The existing 24.576 MHz MCLK is 512 Fs and divides by two to BCLK. The [CS5308P datasheet](https://statics.cirrus.com/pubs/proDatasheet/CS5308P_DS1314F1.pdf), Table 4-13, specifies TDM minimum-time-slot mode at 44.1/48 kHz as one DOUT, eight slots, BCLK at least 256 Fs; its secondary-mode BCLK range includes 12.288 MHz. It also requires at least one BCLK-wide FSYNC pulse and allows the falling edge anywhere before the next frame provided it precedes the next rising edge by one BCLK. Channels 1–8 occupy slots 0–7.

XMOS [lib_xua TDM configuration](https://www.xmos.com/documentation/XM-012296-UG/html/doc/rst/opt_i2s.html) supports eight channels per data line, 32-bit words, XU as controller, and a one-bit data offset after frame sync. The lower-level [lib_i2s TDM documentation](https://www.xmos.com/documentation/XM-007055-UG/html/doc/rst/lib_i2s.html) exposes `CHANNELS_PER_FRAME`, `FSYNC_OFFSET`, and `FSYNC_LENGTH`, explicitly including the required offset 1 / length 1 form; it lists 12.288 MHz, eight slots, 48 kHz as a known-working TDM configuration. This is a strong paper match to the CS5308P timing diagrams, but it is not yet a captured waveform. Before source acceptance, a firmware timing proof must establish FSYNC polarity, one-BCLK pulse width, one-bit slot-0 offset, sampling/launch edges, and slots 0–7 channel identity. First article must confirm all eight impulses and retained 24 MSBs with a logic analyzer plus ALSA capture.

## Candidate comparison

| Candidate | Evidence for 8-channel USB capture | Firmware / license | Supply and assembly evidence observed 2026-09-22 | Decision |
|---|---|---|---|---|
| **XU316-1024-TQ128-C24**, exposed-pad TQFP-128 14 x 14 mm | Integrated USB 2.0 HS PHY; XMOS supports XU316 8-in/8-out hardware and TDM master/slave. Current `sw_usb_audio` 9.2.0 and `lib_xua` 5.5.0 support UAC2 asynchronous operation. | Board-specific build required. Source is under XMOS Public Licence v1: commercial use and derivatives are allowed on XMOS devices, with notices, license-copy and derivative/distribution obligations; compiled code supplied by XMOS may have separate terms. [License](https://github.com/xmos/sw_usb_audio/blob/develop/LICENSE.rst). | DigiKey listed active and stocked; Mouser listed stocked. XMOS identifies DigiKey and Mouser as global channels and announced Mouser as an authorized distributor. JLC lists exact part **C6362698** as extended, SMT-assemblable for economic/standard PCBA; current allocation must still be rechecked at order staging. [DigiKey](https://www.digikey.ie/en/products/detail/xmos/XU316-1024-TQ128-C24/17764326), [Mouser](https://www.mouser.in/en/ProductDetail/XMOS/XU316-1024-TQ128-C24?qs=ST9lo4GX8V1f%2F4v9zGd%252BXw%3D%3D), [JLC](https://jlcpcb.com/partdetail/XMOS-XU316_1024_TQ128C24/C6362698), [XMOS channel statement](https://www.xmos.com/xmos-announces-mouser-electronics-as-new-global-distributor). | **Preferred.** Best evidenced path and current software generation. Firmware authorization is a gate. |
| **XU208-256-TQ64-C10**, exposed-pad TQFP-64 10 x 10 mm | xcore-200 remains an orderable XMOS USB part and the XMOS stack supports xcore-200. | Same custom-build and XMOS license obligations; less RAM/compute and older platform. | DigiKey showed stock; Mouser listed the exact part but non-stocked/request quote. JLC/LCSC list **C2640016** as extended/assemblable but LCSC showed out of stock. [DigiKey](https://www.digikey.pl/pl/products/detail/xmos/XU208-256-TQ64-C10/5148722), [Mouser](https://www.mouser.com/en/ProductDetail/XMOS/XU208-256-TQ64-C10?qs=ST9lo4GX8V1sPpD5GG0Ubw%3D%3D), [JLC](https://jlcpcb.com/partdetail/XMOS-XU208_256_TQ64C10/C2640016). | **Do not select for this topology.** XMOS's current USB Audio guide records “input via TDM master unreliable due to low-level timing issues (xcore-200 only).” Changing the ADC into clock master would reopen the established clock architecture. [XMOS guide](https://www.xmos.com/file/sw_usb_audio-sw_usb_audio-design-guide). |
| **C-Media CM6637**, QFN-100 12 x 12 mm | Manufacturer datasheet specifies USB 2.0 HS/UAC2, an 8-channel TDM input, MCLK output, BCLK/FSYNC outputs, and 24/32-bit 48 kHz input support. Pins 42/43/44/45 are ADC MCLK/BCLK/FSYNC/data. | Not actually fixed function: it contains an 8051 and 512 KB flash. Manufacturer says USB topology is firmware-programmable and a blank device enumerates only as HID. Public datasheet does not provide a production image, programming tool/API, TDM mode-selection register map, or license terms. | No exact DigiKey, Mouser, LCSC, or JLC listing was found. Public route is C-Media sales contact. Authorized two-source availability and JLC feasibility are **UNKNOWN**. [CM6637 datasheet v1.30](https://www.cmedia.com.tw/storage/upload/sync_file/E02-0067%20CM6637_Datasheet_v1.30.pdf), [product page](https://www.cmedia.com.tw/tw/applications/headset/CM6637). | **Conditional fallback only** if C-Media supplies a licensed production image/configuration package, confirms mode/edge compatibility in writing, and names two authorized suppliers. It presently has more commercial/tooling uncertainty than XU316. |
| Other advertised fixed-function bridges (Savitech/Comtrue/etc.) | No current manufacturer-primary public evidence was found in the bounded search for an exact bare IC that simultaneously provides HS UAC2, eight synchronous capture channels, one-wire 8 x 32-bit TDM input at 48 kHz, production programming collateral, and traceable supply. | Unknown. | Unknown. | Not admissible without exact manufacturer documents and authorized sourcing evidence. |

The XMOS [multichannel platform](https://www.xmos.com/xk-audio-316-mc-ab) is useful reference evidence: it uses XU316-1024-TQ128-C24, supports more than 32 simultaneous USB channels, and publishes design files. It is not proposed as the deliverable; the user requested the IC on the Crow PCB.

## Required XU316 circuitry and pin budget

Use the exact commercial part **XU316-1024-TQ128-C24**. The [XU316 product-series datasheet](https://www.xmos.com/documentation/XM-015129-PC/html/rst/XU316-1024.html) specifies the integrated HS PHY, TQ128 package, external boot options, application PLL, and schematic checklist. Package-fixed USB pins are TQ128 pin 59 `USB_DM` and pin 60 `USB_DP`; `XIN`/`XOUT` are pins 34/33. The remaining audio port assignment must be selected from 1-bit ports on one tile and then frozen simultaneously in the schematic and the firmware XN file. Required logical roles are one MCLK input, one BCLK output, one FSYNC output, and one TDM data input. Guessing physical GPIOs before that co-design would create an unroutable or unbuildable firmware target.

Minimum support BOM/functions for the next electrical stage:

- XU316-1024-TQ128-C24 plus exposed-pad thermal/ground via field per manufacturer land pattern.
- External QSPI boot flash on the documented six-pin boot port, plus XTAG/JTAG programming/debug access and reset supervisor. Exact flash and supervisor MPNs remain to be selected against XMOS boot timing and JLC stock.
- 24 MHz system crystal/oscillator and its specified load/bias network.
- Dedicated digital rails derived from protected local 5 V: nominal 0.9 V core, 1.8 V USB analog, and 3.3 V digital/I/O, with PLL filtering, sequencing, and datasheet decoupling. Do not load the low-noise `3V3_ADC` rail with XU316 digital current. Exact regulator MPNs and the new 5 V allocation remain a power-tree calculation, because the XU316 datasheet's 203 mW active figure is typical, not a board maximum.
- One 24.576 MHz low-jitter oscillator for the only admitted 48 kHz family, fanned to CS5308P MCLK and the XU MCLK input. A 22.5792 MHz source and selector are unnecessary unless 44.1 kHz-family support is later required. The XU316 application PLL is a lower-BOM alternative, but XMOS states its jitter is worse than an external clock-generator option; audio performance must choose this deliberately. [XMOS clock discussion](https://www.xmos.com/documentation/XM-008854-UG/html/doc/rst/app_316_mc.html).
- Retain or reselect Ioff-capable clock/data buffers between the noisy digital domain and `3V3_ADC`, with enables gated by both relevant power-good/reset states. Add source damping only after edge-rate/SI review.
- USB-C USB2-only receptacle wired as device/UFP, two independent 5.1 kOhm Rd resistors on CC1/CC2, low-capacitance D+/D- ESD protection, controlled 90-ohm differential routing, VBUS sense, shield/chassis treatment, and no SuperSpeed pairs. The Pi remains host.
- USB descriptor identity in flash, a reproducible programming image, programming fixture/path, and recovery path. OTP locking is not required for first article.

## USB and independent-power-state contract

The Crow carrier remains powered from its protected isolated 12 V input. USB VBUS is used for attach detection only; it must not feed the carrier's 5 V or audio rails. XMOS explicitly requires a self-powered design to detect VBUS so the device removes its D+/D- pull-up behavior when VBUS is absent (“USB Back Voltage Test”). The four states to design and test are:

| Carrier 12 V | Pi / USB VBUS | Required behavior |
|---|---|---|
| off | off | All interfaces unpowered/Hi-Z. |
| on | off | Local audio/digital rails may be alive, but USB must appear detached and must not drive D+/D-. TDM clocks should be disabled or held in a defined reset state until the bridge and ADC rails are valid. |
| off | on | No powering of XU316, ADC, or 12 V tree through VBUS, D+/D-, CC, TDM, or protection parts. Only a bounded VBUS-sense path may draw current. |
| on | on | Enumerate as one HS UAC2 capture device; then enable the 24.576/12.288/0.048 MHz clock tree and stream eight synchronous channels. |

The existing MCHStreamer-specific presence-sense behavior cannot simply be renamed. Replace it with VBUS-present plus local power-good/reset logic, and measure leakage/current in all four states.

## Linux / Raspberry Pi host behavior

A standards-conformant UAC2 device should bind to Linux `snd-usb-audio` without a vendor driver. The current [Linux ALSA driver guide](https://cdn.kernel.org/doc/html/latest/sound/alsa-configuration.html) explicitly documents `snd-usb-audio` and UAC2 automatic clock selection; XMOS states that current Linux distributions support UAC1/UAC2 without extra drivers in its [driver support page](https://www.xmos.com/software/usb-audio/driver-support/). This is class compatibility evidence, not proof of this future descriptor set. Acceptance must include `lsusb -t` showing `480M`, `arecord -l`, `arecord --dump-hw-params`, sustained 8-channel `S24_3LE` or `S32_LE` capture as actually advertised, no xruns, and channel impulse mapping against `crow-carrier-channel-map-20260912`.

## VID/PID and product obligations

Do not ship with XMOS's example VID `0x20B1` or any copied development-board PID. XMOS's lib_xua documentation says no VID may be used without express permission. The product owner must either obtain its own USB-IF VID or obtain written sublicense/assignment authority from a party whose VID permits this product, then allocate a unique PID and stable product/serial strings. USB-IF says a VID is assigned to one company for exclusive use and unauthorized use of assigned or unassigned VID/PIDs is prohibited; its current VID-only fee is US$6,000. Logo use is a separate license/compliance matter. [USB-IF VID rules](https://www.usb.org/getting-vendor-id), [XMOS VID warning](https://www.xmos.com/documentation/XM-012296-UG/pdf/lib_xua_v5.4.0.pdf).

## Gates and unresolved facts before schematic freeze

1. Obtain user authorization for the firmware workstream, or obtain a vendor-supplied, licensed, exact production image. Without one of those, no candidate can satisfy the USB request as a populated bare IC.
2. Prototype the XU316 timing on an XK-AUDIO-316-MC or XU316 evaluation setup: 8 capture-only channels, 48 kHz, 32-bit TDM slots, offset 1, FSYNC length 1, XU controller. Capture BCLK/FSYNC/DOUT and compare to CS5308P setup/hold and channel timing.
3. Freeze XU one-bit port pins and the `.xn` map together; then verify TQ128 port/resource conflicts, boot pins, JTAG, and USB pins.
4. Re-budget protected 5 V and thermal load using a measured/qualified XU316 application configuration. The inherited 300 mA local-5-V allocation is not evidence that the added USB subsystem fits.
5. Select exact oscillator, QSPI, regulators, reset, USB-C, ESD, and buffer MPNs with manufacturer data plus two authorized-source checks. Only the bridge IC itself was sourced in this spike.
6. Acquire a lawful VID/PID plan before a distributable firmware image is sealed.
7. Treat JLC catalog presence as feasibility only. Recheck live stock, package/land pattern, assembly tier, MSL handling, and economics at release staging.

### Honest unknowns

- Whether the user will authorize the necessary board-specific firmware build.
- Exact XU316 1-bit port/pin assignment and whether the current Crow outline can route TQFP-128 USB, QSPI, clocks, and power without degrading the analog placement.
- Maximum subsystem current and revised 5 V margin; only typical silicon power is public in the evidence reviewed.
- Whether XU316's application PLL alone meets Crow's ADC jitter/noise target; an external 24.576 MHz oscillator is recommended pending measurement.
- CM6637 production firmware access, license/NRE, programming flow, precise TDM mode/edge configuration, two authorized suppliers, and JLC assembly availability.
- Final UAC2 sample subslot format (`S24_3LE` versus 24 valid bits in `S32_LE`); choose and test it in the descriptor build rather than assuming ALSA presentation.

The architecture is therefore **selected for continued design as XU316, conditional on firmware authorization and timing/power proof**. It is not ready for schematic acceptance, layout, release, or order.
