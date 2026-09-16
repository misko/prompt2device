---
schema: 1
kind: pcb-human-report
report_id: 2026-09-16-carrier-design-math
title: Crow audio carrier v1 first-article design math
project: crow-audio-carrier-v1
date: 2026-09-16
status: FIRST-ARTICLE-ONLY
---

# Design math and qualification boundary

The source contracts bound the common 12 V trunk at 1.0 A and each of eight
pod branches at 0.10 A. The protected-source budget allocates 75 mΩ to F_IN,
25 mΩ to Q_IN and 100 mΩ to common copper, vias and joints. At 1.0 A this is a
0.200 V loss, so the 11.4 V source floor yields 11.20 V before branch loss,
above the declared 11.16 V protected-node floor. Each branch budgets 2.2 Ω for
its protection device, board path and contacts. At 0.10 A that is 0.220 V; with
the source/common allowance and the declared 20% margin, the source contract
calculates a 10.896 V carrier-header floor, 96 mV above the 10.8 V threshold.
Hot four-wire confirmation remains a first-article requirement.

Q_IN uses a 25 mΩ maximum resistance at the governed drive condition. At the
1.0 A trunk bound, `P = I²R = 25 mW`. This supports the exact Q_IN.5 R-THERM
disposition; it is not a thermal measurement. The final board's 54 declared
layer-transfer banks all pass the retained 0.55 A per 0.20 mm finished-hole
screen at their stated continuous allocations. Only the geometrically parallel
12V_IN pair receives summed capacity credit. Loaded current sharing and
barrel/copper temperature remain physical first-article checks.

The 5V_BUCK rail is bounded at 0.30 A steady and 4.85–5.15 V. Its three 10 uF
50 V X7R input capacitors retain 13.77 uF after the declared tolerance, bias
and temperature deratings, above the 10 uF requirement. Three selected 47 uF
10 V X7R output capacitors retain 64.72 uF, above the 44 uF reference-design
basis. The 3V3_ADC LT3041 rail is bounded at 0.23 A and 3.23–3.35 V with a
500 mV dropout allowance and 702 mW modeled dissipation ceiling. Each selected
47 uF input/output ceramic retains 17.9775 uF under the source deratings;
installed effective capacitance and loop stability remain unmeasured.

The final analog-copper audit measures all 155 declared paths. The differential
filter endpoint, length, resistance and return contracts pass on the exact PCB.
Those modeled results do not replace gain, noise, CMRR, clipping, channel-map,
reset/TDM timing or thermal measurements. The immutable release is therefore a
sound engineering first article and remains DO-NOT-ORDER while sourcing is
blocked and until the retained physical test plan is complete.
