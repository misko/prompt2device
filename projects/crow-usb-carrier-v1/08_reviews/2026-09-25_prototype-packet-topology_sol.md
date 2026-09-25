# Crow prototype-only schematic packet: independent topology review

**Verdict: topology parity SOUND for this private prototype packet only.** This is
not full schematic acceptance, electrical protection qualification, PCB layout
acceptance, release, or an order decision. The packet is
`06_build/prototype_only/20260925T044907Z-581549/`; its `receipt.json` has
SHA-256 `5cccaaa7b577a9ad07b647e77a7759ce203e81d8e6efd35a3fa55e7a9ab5cd42`
and declares `PROTOTYPE_ONLY`.

I recomputed all four artifact hashes in the receipt and all 21 recorded input
hashes against the current local files: all match. The circuit JSON contains
569 `source_component` records and 569 `schematic_component` records. The
exported KiCad netlist has the same exact 569-reference set, 1,787 assigned
native pads and 428 nets. The source has 1,641 connected ports with numeric
pin identities; every one maps to a unique exported native pad on the same
net, with zero missing pads or net mismatches. The only pad-name translation
needed for that comparison is the authored J_USB connector map from its
numeric source ports to physical A/B names (`SHIELD` to `SH`). The native
schematic has 39 source sheets; the generated PDF is 45 pages. I did not
perform a visual page-by-page readability review.

`U_USB_ESD` is exactly TI `TPD2EUSB30ADRTR`, JLC code `C94934`, with native
`Package_TO_SOT_SMD:Texas_DRT-3`. Its source ports and native pads agree:
pin 1 `USB_DP`, pin 2 `USB_DN`, pin 3 `GND`. This matches the retained TI
SLVSAC2G pin table (local PDF SHA-256
`a2c0dd845043a5bbfe610f673879c29e38649544385dea51dbe0a4c49df39136`).
Native `USB_DP` joins J_USB A6/B6, U_USB_ESD.1 and U_XU.60; `USB_DN`
joins J_USB A7/B7, U_USB_ESD.2 and U_XU.59. The two data nets remain
distinct. The XU316 TQ128 pin identities 59=DM and 60=DP also agree with
the retained XMOS primary dossier and source declaration.

Independent mechanical checks were outside this review. The packet's circuit
diagnostic has zero embedded errors, though 1,821 advisory records remain;
native label survival passes 281/281 labels with no configured pin-map
assertions. Those results support artifact integrity, not USB signal
integrity, ESD transient coordination, connector placement, P1/P2/P3, or
manufacturing acceptance. The open `USB-ESD-selection-transient` finding and
prototype-only release hold remain in force.
