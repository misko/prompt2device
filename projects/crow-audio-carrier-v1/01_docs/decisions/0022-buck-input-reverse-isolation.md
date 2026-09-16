---
id: '0022'
date: 2026-09-09
status: proposed
tags: [protection, topology]
---
# ADR-0022 — Isolate the buck VIN bank from the shared spoke bus

Status: implemented source candidate; generation, independent review and
physical qualification NOT admitted by this decision.
Date: 2026-09-09
Authority: BRIEF A2/A3/A5; fresh PCB-ARCHITECTURE D-BACK at53465896.

## Decision

Insert one Diodes US1B-13-F, C154439, D_BUCK_IN: anode2 on
12V_PROTECTED, cathode1 on new12V_BUCK_IN. Move U_BUCK VIN3/EN2 and
ALL THREE10uF input ceramics to that local net. Leave Q_IN, all eight
spoke paths, the50mOhm OPA feed, D_HOLD and every signal component unchanged.
The diode drops only the buck input; it does not consume OPA supply headroom.

## Context

The old direct-VIN topology exposed raw/OPA hold energy to the shared input
bus through the buck's reverse port. AP63205 DS41326 Rev.3-2 p3 shows one
high-side Q1 and low-side Q2, not an opposed reverse blocker. Its p10
no-sinking statement is light-load PFM behavior, not removal/brownout
isolation. Section13 p14 forces Q2 on for220ns bootstrap refresh and uses
near100% Q1 duty in dropout. SW's VIN+0.3V absolute limit is not permission
to sustain a reverse-biased output. These establish an exposed path and a
credible mechanism; they do not specify an exact reverse-current waveform.

Crucially, the sealed pod source has its own M7 input diode and10.1uF
input capacitance. Normal removal from11.16V does NOT instantly apply eight
pod loads to the carrier's5V reservoir: their charged reservoirs keep those
diodes off. A slow preceding brownout can instead discharge each pod's
reservoir while the carrier still regulates5V. This creates a normal,
reachable enabled state with the spoke diodes able to conduct during removal.
An assumption that only110mA OPA load remains is therefore architecturally
unsound; Q_IN and D_HOLD do not cut this path.

The packet's conditional averaged L/C experiment includes the3.3uH buck,
three input ceramics (13.77uF minimum),141uF raw ceramics,94.9uF OPA
ceramics,470uF OPA reservoir/ESR, held bank, eight2.2ohm branches, each
pod diode and12.5uF effective reservoir.12mA/pod continued smoothly into
undervoltage is a NORMAL PROTOTYPE BUDGET, not a TPS7A49/OPA1679 guaranteed
undervoltage current. It conservatively offers pod output charge to the
input reservoir and contrasts a below-dropout load-cutoff case. Initial
held/OPA/inductor/pod states are balanced before removal; no arbitrary
independent precharged fault is introduced.

In the balanced experiment ordinary11.16V removal leaves OPA about4.5139V
after the100+220us response budget. A5.2V pre-brownout with12mA pod draw
gives about4.4769V and41.6mA spoke loading at raw trip; forcing the pod
undervoltage load off gives about4.5139V. This is a source-design
counterexample under declared budgets, NOT measured silicon or a claim all
parts fail. With the isolator, eligible5.85V/6V/11.16V pre-removal states
remain about4.5138V in the same model. At5.2V external input the isolated
raw rail is already below the supervisor threshold; that is an already-off
state, not an enabled-removal PASS. Slow brownout remains in the envelope.

## Options

| VIN blocker | Selection consequence |
|---|---|
| Existing B340A-13-F | Reject for this duty:20mA100C maximum reverse leakage exceeds the shutdown reserve. Keep existing D_HOLD unchanged. |
| Existing exact pod1N4007(M7)SMA | Low leakage and modest VF, but its archived JKSEMI dossier has no recovery-time/charge specification. Do not import generic1N4007 recovery numbers. |
| US1B-13-F | Select:100V,5uA25C/100uA100C,1V@1A25C and50ns at the specific25C recovery test. New exact dossier and public catalog identity retained. |

