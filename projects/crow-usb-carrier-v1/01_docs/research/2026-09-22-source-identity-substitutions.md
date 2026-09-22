# Source identity substitutions

Baseline: `74c94f08`. Read and checked 2026-09-22 PDT. This source-only
change selects two manufacturer packaging variants with qualifying dated
distributor observations. It does not claim purchase allocation, assembly
acceptance, native schematic acceptance, PCB geometry acceptance, or physical
validation.

## CS5308P-DNR

Cirrus Logic DS1314F1 Table 12-1 defines `CS5308P-DN` as the tray orderable
number and `CS5308P-DNR` as the tape-and-reel orderable number for the same
commercial-temperature CS5308P, 48-pin QFN product. The selected `DNR` identity
therefore retains all pins, value, limits, and the existing
`crow_usb_analog:Cirrus_CS5308P_QFN48_6x6_P0.4_EP4.6` footprint.

Five boards require 5. Dated exact-MPN observations in `manual_quotes.yaml`
record DigiKey stock 3,105 and Mouser stock 62, both with quantity-one cut-tape
access. No exact JLC PCBA code is asserted.

## R82DC4100CK60J

The exact KEMET specification retained in the new dossier identifies
`R82DC4100CK60J` as 1 uF, +/-5%, 63 V, metallized stacked PET with a 7.2 x
5.0 mm body, 10.1 mm maximum height, 5.00 mm lead spacing, and 0.50 mm lead
diameter. These are the selected `DQ60J` circuit and mechanical properties, so
the existing `Capacitor_THT:C_Rect_L7.2mm_W5.0mm_P5.00mm` footprint is retained.
The change does not accept the observed `K` tolerance suffix.

Five boards require 80 (16 per board). Dated exact-MPN observations record
DigiKey stock 6,466 and Mouser stock 5,775.

## Source verification

The adopted source-only expansion produced 489 components, 489 unique references,
85 unique populated MPN strings, and zero source errors. `U_ADC` alone carries
`CS5308P-DNR`; the 16 refs `C_A1N` through `C_A8P` carry
`R82DC4100CK60J`. The exact-parts rows retain quantities 1 and 16 and their
existing footprints. No PCB or native artifact was generated.

Root integration retained the LT3045 change, replaced the active DN/DQ dossier directories with DNR/CK (history remains in Git), retained primary PDFs as regular files, and corrected the CK specification date to2026-09-22. All1493 named source pin/net edges remain identical before/after these packaging substitutions;17 identities change (U_ADC and16 coupling capacitors). Modular489/489refs and54/54 crossings and P-MOD3/3 pass. Current source SHA-256:1c6a378bf80980d23adf0ac5e4b0ab6f0ab559c4b75779233e357a009e7bd352. The copied dated Mouser observations still need explicit orderability provenance before the strict manual-source gate can credit them; this is not a two-pool procurement PASS.
