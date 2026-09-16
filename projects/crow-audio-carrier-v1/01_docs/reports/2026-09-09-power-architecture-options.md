---
schema: 1
kind: pcb-human-report
report_id: 2026-09-09-power-architecture-options
title: Power architecture reassessment before the carrier release
subtitle: One amplifier candidate, explicit model limits, no release admission
project: crow-audio-carrier-v1
date: 2026-09-09
status: DRAFT
evidence_status: INCOMPLETE
---

## Executive conclusion

**PROPOSED:** take **OPA2320AIDR on the existing 5V_OPA rail** to source-part
and protection review. The limited headroom screen is promising; neither the
substitution nor the complete protection architecture is accepted or implemented.
Do not keep refining the old supervisor divider.

**OWED:** the carrier is not releasable. Startup, restart, actual filter behavior
and feed-current duration remain source obligations. Regeneration, independent
reviews, placement, routing and release verification follow their acceptance.
JLCPCB login is not the reason this design work is waiting.

## Question and scope

Which correction reduces dependence on nearly coincident voltage thresholds
while preserving the eight-channel, 1.2 Vrms differential audio and eight-spoke
envelope? The [brief](../BRIEF.md), pod and firmware boundary remain unchanged.
CAR-F12 in [findings.yaml](../findings.yaml) still owns the decision and budget.

## Evidence boundary

Live circuit: commit `be1e401d`, TSX SHA-256
`b95f1b709d4b09829c2613d82883500729e3d1889397deaee199a4bffc0073cf`.
The native PCB is stale and unrouted, SHA-256
`66003462ab2221377fd8ad54fdeabe3097983e496f1fe7b22c345fd7843c3060`.
The pod's `v0.1.0-2026-09-03` release remains unchanged, DO-NOT-ORDER.

The [durable outcome](../SOURCE-CORRECTION-20260909-architecture-options-outcome.json)
retains the executed script, result, command/log and exact source identities.
All 503 protected source/native/pod inputs were reopened and match the prior
inventory. Four scalar cases and five negative controls are **INFERRED numerical
evidence**, not physical measurements or a fresh coupled simulation. The earlier
250 passing source tests are **INHERITED**, not rerun for this proposal.

## Findings

### Architecture comparison

| Arrangement | Tradeoff | Disposition |
|---|---|---|
| OPA1656 plus divider adjustment | Earlier analysis excludes this correction to the full-range linear model | **INFERRED:** stop this branch |
| Earlier 12 V detection plus isolated reservoir | Preserves amplifiers but adds charging/inrush, energy-readiness and restart-control obligations | **PROPOSED:** fallback; not fully sized |
| OPA2156 on the present rail | Prior screen had little supply margin; differential-input protection needs a retained-charge audit | **INFERRED:** not preferred |
| OPA2320AIDR on the present rail | Different input/supply range without another reservoir or rail migration | **PROPOSED:** next bounded part/protection review |
| OPA2320 directly on 3V3_ADC | Pod steering can inject into the ADC/LDO output with an empty held input | **INFERRED:** do not make this rail merge without a separate remedy |

