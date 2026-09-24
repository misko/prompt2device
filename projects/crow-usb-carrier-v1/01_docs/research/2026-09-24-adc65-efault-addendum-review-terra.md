# Independent E-FAULT source-envelope addendum review

review_verdict: SOUND

conditional_source_binding: ELIGIBLE

physical_qualification: OWED

mutation: NOT_PERFORMED

## Scope and packet integrity

Fresh READ_ONLY judgment, limited to whether the proposed clarification makes
the existing conditional external-source contract semantically applicable to
the exact supplied CJ. It is not acceptance of a producer result, schematic,
native or copper artifact, placement, routing, part procurement, released
design, or physical test.

The supplied source-review envelope SHA-256 is exactly
`214babcff0e138f977ee4c5c6ab12a651f82e5f4d86ec83781e04bd20eb5bbc8` and
the detached manifest SHA-256 is exactly
`053b2befcd027a4a4ae699f929c8ff18c10a1dac6a88d186cbefa611e9724765`.
All 12/12 input entries and the envelope entry listed by the manifest passed
`sha256sum -c` with zero mismatch. The deadline stated by the verified
envelope is `2026-09-24T00:23:55.220396Z`.

The reviewed clarification patch SHA-256 is exactly
`be379a2cf45d129a1a403543a66ae3a41030c24838244aaa060ae7613f5b4297`; the
engineering disposition SHA-256 is exactly
`90a8c4dbf0fdbe880e81bea1f43e96ed53059b87e911ad22424553afc79ef1e3`; the
exact reviewed CJ SHA-256 is exactly
`1f01be73e0699cd62bc734aa189b25e9d66f1097b5ce6f52a8db30533ecc6448`; and
the prior INCOMPLETE review SHA-256 is exactly
`c252da2db1f9ca50bcf7ab3b3533bdb157fcc3edc72d827c2884e29f518d8f4b`.

## Clarification and authority coverage

The patch has exactly two text hunks, in `power_tree.yaml` and
`protection_paths.yaml`. Each replaces only the outstanding-qualification
sentence to say that source/output-capacitor discharge includes every fitted
downstream capacitor, naming `C_ADC_3V3X_OK_VDD`, and that the J_PWR
whole-episode envelope must be qualified before procurement or release. It
adds no numerical waiver or new operating mode. The 3.4 A instantaneous cap,
2.85 A persistent cap, 10 ms cumulative excess limit, 13.2 V delivery and
recovery ceilings, no-excess autonomous retry rule, fault-removal plus input
power-cycle rearm rule, fuse allocation, and thermal limits are unchanged.

Existing authorities already define the envelope at J_PWR: the contract says
it includes source-output/cable-capacitor discharge, applies across the entire
fault episode, disallows a new allowance on autonomous retry, and is a
procurement/test requirement rather than a measured supply characteristic.
`power_tree.yaml` and `protection_paths.yaml` repeat the same values and state
`entire_fault_episode_including_cap_discharge_and_retries`. Their
qualification status remains conditional, local post-fuse capacitor discharge
remains first-article owed, and no supply is selected. The patch therefore
makes a pre-existing load-independent whole-board qualification obligation
explicit; it does not establish physical compliance.

## Exact downstream delta and limits of the evidence

The supplied CJ contains `C_ADC_3V3X_OK_VDD` as Samsung
`CL05B104KO5NNNC` / JLC `C1525`, a 100 nF, 16 V, X7R 0402 capacitor. Its two
ports resolve solely to `N3V3_ADC` (pin 1) and GND (pin 2). The supplied
capacitor authority gives +/-10% initial tolerance, so at the declared
N3V3_ADC upper value of 3.38 V, Cmax = 110 nF, Q = C*V = **0.3718 uC**, and
E = 0.5*C*V^2 = **0.628342 uJ**. These are finite delta magnitudes only. They
do not create a source-current, ramp, inrush, discharge, cable, ESR, ESL, or
fault waveform.

The exact path is J_PWR -> F_IN -> Q_IN -> N12V_PROTECTED -> U_BUCK ->
N5V_BUCK -> D_HOLD/Q_PRE -> 5V_LDO_HOLD -> U_LDO (LT3045EDD#PBF) ->
N3V3_ADC -> C_ADC_3V3X_OK_VDD. The LT3045 primary authority specifies its
programmable current limit at stated test conditions, including 450--550 mA
with VIN=2 V, VOUT=0 V, and RILIM=300 ohm. Its foldback and test-conditioned
limit cannot be treated as a guaranteed connector-current or rail-ramp model.
It supplies no substitute for exact source/cable and fitted-board waveform
qualification.

## Reconciliation, findings, and decision

The prior P1 correctly rejected a physical PASS because a capacitor
charge/energy calculation cannot bound the instantaneous or cumulative
connector waveform. That physical point remains open. It does not prevent
this narrower semantic result: the clarification expressly includes the new
fitted downstream capacitor in an already load-independent, J_PWR-measured,
entire-episode conditional procurement/test envelope. A candidate source or
cable must still demonstrate all stated limits with the complete fitted board,
including this capacitor, relevant discharge paths, a hard fault, and every
retry. If it fails, the envelope has not been met.

* P0: none for this SOURCE-stage semantic addendum.
* P1: physical waveform and first-article qualification remains open and is
  an explicit procurement/release hold, not a reason to present a physical
  PASS.
* P2: none introduced by the clarification patch; the previously noted
  comparator-method limitation is not relied on as physical evidence.

Accordingly, the clarification and this exact existing CJ digest are eligible
for conditional SOURCE binding without CJ regeneration solely for this review.
That eligibility neither mutates the source/digest nor authorizes any
downstream activity. Any later full rebuild must reproduce the reviewed
clarification semantics and CJ hash; otherwise it fails closed and requires a
fresh comparison and review.

Exact next source action: retain the clarification in both authoritative
contract locations, then before procurement or release select the exact
isolated source and cable and obtain qualified J_PWR measurements over the
complete fitted board. The test must cover source/output and downstream
capacitor discharge, startup/recharge, fault application, the full episode,
all retries/rearm behavior, recovery voltage, local post-fuse behavior, and
the 3.4 A, 2.85 A, 10 ms, and 13.2 V limits. Bind any later rebuilt CJ to the
same reviewed semantics/hash or perform the required fail-closed fresh review.
