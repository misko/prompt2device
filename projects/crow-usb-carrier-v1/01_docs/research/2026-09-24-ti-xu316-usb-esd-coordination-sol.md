# Crow D13: TI USB TVS versus XU316 transient coordination

**Research only, 2026-09-24.** Subject: Crow's selected `TPD2EUSB30ADRTR`
on USB D+/D−, followed by XU316-1024-TQ128-C24 USB_DP/USB_DM pins 60/59.
This does not change the selection, qualify an assembled board, or close
`USB-ESD-selection-transient`.

## Published limits and the calculation

The [TI SLVSAC2G Rev. G datasheet](https://www.ti.com/lit/ds/symlink/tpd2eusb30a.pdf),
§§6.1, 6.3, 6.5, 9–10, specifies the **A** device's normal operating
range as 0–3.6 V, its IO absolute maximum as 0–4 V, breakdown **minimum**
4.5 V at 1 mA, and positive clamp **maximum** 8 V at 1 A. The 0.6 Ω dynamic
resistance is typical, not a worst-case pulse model. The lower clamp diode
is 0.6–0.95 V at 8 mA. TI rates the *component* for IEC 61000-4-2 8-kV
contact and 5-A 8/20-µs surge; its passive clamp needs no rail. TI's
connector-adjacent and low-impedance-GND layout advice still applies.

The [XMOS XU316 TQ128 v2.0.0 datasheet](https://www.xmos.com/documentation/XM-014532-PC/html/rst/XU316-1024-TQ128.html),
§§4.6, 11, 15.1–15.2, identifies the USB pads and specifies USB_VDD33's
**operating** range as 3.00–3.60 V. Its general IO absolute maximum is
`−0.5 V ≤ V(Vin) ≤ VDDIO + 0.5 V`, but the USB pads are PHY IO rather than
identified GPIO-bank pins. XMOS does not identify which rail, if any, sets
this USB-pad limit, or publish a USB-pad pulse-voltage, injection-current,
or unpowered tolerance envelope. The 2-kV HBM / 500-V CDM *handling*
ratings in §15.5 are not system IEC limits. XMOS says extra components may
be required for USB EMC/ESD. Its self-powered VBUS transient divider in §11.1
protects the **VBUS-sense GPIO** and supplies no DP/DM limit.

Even under the optimistic *assumption* that a 3.3-V VDDIO bank's general IO
limit applies to USB_DP/DM, the highest published powered rail maximum gives
`3.63 + 0.5 = 4.13 V`; TI permits `8 − 4.13 = 3.87 V` more at its 1-A
clamp test point. With that rail off, the conditional ceiling is `0 + 0.5 =
0.5 V`, a `7.5 V` difference. Using USB_VDD33's 3.60-V operating maximum
as a USB *pin* absolute limit would be unjustified. These differences are a
**proof gap, not measured XU overstress**: the 8-V value is at the TVS pin
and one specified current, whereas the XU pin depends on current sharing,
trace/return inductance, and pulse shape. For scale, just 1 nH of common
return inductance at 1 A/ns contributes `L·di/dt = 1 V`; neither that
inductance nor slew is a measured Crow value. The 8-V maximum cannot bound
an IEC pulse at all currents or the XU rail response. Rail-off is especially
unresolved because the TVS remains passive while XU internal pad injection
and back-power behavior are unpublished.

## Closure path

No public primary record found here supports a design-clean claim for this
exact TI–XU pair. A calculable design closure needs XMOS's USB_DP/DM limits
for both powered and unpowered states (positive/negative pulse voltage versus
duration, injection current/charge, and rail behavior), plus a bounded TVS
and exact-board interconnect/return model for the selected stress. Only then
could the worst XU-pad waveform and rail currents be compared to XMOS's
limits. A generic GPIO AMR, TI's component IEC rating, or a typical TVS
resistance cannot substitute for those bounds.

The bounded empirical alternative is the existing
[exact-board prototype test plan](2026-09-25-ti-usb-esd-prototype-test-plan.md):
an electrical owner first fixes board revision, cable/enclosure/return,
discharge locations, IEC method, levels, polarity, strike count, and pass/stop
criteria. Instrument both XU-side DP/DM pins relative to nearby XU ground
with a probe whose bandwidth/loading and connection are documented; capture
USB_VDD33, USB_VDD18, other relevant rails, and TVS-ground bounce in
powered, VBUS-connected/rail-off, VBUS-absent/powered, and fully-off states.
Record raw waveforms, rail injection/back-power, pre/post leakage and USB
enumeration/data operation. A pass can support only the tested system-level
target and configuration; without an applicable XMOS USB-pad transient limit
or XMOS acceptance of the measured stresses, it cannot establish silicon
margin or close D13 by numerical coordination. A different TVS or routing
requires renewed analysis and testing.
