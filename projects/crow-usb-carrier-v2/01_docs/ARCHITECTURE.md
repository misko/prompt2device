# Crow USB carrier v2 — architecture at commission

This is a block plan, not an admitted circuit or layout. The [restart record](RESTART.md) points to v1 evidence; no v1 board geometry or route is adopted.

| Block | Intended function | Decision still owed |
| --- | --- | --- |
| Raspberry Pi USB link | Cable to an onboard USB audio interface IC; observe host VBUS without assuming it powers the carrier | USB connector/service envelope, data ESD and exact stack/cross-section |
| Digital audio | Retain the selected XMOS XU316 direction, flash, clock, reset and programming access | Re-admit exact schematic and operating-state proof in v2 |
| Analog/spokes | Eight-channel conversion, analog input paths and eight Crow spoke interfaces | Exact channel, connector, reference and return contracts |
| External power | Protected external input feeding digital, converter and quiet analog rails | Input/load envelope, sequencing, thermal and fault bounds |
| Manufacturing | JLCPCB-populated SMD, specified manual through-hole parts | Exact v2 population, package/footprint and fabrication review |

Place connector mating and service envelopes, USB/ESD/controller transition, clocks, analog channels, return paths and power loops only after v2 commission, schematic and sourcing admission. The first unresolved choice is the USB ESD device; the stack and USB geometry are also open. The seeded `03_src/` files are generic schema examples behind the commissioning hold, not this block plan's machine authority.
