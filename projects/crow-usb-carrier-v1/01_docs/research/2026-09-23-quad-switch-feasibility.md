# Crow quad-switch candidate screen — 2026-09-23

**Result:** TI **TMUX1511PWR / JLC C2866750** is a stocked *candidate for
engineering qualification*, not an approved replacement. Direct JLC
component endpoint returned exact TI MPN, TSSOP-14, `stockCount=2987`,
`canPresaleNumber=2704` at **2026-09-23 03:26:33 UTC**; retained response:
`/tmp/crow-tmux-quad-raw/C2866750.json`. Four quad packages per board,
20 for five boards, plus the user-confirmed 150-extra requirement gives a
**170-unit threshold**, numerically covered. Exact `TMUX1511RSVR` /
C2673275, UTQFN-16 also showed 4,792 stock / 4,752 presale but demands
harder placement and escape. `TMUX1511RWBR` / C47068278 showed zero;
no `TMUX1511RUMR` result was found. Catalog stock and presale fields do
not guarantee PCBA uploader allocation or order-time availability.

## Why this is a real topology candidate

[TI SCDS390B primary datasheet](https://www.ti.com/lit/ds/symlink/tmux1511.pdf)
identifies four independent active-high SPST channels and a 5 V-capable
single supply. PW/TSSOP-14 top-view pin map is:

| Channel | SEL | S | D |
|---|---:|---:|---:|
| 1 | 1 | 2 | 3 |
| 2 | 4 | 5 | 6 |
| 3 | 10 | 9 | 8 |
| 4 | 13 | 12 | 11 |

Pin 14 is VDD, pin 7 GND. Each SEL=0 opens its S-D path; SEL=1 closes
it. There is no shared selector or throw that would short P and N. Map
one PW package to **two audio channels**: channels 1/2 of the IC carry
P/N of audio channel n, channels 3/4 carry P/N of n+1. Use four groups:
(1,2), (3,4), (5,6), (7,8), keeping each `FILTERnP/N` to its own
`ADCnP/N`. Tie all 16 SEL pins to existing `AUDIO_EN` and keep VDD on
**5V_LDO_HOLD** and GND on board GND. The present switch is on the held
5 V rail; `3V3_ADC` powers AFE and ADC. Supply each new package with
0.1 uF local bypass (four instead of eight existing C_ISO positions).
This is new native TSSOP placement/land, not a pin-compatible substitution;
ADC-pulldown/ADC-capacitor adjacency must be reworked for four packages
serving two ADC channels each. The existing joint ADC cell may make
particular pairs impractical; placement/route proof is owed.

## Actual voltage envelope versus TI limits

The current TSX biases each AFE input through equal 1 kohm dividers
from `3V3_ADC`, nominally **1.65 V**. The inherited pod ceiling is
**1.2 Vrms differential**, with unity-gain balanced AFE. For symmetric
opposite legs, peak differential is 1.2*sqrt(2)=1.697 V and each leg's
nominal sine lies **1.65 +/-0.849 V = 0.801..2.499 V**. The switch
is *after* OPA2320 and its filter, not directly on the pod cable. That
nominal sine fits TMUX1511's positive-only signal range. This calculation
is conditional on matched balanced legs, bias accuracy, and the AFE not
railing; it is not a fault or startup bound.

TI SCDS390B sections 5.1/5.3, 5.5 and 7.3 specify:

| Condition | Allowed signal-terminal voltage to GND | Consequence |
|---|---|---|
| VDD 1.5..5.5 V | **0..min(2*VDD, 5.5 V)** recommended | At held 5 V, 0..5.5 V; unlike TMUX2821, no negative operation. At VDD=1.5 V, ceiling is 3.0 V. |
| VDD <1.5 V, including off | **0..3.6 V** recommended; VDD=0 isolation to 3.6 V | Nominal AFE 3.3 V full-rail output has only 0.3 V headroom while off. |
| Any state | **-0.5..6 V** source/drain absolute maximum | An undershoot can violate recommended operation immediately and -0.5 V abs max. |
| Logic | 0..5.5 V recommended, VIH>=1.2 V, VIL<=0.45 V; fail-safe to 5.5 V while VDD=0 | The existing held-rail `AUDIO_EN` is a plausible control if its high/low transients meet these thresholds. |

TI's VDD=0 leakage limit is +/-2 uA through the specified range at
0..3.6 V (10 nA maximum only at 25 C/0..3 V); across the existing
10 kohm ADC pulldown that is up to 20 mV per leg under the specified
test condition. Off leakage with VDD present is +/-100 nA, up to 1 mV
per leg into that pulldown. RON is **4.5 ohm maximum** versus the
TMUX2821 family <=0.3 ohm to 125 C. A resistor-only screen against
10 kohm gives a <=0.045% gain term per leg at 4.5 ohm, but the actual
ADC input/filter loading can differ. TI specifies up to 1.8 ohm RON
flatness and 0.28 ohm within-package channel mismatch; this is
materially larger than the current switch. The TMUX1511 primary sheet
has **no audio THD+N limit** at Crow's 1.2 Vrms differential level.
Its 3 GHz bandwidth and low 3.3 pF typical on-capacitance do not prove
noise/distortion. Audio sweeps, gain/phase balance, isolation/crosstalk,
ADC settling and channel coherence need measured qualification.

**Blocking electrical uncertainty:** during held-rail fall/rise, the
3V3_ADC domain and filter/ADC capacitors may retain signal while
5V_LDO_HOLD drops. In the VDD=1.5..1.65 V interval the candidate's
`2*VDD` ceiling is only 3.0..3.3 V, and at all times it has a **0 V
negative-signal floor**. The old TMUX2821 guarantees -5.5..+5.5 V
operation and VDD=0 isolation over that range; TMUX1511 does not.
Pod hotplug/fault, unpowered OPA output behavior, shunt-capacitor
charge, overshoot/undershoot, and the ADC input may drive S or D
outside TMUX1511's envelope. The current source evidence does not
close this. Therefore stock alone does not authorize adoption.

## Required next proof before source edits

Measure or rigorously bound both S/D nodes for all eight cells at pod
1.2 Vrms maximum and at fault/hotplug, OPA/ADC power sequences,
`AUDIO_EN` transitions, brownout, held-rail decay, and reverse
energization. Compare every waveform to **0..min(2*VDD,5.5 V)** when
VDD>=1.5 V, **0..3.6 V** when VDD<1.5 V, and the -0.5..6 V absolute
limits, including negative ringing. Prove output loading and audio
THD+N at the admitted amplitude, not from high-speed bandwidth.
If any negative or >3.6 V off-domain transient cannot be ruled out,
retain the block and choose a protection-preserving switch or add an
explicitly qualified clamp/isolation stage. Only after that and exact
uploader stock >=170 should the four-package TSX/dossier/land,
`C_ISO` ownership, ADC joint placement, netlist and physical checks
be authored. Do not reduce the 150-extra requirement.

Sources: [TI TMUX1511 datasheet](https://www.ti.com/lit/ds/symlink/tmux1511.pdf),
[TI TMUX2821/TMUX2819 datasheet](https://www.ti.com/lit/ds/symlink/tmux2821.pdf),
[JLC TMUX1511PWR catalog](https://jlcpcb.com/partdetail/TexasInstruments-TMUX1511PWR/C2866750),
project `03_tscircuit/src/crow_retained_analog.tsx` (current analog path,
held switch rail, divider and ADC-side loads), direct endpoint responses
under `/tmp/crow-tmux-quad-raw/`.
