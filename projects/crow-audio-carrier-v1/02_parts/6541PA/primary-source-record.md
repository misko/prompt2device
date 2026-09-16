# Belden 6541PA primary-source fact record

Accessed: 2026-09-01
Authority status: exact manufacturer technical-data facts; physical harness owed

Primary document: [Belden 6541PA Technical Data Sheet](https://catalog.belden.com/techdata/EN/6541PA_techdata.pdf), revision 0.544 dated 2025-09-07.

The retained source blob in the sibling pod project is gzip-compressed despite
its `.pdf` name. Its ordinary-file SHA-256 is
`ae16604fa9885cf3757847f47e4694f7d6aac3a743937f8ed201de95b4d8b971`;
the decompressed PDF payload SHA-256 is
`c0d308390f92e693334217277ca45729d4cdb459e3ec4aa1b47b6c7ec25d2475`.
This carrier record captures the reviewed facts without pretending that a
second raw PDF copy is locally vendored.

Exact facts used here:

- two individually Beldfoil-shielded 22 AWG (7x30) bare-copper twisted pairs;
- FEP conductor insulation, nominal insulation diameter 1.2 mm;
- PVDF jacket, nominal overall diameter 5.44 mm;
- 53 mm stationary and installation minimum bend radius;
- 53.8 ohm/km nominal conductor DCR and 2.2 A per conductor at 25 C;
- 90.2 pF/m nominal conductor-to-conductor capacitance;
- 300 V CMP rating and -20 C to +150 C operating range.

The 1.2 mm insulation diameter is inside the selected 43030-0007 contact's
1.85 mm maximum. Cable facts do not prove crimp quality, gland fit, connector
access, or the all-eight installed bend envelope.
