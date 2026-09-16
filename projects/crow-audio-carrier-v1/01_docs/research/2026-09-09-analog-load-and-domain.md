# Analog loading derived; full-range shutdown needs a different proof

Subject: `ea148a54067063ca9844cdc46e6c4b1d9a6c9fe9`. Author analysis only;
no circuit, acceptance limit, generated board, pod or release was changed.
The 1.2 Vrms level below is the project's declared differential signal range,
not the ADC's own full-scale rating. Source admission remains open.

## Actual network and finite-window current

MEASURED: the live source topology check covers eight channels, sixteen input
limiters, sixteen same-leg feedback resistors, two VMID isolation networks,
two external dividers and the separate ADC reference decouplers. The active
filter follows [Cirrus AN0556R1 Figure 2](https://statics.cirrus.com/pubs/appNote/CS530x_Input_Buffer_Filter_Circuits.pdf).
The ADC's 3 kohm differential resistance is a typical equivalent from DS1314F1,
not a minimum resistance or switched-input-current guarantee.

For one balanced half-circuit, with input normalized to 1 V:

```
s = j * 2*pi*f
Y = 2/R_ADC_diff + 1/R_pulldown + s*(2*C_diff + C_ADC_ground)
Gfilter = [1+s*Cfeedback*(Rfeedback+Rout)] /
          [1+s*Cfeedback*(Rfeedback+Rout)+s*Cfeedback*Rfeedback*Rout*Y]
Iout / Vin = Y*Gfilter
```

The derivation includes the 10 ohm output resistor, 300 ohm feedback leg,
680 pF feedback capacitor, 15 nF differential capacitor and 1 nF ADC shunt.
An independent two-node KCL solution agrees within6.7e-16. MEASURED448 cases
cover64 independent component-corner combinations and seven frequencies from
20 Hz through20 kHz. This is a finite sample, not a continuum maximum.

With balanced opposite output currents, a pair's positive supply contribution
is proportional to `abs(sin)`, not both legs' positive peaks simultaneously.
The conservative calculation additionally reserves all18 zero-load quiescent
maxima, output pulldown DC and a separately conditional reference-buffer bound.
The selected20 kHz case gives:

| Quantity | Calculated value |
|---|---:|
| Pair output-current amplitude | 3.532587 mA |
| All-channel pointwise OPA allocation | 121.274948 mA |
| Whole-cycle positive average | 111.005569 mA |
| Maximum320 us positive charge | 35.589725 uC |
| Equivalent current for that window | 111.217890 mA |

The reference term is2.727935 mA. It follows from the external-reference RC
slew, two buffered reservoirs and a bias-source bound. Its tracking-error
invariant requires linear buffers with reachable tracking-lag initial states;
retained VEXT with an emptied buffer is excluded and still requires a restart
analysis. It is not a universal reference-current specification.

The unchanged scalar shutdown arithmetic gives4.499468 V when independent
worst window charge and peak feed drop are combined. Jointly maximizing their
shared phase gives4.499806 V. The latter extremum is solved piecewise, with
stationary points and absolute-sine kinks included;200,000-point independent
quadrature and a100,000-phase grid verify the selected maximum. Omitting half
the differential capacitance or substituting a whole-cycle average is detected
by executed known-bad controls. Neither sub-millivolt miss proves a reachable
hardware failure: ADC loading, internal loaded supply overhead, waveform and
reference-state premises remain conditional.

## Coupled removal and the model's operating domain

MEASURED:82 scenarios completed in32.016 s. The preceding nine-state signed
VIN/buck/OPA/held energy model now receives the time-dependent audio load at
each integration substep. A powered warm-up precedes input removal; frequency,
phase, two input capacitances and three signal levels vary. The controller law,
parasitic parameters and conservative current additions remain assumptions.

| Differential signal | Cases | Input-range violations | Lowest ideal continuation supply |
|---|---:|---:|---:|
| 0 Vrms | 2 | 0 | 4.530131 V |
| 0.6 Vrms | 16 | 0 | 4.521404 V |
| 1.2 Vrms | 64 | 64 | 4.512466 V |

The last column is NOT a hardware endpoint where the linear domain was lost.
The simulation deliberately records that loss rather than inventing a clamp
model. Domain preservation in the lower-level cases does not validate the
other premises either, and does not narrow the user signal requirement.

CITED: [TI OPA1656 SBOS901C](https://www.ti.com/lit/ds/symlink/opa1656.pdf)
pp6–7,15,18 distinguishes4.5 V minimum supply from the input ceiling
`V+ - 2.25 V`. The5 mA/channel maximum is specified at zero output current.
Phase-reversal protection limits overdriven behavior but does not preserve
linear gain, bound loaded supply current or protect the ADC from every output
excursion. Consequently the existing4.5 V supply-only screen cannot prove
linear audio loading through shutdown.

With the source's1.7 V bias envelope and10.5 mV leakage reserve, full-range
input peaks require4.809028 V supply. In the selected worst endpoint scenario,
the first common-mode violation occurs529.050 us after input removal; the raw
trip is1006.489 us and the modeled isolation deadline1326.489 us. A violated
linear model is not evidence that the hardware necessarily fails, but its
later favorable voltage cannot close the source question.

Four convergence/warm-up controls cover RK4 at100/50/25 ns, midpoint at25 ns,
and doubled warm-up. A separate constant110 mA replay matches the previous
model to1e-10 V. All87 saved-state total-energy and signed-buck-port checks
pass the unchanged10 nJ numerical budget. Independent common-mode checks
reopen actual saved voltages. Known-bad controls reject omitted VIN energy
(261.030 uJ residual) and supply-only acceptance despite four negative
common-mode witnesses. This checks the mathematics, not the silicon model.

## Source correction options narrowed, not selected

MEASURED: under the existing divider tolerances and4.85 V maximum rising
ceiling, the top-resistor supremum is31.192261 kohm. Its lower falling corner
is only4.664494 V, already144.535 mV below required full-range headroom before
feed drop or response delay. A top-resistor-only change cannot establish the
desired linear-domain proof. This is not an impossibility claim for other
supervisors, power arrangements or isolation timing.

CITED: [OPA2156 SBOS900B](https://www.ti.com/lit/ds/symlink/opa2156.pdf)
has compatible SOIC-8 signal/power pin roles, a supply-extending input range,
20 MHz unity-gain bandwidth and3 nV/sqrtHz typical10 kHz voltage noise. Its
SOIC zero-output-current maximum is5.2 mA/channel. Input crossover degrades
some precision/noise characteristics. Crucially, its0.5 V differential-input
absolute rating and protection topology require a new retained-charge and
connected-start audit; the OPA1656 protection proof cannot simply be reused.
The public [JLCPCB catalog identity](https://jlcpcb.com/partdetail/TexasInstruments-OPA2156IDR/C1850241)
is C1850241/SOIC-8. No live stock quantity, reservation or orderability is
claimed, and this identity lookup does not adopt the part.

An UNSELECTED calculation replaces only the eight signal packages, retains
the OPA1656 reference buffer, and adds an existing-family100 ohm resistor in
series with the30.9 kohm supervisor top. The extra16-channel IQ is3.2 mA.
Using5% reserve for the trim gives4.827875 V maximum rising threshold and
4.506853 V independent-worst conditional shutdown scalar. Without the trim,
the substitution instead gives4.496081 V. This identifies a candidate, not
a robust qualified margin or permission to edit parts by pin compatibility.

The alternatives inspected are not automatic substitutes:
[OPA2192](https://www.ti.com/lit/ds/symlink/opa2192.pdf) has10 MHz unity-gain
bandwidth, below Cirrus's15 MHz recommendation;
[OPA2328](https://www.ti.com/product/OPA2328) specifies6.1 nV/sqrtHz typical
at10 kHz, above the5 nV/sqrtHz recommendation. No performance requirement was
relaxed to admit them. OPA2156 filter-loop stability, input crossover/current
noise, differential clamps and ADC kickback must be checked before selection.

Next: audit that replacement's protection/retained-charge paths, compare an
earlier-isolation alternative, and select a coherent source correction. Then
complete correlated reference/CT/DUMP_RC/NR restart and feed current-duration
authority. No JLCPCB upload or account operation is needed for this source work.

## Evidence and unchanged artifacts

The [durable outcome](../SOURCE-CORRECTION-20260909-analog-load-outcome.json)
contains the executed scripts, their dependency, actual bounded logs, all
results and503 verified unchanged source/native/pod input hashes.
Size1,055,862 bytes; SHA256
`ce0dc452d796360ededf0f78193eab5389db7f395e8535d0b1162226744e8932`.
The source suite250/250 PASS is INHERITED from the source-identical preceding
checkpoint, not rerun. No gate limit or source-generation admission changed.
MEASURED09:30:42Z: handoff validation and the1/1-beacon check return0.
The contracts audit returns1 with2891 inherited structural findings,16 in
this carrier, and zero strays. Its complete failure lines match the preceding
audit, not merely its count; no ratchet was relaxed. Audit log SHA256
`31b8415f8a9e162fae2e074401b7666762a1b8905813426ea3d3e27b31ff6607`.
The current native carrier remains stale and unrouted; no carrier release
was minted. The sealed pod and all existing physical/sourcing/publication
holds are unchanged. No vendor upload, order, push or remote write occurred.
