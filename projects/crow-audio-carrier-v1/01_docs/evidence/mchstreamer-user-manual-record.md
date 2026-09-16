# miniDSP MCHStreamer user-manual authority record

Accessed: 2026-09-01
Primary authority: [miniDSP MCHStreamer User Manual](https://www.minidsp.com/images/documents/MCHStreamer%20User%20Manual.pdf)
Inspected PDF: 40 pages; 2024-01-16 creation metadata; SHA-256
`2cf36d628df68607d007b971a13a3a578916d74629d6660571daf218cfbc6edd`.

The raw PDF is not duplicated in this child-project directory. Its digest is
also retained by parent ADR 0010. This file binds only manufacturer statements
visible in the inspected manual; it is not a cable-fit or bench-test receipt.

Relevant exact facts:

- section 2.4: J2 pin 12 accepts external 5 V through a diode-OR with USB;
  module consumption is no more than 120 mA plus any load on J3 pin 2;
- section 2.4: J3 pin 2 provides 3.3 V with 200 mA maximum external draw;
- section 2.5.1: the MCHStreamer is always clock master and all logic lines
  use 3.3 V levels;
- section 2.5.2 and Figure 1: J1/J2/J3 are 12-pin interfaces numbered as two
  rows, with pins 1 and 2 at the marked first-position end; two suitable 2x6,
  2.00 mm-pitch cables are supplied, but no cable or board-header MPN is given;
- Table 1: J1 pin 2 is data input, pin 9 MCLK output, pin 10 BCLK output,
  pin 11 GND, and pin 12 frame-sync output; J3 pin 1 is GND and pin 2 is 3.3 V;
- TDM firmware Table 12: TDM8 uses J1 pin 1 data output, pin 2 data input,
  pin 9 MCLK, pin 10 BCLK, pin 11 GND, and pin 12 FSYNC;
- TDM input is always treated as 24-bit; at 48 kHz TDM8 uses 24.576 MHz MCLK,
  12.288 MHz BCLK, and 48 kHz FSYNC.

Firmware-access boundary:

- manual section 4.1 says application-dependent firmware may need to be loaded;
- direct purchasers receive the software in the authenticated miniDSP User
  Downloads area when the order ships, while dealer purchasers redeem the
  supplied coupon;
- the official miniDSP support article [*How do I change the firmware on my
  MCHStreamer/USBStreamer?*](https://support.minidsp.com/support/solutions/articles/47000681709-how-do-i-change-the-firmware-on-my-mchstreamer-usbstreamer-)
  says the updater is in the software/driver package and directs users without
  access to open a support ticket;
- neither public page supplies immutable TDM8 image bytes, so exact authorized
  image/package versions, hashes, load evidence and module readback remain
  OWED. A community-posted filename is not release authority.

The manual does not publish the MCHStreamer J1/J3 male-header manufacturer,
part number, square-post dimension, exposed contact length, insertion force,
retention force, or supplied-cable wiring table. Those facts cannot be inferred
from pitch and pin-count alone.
