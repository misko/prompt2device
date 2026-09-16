---
schema: 1
kind: pcb-human-report
report_id: 2026-09-09-protection-architecture
title: Shared-rail protection architecture source correction
subtitle: Bounded D-BACK decision and executable handback, not physical acceptance
project: crow-audio-carrier-v1
date: 2026-09-09
status: REVIEWED
evidence_status: INCOMPLETE
---

## Executive conclusion

**PROPOSED / implemented source:** select a shared3V3 rail for the CS5308P
and eight OPA2320 duals, using reverse-protected LT3041 A-grade, a200ohm
rail bleed, passive1k/1k external bias,16 ADC10k pulldowns and independent
30nF filter shunts per leg. The final source has333 components and937 pins.
The protection checker and22 focused positive/hostile tests pass their
explicit engineering bounds. Generation, routing, first-article qualification,
order and release are NOT admitted. This is a useful partial source correction.

**OWED:** physical-source integration of the new regulator and32 filter
shunts, selected-part rules and legacy source fixtures. The full regression
receipt remains red; it must not be described as an electrical/physical PASS.
The exact next owner action and acceptance boundary are in
[ADR0025](../decisions/0025-shared-rail-protection-architecture.md).

## Question and scope

Compare at most three whole-circuit arrangements under the frozen fresh
commission. The exact brief and pod are unchanged: eight channels,
CS5308P/Cirrus receive function,1.2Vrms differential,8x0.10A spokes,
carrier header>=10.8V, no hot plug and no firmware. The decision did not
require an optical arrangement, valid shutdown audio, guaranteed maxima at
every test point, or a proprietary full-device model. No new numerical
investigation was launched under CAR-F12 REASSESS4/6.

## Evidence boundary

**CITED:** initial electrical authority0c999ab7, committed handoff09b57113,
TaskEnvelope SHA256
`895817016eb3b0a4f2c7f018b1e31d71a6bc956c8dab9b704475ceffc17abf03`.
Its five input members were verified before work and are reverified in the
observed-outcome receipt. Parent-only status/journal commit1b725986 did not
change electrical authority. The hard session deadline is2026-09-10T00:16:22Z.

**INFERRED:** algebraic envelopes run against live JSX source, not a native
board, proprietary silicon model, instrument capture, or production lot.
The final receipt binds exact changed-file/test-log hashes; no process
TaskAttempt or independent native witness is fabricated. No native KiCad,
release, staging, commit, account, upload, supplier-contact or order action
was performed by the architect.

## Findings

| Grade / arrangement | Deciding result |
| --- | --- |
| **PROPOSED**, prior split5V driver / held3V3 ADC | Not selected: independent energy and sequence dependencies remain. Missing timing maxima alone are not evidence of an unusable part. |
| **PROPOSED**, shared3V3 rail with passive bias | Selected: removes independent driver/reference reservoirs and TPS reverse-output dependency. Realized rail tracking/node-discharge budgets remain explicit. |
| **INFERRED**, independent5V with passive ADC attenuation | A ratio<=0.63 is needed for a3.4V ceiling from5.4V, conflicting with retained unity receive gain without more circuitry. Not selected; search stopped. |

**DATASHEET:** ADI LT3041 Rev.A gives reverse OUT-to-IN protection and
exact15-pad identity. It also permits SET-related discharge and up15mA
overshoot recovery; those are not treated as zero. Two local output capacitors
each require>=10uF effective, ESR<20mohm and ESL<2nH. A-grade SET limits
and the exact33k resistor yield an allocated3.255199..3.344999V range.
Engineering rail upper allowance becomes3.35V; no brief requirement changes.

**INFERRED:** all16 cold/restart input paths at a3.4V rail barrier inject
12.977mA under the stated pod/coupling-charge envelope. The worst200ohm
bleed sinks16.190mA, leaving3.114mA after a100uA reserve. Positive and
negative input-limiter currents remain1.169/0.590mA against the10mA limit.
Old500ohm bleed fails this bound, a discriminating source change.

**INFERRED:** fastest dump includes0.95ohm, only32.3595uF credited direct
capacitance,0.30A added load and15mA LT recovery sink. ADC-node10k/1nF
maximum time constant10.605us supports the affine inward-barrier proof;
old100k bleeds fail it. Final relative-pin allocation is243.759mV of300mV:
41.127mV filter lag,50pC switch-charge allocation (52.632mV),100mV
return error and50mV amplifier-output tracking error. The last three are
explicit engineering budgets, not guaranteed datasheet limits.

**INFERRED / corrected:** root's read-only review supplied a counterexample
to bounding a cross-leg15nF bridge from rail slew alone. Stored differential
charge can produce negative filter voltage if both outputs collapse faster
than the differential mode. This was not claimed as a reachable measured
waveform. The final source replaces each bridge with30nF to ground per leg,
using four existing15nF C0G parts; differential equivalent is unchanged.
Independent positive RC legs remove cross-leg energy transfer. Common-mode
loading/stability and realized ground returns are reopened, not waived.

