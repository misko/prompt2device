# Coupled-power findings: fixed-source premise rejected, no thermal failure shown

Electrical subject: `f04370b66f829ca85ae108009b0e678cf51f8358`, unchanged
during this study. The concurrent WSLP model source correction is documented
in [its separate report](2026-09-09-wslp-model-source.md). No carrier native
generation, electrical substitution, pod change, release, upload or order occurred.

## What the fresh study established

The approximately 49 mV loaded precharge calculation is valid for its fixed
source scenario; it is not a bound on every qualified startup. For constant
R/C and load, the exact residual includes a weighted source-movement term:

```
e(T) = e(0) exp(-T/RC) + RI (1-exp(-T/RC))
       + integral[0,T] exp(-(T-s)/RC) dV_FEED(s).
```

The timer senses raw voltage, not the difference across R_PRE. A rise near
timer release need not have settled. A modeled 4.85 to 5.15 V rise over 250 us,
after at least 298.35 ms qualification, requires only 1.189013 A buck source
current yet produces a 5.7924 A reverse feed pulse in the passive zero-ESR,
ideal-bypass limit. It spends about 9.885 us above 4 A and deposits 20.465 uJ
in R_OPA_FEED over the modeled 200 us window. The 10 mOhm bulk-ESR sensitivity
also exceeds 4 A briefly. Both retain finite 10 nH feed inductance.

This falsifies the inference from the voltage/current/timer abstraction,
not an exact AP63205 silicon trajectory. The conservative pre-state omits
small extra charge from the preceding startup ramp; a complete causal
controller/startup prefix was not proved. It is not a demonstrated thermal
failure or an independently precharged-capacitor fault. Switching to 75 mOhm
solely to reduce this peak would also fail the existing conditional 4.5 V
shutdown screen; no resistor substitution was adopted.

Root independently reproduced the limiting case using implicit trapezoidal
integration and an analytic held-bank ramp response, separate from the
worker's RK4. At 2.5 ns steps: peak 5.792412505 A, integral i-squared dt
0.000430842849 A-squared-s, energy 20.465035 uJ. Two initial diagnostic runs
failed an overly tight absolute comparison against the 20 ns RK4 reference;
the retained final run checks four-significant-digit agreement and convergence.
These are numerical corroboration, not source or physical acceptance.

## Repetitive energy: useful bound, explicit remaining premises

With a common 5.15 V reference, rail-capacitor incremental energy plus feed
inductor energy gives the following sufficient bound under the handback's
explicit load, passive-steering and nonnegative buck-source assumptions:

```
R_FEED integral i_feed^2 dt
 <= W(start)-W(end) + 0.768813437 W * T + 1.05 V * Q_LDO_excess.
```

It includes both bulk RC branches and passive switching without inventing a
minimum switch resistance or restart interval. Its long-run resistor-only
screen permits at most 77.320536 mA of excess LDO charge throughput, under
those premises. This is not a demonstrated operating limit, a circuit defect
when exceeded, or a route/return acceptance proof. The earlier, looser 5.4 V
reference result is superseded, not an additional product requirement.

The assumed 112 mA uniform OPA draw cannot be inferred from the steady audio
average. Output charging and recovery need a dynamic bound. Likewise, the
TPS3890's typical-only CT discharge resistance does not establish a full
298.35 ms rearm interval after every brief reset. Partial CT reset and partial
ADC-bank discharge must be correlated rather than counted as fresh full cycles.

## Prioritized next engineering action

First resolve buck-port reverse current on ordinary J9 removal. Actual source
connects AP63205 VIN/EN directly to 12V_PROTECTED, which also supplies eight
spokes. Q_IN provides reverse-hookup protection, not a separately qualified
buck-input reverse blocker; D_HOLD isolates only the held LDO branch. A reverse
path through the buck could invalidate both a nonnegative buck-current premise
and the existing OPA-only hold-up load model. This is a topology question,
not a newly demonstrated destructive current or a requirement for vendor contact.

Use the actual 12 V input capacitance, 3.3 uH buck-inductor current, raw/OPA/held
capacitor states and spoke loads in a bounded input-removal calculation, with
public primary controller evidence. Then close the correlated CT/DUMP_RC/NR/
ADC recharge relation and dynamic OPA loading. Do not repeat an uncorrelated
startup grid or change hardware based only on the 5.8 A peak. A coherently
justified prototype budget remains possible; physical first-article testing
is not made a prerequisite to generate a candidate under ADR0007.

## Exact handback and verification

The fresh evidence-only worker terminated INCOMPLETE at 07:03:22.315415Z,
before its 07:07:02Z deadline. Root independently reopened it at
07:03:52.870343Z: strict task/subject/canonical-envelope binding matched,
483/483 immutable inputs verified, 480 baseline files compared, and only
seven known root model/status files differed. All nine recorded child PIDs
had exited; the writer scope was explicitly released. Electrical and native
artifact bytes remained unchanged.

The [durable outcome record](../SOURCE-CORRECTION-20260909-coupled-power-outcome.json)
retains the strict terminal, task/envelope/index, handback, scripts, actual
logs, numerical results and root replay. SHA256:
`1627a9ed495cfb12e5af690273a97a3d54b23e62702e5b4e44003ab6f0443011`.
The dense reproducible CSV and primary text extracts are indexed by hash,
not embedded as durable copies. This record is evidence, not acceptance.

The model-source suite remains 241/241 PASS. Current native generation,
independent review, routing and release sealing remain ahead. Existing pod
seal, TOP77/0.20 A bring-up, conditional TDM, sourcing and publication holds
are unchanged. No new user choice or JLC upload is needed for the next analysis.
