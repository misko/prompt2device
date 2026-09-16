# Samtec TMM-106-01-L-D primary-source fact record

Accessed: 2026-09-01
Authority status: manufacturer drawing facts; module-side fit still owed

Primary drawing: [Samtec TMM series print, revision AS](https://suddendocs.samtec.com/prints/tmm-mkt.pdf). The inspected PDF payload is 143,320 bytes with SHA-256
`66d9ffaa15ef8ff9b1614640d81fd2d1c2c6629b522df0cddc64acac3e73efc3`.
The exact PDF is vendored as `TMM-Series_RevAS.pdf`; its bytes match that
digest. This record retains the reviewed fact extraction separately from the
immutable drawing.

The exact order code `TMM-106-01-L-D` selects six positions per row, terminal
style `-01`, light selective gold/matte-tin plating `-L`, and a double-row
body `-D`. Drawing-controlled facts used here are:

- 2.00 mm pitch in both axes and 0.50 mm square posts;
- double-row numbering places odd pins down one row and even pins down the
  opposing row, beginning with pins 1 and 2 at the first-position end;
- six-position body length 12.00 mm with +0/-0.25 mm drawing limit;
- double-row body width 3.94 mm reference and insulator thickness 1.50 mm
  reference;
- `-01` post above the insulator is 3.20 mm, contact area is 2.54 mm
  reference, tail is 3.50 mm reference, and straight overall pin length is
  8.20 mm reference;
- the TMM is an unshrouded friction-mating header and provides no inherent
  cable polarization.

These facts bind the carrier J10/J11 header identity and local land pattern.
The drawing table does not label post A or contact area C as minimum; A is a
critical dimension and the drawing title-block tolerances apply where a
dimension has no individual tolerance.
They do not identify the miniDSP board headers and do not prove that any cable
socket seats, retains, or can be serviced in the final assembly.
