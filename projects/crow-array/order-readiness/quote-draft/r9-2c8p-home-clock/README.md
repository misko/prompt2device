# Crow r9 — user-installed TI clock, quote only

User decision, 2026-11-01: install the TI oscillator at home using SMT methods.
No purchases, reservations, vendor messages, uploads or manufacturing commitments
are authorized by this package. No new design or production acceptance is issued.

## Matched uploads and quantities

Fabricate **5 carriers / assemble 2** and **10 pods / assemble 8**.
Each BOM/CPL describes ONE board; set job quantities separately.

| Board | Upload these r9 files together |
| --- | --- |
| Carrier | `carrier-gerbers.zip`, `carrier-bom.csv`, `carrier-cpl.csv` |
| Pod | `pod-gerbers.zip`, `pod-bom.csv`, `pod-cpl.csv` |

Carrier fabrication, schematic and all native design files are byte-identical
to reviewed r8. Pod files are unchanged. Only carrier X1 leaves the factory
BOM/CPL and moves to HOME in scope/procurement tables. **C4 stays factory fitted**:
Samsung CL21B105KBFNNNE / C28323, 1uF 50V X7R 0805. Total demand for that MPN
remains 14. Do not use r7 carrier fabrication: its clock footprint is different.

| Installation owner | Parts across 2 carriers + 8 pods |
| --- | ---: |
| JLC SMT | 476 |
| JLC through-hole | 28: 24 RJ jacks, 2 power jacks, 2 TRACO regulators |
| Home | 20: 2 Picos, 2 TI oscillators, 8 microphones, 8 buzzers |
| Total fitted | 524 |

X1 is **required in the finished device, not a circuit DNP**. Its omission from
factory uploads is an explicitly authorized installation split, not permission
to bypass other shortages. Native design population flags remain unchanged;
use these scope-filtered quote files, not an unfiltered CAD BOM/CPL re-export.

## Home clock: exact part and work instruction

Buy only **Texas Instruments LMK6CE012288CDLFR**, 12.288MHz, DLF 2.5 x 2mm,
four bottom contacts. Need **2 installed**, one X1 per carrier; purchase quantity
and any practice/spare allowance are not selected. [DigiKey exact offer](https://www.digikey.com/en/products/detail/texas-instruments/LMK6CE012288CDLFR/22107194)
was browser-observed November 1: 2,884 units, MOQ1, USD3.34 each. Two installed
parts cost USD6.68 before spares, shipping and tax. This is not allocation or a
delivery promise; recheck before purchasing. JLC's oscillator warehouse date
is no longer a dependency for factory assembly of this split.

1. Work on an unpowered carrier with USB, 12V and other connections removed.
   Prefer installing X1 before home-installed Pico or other heat-sensitive parts.
   Use ESD precautions, magnification, fine tweezers, compatible solder paste/flux
   and controlled hot air. An ordinary iron alone is not the intended method.
2. Verify the r8/r9 carrier and exact part. Inspect X1 lands for damage, residue
   and excess solder; prepare evenly without scratching pads. Confirm C4 is
   present and surrounding components can be protected from airflow/heat.
3. From the native TOP view, X1 is centered at (86,85.5)mm, rotation 90 degrees.
   Pin1/OE is bottom-left, pin2/GND bottom-right, pin3/OUT top-right and pin4/VDD
   top-left. Use the actual package pin1 mark and native pad numbering together;
   do not infer orientation from printed text or view the package underside as
   if it were the board top. `home-clock-placement.csv` retains export coordinates
   (86,-85.5)mm for reference only; it is **not** a factory upload.
4. Apply a controlled small paste deposit and align all four contacts. Reflow
   using the [TI package/reflow guidance](https://www.ti.com/lit/ds/symlink/lmk6c.pdf)
   and paste profile, respecting nearby parts' limits. No universal hot-air knob
   temperature or dwell is prescribed: nozzle setting is not package temperature.
   Avoid moving neighboring parts or prolonged reheating; let the solder solidify
   before disturbing the board. Do not apply whole-board wave soldering or washing.
5. Inspect orientation, seating and adjacent parts under magnification. Check
   for supply shorts with power off. Hidden joints cannot be fully accepted by
   top-view appearance alone; investigate suspect continuity or alignment before
   energizing. Follow flux-specific cleaning rules without washing protected parts.
6. Use a current-limited first power-up under the retained bring-up procedure.
   Verify device-local 3V3 and its startup before judging clock operation. Probe
   the clock test point with a low-capacitance probe and short ground connection;
   ordinary probes add load to the reviewed approximately26pF network. Record
   probe loading and use the retained clock model for edge/amplitude evaluation.
   Verify 12.288MHz, receiver clock operation and continuous eight-channel USB
   acquisition. No clock/no USB acquisition means troubleshoot, not acceptance.

This is a home-rework instruction, not proof the work has been performed or
independently accepted. If tooling/access or solder joints are uncertain, use
a local technician; do not bypass the clock or substitute another MPN.

## Retained engineering / production holds

The independent engineering review in `qualification.json` applies to the r8
circuit, not a new r9 assembly release. Read `engineering/CLOCK-POWER-MODEL.md`
and `engineering/clock-model.json`. Prototype planning allocations remain
192mA external3V3 / 350mA5V / 680mA whole-array12V. Voltage/ramp/restart,
full-load thermal and clock limits remain bounded models requiring first-article
measurement. No X1 qualified 3D model is supplied. The historical r8 factory-clock
instructions at `engineering/R8-HISTORICAL-INSTRUCTIONS.md` are superseded ONLY
for oscillator installation ownership; they are not current upload instructions.

Keep LUTE reflow/no-unqualified-wash, TRACO localized THT/seating, original Pico
SC0915 D1-only removal, connector/hole/edge/underside inspection, carrier
JLC04161H-7628A acknowledgement and pod JLC04161H-7628 rails/finished-edge controls.
Preserve supply, temperature, USB/backfeed/fault-recovery and acquisition testing.
Retained geometry and engineering do not close vendor or assembly acceptance.

## Next browser steps — quote only

1. Run `python3 projects/crow-array/order-readiness/r9_quote.py verify`.
2. Upload the matched r9 sets while preserving older drafts/history. Use the
   stated fabricated/assembled quantities. Do not upload `home-clock-placement.csv`
   or `home-install-parts.csv` as factory placement/BOM input.
3. Confirm X1 is intentionally absent from factory placements, but C4 and every
   other factory reference remain included. Do not use "Do not place" for any
   other required factory part. Check exact manufacturer/MPN/package, not counters.
4. Obtain both placement previews and check C4, retained THT positions/polarity
   and all other factory references. Keep "Do not confirm automatically".
5. Check availability and exact gross quantities for the remaining factory parts.
   Confirm empty X1 lands remain accessible and suitable for later home reflow;
   reconcile factory paste/stencil treatment without changing released copper.
6. Resolve stack, rails, stencil/process and mechanical holds; obtain itemized
   fabrication, SMT/THT, parts, setup, sourcing, shipping and tax. Stop before
   payment, reservation, noncancelable sourcing or manufacturing commitment.

No browser draft was changed by creating this local package.