**DATASHEET:** TI SBOS513F identifies the dual SOIC-8 part, rail-to-rail inputs,
1.8–5.5 V operating supply and rail-steering input protection with a 10 mA
current limit. Its eight pin functions match the present footprint's functions.
The author viewed the pin figure; this is not an independent pin review.
The 20 MHz bandwidth, 10 V/µs slew and noise/distortion figures are typical
under specified tests, not guarantees for this filter.
[TI primary data](https://www.ti.com/lit/ds/symlink/opa2320.pdf).

**DATASHEET / INFERRED:** TPS7A92 OUT has an input-dependent absolute maximum.
Moving pod-injected current onto the ADC rail creates a new reverse-bias
obligation; rail-to-rail amplifier inputs do not solve it.
[TPS7A92 primary data](https://www.ti.com/lit/ds/symlink/tps7a92.pdf).

### Executed screen

**INFERRED, conditional:** retain the previous lumped hold-capacitance model,
100 nC recovery allowance and divider corners. Allocate 100 mA to the amplifier
block, plus bleed and controls/leakage. This is an engineering budget, not the
zero-output quiescent rating extended to nonlinear operation. A 10% filter-output
amplitude reserve and 0.2 V output-headroom reserve also remain budgets.

```text
Vinput_peak = 1.7 + sqrt(2)*1.2/2 + 0.0105
Vrail_screen = Vtrip_low - (Iallocated*t + Qrecovery)/Cmin - Iallocated*Rfeed_max
candidate_input_headroom = Vrail_screen + 0.1 - Vinput_peak
```

| Delay sensitivity (µs) | Conditional rail (V) | Candidate input headroom (V) |
|---:|---:|---:|
| 320 | 4.512 | 2.053 |
| 420 | 4.476 | 2.017 |
| 600 | 4.413 | 1.954 |
| 1000 | 4.271 | 1.812 |

All four candidate rows pass this limited screen. The baseline fails the
common-mode check even where its supply-only test passes. Five negative controls
reject baseline common-mode loss, candidate undervoltage, overvoltage, excessive
input and excessive output. Five additional arithmetic/budget checks pass.

**OWED:** this scalar does not explicitly evolve signed VIN/controller and
reference states. It establishes neither a reachable trajectory nor a maximum
shutdown delay. The existing 5.4 V rail-barrier budget leaves only 0.1 V below
the candidate's operating ceiling; real transients still need attention.

| State | Evidence now | Still required |
|---|---|---|
| Normal audio | Conditional headroom and primary range/pin facts | Actual gain, loading, stability and noise compatibility |
| Input removal | Four conditional delay sensitivities | Source argument using the existing signed energy account |
| Cold startup | Manufacturer current-limited overload route identified | Partial supply, ADC isolation and stored-charge behavior |
| Brownout | Scalar delay sensitivity only | Correlated detector, reference and held-supply transitions |
| Rapid restart | No closure claimed | Partial CT reset, NR/reference charge and ADC input stress |

## Recommendations

**PROPOSED:** review this one candidate with the existing filter, input resistors,
power topology and spoke supply fixed. The other sketches are different circuits,
not interchangeable implementation instructions.

The candidate has public LCSC identity C2863402; this is not JLCPCB PCBA
allocation. No new dossier or BOM line is adopted.
[Exact-part record](https://www.lcsc.com/product-detail/C2863402.html).

Do not credit `choose_source_correction`: its all-relevant-state condition is
stronger than this result. Reservation four is consumed, not reset. The next
step is source-part/protection judgment, not more samples of this scalar.

## Validation plan

1. Complete a bounded exact-part/protection review challenging powered and
   unpowered pod steps, retained filter/reference charge, partial CT reset,
   ADC input stress and the narrower supply ceiling. Do not assume a complete
   CT discharge or a guaranteed NR settling time.
2. If supported, implement the nine-package change in TSX, dossier and affected
   source checks/ADR. Exercise real failing controls before changing their
   expected source; regenerate through the full conductor.
3. Obtain fresh exact-artifact topology/readability reviews. Grade actual power
   and return copper at placement/routing; preserve first-article stability,
   noise, temperature and power-cycle measurements as owed.
4. Complete release gates before sealing. No upload, order or push is authorized
   by this report.

## Source register

- [Executed script, result and protected inventory](../SOURCE-CORRECTION-20260909-architecture-options-outcome.json).
- [Prior load/model-domain findings](../research/2026-09-09-analog-load-and-domain.md).
- [Decision-control adoption](../research/2026-09-09-decision-control.md).
- [TI OPA2320 SBOS513F](https://www.ti.com/lit/ds/symlink/opa2320.pdf), pp.4, 6–9, 17, 19 and 28. Fetched SHA-256 `1d13d91bc220d3f37e814e29599ce23e086bd661227618104dcae5482c8144fc`; candidate PDF is outside the project until adoption.
- [Local TPS7A92 SBVS318B](../../02_parts/TPS7A9201DSKR/TPS7A92_SBVS318B.pdf), p.3, OUT rating and footnote 2.
- [LCSC OPA2320AIDR / C2863402](https://www.lcsc.com/product-detail/C2863402.html), public identity inspected 2026-09-09; no allocation claim.
