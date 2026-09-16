# Reference loading and exact amplifier model authority — 2026-09-09

Author analysis of source8e8a2910 and the ADR0024 correction. This is not a
native schematic verdict, hot/lifetime guarantee, physical measurement or
release. The unchanged acceptance window remains1.60..1.70V. The source
change improves a demonstrated initial-tolerance margin, not the whole
CAR-F12 power-state argument.

## Exact primary facts and their domains

- CITED: YAGEO RT V17,2026-02-12 p2 decodes RT0603**B**R**D**0710KL as
  0.1percent,25ppm/C; p4 gives its0603 body. Existing dossier primary SHA256
  `00a9148c2958122200e8a93292e389392a795adcfe40562d6ca4f690d1e5d7d1`.
  No matched-network correlation is specified. Endurance and solder tests
  are not replaced by initial tolerance or a small engineering aging factor.
- CITED: Panasonic FK ABA0000C1181 p1 states leakage at20C, two minutes
  after reaching rated voltage. For the exact35V4.7uF part, the larger of
  0.01CV and3uA is3uA. Endurance/shelf leakage is measured after returning
  to20C, not at105C. Primary SHA256
  `b36857d089adaddf3042b33bf11d0f7d83bf70734e983f33b7827152e11854e3`.
  Applying3uA to the installed low-bias circuit is a conditional engineering
  screen; the PDF does not establish every temperature/startup leakage.
- CITED: exact KEMET C0805C106K8RACTU and C0603C105K4RACTU sheets specify
  insulation resistance10Mohm and100Mohm, respectively. Do not treat their
  Y-SIM typical plots as guaranteed capacitance, ESR, ESL or leakage corners.
- CITED: KEMET/YAGEO R82 F3101_R82,2026-05-19 p4 specifies IR*C of at
  least5000Mohm*uF for the1uF class at25C±5C after50V/one-minute testing.
  That is5Gohm for each exact1uF coupling capacitor, not a hot-temperature
  insulation guarantee. Eight coupling capacitors load each reference bank.
- CITED: TI SBOS513F p7 gives150uV maximum25C offset,5uV/C maximum drift
  under its stated5.5V condition, and50pA maximum input bias through85C.
  p8 gives typical5pF differential/4pF common-mode input capacitance and
 90ohm open-loop output resistance at1MHz. These typical AC facts are not
  all-corner model guarantees. Primary SHA256
  `1d13d91bc220d3f37e814e29599ce23e086bd661227618104dcae5482c8144fc`.

## Initial DC screen and source correction

DERIVED, conditional: solve the actual divider node by Kirchhoff's current
law. At the low corner, top resistance is high and bottom is low; both
external ceramic insulation paths shunt the divider. Input bias is signed
against the lower bound. The new10k input limiter contributes its own bias
drop. The buffer's feedback remains before the1k output isolator, so buffered
capacitor and eight-leg net leakage cause a real DC drop across that isolator.

```text
Gext = 1/10Mohm + 1/100Mohm
Vext_low = (3.23/Rtop_high - Ib)/(1/Rtop_high + 1/Rbot_low + Gext)
Ibank_signed = 8 * (5.4V/5Gohm + Ib)
Vbuf_low = Vext_low - 10.1kohm*Ib - 175uV
           - 1.01kohm*(3uA + Ibank_signed)
```

The signed5.4V film-leakage differential is a deliberately loose DC screening
allowance, NOT a newly proven reachable transient envelope. The175uV term
uses150uV plus five degrees of the cited maximum drift, with the primary
conditions retained. Initial resistor tolerance is used, not all-life drift.
The upper corner omits positive-to-ground capacitor leakage rather than
crediting it as necessary to meet the limit.

| Source | Conditional low / high | Initial-window screen |
|---|---|---|
| Original independent1percent dividers |1.5947563185 /1.6868848854V|FAIL lower edge|
| ADR0024 independent0.1percent dividers |1.6092832417 /1.6718548854V|PASS, conditional|

MEASURED SOFTWARE ARITHMETIC: the source regression uses nodal conductances;
the coordinator separately recomputed the same corners using divider
Thevenin voltage/resistance and obtained agreement to floating-point rounding.
No specimen was measured. These values do not guarantee installed low-bias
leakage, hot/lifetime operation, PCB contamination resistance or startup.

Implemented four exact RT0603BRD0710KL/C95204 dividers. Nominal values, nets,
all capacitors, input/output limiters, raw feedback and325-part/923-pin source
census are unchanged. Existing floorplan anchors clear the larger0603 lands
and courtyards in the full source-native-library test; native geometry still
must be regenerated and independently reviewed. No footprint or limit was
silently shrunk. First-article acceptance limits are unchanged.

