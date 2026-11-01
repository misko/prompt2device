# Local TI implementation — review packet, NOT accepted

Latest native candidate: `draft7/native/pcb/carrier/carrier.kicad_pcb`.
This is a quote-candidate engineering branch, not an issued routing/layout stage
or inherited release acceptance. No upload package is emitted by build_draft.py.

## Design delta

X1 becomes TI LMK6CE012288CDLFR. DLF0004A standard drawing 4225946/E, page60
of retained `lmk6c.pdf`: .9 x .65 mm lands, 1.5 x 1.65 mm pitch, .05 mm corner
radius; .9 x .6 mm paste, no hole in pad. Package max 2.1 x 2.6 x 1.0 mm.
Footprint uses TI top-view convention (pin1 upper left); placed at (86,85.5),
rotation90 degrees, giving pin1 lower left,2 lower right,3 upper right,4 upper
left on this board. Quote preview orientation still needs JLC confirmation.
Drawing's 125um stencil is an example, not approval of the inherited fabrication
process. Existing stencil controls remain; exact TI solder-volume/process review
must precede production. No unqualified old CTS 3D model is attached.

C4 becomes existing qualified family Samsung CL21B105KBFNNNE, 1uF50V X7R0805,
at (83.46,82.9),rotation0; sourcing need now14 across2carriers8pods (6+8), not2.
Public lookup `bypass-stock.json` records exact identity and large overseas/
presale pools, not job allocation. Reuse of existing MPN is not a guarantee of
job-specific supply. 0805 is larger than TI's preferred0402/0201; short same-side
power path and dedicated local ground via implement its bypass intent. Effective
capacitance at3.3V/temperature and actual noise remain prototype checks, not a
new exact-minimum1uF invention for a noncritical bypass recommendation.

Only X1,C4 footprints/source properties and their terminal escapes change.
R3/R4/R5 remain68/56/56ohm; both ADCs and other physical placements stay fixed.
Added GND spreader x86.825..89.7,y85.95..88.5 mm nominal7.33125mm2, full
pad connection, with two .6/.3mm through vias outside the X1 solder lands.
Additional C4 ground via at(85.7,82.9). Both GND inner planes remain intact.
No D2/D3 copper or new protection circuit is added. No pod design changes.

## Proposed bounded prototype power model — reviewer must disposition

Use192mA external3V3=110ADCpair+80clock+2pullups/OE, plus80mAPico;
350mA5V and680mAwhole-array12V. These are explicitly load allocations, not
guaranteed manufacturer maxima. Eight50mApods remain simultaneous; no double
counting their loads into carrier3V3. 70% conversion-efficiency sensitivities
and VSYS>=4V retain their model character. TRACO steady upper5.16375V and
transient/VSYS checks retain r7's explicit test-condition limitations.

Proposed useful-operation rail3.135..3.465V is a falsifiable prototype envelope,
NOT a measured or guaranteed module range. Rationale: nominal3.3V Pico regulator;
Richtek relevant typical buck plots near3.34V, small ripple and~80..100mV load
excursions; no intentionally boosted or independently sequenced3V3 source.
This replaces the old3.6V sensitivity only if reviewer accepts its evidentiary
basis. Do not interpret3.63V absolute max as permission to operate above3.5V.
Typical .65ms/no-load max1ms regulator soft start supports a model within TI
.1..100ms ramp; it does not certify cold or loaded startup. After first assembly,
scope actual pins during startup/removal/restarts and simultaneous full load;
reject rail excursions outside TI limits, nonmonotonic failed startup, unstable
clock, missing lock or capture errors. Preserve existing reset/reinitialization
requirement and do not promise valid audio during power transitions.

The proposed rail envelope is measured **VDD pin to local ground**, inclusive
of ripple and operating transients. The separate 100 mV clock-reference/noise
allocation is NOT an extra permitted VDD overshoot and cannot enlarge TI's
3.5 V operating maximum. Below the useful-operation range during ramp-down,
valid audio is not promised; absolute limits and reliable restart still apply.

