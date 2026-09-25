# XMOS XU316 public USB-protection reference topology

**Research evidence only.** The following is newly inspected public XMOS
schematic evidence. It neither changes Crow's selected TI protector nor
qualifies a powered or rail-off Crow assembly.

## XK-EVK-XU316: named USB protection part

XMOS's [xcore.ai Explorer v2 hardware manual](https://www.xmos.com/file/xcore_ai-evaluation-kit-v2_0-hardware-manual?version=latest),
Figure 16, `MIPI_USB.SchDoc` (schematic page 20 in the PDF), shows the
micro-USB `J3` (`10118193`) and `D1 NUP4114`. The sheet labels the data nets
`USB_D_P` and `USB_D_N`, connects them to the XU316-1024-FB265-C32 USB pins
`USB_DP`/`USB_DM` (U14/U13), and shows `NUP4114` pins on those two nets plus
`USB_VBUS` and `GND`. This is an explicit XMOS reference-board shunt-protector
topology, with the named device MPN `NUP4114`.

It is not a self-powered rail-off example: the same manual §3.1 and §4.3 say
that J3 supplies board power and that its 5 V is converted by on-board
regulators. It consequently offers no evidence for an unpowered-XU316
USB-pad limit, injection current, or clamp waveform.

## XK-AUDIO-316-MC-AB: self-powered functional arrangement

XMOS's [xcore.ai Multichannel Audio Platform hardware manual](https://www.xmos.com/file/xcore_ai-multichannel-audio-platform-1v1-hardware-manual/?version=latest),
Figure 10 (`Top Level.SchDoc`, schematic sheet 1 of 8), names `NUP4114` in
the USB-device sheet with the XU316-1024-TQ128-C24 USB DP/DM nets. The same
official manual's **USB Device** section states that the board supports bus-
or self-powered operation: self-powered mode uses J22 `PWR SRC` at `EXT` and
fits J14 `VBUS DET`; the documented bipolar-transistor VBUS-detect circuit
then disables the D+ pull-up when the host is unpowered.

This establishes an XMOS self-powered *functional* topology and the presence
of the named NUP4114 protector. It does **not** state the NUP4114 ordering
suffix/BOM row, its measured powered or rail-off DP/DM clamp voltage/current,
USB-pad injection behavior, board ESD test levels, probe point, cable or
return configuration, or a qualification result. The VBUS-detect/pull-up
requirement is not a DP/DM ESD-stress limit.

## Disposition for Crow

The records support retaining a grounded USB protection topology as a
reference pattern. They supply no numerical or state-qualified
XU316 limit that can be compared to Crow's `TPD2EUSB30ADRTR`, and no evidence
that its behavior transfers to Crow's connector, trace, return, or rail-off
state. `USB-ESD-selection-transient` therefore remains prototype-only under
the existing exact-board test plan.