## Settling: which time constants actually exist

DERIVED topology, not simulated settling: the55ms nominal divider pole and
4.7ms nominal output-isolator/capacitor product are different states. Each
reference bank additionally sees eight100k bias branches through1uF coupling
capacitors and the pod output impedance. For an ideal linear raw buffer,
ignoring tiny bias/leakage currents only in this AC expression:

```text
Zleg_i(s) = Rbias_i + Rpod_i + 1/(s*Ca_i)
Vbuf(s) = [Vraw(s)/Riso + sum(Vpod_i(s)/Zleg_i(s))]
          / [1/Riso + s*Cbuf + sum(1/Zleg_i(s))]
```

The eight actual pod/common-mode waveforms are inputs, not eight independent
full-amplitude adverse steps. Balanced differential signals cancel ideally
in the bank; mismatch and common-mode changes do not. This passive-network
expression is not a substitute for the OPA loop, actual capacitor domains,
or correlated restart states. Do not call4.7ms complete reference settling.

## Correct public model for the filter-loop estimate

MEASURED retrieval from the links on
[TI's OPA2320 product page](https://www.ti.com/product/OPA2320):

- [SBOM437 PSpice archive](https://www.ti.com/lit/zip/SBOM437), SHA256
  `04060dbd12c8a07601290ad22b6de2865132619860741c5577956c2f79232bd6`,
  contains OPAx320-Q1.LIB Final1.7,2022-06-17, referencing SLOS884B.
  It is not adopted as the exact non-Q1 model simply because this product
  page links it.
- [SBOM438 TINA-TI archive](https://www.ti.com/lit/zip/SBOM438), SHA256
  `d0478194a9914fe1813eb9675623a3127e0fc0c9ee2fe82e4988de710c12deaf`,
  contains OPAx320.LIB Final1.6,2021-07-22, explicitly referencing SBOS513F
  and both single/dual cores. Unchanged LIB SHA256
  `a3ecb23eb81d73b9d03cc4d44ef0e06ffdaadc995301bad1cb4882ba8a0f3b8c`.

The second model explicitly includes Aol/phase, output impedance and load
effects. It is publicly readable, unencrypted and supplied as-is; no login
or decryption was used. Its ESD switch elements are behavioral approximations,
not new device ratings. No simulation was run, and it supplies neither
startup protection proof nor physical performance evidence. Files are retained
in the source-correction outcome's disposable raw-authority packet; the URLs
and exact hashes distinguish them on any future retrieval.

For an ideal voltage at the amplifier's raw output, the passive feedback
network alone has the following modal relation, neglecting amplifier input
capacitance ONLY in this explanatory expression:

```text
q(s) = s*Cfb/(1+s*Rfb*Cfb)
Hfilter(s) = (1/Rout + q)/(1/Rout + q + Yload)
beta_passive(s) = (Hfilter + s*Rfb*Cfb)/(1+s*Rfb*Cfb)
```

Differential excitation sees twice the15nF cross-channel capacitor in its
half-circuit; common-mode excitation sees no ideal contribution from that
capacitor. Yload must also represent the switched post-filter1nF/100k legs
and the actual ADC impedance; an undefined ADC sampling load is not silently
fixed at10k. The10k positive-input limiters and model input capacitances also
belong in a complete return-ratio analysis. Therefore a GBW/s ideal amplifier
or a generic unity-buffer capacitor rule cannot close this filter obligation.

Next filter work is now specific: validate the exact non-Q1 model against
its primary reference AC response, then evaluate both modal loops and the
actual switched load. This remains a guarded, decision-oriented numerical
attempt under CAR-F12 after reassessment; ngspice is not installed (checked
with command lookup and the package database). No claim about every possible
simulator is made. No attempt was spent or reset by this authority inspection.

## Verification and remaining boundary

Actual old-source RED on8e8a2910:17 tests, six failed subtests (four exact
identity mismatches and two low-corner failures), no import/runtime errors.
Focused corrected run17/17 PASS; full source run267/267 PASS in112.275s,
2026-09-09T21:36:17.512069Z..21:38:10.216498Z. Logs and hashes are retained
in the source-correction outcome. Existing KiCad PROPERTY_ENUM warnings and
parser ResourceWarnings were nonfatal and are not claimed fixed.

This routine correction and its fixed-source regressions do not constitute
a new shutdown sweep or credit the all-relevant-state milestone. The4/6
investigation history and one non-improving count remain intact. Correlated
power/protection review, source admission, regeneration, native review,
routing and release remain outstanding. The microphone pod is unchanged.
