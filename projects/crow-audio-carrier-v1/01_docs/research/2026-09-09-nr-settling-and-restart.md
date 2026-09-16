# NR settling corrected; correlated restart remains a separate obligation

Source base: `86ca72eea2798ad0f8333c1d583ff78f05820c5d` plus the
checker/test correction bound by the retained outcome. No circuit, footprint,
generated PCB, pod release or acceptance threshold changed.

## Corrected calculation

CITED: [TI TPS7A92 SBVS318B](https://www.ti.com/lit/ds/symlink/tps7a92.pdf),
p14 Figure36 and p19 Equation5, distinguishes initial charge from final
settling. The source checker no longer calls the equivalent constant-current
charge interval a full ramp. Its former 3.9174124–9.9986061ms range is
unchanged under `NR_linear_charge_equivalent_ms`; the 10–90% screen remains
3.13392992–7.99888488ms. The existing linear-proxy acceptance limits remain
unchanged and cannot establish full settling within10ms.

MEASURED arithmetic: the new explicitly approximate two-phase calculation
gives5.882580645ms to97% using Equation5's linear approximation and
14.457737719ms for the typical280kohm/47nF tail from97% to99%, totaling
20.340318364ms. It omits the initial parallel-resistor contribution and
regulator-loop dynamics; it assumes initially discharged NR and tracking
feedback. This is neither an exact Figure36 simulation nor a guaranteed
maximum or a loaded-bank/restart verdict. The p5 typical250ohm discharge
specification belongs to OUT, not NR. The checker explicitly leaves maximum
settling and NR reset times unknown.

## Actual verification

MEASURED: all four new tests were first run against the actual old checker:
one failure and nine subtest/errors, including the false full-ramp label and
absent settling calculation. The first corrected run exposed a test constant
rounded too coarsely for its seven-place assertion; correcting that constant
produced4/4 PASS. The independent tail check integrates the RC differential
equation in100ns steps, rather than calling the producer's logarithm.
Invalid target/capacitance, proportional-capacitance scaling and unknown
qualification limits are also covered.

The full source suite passed250/250 in101.090s, ending08:33:08Z;
log SHA256 `ff0bab7141e7a3df07e4be650d7fc4f0e643b531ae38850f335fc051a0127796`.
The verifier compared old and new arithmetic at12 distinct parameter sets:
all non-NR fields, including every existing check result, are identical.
All503 pinned source/native/pod-release input hashes remained unchanged
throughout verification.
The live source-power command also returned
`PASS_CONDITIONAL_SCREENS` with `generation_admitted: false`.

The contracts audit at08:39:26Z returned rc1 with2891 structural findings,
including16 in this carrier: the complete structural finding lines are
identical to the pre-change baseline. Its two untracked-file notices name
this checkpoint's new report and outcome; no shared audit limit was changed.
Audit log SHA256
`6fc09f646dffe73a2d439e95ca8f859203c2c1b015921039cb2566e994765fd9`.

After source commit `7a1450f2`, the audit at08:41:22Z retained exactly the
same complete failure lines as the baseline and had zero untracked strays;
it remains rc1, not PASS. Log SHA256
`8ca81826456651ca8f9896558b0f7d211b4a3c9499e1e79046c9394e7e15ed96`.
The compact schematic-stage handoff was regenerated and validated rc0 at
08:41:23Z against current source, unchanged board and unchanged tools.
Validation log SHA256
`19e6c98afb8b36831707a49da56d0f2def636a919307ee1bbf4d4c021e6bf00d`.
That identity check does not admit generation or routing.

## What the public models can establish

MEASURED inspection, not SPICE execution: TI's public
[TPS389001 model](https://www.ti.com/lit/zip/SLVMBN4) uses a200ohm CT
discharge switch and retained CT state; its nominal model excludes temperature.
TI's [TPS7A9201 model](https://www.ti.com/lit/zip/SBVM668) excludes
temperature, quiescent and shutdown currents. Its NRSS branch has a100Mohm
bleed and controlled charging current, not an explicit active NR reset path.
Its internal reference limiter is not a physical NRSS shunt clamp. Thus
neither model supplies the missing guaranteed partial-reset timing.
Exact archive/member hashes and public-download logs are retained; vendor
model source is not redistributed in this project.

## Conditional restart charge study

MEASURED before this reporting correction:972 declared CT/DUMP scenarios,
with120 cycles each, plus a1200-cycle replay and1000 seeded variable pulses.
The module preserves CT/DUMP_RC state and charges only actual dump-release
events. Its selected three-capacitor discharge has an independent500,000-step
Euler control, constant-segment splitting control and no-release controls.

It deliberately restores ADC charge instantaneously at release. That is an
available-charge ceiling only for the selected RC scenario, not an actual
current waveform or an all-load bound. Logical SENSE pulses are inputs, not
proven accepted glitches or complete reachable supply histories. In particular,
the471mA case uses a1us logical fault and CT clamp equal to threshold; it does
not prove a real board fault. In the200ohm/1.28V-clamp subset with faults at
least10us, the largest selected estimate is58.887809mA. Neither subset closes
the whole-board energy/current-duration requirement.

The [durable outcome](../SOURCE-CORRECTION-20260909-nr-settling-outcome.json)
retains the executed scripts, actual result data, tests, failed attempts and
input identities. It is1,611,004bytes, SHA256
`37d520e3e5c5ffdb63a30f7e0d3c5bd18d8795641cff9dda73a3b57dd49eadb7`.
Source-engineering acceptance remains false. Next: correlate
local VIN/signed buck energy, partial-reset recharge and dynamic OPA loading
with the feed-current/thermal envelope, then regenerate and obtain fresh
schematic/placement/routing/release evidence. No JLC upload, account access,
order, push or release was performed; no new user choice is required for this
remaining source work.
