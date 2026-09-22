# Spoke eFuse source adoption

Eight TPS26625DRCR channels replace F1–F8 branch PPTCs. Each channel adds
44.2 kΩ current programming, 1 MΩ UVLO bias, 10 nF slew programming and
input/output 100 nF bypass. Connector/audio/CHASSIS identities remain intact.
TI SLVSDT4F supports the selected pin functions: RTN pin 5 and exposed pad 11
share a local return island; GND pin 6 connects separately to system GND.
OVP ties to RTN, SHDN to IN, and unused FLT remains open.

This integrates the isolated SOL candidate after review while preserving
C_IN3 and the three single 47 µF TPS62825 output banks. Root repaired missing
schematic poses/symbol arrangement and 24 missing ground endpoints in the
modular interface. Each channel now has a separate schematic protection sheet.
Those positions have not yet passed rendered-schematic readability review.

Root verification of the actual combined source:

- 460 components, 86 selected MPNs, 1539 ports, 1416 traces.
- Zero source diagnostics; all 26 existing critical endpoint assertions pass.
- Modular ownership 460/460 and crossings 53/53 pass.
- E-CAP passes all eight banks, retaining the earlier derating assumptions.
- Project contracts pass 349 files with zero violations before this note.

The interface review is retained as informational research in
`2026-09-22-spoke-interface-review.md`. It is not an executable rule schema;
the power-tree file remains the machine-owned electrical authority.

The 2.185 A one-fault source screen is an engineering allocation, not a
guaranteed 12 V hard-short current. The input PPTC has inadequate design
margin at 70 °C for that screen and is being reselected. Source load-line,
TVS/transient coordination, startup and reverse-powered-pod behavior remain
open engineering work. Realized copper/thermal and fault testing remain
later verification. No full E-FAULT/E-SURGE, native schematic, placed board,
USB operation or fabrication acceptance is claimed.
