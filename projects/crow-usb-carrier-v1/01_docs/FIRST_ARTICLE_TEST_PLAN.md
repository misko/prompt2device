# Crow USB carrier — first-article test plan

Status: **DRAFT, not executed**. This plan defines future physical verification
for the new carrier. It does not authorize fabrication, ordering, firmware
creation or programming. It must be completed against the final reviewed board,
BOM and power contract before a powered test is released to an operator.

## Test admission and records

Identify board serial/revision, source commit, native board and schematic
hashes, assembly population, component substitutions, supply, cables, probes,
instrument calibration and ambient temperature. Record raw measurements and
waveforms with those identities; a photograph or successful USB enumeration
cannot substitute for electrical or audio measurements.

`03_src/rules/first_article.yaml` is intentionally absent during design. Before
applying power, create it from the exact released CPL, exposed-pad population,
closed numeric probe ranges and reviewed bench-supply current limit. Record
physical measurements in `01_docs/journal/first_article.json` and run the owning
first-article gate. The current limit must follow the closed startup/fault
analysis; neither the 4 A input fuse rating nor the quiet-rail 250 mA allocation
is a valid substitute. Missing card data keeps first-power admission incomplete.
This physical first-article gate is separate from schematic and layout design.
The unresolved power, connector and thermal obligations must be reviewed before
this plan becomes an approved test procedure.

## Unpowered inspection

1. Verify the exact installed BOM, polarity, XU316 exposed-pad assembly,
   TPSM module orientation, USB receptacle shell stakes, converter inductors,
   fuse identities and all analog isolation parts against the native assembly
   drawing. Inspect fine-pitch joints and exposed pads with the appropriate
   inspection method for the final assembly process.
2. Confirm all eight RJ45 connectors use the Crow power/audio pinout; they are
   not Ethernet or PoE ports. Verify their channel-to-ADC mapping against the
   source, including the first four channels' reversed ADC numbering.
3. Measure each supply-to-ground resistance after the instrument reading
   settles. Record diode-mode polarity and discharge state. Low core-rail
   resistance alone is not a diagnosed short; use the reviewed numeric test card.
4. Confirm USB shell continuity to GND and RJ45 shells to CHASSIS, with the
   intended separation between those domains. Confirm USB VBUS is not wired
   as the carrier/spoke supply. Check both Type-C orientations' D+/D- paths,
   Rd resistors and ESD device pin connections.

## Carrier power and shutdown

Start with no USB cable or spokes attached. Apply the reviewed current-limited
external input and record startup waveforms at input, protected input, parent
5 V, all three digital rails, quiet ADC rail and reset/enable nodes. Verify
rail limits, overshoot, sequencing, reset release and steady consumption using
the final power contract. Do not interpret repeated brownout caused by an
unqualified bench limit as a functioning power sequence.

Repeat at the adopted input-voltage corners and intended ambient extremes.
Exercise controlled input removal, slow brownout and restoration. Capture the
held analog rail, ADC reset, clock/data input levels and discharge behavior.
Confirm that input levels remain within each receiving device's supply-domain
limits while its rail falls. Measure stored-energy discharge and inspect the
input fuse, PFET, converter, quiet regulator and dump circuit temperature.

After unloaded power passes, attach one representative spoke and then all eight
with the supply off. Verify the declared concurrent 0.1 A-per-spoke delivery
case at each carrier connector's power-contact bank: 10.8–13.2 V is the current
requirement, before the mate and cable. Record contact, copper and protection
drops separately. Cable-end performance requires the separate cable/load model.

## USB power-state matrix

Test carrier-only, Pi/USB-only, both powered, and transitions between them,
including removal of either supply and both Type-C insertion orientations.
Record VBUS, VBUS presence indication, XU reset and relevant rail/input currents.
Verify the source-defined no-backfeed behavior with current measurements rather
than continuity alone. USB GND joins the Pi and carrier reference; no galvanic
isolation is claimed.

Perform populated-neighbor mating and removal checks with the selected power,
RJ45, USB and JTAG mates. Confirm grip, latch and cable access, board support,
strain relief and permissible bend/straight-run geometry against the completed
connector contract. Neither this prose nor a nominal body gap qualifies fit.

## Clock, programming interface and audio

Hardware power checks may precede firmware. USB audio and generated TDM timing
checks require a separately authorized and identified board-specific image;
none is presently supplied or claimed tested. Verify the complete JTAG cable,
adapter, voltage reference and end-to-end pin mapping before programming.

With that prerequisite met, capture the actual ADC pins and translated XMOS
side. The required operating point is eight synchronous channels at 48 kHz,
24-bit samples carried in eight 32-bit slots: 24.576 MHz MCLK and 12.288 MHz
BCLK. Check clock levels, ringing, setup/hold, FSYNC pulse width and framing
against the exact current ADC and translator specifications. Inspect the FSYNC
extender at its input and final ADC output; a nominal frequency is not a timing
margin measurement. Repeat during reset, ADC-rail brownout and restoration.

On the Raspberry Pi host, record USB speed, descriptors, channel count, sample
format and rate, selected image identity and capture software configuration.
Confirm high-speed operation and simultaneous eight-channel capture. Apply a
known signal to each physical spoke in turn to prove channel/slot mapping, then
a common synchronous stimulus to all eight to check sample alignment. Measure
noise, gain, distortion, clipping and bandwidth against the retained Crow audio
requirements; unresolved numeric limits must be filled before acceptance.
Record sustained-capture errors or dropouts and retain the source audio data.

## Signal integrity, temperature and faults

For the exact manufactured stack, verify the USB pair's impedance against the
90 ohm ±10% requirement and perform the applicable high-speed eye test. Bind
coupon/TDR and eye evidence to the actual stack, copper/mask process and
production width, rather than treating the nominal vendor solve as a test.

Measure thermal behavior at simultaneous full load and maximum specified
ambient. Apply the final converter efficiency/loss model consistently: the
current 85% parent-converter screen at 5 V/1.9 A implies 1.67647 W loss and a
32.807 °C/W maximum effective junction-to-ambient resistance for 70 °C ambient
and a 125 °C junction ceiling. This is a design obligation, not a measured value.

Fault testing requires an approved prospective-current, time/current and
let-through-energy envelope first. A passive PPTC trip current is not a hard
current ceiling. Do not infer an arbitrary short-circuit test from the nominal
spoke load or run a fault beyond the qualified component/fixture limits.

## Acceptance

Every required result must bind to the tested revision and pass its stated
limits. Unmeasured, stale or failed items remain open. Passing one test family
does not imply another: electrical power, connector service, USB signaling,
audio performance and physical thermal/fault qualification have separate
measurements. Reopen affected tests after any material source or assembly change.
