# PESD2USB5UX-T / XU316 USB transient screen — HOLD

**Scope.** Independent source-stage screen of `U_USB_ESD` only. This note does
not qualify the Crow board, connector, return geometry, routing, SI, assembly,
P1/P3, or a system IEC test.

## Exact primary records

- Nexperia [PESD2USB5UX-T product data sheet](https://assets.nexperia.com/documents/data-sheet/PESD2USB5UX-T.pdf), 2020-09-09, retained as
  `02_parts/PESD2USB5UX-TR/PESD2USB5UX-T.pdf`, SHA-256
  `6e86f26606d8dd9bd563f172b68f5db53f8ee1d9b7c1105a88598d9d7344b112`.
- XMOS [XU316-1024-TQ128 xcore.ai Datasheet v2.0.0](https://www.xmos.com/documentation/XM-014532-PC/html/rst/XU316-1024-TQ128.html), retained as
  `02_parts/XU316-1024-TQ128-C24/XM-014532-PC-v2.0.0.pdf`, SHA-256
  `a2ce2dc835df06793a4e1aa6c5d226c6a01c25c979a63b09a2b57059c17321cf`.

The XMOS record identifies `USB_DM` as TQ128 pin 59 and `USB_DP` as pin 60
(§4.6), with `USB_VDD33` pin 61 and `USB_VDD18` pin 62. Its §15.2 operating
range for USB_VDD33 is 3.00–3.60 V. Its §15.1 generic I/O AMR is `V(Vin) =
-0.5 V .. VDDIO + 0.5 V`; the published TQ128 table does **not** give a
separate powered or unpowered transient-voltage/current limit for USB_DP or
USB_DM, nor does it state which supply should be substituted for `VDDIO` for
those USB-PHY pins.

XMOS also says a self-powered USB device must disable D+/D- pull-ups when VBUS
is absent (the “USB Back Voltage Test”, §10.6/figure text). That is required
USB behavior; it is not a published powered-off DP/DM injection or ESD-survival
specification.

## What the 5UX record establishes

Nexperia Tables 1, 2, 5, and 6 establish that pins 1/2 are the two cathodes
and pin 3 the common anode, that `VRWM` is 5 V, and that capacitance is
0.47 pF typical/0.60 pF maximum. Thus 5UX has a standoff rating above the
Crow USB_VDD33 3.60-V operating ceiling; this closes neither an XU pin-stress
case nor a board-level back-power case.

The same primary does **not** supply a guaranteed safe voltage at the XU pins:

- its 8/20-us rated peak pulse current is 4 A;
- its component rating is 8 kV IEC 61000-4-2 contact discharge, 8 kV ISO
  10605 (150 pF/330 ohm), and 6 kV ISO 10605 (330 pF/330 ohm), each measured
  from pin 1 or 2 to pin 3 and for ten non-repetitive ESD pulses;
- the 3.3-V clamp at 8 A is **typical**, TLP, non-repetitive, and has no
  maximum limit in Table 6;
- Figure 10 shows a 4.32-V positive clamp at 30 ns for its depicted +8-kV IEC
  test, and Figure 11 shows -3.70 V for the depicted negative test. These are
  figure/test results, not guaranteed limits and not measurements at a Crow
  XU pad.

Trace and return inductance between the connector, clamp, ground plane and
XU pins can further change the voltage at the protected IC. The 5UX component
survival rating therefore cannot be transferred to the complete USB port.

## Disposition

**HOLD — not electrically accepted as a Crow USB protection selection.** The
5-V standoff and low capacitance are sufficient to retain 5UX as a provisional
source candidate. The primary XMOS material does not provide a USB_DP/DM
powered or unpowered transient limit against which Nexperia’s typical clamp or
waveform can be compared. A generic I/O AMR cannot safely be promoted to that
missing USB-PHY qualification; if it did apply while its relevant rail is off,
the upper bound would collapse toward 0.5 V, which makes the missing rail-off
analysis more important, not less.

## Smallest next evidence/test

Obtain an XMOS primary written limit or application approval for USB_DP/DM
voltage/current under both powered and USB/rail-off conditions. It must define
the supply state and transient waveform. With a defined limit, test an exact
Crow board at the connector using positive and negative IEC 61000-4-2 contact
discharges up to the selected requirement in both states, and measure DP, DM,
local ground, USB_VDD33 and USB_VDD18 at the XU-side pads with suitable
bandwidth. Record the actual connector-to-clamp-to-ground return geometry.
Until then, neither the device’s 8-kV rating nor a 3.3-V typical TLP number is
an XU316 protection result.