Updated upstream dissipation: retaining the older conservative doubled fuse
resistance .306 ohm gives .68^2*.306=.14149 W. The 70%-efficiency U10 model
gives 5.16375*.35*(1/.70-1)=.77456 W. These replace .1215 W and .675 W in
the neighbor assessment. Retain the +20 C neighboring-heating allocation as
an explicitly unmeasured prototype sensitivity covering these modeled losses,
not a guaranteed unchanged temperature rise. The additional approximately
.12 W modeled neighbor loss must be included in full-load thermal validation.
Independent review found the existing 1 A fuse's continuous/temperature
derating supports the .68 A allocation; no larger fuse is proposed. Adapter
current-limit/inrush and fuse-trip behavior retain their existing falsifiers.

Thermal: LMK at .080A*3.465V=.2772W. Published128.1K/W reference-board metric
predicts115.51C with60C localair+20C neighbor allocation. Sensitivity160K/W
predicts124.35C, narrowly below125C;180K/W fails129.90C. New ground spreading
and vias are necessary practical implementation support, not proof of any
guaranteed theta. This is a candidate prototype model to review, not accepted
continuous-roof or lifetime reliability. Require measured full-load temperature
and capture stability before deployment; if the actual thermal behavior misses
the model, repair instead of silently reducing mission or ambient requirements.

D2: existing actual filled ground beneath its lands on both inner layers helps
spreading. Manufacturer225K/W requires much larger reference copper and is NOT
applied. First-order pad/trace-to-plane reasoning supports testing a conservative
400K/W whole-device sensitivity; at hotdrop.45V,.35A,60Cair+20Cneighbors gives
143C versus150C limit. .45V is room-temperature maximum at1A with typical hot
curves decreasing, used as an explicit lower-current hot prototype model, not
a guaranteed full-temperature limit. A .50V/400K/W corner reaches150C and fails
margin. Reconcile that uncertainty independently; do not disguise it as proof.
D3: .68A*.75V=.510W; retained110/130K/W+20C models136.1/146.3C;150K/W fails.
No source-fuse increase or demand-relief assumption is introduced.

## Executed / remaining

Jitter: no invented 12.288MHz maximum. TI figure6-24 supports order-of-1ps
typical integrated phase jitter near the low end, with its stated bandwidth.
As a separate sensitivity, 10ps RMS sampling uncertainty at the retained8kHz
audio-band edge gives -20log10(2*pi*8000*10e-12)=125.97dB jitter-only SNR.
This is not an oscillator guarantee, complete phase-noise integration or a
system SNR promise. The shared source remains common to both ADCs; later
acquisition/noise/phase stability tests remain necessary. Do not transfer the
500fs-at100MHz headline. No changed firmware clock ratio is proposed.

The completed expanded `draft7/clock-v2.json` includes both-low receiver
capacitance and both dielectric sensitivities:32fast/128periodic cases;
26.3525533pF load,1.620671mV physical overshoot,28.808318ns minimum high/low
dwell. This replaces the smaller first screen for this draft; sampling and
source-envelope limitations remain, and no required ADC pulse-width limit is
invented from these results.

draft5: 0 ERC findings; existing four disabled ERC checks unchanged. draft7
schematic bytes unchanged from draft5. draft7: strict all-severity/all-track
refill+DRC+native schematic parity: zero findings, opens, parity issues and
ignored DRC checks. Routing geometry with inherited .15mm annulus-gap allocation:
zero drill/SMD overlaps and zero gap findings. These are real checks, not stage
admission. Changed-layout clock analysis is in draft7/clock.json when complete.

The first authoring integrations failed on three KiCad/parser API mismatches
(symbol token form, field-map API, immutable UUID). No changed board was saved
in draft1..3. draft3's DRC against its stale copied board is NOT a passing new
design. draft4 found a local new ground-via/power-track short; draft5 causally
repairs that route and passes. draft6 was a zone-outline Python-binding failure,
not a copper finding; draft7 uses the inspected AddPolygon interface. Failed
directories remain history, not alternatives for upload. No exclusions added.

Need independent disposition on exact new native/model bytes: power envelope,
thermal support, geometry/return/loading, bypass and manufacturer lands/paste.
Only then consider a distinct r8 quote derivative with consistent revised
native/schematic/PDF/BOM/CPL/Gerbers and explicit non-production status. Missing
job lead time and existing process/stack/placement-preview holds remain.
