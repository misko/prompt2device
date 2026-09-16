# Isolated-input energy accounted; shutdown loading remains decisive

Subject: `c08ba9d2`, with no circuit, acceptance-limit, generated-board or pod
change. This is source-author engineering evidence, not an independent review,
source admission, or a release. The source suite's 250/250 PASS is INHERITED
from the preceding source-identical checkpoint; it was not rerun here.

## What changed in the analysis

The new averaged model explicitly includes nine physical states: local VIN
capacitance, buck-inductor current, raw capacitance, feed-inductor current,
OPA ceramic and bulk capacitance, held ceramic capacitance, and both separate
held bulk capacitors. It starts from a balanced, regulated equilibrium before
input removal. The shared spoke bus cannot drain the isolated VIN bank.

The bridge uses `I_VIN = duty * I_L`, including negative inductor current.
Its duty law is a declared controller approximation, not a calibrated AP63205
model. Unlike imposing an independent output-current response and an unrelated
input-power expression, this law transfers the same power at both ports.
With the source disconnected, the measured state trajectory must satisfy:

```
E = sum(C * V^2 / 2) + L_BUCK * I_L^2 / 2 + L_FEED * I_FEED^2 / 2
E(end) - E(start) + integral(all resistor/diode/control/load powers) = 0

delta(E_VIN + E_BUCK_L)
  + integral(V_RAW * I_L + R_BUCK * I_L^2 + V_VIN * I_controls) = 0
```

The second identity separately checks the signed converter port. Both are
physical accounting identities for the declared model; neither identifies the
actual silicon control waveform. Independent verification maps the saved
states back to each component and sums the port and loss integrals separately.

## Measured results and controls

MEASURED: 21 selected scenarios plus three convergence controls completed in
6.264 s, ending at 08:51:52Z. The matrix uses two local input capacitances,
four initial VIN levels, two baseline OPA loads, three added load pulses, and
two maximum-duty sensitivities. These are finite sensitivities, not an exhaustive
normal-operation or component-corner proof. RK4 at 100/50/25 ns and midpoint
at 25 ns agree within the declared 20 uV comparison limit.

All 24 total-energy and signed-port balance checks pass a 10 nJ numerical-error
budget. The largest independently calculated residual is 0.000319 nJ. Three
actual known-bad checks FAIL when VIN capacitance, buck inductance, or one held
bulk capacitor is omitted: residuals are approximately 95.220 uJ, 0.125 uJ,
and 421.554 uJ respectively. Numerical error is not a component uncertainty.

| OPA loading scenario | Local VIN capacitance | Minimum OPA voltage after trip |
|---|---:|---:|
| 110 mA constant | 13.77 uF | 4.513837 V |
| 110 mA constant | 37.95 uF | 4.521393 V |
| 130 mA constant | 13.77 uF | 4.494375 V |
| 130 mA constant | 37.95 uF | 4.503181 V |
| 110 mA plus 20 mA for 320 us | 13.77 uF | 4.493716 V |
| 110 mA plus 80 mA for 20 us | 13.77 uF | 4.509029 V |
| 110 mA plus 200 mA for 4 us | 13.77 uF | 4.511439 V |

The pulse starts at most one timestep after the interpolated detector crossing;
its finite duration is retained. The model stops 320 us after the crossing.
All selected VIN states remain above 4.496 V, inside the model's explicit
greater-than-3.5 V operating range. Maximum modeled reverse buck current is
122.240 mA, but its positive incremental-energy correction is at most
0.309 uJ over these intervals. Dropping that term merely because the external
input diode blocks the spokes is incorrect. It is internal energy exchange,
not indefinite spoke backfeed. Feed-resistor energy is at most 2.014 uJ in
these removal cases; this does not cover the separate precharge/restart event.

A separate 12-step bisection puts the declared model's 4.5 V boundary between
124.218750 and 124.223633 mA at minimum VIN capacitance. This is not a product
current rating or a manufacturer guarantee. The 130 mA cases are not proof
that actual amplifier outputs can sustain that load during the critical window.

## Consequences for the next source decision

CITED: [TI OPA1656 SBOS901C](https://www.ti.com/lit/ds/symlink/opa1656.pdf),
p7, specifies the 5 mA per-channel quiescent maximum with zero output current;
the short-circuit current is typical and scoped to one channel. Thus it cannot
close the dynamic-load question. The actual source has sixteen 10 ohm output
resistors, eight 15 nF differential capacitors, sixteen 680 pF feedback
capacitors, sixteen 1 nF ADC capacitors, and two buffered 4.7 uF reservoirs
behind 100 ohm resistors. Those paths and their pre-existing charge, reference
slew, isolation and reset timing must determine the next load/time analysis.

CITED: [Diodes AP63205 DS41326](https://www.diodes.com/assets/Datasheets/AP63200-AP63201-AP63203-AP63205.pdf)
shows the synchronous bridge. Its PFM description does not specify the entire
removal waveform. Switching ripple, bootstrap refresh, diode recovery, control
current corners and real transfer/return geometry remain unqualified. The
averaged duty/resistance/diode parameters are assumptions, not published bounds.

The existing scalar source screen remains 4.501285 V at its 110 mA OPA
allocation; at 130 mA the same arithmetic yields 4.480115 V. A hypothetical
31.1 kohm top divider yields 4.502723 V at 130 mA and a 4.839118 V maximum
rising threshold. A 31.2 kohm top instead exceeds the existing 4.85 V startup
ceiling. These calculations do not select a new resistor or justify changing
the threshold before the actual load history is established.

Next: use this signed-port/storage account in the correlated CT/DUMP_RC/NR/ADC
restart calculation, and bound OPA output charge versus time from the actual
network. A source correction must address a reachable failing case or a
coherently justified prototype budget, not merely optimize one sensitivity.
The earlier loose 0.7688 W sufficient inequality is not a measured resistor
failure, and the 5.79 A / 20.5 uJ precharge event remains a separate obligation.
Source engineering, regeneration/reviews, routing and release remain open.

## Reopenable evidence

The [durable outcome](../SOURCE-CORRECTION-20260909-isolated-energy-outcome.json)
retains both executed scripts, the independent audit, actual bounded logs,
all results, and 503 verified unchanged source/native/pod input hashes.
Size: 247,579 bytes. SHA256:
`85edf06eb70ba7c457ad8beffa18a734cbf07dedfdcb8ff8a0e1e5e5297b3b21`.

MEASURED closeout at09:01:06Z: compact handoff validation and the one-beacon
check both return0. The contracts audit returns1 with the identical complete
failure lines as the preceding checkpoint:2891 structural findings,16 in
this carrier, and zero untracked strays. No audit limit changed. Audit log
SHA256 `5a7c7be618908b2639e41a081c42067ca43ba1f9d30e140c2c92ab51623a6a2b`.
Source/native/pod diffs against c08ba9d2 are empty.

No account access, upload, order, push, native regeneration or release occurred.
TOP77/0.20 A bring-up, conditional TDM, physical, sourcing and publication
holds remain at their existing boundaries. No new user choice is required for
the identified source work.
