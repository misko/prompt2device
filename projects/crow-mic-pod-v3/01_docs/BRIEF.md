# brief: crow-mic-pod-v3

status: in-progress
prompt_sha256: a6fcb7d5b8465bc23415c7d5f9381b368f12d69455da135d8b6b0b1cb89965b3
current_release: no
order_status: DO-NOT-ORDER

## Original prompt

<!-- prompt-verbatim-begin -->
/pcb-design please help me design a star shaped distributed microphone array to record and isolate which crow is talking from my roof

<!-- prompt-verbatim-end -->

- date: 2026-09-01
- channel: `/pcb-design`

## Current source interpretation — 2026-09-12

The later user-approved factory RJ45 direction supersedes the spoke
Micro-Fit/Belden/Cat5e assumptions retained in the dated log below. The current
source selects Würth 615008160221 and Weidmüller 8909650150 Cat6A cords,
with the exact pin map in `03_src/rules/spoke_interface.yaml`. This is
source adoption, not hardware qualification or release acceptance.

## End goal — definition of done

A reviewable, regenerable roof microphone pod accepts the protected shared
spoke supply, biases one exact electret capsule, and sends a low-impedance
active-balanced analog signal to the central eight-channel carrier. The
array has a nominal 4 m acoustic radius / 8 m diameter; the selected complete
cord is 15 m, without claiming that cable distance qualified
before measurement. Exact cable/capsule/enclosure assembly, schematic/layout
reviews and fabrication gates precede a separately authorized prototype order
under ADR0005. Measured first-article evidence precedes tested/deployment claims.

| # | Criterion | Source | Status |
|---|---|---|---|
| G1 | J1 implements the shared factory RJ45 spoke contract: pins 1/3/7 `12V_POD`, 2/6/8 `GND`, 5 `AUDIO_P`, 4 `AUDIO_N`, shell 9/10 isolated `POD_SHIELD`. | A1 | unmet |
| G2 | The pod accepts 10.5–13.2 V at J1, stays within the 0.10 A allocation and derives a protected, quiet nominal 5.02 V rail. | A1, A2 | unmet |
| G3 | One AOM-5024L-HD-R capsule operates at the characterized filtered bias condition through a hand-wired landing; no undimensioned direct-placement pitch is invented. | A3 | unmet |
| G4 | The exact OPA1679 topology provides 18/11 V/V differential gain, nominal 2.5 V common mode, complementary 100 Ω legs and no more than 1.2 Vrms differential output over the admitted signal range. | A4 | unmet |
| G5 | Gain, phase, noise, common mode, CMRR, stability, polarity and clipping pass through the exact selected 15 m cord into the carrier receiver; any shorter installed cord requires exact-source adoption and qualification. | D1, D2, A1, A4 | unmet |
| G6 | Capsule mount, port, wire dress, strain relief, windscreen, drainage, condensation control and connector service are qualified in the exact enclosure. | A3, A5 | unmet |
| G7 | The pod contains no MCU, ADC, USB, Ethernet or PoE circuitry and requires no project-authored firmware. | D1, D4, A1 | met — [architecture boundary](ARCHITECTURE.md) |
| G8 | The candidate remains FIRST-ARTICLE-ONLY / DO-NOT-ORDER until sourcing, JLC, review, cable/audio, mechanical, environmental and hardware-evidence holds close. | D5, A5 | met — [maturity and findings ledger](findings.yaml) |

## Log

### D1 — 2026-09-01 — user directive
> i think we can do 8m radius! can we have the array be planar? identity needs to persist across recordings of 120s long , simultaneous crows do not need to be separated, short internal usb is acceptable

Impact: permits a planar array and short internal USB, removes simultaneous-
source separation from acceptance and supplies a provisional size later
corrected by D2.

### D2 — 2026-09-01 — user directive
> 8m diameter

Impact: corrects only D1's array dimension to 8 m diameter / 4 m radius.

### D3 — 2026-09-01 — user directive
> must recognition persist only across consecutive 120-second files, or across separate visits/hours/days and different perches? - no , it must only persist in the 120 second file if the crow does not move much

Impact: limits identity to an anonymous stationary-source signature within one
120-second recording; no cross-file or changed-perch identity is required.

### D4 — 2026-09-01 — user directive
> Great sounds good lets use the rpi5 with this, please continue design!

Impact: selects Raspberry Pi 5 as the roof-appliance host and authorizes
continued design under the accepted network plus short-internal-USB boundary.

### D5 — 2026-09-01 — user directive
> Great! Lets make a new branch for this board dev, and lets finish the board and get a release ready

Impact: authorizes the board-development branch and a governed release target;
it does not authorize ordering, production or fabricated-hardware claims.

