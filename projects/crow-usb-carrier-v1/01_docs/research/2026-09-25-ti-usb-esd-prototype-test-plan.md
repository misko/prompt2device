# Crow USB ESD engineering prototype test plan

**Planning record only. No board has been fabricated or tested, and this record
does not qualify the XU316 or authorize an order.** The subject is the exact
Crow source with `U_USB_ESD = TPD2EUSB30ADRTR / C94934`, J_USB to TI D+/D−
pins 1/2 and TI pin 3 to local ground, continuing to XU316 TQ128 USB_DP/DM
pins 60/59. A source, footprint, return-path, or device change requires a new
plan/review. The retained TI `SLVSAC2G` and XMOS `XM-014532-PC v2.0.0`
datasheets in `02_parts/` are the component evidence; the independent
assessment is `08_reviews/2026-09-25_ti-usb-esd-prototype-only_terra.md`.

## Before a test article is ordered

The electrical owner must approve the exact assembled board revision, USB
cable/host fixture, connector shell and ground return arrangement, discharge
points, contact/air method, polarity, target level, number of strikes, and
acceptance criterion. Record the laboratory's applicable IEC 61000-4-2 setup
and calibration. Component-level 8-kV contact performance from TI is a
screening fact, **not** the board target or a board result. Start no test if
these parameters or a safe instrumentation setup remain unspecified. The
prototype-order decision is separate from this source design decision.

## Measurements and matrix

For each approved level and both polarities, test at least these operating
states: USB/carrier powered with enumeration active; USB cable attached with
carrier rail off; carrier powered with USB VBUS absent; and both domains off.
Capture the exact board revision, probe location and bandwidth, XU-side DP and
DM waveforms relative to local XU ground, USB_VDD33 and USB_VDD18 behavior,
and the TI return-path voltage/geometry. Record whether any protective current
enters supply rails during powered or rail-off strikes. Repeat baseline and
post-strike checks for USB enumeration, audio data transfer, reset/recovery,
rail leakage/current and visible damage; preserve raw waveforms and logs.

The test owner must define a stop condition before exposure. Any latch-up,
uncommanded rail rise, loss of enumeration, excess leakage, damage, or inability
to observe the XU-side stress ends that branch and leaves the release finding
open. Passing functional checks at a particular setup supports only that
bounded empirical result. It does not establish an unpublished XU316 USB-pad
absolute transient limit or transfer to another routing, enclosure, cable,
ground return, or ESD level.

## Release decision

`USB-ESD-selection-transient` stays open until an independent reviewer checks
public XMOS limits or exact-board measurements against a stated product target
and records a hash-bound decision. If the limit remains unavailable, the
reviewer must explicitly state what empirical system-level claim, if any, the
test data supports and whether residual silicon stress uncertainty is
acceptable for that target. A failure requires changing protection or layout
and retesting the new exact subject. No prototype-only source gate can close
this finding or make the board orderable.
