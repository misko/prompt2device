# Crow r8 — TI clock, prototype quotation only

**Not production approval. No purchases, reservations or manufacturing commitments.**
The TI local design passed independent prototype engineering review. This is
not a new release or automatic inheritance of prior stage acceptance.

Fabricate **5 carriers / assemble 2**. Fabricate **10 pods / assemble 8**.
Files describe ONE board; select these quantities separately in JLC.
Factory scope remains 478 SMT + 28 THT placements. Home: 2 original SC0915
Picos with controlled D1-only removal, 8 microphones and 8 buzzers.

## Complete matched file sets

| Board | Upload together |
| --- | --- |
| Carrier | `carrier-gerbers.zip`, `carrier-bom.csv`, `carrier-cpl.csv` — ALL r8 |
| Pod | `pod-gerbers.zip`, `pod-bom.csv`, `pod-cpl.csv` — unchanged from r7 |

Do not combine r7 carrier Gerbers/CPL with the r8 BOM. Carrier copper, pads,
paste, mask, added vias and fabrication outputs changed. X1 is now TI
LMK6CE012288CDLFR / C36974742, 12.288 MHz, DLF 2.5 x 2 mm. C4 is now
Samsung CL21B105KBFNNNE / C28323, 1 uF 50 V X7R 0805, relocated nearby.

| Reference | Native center mm | CPL center mm | Rotation | Check |
| --- | --- | --- | --- | --- |
| X1 | 86, 85.5 | 86, -85.5 | 90 degrees, Top | Pin1 bottom-left;2 GND bottom-right;3 OUT top-right;4 VDD top-left in native top view |
| C4 | 83.46, 82.9 | 83.46, -82.9 | 0 degrees, Top | Nonpolar; pin1/3V3 left, pin2/GND right |

Installed clocks: **2**, not 5. Aggregate C28323 need rises from 12 to **14**
across both jobs (6 carrier + 8 pod). Other fitted quantities remain unchanged.
Native schematic and a refreshed carrier PDF are included. No qualified X1 3D
model is supplied; assembly approval must use actual land/pin evidence and preview.

## Stock and lead time — not a reservation

November 1 exact JLC offer shows 10 TI clocks, MOQ1, $4.9424 each: **$9.8848
for two installed**, before any attrition, fees, tax or assembly charges.
Raw fields identify overseas/presale stock. Do not add overlapping pools or
claim zero lead time. **Usable JLC warehouse date is unconfirmed.** Generic
attrition4/minimum5 fields were not evaluated for this job; if applicable the
scenario is max(2+4,5)=6, not 9, but actual gross demand still needs confirmation.
Bypass stock observations show adequate overseas/presale quantities; not allocation.

## Engineering and process controls

Use revised planning allocations: **192 mA external 3V3, 350 mA 5 V,
680 mA whole-array 12 V**. All eight pods remain in the load model. No larger
fuse, lower ambient requirement, new power source or reduced mission is assumed.
Read `engineering/CLOCK-POWER-MODEL.md` and `qualification.json`: voltage/ramp,
clock waveform and thermal results are bounded prototype models, not measured
or guaranteed full-temperature limits. The current clock result is
`engineering/clock-model.json` (source draft7/clock-v2.json).

Preserve all r7 LUTE reflow/no-unqualified-wash controls, TRACO localized THT
process and seating controls, Pico D1-only modification, connector/hole/edge/
underside inspections, carrier JLC04161H-7628A stackup acknowledgement and pod
JLC04161H-7628 rails/no-depanel controls. The TI land/paste drawing's 125 um
stencil is an example, not automatic approval of the actual factory process.
Confirm compatible stencil and profile; do not apply whole-board wave/wash.

First-article tests remain: device-local 3V3/ramp/restart, full simultaneous
load, converter/diode/oscillator temperatures, clock/reference integrity,
continuous eight-channel acquisition and USB/backfeed/fault recovery. The
documented narrow thermal margins and failing sensitivities cannot be waived.

## Next TinyFish / browser steps — quote only

1. Verify locally with `python3 projects/crow-array/order-readiness/r8_quote.py verify`.
2. Deliberately replace the carrier's Gerbers, BOM AND CPL with r8; preserve
   both existing drafts/history and quantities. Do not upload mixed revisions.
3. Recheck every detected reference against exact manufacturer/MPN/package,
   especially TI C36974742 and the new C4 row C28323. No substitutions or
   "Do not place" omissions. Pod files and home-install split stay unchanged.
4. Ask the read-only interface for exact gross demand, stock pool, fees and usable
   warehouse dates. A purchase, noncancelable preorder, reservation or vendor
   message requires appropriate separate authority; stop before commitment.
5. Obtain both complete placement previews. Verify X1 actual pin1/orientation,
   C4 location, all retained THT placements and all matched rows. Row counters
   alone are not complete coverage. Keep "Do not confirm automatically".
6. Resolve stack, rail/finished-edge, stencil/process and mechanical holds;
   collect itemized fabrication, SMT/THT, components, setup, sourcing, shipping
   and tax. Do not call the result an order approval or full production release.

Nothing in this package submits an order or authorizes purchasing.