### A1 — 2026-09-01 — assumption (not asked)
Assumed: each roof node is a passive analog pod on one exact four-wire
Micro-Fit/Belden home run. PoE, Ethernet, USB, Raspberry Pi and ADC remain in
the central roof appliance; the installed harness is 4 m and 15 m is an
electrical qualification boundary, not a qualified maximum.
Authority: P and D1/D2 delegate the star-array electrical partition.
Escalate if: the pod must itself digitize, network or receive PoE, or the cable
and connector family changes.

### A2 — 2026-09-01 — assumption (not asked)
Assumed: a pod-local PPTC, low-leakage series reverse-polarity rectifier,
bounded protected-node pull-down and shunt TVS precede
an adjustable TPS7A4901 nominal 5.02 V quiet rail, within the shared 0.10 A
continuous pod allocation.
Authority: A1 delegates a protected low-noise analog implementation.
Escalate if: the admitted supply envelope, protection posture, current or
thermal boundary changes.

### A3 — 2026-09-01 — assumption (not asked)
Assumed: use exact capsule AOM-5024L-HD-R at its characterized filtered nominal
3 V / 2.2 kΩ bias condition. The capsule is hand-wired to MK1 because the
official drawing does not dimension terminal pitch; its acoustic/mechanical
integration belongs to the enclosure.
Authority: P delegates microphone selection while forbidding invented geometry.
Escalate if: capsule identity, direct mounting or acoustic enclosure changes.

### A4 — 2026-09-01 — assumption (not asked)
Assumed: one OPA1679 creates buffered VREF and complementary active-balanced
outputs with 18/11 V/V differential gain, nominal 2.5 V common mode and 100 Ω
series impedance per leg; the pod is DC-coupled and the carrier owns input
coupling capacitors.
Authority: A1 delegates the analog interface and D5 requests completion.
Escalate if: gain, output ceiling, common mode or carrier receive topology changes.

### A5 — 2026-09-01 — assumption (not asked)
Assumed: plan ten first-article pods—eight installed plus two matched spares—
but keep every artifact DO-NOT-ORDER until live JLC, exact assembly, cable,
capsule/enclosure, audio, thermal and roof-environment holds close.
Authority: D5 delegates release preparation, not order or production approval.
Escalate if: build quantity or lifecycle target changes.

### D6 — 2026-09-12 — user directive

> Great lets do it!

Context: approval of the proposal to use RJ45 ports and commercially
preterminated shielded Cat6 patch cords between carrier and pods. Replace the
pod spoke connector together with the carrier ports and parent interface.
Balanced analog audio, 12 V supply, 0.10 A maximum continuous pod current,
15 m design length and outdoor service requirements remain. Ethernet and PoE
remain false. Exact parts and all affected source and native-artifact gates
must be accepted before a new release; existing sealed entries stay immutable.

## Decision register

| id | decision | decided by | depth |
|---|---|---|---|
| 0001 | Original four-wire interface decision; connector/cable choices superseded by ADR0007, analog/power function retained. | agent (A1 / P-delegation) | [interface ADR](decisions/0001-four-wire-analog-spoke.md) |
| 0002 | Protect the admitted 12 V input and derive a quiet linear nominal 5.02 V rail. | agent (A2 / P-delegation) | [power/protection ADR](decisions/0002-protected-quiet-five-volt-rail.md) |
| 0003 | Use an OPA1679 active-balanced 18/11 V/V topology at nominal 2.5 V common mode. | agent (A4 / P-delegation) | [analog ADR](decisions/0003-active-balanced-audio.md) |
| 0004 | Use reviewable bare analog ICs because available modules do not preserve the exact interface. | agent (A1, A2, A4 / P-delegation) | [integration ADR](decisions/0004-bare-ic-exceptions.md) |
| 0005 | Separate prototype design and authorized ordering from subsequent physical qualification; current artifacts remain DO-NOT-ORDER. | agent (A5 / D5-delegation) | [lifecycle ADR](decisions/0005-first-article-only-release.md) |
| 0007 | Adopt exact factory RJ45 analog/power spokes and isolated shield island; physical qualification remains owed. | user D6 / independent source review | [RJ45 ADR](decisions/0007-rj45-factory-spoke.md) |
| 0006 | Permit design-only continuation from an exact-code public catalog screen while keeping authenticated JLC allocation mandatory for order readiness. | agent (A5 / D5-delegation) | [sourcing-boundary ADR](decisions/0006-public-catalog-prelayout-only.md) |

## Spec tensions

