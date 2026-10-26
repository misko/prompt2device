# Carrier R3 Panasonic replacement — engineering author disposition

SOL engineering author, 2026-10-22, FR1 bounded attempt. Recommendation for
independent review: adopt **Panasonic Industry ERJ-3EKF68R0V at carrier R3 only**
in the five-carrier/ten-pod successor, retaining the existing copper, lands,
placement,68ohm±1%,0.1W and source-series clock role. This report is not its own
review, a stage acceptance, a release, or permission to order/contact/upload.

No demonstrated affected electrical or land/body incompatibility remains after
the finite checks below. A new exact part dossier/model and affected-stage
source/regeneration/admission remain required. Historical Vishay receipts retain
their old subjects and are not refreshed by this recommendation. No mission,
environment, functionality or physical-qualification requirement is reduced.

## Actual source and retained facts

Read the current pcb-design skill, part-recheck and registered3D procedures;
project contracts/brief/raw decisions; active first-run authority; authoritative
LS13 author/ordering; P038; LS12 clock review/model; LS19/LS20 construction and
clock dispositions; accepted LS44 native; and current LS46/LS43 mechanical
model/controls. Some historical commission/hold paths named in contracts are
absent in this standalone tree; current first-run authority and frozen reviews
are available. They are not silently recreated.

The source role is `X1.3 → MCLK_SRC → R3(68ohm) → MCLK_FAN →
R4/R5(56ohm) → U1/U2.15(SCKI)`. Pod R3 is a separate10kohm position and must
not change. R3 remains one per carrier, zero per pod:1×5+0×10=5 installed;
no spares/attrition are assumed. Both branches and all eight-channel functions
remain unchanged.

Primary retained evidence is under `02_parts/first-run-r3-evidence/`:
`AOA0000C304.pdf` (May29,2025), `DMM0000COL17.pdf` (land guidance,Dec24,2025),
`DMM0000COL14.pdf` (solder guidance), exact maker HTML and filtered lifecycle
list. URLs/hashes and exact supplier observation are in `observations.json`.
Maker identity lacks supplier's hyphen, with matching exact attributes and
supplier link to the same maker family. The exact maker list supports Active;
the family's NRFND warnings apply to other series, not ERJ3EK.

The retained maker sheet supports68ohm±1%,±100ppm/K,0.1W at70C,75V limiting
element voltage and−55..155C category range. The case-temperature restriction
and derating above70C remain. Panasonic max body1.75×0.95×0.55mm exceeds old
Vishay max1.65×0.95×0.50mm. Minimum bottom termination is0.15mm. Nonpolar0603
is unmarked. Its separate endurance test allows±2% after1000h at70C/rated
voltage with1.5hON/0.5hOFF; solder-heat allows±1% under its own test.

## Clock/resistance and power judgment

Changing maker while preserving resistance does not change the intended clock
topology. Initial+temperature sensitivity from25C over−20..60C is about1.455%
high using100ppm/K. This is an arithmetic engineering sensitivity, not a new
guarantee outside a manufacturer's specified test basis. Multiplying initial,
temperature and the separate2% endurance limit gives3.484%; multiplying the
separate solder-heat1% as well gives4.518%. **Neither multiplication is a
combined-stress guarantee**; neither establishes a mission duration. The old
±4% sweep was a prototype sensitivity, not a Vishay lifetime certificate.
Do not relabel it as a Panasonic guaranteed drift bound, or convert1000hours
into a shortened intended service life.

I recommend retaining that conditional prototype posture, with this stronger
R3-specific stress evidence: `check.py` independently extracts the accepted
LS44 clock graph, normalizing only leading-slash net names, and reruns the
retained MNA model with **R3 independently±6%, R4/R5 independently±4%**. These
are design sensitivities, not new part ratings or maximum lifetime claims.
The exact source hash is
`bbb12bcd67bf42567a30900708d26a1cae0b979d3c319874c4cd82e7b913a0c4`.
All nine clock lands,32.115128mm F.Cu and zero clock vias remain. The128fast
and48slow cases span both retained7628A spacing sensitivities and asymmetric
receiver loads. Results in `v2-clock-sensitivity.json`:

- Maximum sampled physical SCKI overshoot26.254mV; finer sampling/line mesh26.226mV.
  Adding the existing SINGLE100mV combined reference allowance remains below
  the300mV physical-pin excursion allowance in these cases.
- Minimum modeled high/low valid dwell24.803/33.120ns; maximum sampled midpoint
  skew0.366ns. These are not invented SCKI minimum-pulse specifications.

The accepted LS20 prototype rationale therefore remains coherent for this
replacement. Keep local3.0..3.6V rails,100mV combined residual allowance,
named7628A construction/no-substitution controls and all first-article
rail/clock/startup/continuous-capture falsifiers. The slow source is an
extrapolation of8ns at15pF, not a30pF timing guarantee. The model retains its
0.5nH resistor allocation, not a Panasonic RF parasitic guarantee. Ideal-source
X1 pad peaks remain model sensitivities, not observations. No source-current,
PDN or field-extracted simulation is claimed.

There is no added DC shunt. The30pF/3.6V/12.288MHz capacitive energy screen
gives4.778mW total RC loss, under4.8% of0.1W even if assigned wholly to R3.
This supports the ordinary low-energy clock-damping application, not a proof
of repetitive-pulse or oscillator-current maxima. Nanosecond instantaneous
power may exceed the continuous rating; no special pulse rating is inferred.
Inherited waveform/power qualification remains. RCWV=min(sqrt(P×R),75V)=2.608V
for steady DC across68ohm; retain25V as the circuit's selection field only,
never as permission for25V continuous across this resistor. No continuous
clock high places3.6V across a series resistor into a capacitive receiver.

