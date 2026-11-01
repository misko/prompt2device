# JLC r5 quote session — 31 October 2026

At approximately 17:14 PDT the signed-in Chrome session processed the r5 carrier and pod BOM/CPL files in the existing saved drafts. The Gerbers were already present in those drafts; no replacement Gerber was uploaded during this pass. No purchase, reservation, part substitution, cart addition or manufacturing commitment was made.

JLC's PCB summary showed carrier Economic PCBA, top side, quantity 2; pod Standard PCBA, top side, quantity 8. The quote-package verifier and release preservation check passed at commit `4fd4bc35`; all 59 order-readiness tests passed. Candidate bare-board quantities and process settings were not reverified in this pass.

## Matching observations

JLC displayed 30 carrier BOM rows, 25 confirmed and five shortage rows; pod displayed 21 rows, 18 confirmed and three shortage rows. These are portal BOM rows, not verified reference/placement counts. Part-number text matches do not establish manufacturer, package, process, identity or placement acceptance. Carrier through-hole rows displayed PJ-102AH C3096093 (two, $2.1162), RJHSE-5080 C599441 (16, $12.6256), and R-78E5.0-0.5 C18212367 (two, $7.1126). The last description lists several incompatible values, so confirm the exact RECOM manufacturer/variant and eligibility before accepting it. Pod RJHSE-5080 displayed C599441. These line displays are snapshots, not a full sourcing or assembly quote.

Carrier shortages shown: C3216X7R1V106K160AC four, GRM21BR71A105KA01L twenty, 1206L010/30WR eleven short with seven displayed stock against gross eighteen, PCM1864DBT four, and CB3LV-3I-12M288000 two. Pod showed shortages of ten, twenty and three for the existing shortage rows; check each row and shared fuse stock before allocation. The seven in-stock fuses visible for each job may be the same pool.

Pressing NEXT on the pod produced **Project has unselected parts**: JLC warned that some parts had no selection and offered **Do not place** or **Select parts**. Chose **Select parts**; did not mark shortage parts unplaced. The Component Placements tab on the carrier did not advance from BOM matching. Therefore no complete placement preview, orientation review, complete PCBA price, sourcing fees, combined shipping or delivery date was obtained. Further non-binding resolution is needed; the previous JLC warning says pre-order parts cannot be canceled once quotation is finished, so do not submit that form under the current no-commitment instruction.

The scope in r5 includes 28 batch through-hole operations and 478 SMT placements, while two Picos, eight microphones and eight buzzers remain home installation. The previous home-through-hole proposal is superseded for this quote. No acceptance of any matched part, assembly process, production settings or placement has been given.