US1B's1A average rating is at75C terminal temperature with stated
half-wave conditions and20% capacitive-load derating. Its30A8.3ms
single-half-sine rating does not qualify arbitrary startup or repetition.
Stock D_SMA uses the same±2mm pad centres,1.5mm gap and6.5mm span as
DS16008 p4, with0.05mm extra width per pad edge. Native stock package/model
and polarity remain required; no alternate/sourcing allocation is authorized.

## Consequences

### Headroom, charge and conditional shutdown budget

Common protected floor remains11.16V; a1.3V engineering diode-drop allowance
leaves9.86V at the buck. The unchanged0.30A*5.15V/85% converter allocation
plus0.8A spokes and1mA controls is0.985345543A, below1A. Neither the1.3V
allowance nor VF1V@1A25C is asserted as an all-temperature silicon limit.
The isolated input bank retains its13.77uF minimum. Its upper initial
37.95uF model stores500.94uC/3.306204mJ at13.2V. This gives charge/energy,
not an inrush peak; the existing maximum path resistance is not a minimum
limiting resistance. Precharge and typical4ms buck charging remain unchanged
downstream. Diode cold/hot start current and repetitive thermal capture join
the existing first-article startup qualification, without demanding a board
before source generation under ADR0007.

The source checker now charges100uA diode leakage,1mA local buck/control
reverse-port draw and100nC external-diode recovery charge to the320us
shutdown screen. It obtains4.501285055V, only1.285mV above4.5V.
The latter two are explicit engineering budgets;100nC is NOT derived from
50ns and no manufacturer Qrr guarantee is fabricated.20mA leakage,2uC
recovery and2.1V forward-drop hostile probes fail. Local Q2 refresh losses,
reverse-port/control draw, diode recovery and actual trip/isolation timing
must fit these budgets; a topology-only PASS cannot qualify them.

## Connected start, precharge and rapid restart

The16 input limiters,500ohm bleed and50mOhm feed remain unchanged.
VIN isolation removes a dissipative/backfeed connection; it does not add an
independent source to the raw/OPA/held domain. The local VIN capacitor starts
from the actual input history and can exchange energy with raw through the
buck. It cannot continuously feed the shared spokes backwards after blocking.
Normal connected starts and rapid restart are not excluded.

The preceding coupled study's downstream storage identity applies only while
its named raw-boundary source/current assumptions are maintained:
Rfeed*integral(ifeed^2 dt) <= Wstart-Wend +0.768813437W*T
+1.05V*Q_LDO_excess. Extending that identity to the entire isolated-VIN circuit requires either
the signed buck-port energy integral or explicit VIN capacitor plus buck
inductor storage and converter loss. The input bank stores up to3.306204mJ
under the initial upper-capacitance model; this is finite but cannot be
silently omitted. The new diode cuts the indefinite shared-spoke backfeed
path, not this local exchange. Keep the observed5.79A/20.5uJ equalization event as an
event, not an instantaneous resistor failure; do not increase feed resistance.
A full discharged298.35ms CT wait does not bound every rapid-rearm interval.
Partial CT reset, dump state and partial ADC discharge remain correlated;
The prior study's112mA hypothetical uniform OPA-load budget is not an
all-state load guarantee. The remaining
source work is a reachable-state/current-duration extension of that identity,
not another alleged reverse blocker or a fabricated universal silicon model.

## Evidence and scope

See06_build/verification/reverse-port-20260909-53465896-r1/work/HANDBACK.md
for exact RED/GREEN/full-suite logs, model revisions and immutable packet
audit. Early model r1 had energy-accounting/regulation bugs and is explicitly
superseded; r2/r3 are refinement evidence, not final device validation.
This source correction changes no pod or release bytes. Generated schematic,
board, route reviews and release state are stale. DO-NOT-ORDER remains.
