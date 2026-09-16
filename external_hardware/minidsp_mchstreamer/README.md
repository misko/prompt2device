# miniDSP MCHStreamer external-device facts

This is the single repository home for facts about the externally supplied
miniDSP MCHStreamer consumed by the crow audio carrier. The cited authority is
the miniDSP *MCHStreamer User Manual*, inspected 2026-09-01 (40 pages, PDF
creation metadata 2024-01-16), SHA-256
`2cf36d628df68607d007b971a13a3a578916d74629d6660571daf218cfbc6edd`.
The inspected bytes are retained beside this record as
`MCHStreamer_User_Manual.pdf`; its SHA-256 is the digest above. This local
capture closes document reproducibility only and does not claim physical
inspection.

## Manufacturer-manual facts

The following lines transcribe the exact interface consequences used by the
carrier. They are cited facts, not evidence of a particular cable or header
seating correctly.

**TDM8 header pinout: J1 pin 1 is data output, pin 2 is data input, pin 9 is MCLK, pin 10 is BCLK, pin 11 is GND, and pin 12 is FSYNC.**

Method: miniDSP MCHStreamer User Manual, section 2.5.2, Figure 1, Table 1,
and the TDM firmware Table 12. The same manual states that TDM input is always
treated as 24-bit.

**At 48 kHz TDM8, the MCHStreamer is clock master and supplies 24.576 MHz MCLK, 12.288 MHz BCLK, and 48 kHz FSYNC at 3.3 V logic levels.**

Method: miniDSP MCHStreamer User Manual, sections 2.5.1 and 2.5.2 and the TDM
firmware table. This establishes electrical signal roles; it does not establish
clock integrity through the selected physical cable.

**J3 pin 1 is GND and J3 pin 2 supplies 3.3 V, with at most 200 mA available to an external load.**

Method: miniDSP MCHStreamer User Manual, section 2.4 and Table 1. The carrier
uses J3 pin 2 only as a negligible-current presence sense; it does not power a
carrier rail from J3.

**TDM8 operation requires a miniDSP-provided firmware image; the exact image is not part of the public manual download.**

Method: miniDSP MCHStreamer User Manual, section 4.1, and the official miniDSP
support article [*How do I change the firmware on my
MCHStreamer/USBStreamer?*](https://support.minidsp.com/support/solutions/articles/47000681709-how-do-i-change-the-firmware-on-my-mchstreamer-usbstreamer-),
inspected 2026-09-02. The manual says that application-dependent firmware may
need to be loaded and that direct purchasers receive software through the
authenticated User Downloads area when the order ships; dealer purchasers use
the supplied coupon. The support article says the updater is included in the
software/driver download and directs customers without access to open a
support ticket. Neither public page provides immutable TDM8 binary bytes.

The carrier therefore does not bind a filename seen in a community post or
assume the module ships in TDM8 mode. After acquisition, retain the exact
miniDSP-supplied package and TDM8 image, record their SHA-256 digests and
version/source-account receipt, load the image with the vendor updater, and
verify the selected 48 kHz clocks, eight-slot framing, channel order, 24-bit
input treatment, and recovery after power cycling. Until that evidence exists,
TDM8 firmware identity and interoperability are OWED.

## Physical fact still owed

**Physical J1/J3 male-header keying, exact manufacturer part number, post dimensions, exposed contact length, and the installed pin-1/cable orientation are OWED.**

The manual shows the two-row numbering and first-position end, and names a
2x6, 2.00 mm-pitch supplied cable, but publishes neither the module header MPN
nor a drawing that closes post fit, keying or the installed cable rotation.
Obtain these facts by inspecting a named MCHStreamer hardware revision and
sample, identifying or measuring both J1 and J3 headers, then performing
continuity, polarity, seating, collision and retention checks with the exact
selected `TCSD-06-D-04.50-01` assemblies. Until that first-article evidence is
captured and machine-regraded, the full connector gate remains incomplete.

## Firmware fact still owed

**The exact authorized TDM8 image, updater/package version, image SHA-256, and module readback are OWED.**

This is a COTS acquisition and first-article hold, not permission to author or
modify embedded firmware in this project. A public forum filename is not a
manufacturer-distributed byte authority.