## Native land, bottom contact, paste and larger body

Read-only LS44 load confirms R3(88.4,80.15)mm/90degrees, pad1`/MCLK_SRC`,
pad2`/MCLK_FAN`; pads0.80×0.95mm, center spacing1.65mm, innergap0.85mm,
span2.45mm. They are roundrect with0.20mm corners. Native courtyard2.96×1.46mm
contains the new envelope. Loading pcbnew prints three inherited property-enum
assertions but succeeds; this is not a fresh DRC run.

Panasonic's recommended example is gap0.7..0.9,span2.0..2.2,width0.8..1.0mm.
Our gap/width conform, span is0.25mm above the example maximum. This is an
explicit guidance deviation, not an absolute geometric rejection. Each axial
pad interval is0.425..1.225mm from center. At centered placement both minimum
0.15mm bottom termination intervals lie axially on these pads throughout
bodyL1.45..1.75mm. The larger toe extensions remain symmetric; they do not
create a missing heel contact or polarity/rotation change. Maxbodywidth0.95
has no full-width pad reserve; do not claim a guaranteed side fillet.

The finite contact check goes beyond bounding rectangles: under the EXISTING
radial0.10mm/total3D1degree pose cap, a conservative maker-box displacement
bound is0.119852mm. Each minimum termination contains a central0.15×0.25mm
strip. That strip stays inside actual roundrect copper's central straight
region (halfwidth0.275mm), with≥0.030148mm axial and≥0.030148mm lateral
reserves. This proves positive bottom copper overlap at these finite extremes,
not full-width wetting or guaranteed solder-process yield. Seating/contact
requirements are conjunctive and not waived by a permissive model witness.

Retain standard symmetric copper/paste openings; do not shrink pads or reroute
automatically to match an example span. The longer lands can change solder
volume/fillet; carry exact Panasonic identity and its reflow limits into the
assembly process, including maximum two reflows and compatible terminal
temperature/profile. Stable wetting, no bridge/tombstone/crack/lift and actual
seating remain existing process/inspection obligations. No new minimum lot,
destructive test, vendor approval claim or completed assembly is invented.

## Mechanical model delta and source integration instructions

The old R3 model1.70×1.00×0.65mm fails to cover new maxL1.75. Do not reuse it
under a Panasonic name. `model-proposal.json` provides a proposed replacement
**1.80×1.00×0.65mm** drawing-envelope, with maker-based contacts±0.65mm
(`Lnom/2−bnom/2`), not copied±0.825mm land centers. Keep0.27mm nominal
contact matching tolerance as a registration screen; finite copper overlap
above is separate. This does not relax actual pose/contact limits.

The new envelope at the exact pose hasXY[87.9,79.25,88.9,81.05]. Against every
other mounted carrier envelope in the accepted scene, conservative XY-box
separation minus BOTH existing finite radial/3D-rotation motions remains
positive; nearest is R5≥0.358136mm. Disjoint bounding-box bounds are sufficient
here because positive lower bounds do not assume curved-shape interiors.
No curved/intersecting box has been treated as a passing solid. The eventual
owning registered scene/STEP/views and assembly admission must incorporate
this largerR3 model; this calculation does not issue that acceptance.

Coordinator edits recommended, not performed by this helper:

1. NewP040 dossier is appropriate; leave historicalP038 unchanged. Bind exact
   PanasonicMPN/maker,68ohm±1%,0.1W,±100ppm/K, maker documents, five-piece
   quantity basis and current exact supplier observation. Link R3 only.
2. In adopted successor `author.py`, split the loop's Vishay note so R3 says
   Panasonic while R4/R5 remain Vishay56ohm. In successor `ordering.json`,
   change carrierR3 only; regenerate native/PDF/netlist/BOM/ERC via actual
   producer and verify pin/value/geometry deltas. Preserve25V selection caveat.
3. Bind population/BOM/consignment and carrierR3 to newP040/model key; instantiate
   `model-proposal.json` under that key. Update assembly maker evidence/model
   membership and replay exact registered scene; never edit old accepted scene.
4. Reopen affected sourcing, schematic, placement/mating, routing/layout and
   fabrication/assembly/release dependencies through their owners as required
   by changed exact source/model/5+10 subject. Reuse unchanged geometry only
   with explicit current evidence; do not relabel historical receipts.

All strict current custom controls remain, especially PicoD1-only removal,
pool/relief/contact/seating, finished holes/annuli, RJ/DC prepared mounts,
finite accessory-service/underside zones, exact stack and no substitutions.

## Evidence correction, availability and remaining claims

Author calculation v1 was retained but is superseded: it proved overlap with
the pad bounding rectangle using a0.60mm strip, without accounting for rounded
corners. The corrected `v2-*` evidence uses actual0.20mm corner radius and a
0.25mm strip. Clock numerical results are unchanged; only v2 contact proof is
recommended. This was caught within the same bounded author attempt.

Availability uses the retained exact JLC lookup(no match, not zero stock) and
the exact DigiKey1746805 opened offer64,642 versusneed5; this author reopened
that exact page and observed the same count. Direct rawHTML download403 is
disclosed; `observations.json` is browser fact transcription, not rawHTML.
No broad stock search or alternative part selection was performed. Unreserved
stock is adequate design evidence, not JLC allocation/private-library arrival,
feeder/attrition sufficiency or order permission.

Remaining unperformed work is independent review of this author disposition,
coordinator source/dossier/model integration and owning affected-stage replay/
admission. Existing physical/firmware/environmental qualification remains at
its original lifecycle boundary, not moved before prototype fabrication.
No known presentR3 contradiction is being deferred to those later tests.