**INFERRED:** retained1.2Vrms audio fits0.76085..2.52921V per leg.
Extra10k pulldowns add2.863mA DC load and at most31.6ppm switch-only
gain reduction under the Ron allocation; local feedback remains after10ohm.
The3V3/5V steady bounds are222.374/250.414mA versus230/300mA allocations.
Upstream remains0.985346A; unchanged carrier-header floor10.896V.
Full startup-charge inventory and SET99% budgeting give8.389ms conditional
on1A available charge, not a guaranteed startup trajectory or supply-ramp
endpoint convention. Initial bias1.60938..1.68068V does not qualify hot-life
leakage, drift, noise, crosstalk or distortion.

**OWED:** old TPS pin-specific routes were removed from
`03_src/route.yaml:prep.seed_stubs.stubs`, not transferred to opposite-function
LT pins. All old3V3 seeds, TPS quiet-return masks and width exceptions are
retired. The route top-level ownership remains intact. New anchors are
provisional. Active and historical part dossiers still contain old adjacency/
thermal/source-count references, notably OPA2320 C_DIFF/U_AFE9/5V_OPA
and TPS7A92 local-cell assumptions; these must be reconciled before generation.

## Recommendations

1. **PROPOSED:** accept this bounded electrical direction for upstream source
   completion, without closing CAR-F12 or promoting physical readiness.
2. **OWED, next executable source action:** reconcile exact selected-part
   adjacency/keep-short/thermal ownership, all32 shunt-capacitor positions,
   and the LT3041 IN/OUT/OUTS/SET/GND/EP two-capacitor loops. Run current
   source package, placement and route-contract tests. Acceptance requires
   zero unexplained identity, missing-owner, collision and incompatible-rule
   failures; changing counts alone cannot meet it.
3. **OWED, subsequent owner action:** only after source admission, archive
   the old prelayout cohort, regenerate under owning permission, and obtain
   independent native pin/package/parity/placement review before routing.

## Validation plan

**CITED:** focused tests exercise every shared amplifier supply, all16 ADC
bleeds, both ADC analog supply pins, dump resistance, upstream diode direction,
LDO pin swaps/NC, reference topology, output-cap/charge/load bounds, retired
routes, and bridge restoration. The precise final test results and failures
are in the observed-outcome and raw logs; full regressions are not green.

**OWED, controlled first article after physical-source/native gates:** measure
cold start, normal audio, removal, brownout and correlated rapid restart with
actual pod/reference/filter charge. Falsify the0.315A discharge envelope,
120334V/s rail slew,50mV driver tracking,50pC switch allocation,100mV
return allocation and ADC absolute-relative limits. Measure exact ADC ramp
endpoints, local capacitor ESR/ESL/stability and LT hot thermal behavior.
Exercise all8 channels at1.2Vrms for common/differential loop stability,
noise/distortion/crosstalk and all8 spokes for hot loaded header voltage.

## Source register

- **DATASHEET:** [ADI LT3041 Rev.A](https://www.analog.com/media/en/technical-documentation/data-sheets/lt3041.pdf), local `02_parts/LT3041ADE-TRPBF/LT3041_RevA.pdf`, SHA256 `35dda1deb2ffc9e20545ebe2aefd2fbd690cf9b04e8772290fd4991a4b8ef584`; independent visual inspection of pin/package pages7/36.
- **DATASHEET:** [ADI package05-08-1708](https://mds.analog.com/api/public/content/DFN_14_05-08-1708.pdf), local same dossier, SHA256 `06350528dea237ab82f77aa0addd3b75a5abec90d11d567f152d6777cc76962e`.
- **DATASHEET:** [YAGEO RT0603BRD071KL](https://www.yageogroup.com/component-documentation/download/specsheet/RT0603BRD071KL), exact local dossier PDF SHA256 `33278a8f9ad31a36ed06ca3844dfc5fdb5871a6c1537a47d2de0b09a666b7bdf`.
- **DATASHEET:** [YAGEO RT0603BRD0733KL](https://www.yageogroup.com/component-documentation/download/specsheet/RT0603BRD0733KL), exact local dossier PDF SHA256 `7f76e25770bc9439215477d276c8e445b29507853e43272dd026dc521bc2aaf8`.
- **CITED:** [Public LCSC exact LT3041 identity](https://www.lcsc.com/product-detail/C7452883.html), observed stock zero; identity evidence only, not allocation. Exact resistor IDs C110776/C705768 are recorded in their dossiers.
- **CITED:** existing selected OPA2320, TMUX2821, CS5308P, AP63205, control/capacitor and unchanged-pod primary authorities remain in their exact02_parts dossiers. The selected15nF C0G remains GRM2195C1H153JA01D/C97907; no new capacitor family was adopted.
- **CITED:** [ADR0025](../decisions/0025-shared-rail-protection-architecture.md), source checker `03_src/check_protection_architecture.py`, and actual logs/outcome under `06_build/verification/protection-architect-20260909-*`.