| id | requirement | standard/part cap | how honoured | ADR | user-flagged |
|---|---|---|---|---|---|
| T1 | One complete factory RJ45 analog/power cord per microphone. | Power and differential audio share a cable; 15 m adds resistance, capacitance, pickup and connector/environmental obligations. | Freeze exact pin/cable identity; keep POD_SHIELD isolated from GND and qualify the exact factory 15 m cord; installed-length alternatives require their own identity and evidence. | [0007](decisions/0007-rj45-factory-spoke.md) | yes — first-article hold |
| T2 | Quiet analog supply from 10.5–13.2 V input. | A linear regulator trades low switching noise for worst-case dissipation and dropout; PPTC/diode protection consumes headroom. | Use TPS7A4901 with cited support network and measure regulation, noise and temperature over input/load corners. | [0002](decisions/0002-protected-quiet-five-volt-rail.md) | yes — first-article hold |
| T3 | Active-balanced output below the shared 1.2 Vrms ceiling. | OPA1679 input common mode stops roughly 2 V below the positive rail, constraining non-inverting alternatives and headroom. | Keep signal nodes near VREF with the selected inverting/complementary topology; qualify common mode, clipping and THD+N. | [0003](decisions/0003-active-balanced-audio.md) | yes — first-article hold |
| T4 | Reviewable fixed-gain, low-noise pod. | Common modules expose undocumented grounding/gain/noise or the wrong single-ended/bipolar interface. | Use exact bare OPA1679/TPS7A4901 circuits and retain their layout, bypass, stability and thermal responsibilities. | [0004](decisions/0004-bare-ic-exceptions.md) | yes — source review |
| T5 | “Release ready” while cable, enclosure and hardware evidence remain absent. | Clean source/ERC/DRC cannot prove assembly, acoustics, environment or production readiness. | Permit only a DO-NOT-ORDER first-article candidate until the findings and controlled bench plan close. | [0005](decisions/0005-first-article-only-release.md) | yes — D5 boundary |

## Mating fact-lock

none — this board does not mate to hardware this repo did not design through a
CAD-consumed foreign dimension. J1 and its cable mate are exact sourced parts
governed by the shared spoke contract. The capsule is intentionally hand-wired,
so its undimensioned terminal pitch is not consumed by the PCB footprint; port,
wire dress, strain relief and enclosure registration remain physical holds.

## Commission fact-lock

| Fact | Value | Locked by |
|---|---|---|
| Output rail(s) / signal | Active-balanced AUDIO_P/AUDIO_N at nominal 2.5 V common mode, 100 Ω per leg and no more than 1.2 Vrms differential. | A4 |
| External outputs | One shielded 8P8C RJ45 spoke jack (eight signal contacts plus two shell pads) per pod; eight pods operate simultaneously in the system. | A1 |
| Spoke input | 10.5–13.2 V at pod J1 after cable drop, no more than 0.10 A continuous; input capacitance at most 47 µF and no hot plug. | A1, A2 |
| Duty | Continuous analog operation through each 120-second recording; simultaneous-source separation is not required. | D1, D3, A1 |
| Measurement plane | Pod J1 for supply and balanced audio; the exact selected 15 m factory cord is a separate system fixture, not included in the bare-PCB claim; any shorter cord needs its own adopted identity. | A1, A5 |
| Protection posture | Local resettable overcurrent, series reverse-polarity isolation, shunt TVS and audio ESD clamp; lightning/building-entry protection remains upstream/system scope. | A2 |
| Off control / storage | De-energize the carrier spoke before mating/unmating; no battery or other stored-energy source in the pod. | A1, A2 |
| Hard-cell parts | Exact AOM-5024L-HD-R capsule, OPA1679IDR, TPS7A4901DGNR, Würth 615008160221 jack and Weidmüller 8909650150 cord; JLC/process status remains mutable evidence. | A1, A2, A3, A4 |
| Integration posture | Passive analog pod; bare analog ICs are deliberate exceptions because reviewed modules do not satisfy the fixed balanced interface. No MCU, ADC, USB, Ethernet, PoE or project-authored firmware. | A1, A2, A4 |
| Operating environment | Powered operation and the component-level transient envelope are admitted only from -30 to +70 °C, bounded by the exact microphone specification. Enclosure solar rise, condensation and roof siting must be qualified to keep the assembly inside this range. | A3, A5 |


### 2026-09-12 — user-directed Cat cable change

User: “can we use cat cable instead of custom cable to run to pods?”
After the two termination options were explained, user: “Great! lets do it!”
Implementation assumption announced: outdoor shielded Cat5e bulk cable with
the existing Micro-Fit PCB connectors. The approval does not specifically
select RJ45; no RJ45, Ethernet or PoE conversion is inferred. See parent
ADR0012. All8 audio/power pairs and board pin identities remain unchanged;
only the prospective harness and its qualification contract change.


## 2026-09-13 — single-side SMD assembly directive

> Can we please make sure all SMD components are from one side? it will be tricky and costly to assign from both sides. We can expand the board a bit in size if tha thelps

Current requirement: all fitted SMD components on the top (F.Cu) side of both
carrier and pod, including consigned or manually fitted SMD parts. Board growth
is authorized where needed for placement, soldering and rework access.
Implementation and regenerated layout acceptance remain pending.
