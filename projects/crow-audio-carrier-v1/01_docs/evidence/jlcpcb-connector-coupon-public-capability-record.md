# JLCPCB public capability record — connector coupon

Accessed: 2026-09-06

Subject: `06_build/connector_qualification_coupon/current/`

Scope: public manufacturer documentation only. No design file was uploaded,
no logged-in quote was requested, and no order, CAM acceptance, yield,
turnaround, price, or production allocation is claimed by this record.

## Exact coupon selections

| Selection | Coupon value | Public JLCPCB authority | Result |
|---|---:|---|---|
| Material and layer count | FR-4, 4 copper layers | [Rigid PCB capabilities](https://jlcpcb.com/capabilities/Capabilities,/) lists FR-4 and 1–32 layers | compatible |
| Finished dimensions | 150 x 100 mm | the same table lists a 663 x 593 mm standard maximum for 4-layer FR-4 at thickness at least 0.8 mm | compatible |
| Finished thickness | 1.600 mm | the same table lists 1.6 mm as a standard FR-4 thickness, with ±10% finished-thickness tolerance for thicknesses at least 1.0 mm | compatible; public tolerance is 1.44–1.76 mm |
| Solder mask | green | the same table lists green LPI solder mask | compatible |
| Silkscreen | white | [JLCPCB PCB Color](https://jlcpcb.com/quote/pcbOrderFaq/PCB%20Color) states that green boards use white silkscreen | compatible |
| Surface finish | lead-free HASL | the rigid-PCB table lists lead-free HASL and excludes HASL only for FR-4/HDI boards with 6 or more layers, boards no thicker than 0.4 mm, and other named technologies not used here | compatible |

JLCPCB's [surface-finish guide](https://jlcpcb.com/help/article/jlcpcb-surface-finish)
also identifies lead-free HASL as RoHS-compliant and readily solderable, while
warning that it is not planar enough for fine-pitch packages. The coupon has
only through-hole connector lands and board datums, so the cited fine-pitch
limitation does not apply to its population; that applicability statement is
an inference from the exact coupon footprint census, not a manufacturer
acceptance.

## Handoff consequence

The public capability screen finds no incompatible declared fabrication
selection. Upload only
`crow-audio-carrier-v1-connector-coupon_gerbers.zip` as a bare-board PCB job,
select the exact values above, and confirm that the upload viewer recognizes
four copper layers, one complete 150 x 100 mm outline, plated drills and
non-plated drills before payment. Do not enable PCBA or upload a BOM/CPL; the
exact connector lots must be hand-populated and recorded in the governed
physical response.

An actual upload can still be rejected or requoted during JLCPCB CAM review.
This record therefore establishes public option compatibility only. It does
not change the coupon receipt from `INCOMPLETE`, close any of the 20 physical
targets, establish authenticated PCBA component allocation, or authorize the
carrier product board or any order.
