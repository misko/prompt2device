# Molex 43650-0200 primary-source fact record

Accessed: 2026-09-01
Authority status: manufacturer drawing retained and hash-verified; physical fit still owed

Primary records:

- [Molex 43650-0200 exact product record](https://www.molex.com/en-us/products/part-detail/436500200)
- [Molex 43650 family sales drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/436/43650/436500500_sd.pdf)
- [Molex Micro-Fit 3.0 product specification PS-43650-001](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/436/43650/PS-43650-001.pdf)

The exact D8 family drawing used here is retained locally as
`Molex_436501000_SD_revD8.pdf`, SHA-256
`b8942b95bc3fe4c02171de9e714d99b2688055e249ba1524e3c2a8c3cf78eaa3`.

Exact two-circuit facts used by J9:

- orderable part `43650-0200`, two circuits, right-angle through-hole header;
- 3.00 mm contact pitch, 1.02 +/-0.05 mm signal holes, and 1.60 mm
  recommended PCB thickness;
- two-circuit drawing dimension A = 9.65 mm and B = 3.00 mm;
- shrouded mating interface, polarized to the PCB, with the mating face at the
  carrier west edge;
- the 10.16 mm maximum board-edge datum terminates at the locating-peg centre,
  not the signal-pin row; the row-to-peg dimension is 4.32 +/-0.08 mm and the
  nominal peg-to-mouth dimension is 4.60 mm;
- supported mating housing family `43645`, with 17.56 mm overall mated length;
- product current rating 8.5 A per contact and operating range -40 to +105 C.

The selected J9 harness draws 0.90 A maximum by design, below both the exact
contact rating and the conservative 5 A IEC family value used for screening.
The board admits only a protected, isolated 11.4-13.2 V appliance source at
J9. The connector does not create a PoE, safety-isolation, hot-plug,
overvoltage-cutoff, or reverse-polarity function.

This ordinary record closes source identity and a conservative body envelope.
It does not prove populated seating, enclosure exposure, latch access, or
mating reaction.
