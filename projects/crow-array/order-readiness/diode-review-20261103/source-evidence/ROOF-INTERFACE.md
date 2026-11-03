# Current roof/cable integration — repair 7

Repair9: electrical topology and this2.7k/coupling1–3uF protection model remain unchanged. CAPACITOR-MODEL.md supersedes earlier pod C1/C2/C4 allocations and records exact capacitor curve evidence plus revised VMID phase/startup sensitivity. No stage acceptance is implied.

Unaccepted prototype design. This supersedes the 1.8-kohm carrier calculation
in the retained `INTERFACE-DESIGN.md`; its other named assumptions still apply.
The original prompt and 12-V-only user decision are unchanged. The roof report
in `../../reviews/roof-interface-1.md` is research, not this implementation's
acceptance. In particular, its 5.5-V minimum-knee interpretation and negative-
shunt current-direction claim are not used here.

## Implemented electrical contract

Eight dedicated straight-through U/UTP copper CAT5e/6 cables, proposed maximum
6 m routed length each. Contacts: 1/2 differential audio +/-; 3/6 +12 V/return;
4/5 +12 V/return; 7/8 active-low buzzer/return. These are four intact pairs.
Parallel supply contacts and returns only at the board endpoints. No CCA,
Ethernet magnetics, PoE, crossover cables or network connection. Label enclosed
ports and cables `CROW POD — 12 V / NON-ETHERNET / NO PoE`; power off to mate.
Require <=0.5 ohm aggregate supply and <=0.5 ohm return at hot operation,
including contacts, and 100% cable continuity/pair/short checks after assembly.

The selected unshielded Amphenol RJHSE-5080 sits inside the enclosure. There is
no shell pin or cable shield bond. At each carrier and pod port an SP0504BAHTG
connects pin 2 to local GND, pin 1 to audio+, pin 3 to audio-, pin 4 to buzzer
control. Pin 5 is an unused protection channel, intentionally unconnected, not
a physical NC pin. The three shunts are on the connector side of the coupling
capacitors (carrier) and 1-kohm output resistors (pod). Give the device a short
low-inductance return to the connector return plane; do not route its discharge
through microphone/ADC reference traces. Final return-path implementation is a
layout requirement, not a completed placement claim.

Carrier input isolation is now **2.7 kohm, 1% per leg**, with the existing
grounded Zener and 2.2 nF filter. Pod isolation remains 1 kohm. No new rail
steering path is added; 12 V remains the sole operating input and the modified
Pico retains ordinary USB data and VBUS sensing.

## Current/history model and why the resistor changed

The reviewed prototype bounds are S=[-0.63,+4.23] V for the pod source relative
to carrier ground and P=[-1.1,+4.4] V for the ADC pin. They are extended diode/
temperature models, not all-temperature guaranteed clamp limits. For Vc=X-Y
across the carrier coupling capacitor, retain history [-5.03,+5.33] V. Let
T=P+Vc, giving T=[-6.13,+9.73] V. Connector node X is driven by S through the
pod resistor, T through the carrier resistor and passive shunts to local
grounds within +/-0.03 V. Memoryless passive shunts cannot drive X beyond the
extreme driving voltages. Independently charged cable capacitance initially
lies in the source envelope; its discharge is explicitly not credited with
the pod resistor. Thus max |X-T| is bounded by max source-to-T and ground-to-T
differences: **10.36 V**. No minimum positive TVS knee is needed for this bound.

With carrier Rc_min=2673 ohms, the branch ceiling is **3.876 mA** even when the
pod resistor is bypassed. Add a conservative 20 uA per-leg allowance for the
two connector shunts: **3.896 mA**. Two such currents into the required 330-ohm
1% sink predict **2.597 V** for the off pod rail, below the 3.6-V model ceiling.
At 3.4 V the sink's minimum 10.20 mA exceeds that total injection. The existing
50-mA/pod operating allocation retains ample margin for these leakage currents.

The capacitor-history invariant follows from the scalar RC equation:
dVc/dt=(X-T)/(Rc*C). At Vc_min, T=P+Vc_min<=S_min and the ground references are
above S_min; passivity gives X>=T, hence dVc/dt>=0. At Vc_max, T>=S_max and
the grounds are below S_max; X<=T, hence dVc/dt<=0. A capacitor initially
inside the interval therefore stays there under the bounded source/pin states.
Initial arbitrary external charging, a 12-V/PoE signal miswire and IEC surge/
ESD waveforms are outside this normal/off-state model. Existing filter-cap
discharge energy and device parasitics still require the named first-article
waveform check; this does not turn a scalar model into an ESD immunity result.

`roof_model.py` reproduces the ceiling, corroborates the invariant across
corner states and different shunt knees, and computes the loaded transfer.
It is not a SPICE-qualified device model or an independent acceptance check.

## Normal audio and control

Manufacturer SP05 Rev GD specifications are conditional on their stated test
conditions: do not reinterpret the 5.5-V standoff entry as a guaranteed minimum
knee. The prototype uses **10 uA maximum leakage and 100 pF per connected
channel at -20..60 C** as padded engineering allocations, not published maxima.
They must be falsified or confirmed on first articles. Typical published
capacitance is 30 pF; the model allows more and includes 336 pF cable pair
capacitance (6 m at56 pF/m), represented as672 pF to ground per differential
half-circuit. Confirm the selected cable's actual electrical specification.

Typical ADC10-kohm loading gives midband factor0.730, about0.59 dB below the
prior0.781. With effective coupling>=1 uF, grounded2.2 nF and the stated cable/
ESD capacitances, the half-circuit model gives -2.75 dB at300 Hz/1 kHz and
-3.14 dB at8 kHz. The added ESD capacitance contributes approximately0.52
degree incremental phase at8 kHz. These are model outputs, not measured SNR,
THD or phase matching. Differential resistor thermal-noise upper estimate over
300 Hz..8 kHz at60 C is1.024 uV RMS before ADC loading. No recording range,
24-bit ENOB or full-scale linearity guarantee is added.

At most20 uA combined modeled buzzer-line leakage drops its10-kohm pullup by
0.20 V. Keep the default-off PNP/MOSFET circuit; check actual hot leakage,
PNP turn-off and buzzer gate state during prototype qualification. Do not use
the TVS family name alone as proof of a system off-state margin.

## Roof/weather/grounding boundary

Use UV-resistant polymer enclosures with internal jacks, sealed strain-relieved
cable glands and drip loops. Target at least a rain/dust IP65 assembled housing;
if standing water/immersion is possible choose an appropriate IP67 assembly.
The bare jack is not weatherproof and a housing rating does not certify added
holes. Give microphone and buzzer separate sheltered acoustic paths, with a
specified acoustic membrane and repeatable cavity for the microphone. Verify
assembled ingress resistance, thermal limits and acoustic transfer after the
mechanical design and first article. Keep the proposed -20..60 C electronics
air limit through enclosure/shading design; rooftop sunlight is not ambient air.

USB joins Pi and carrier ground. An isolated12-V adapter does NOT make the
whole array galvanically isolated: the Pi and its other ports may bond to PE.
This conditional schematic is for one short, local installation with Pi and
carrier co-located. Before deployment the installer must verify the building's
lightning/bonding zone, Pi/PE connections and all cable routes. Cross-building,
cross-zone or separately earthed-metal connections require site-specific review
and possibly external SPDs/isolation; they are not silently covered. Keep this
deployment hold without demanding physical roof qualification before schematic
acceptance. Do not attach a shield to arbitrary logic ground to claim safety.

Existing SMBJ15A/fuse/PTCs provide limited local fault/pulse protection, not
lightning immunity; its pulse clamp can exceed the buzzer operating limit.
Component ESD ratings do not establish assembled-system immunity. Before
fabrication define the system ESD/EMC fixture, severity and recovery criteria;
perform those physical tests after first article. No purchases, fabrication,
physical tests or placement are authorized by this document.
