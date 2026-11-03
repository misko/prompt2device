# Crow pod diode substitution engineering review

3 November 2026. **Nexperia BAT54S,215 / C47546 is conditionally recommended
for pod D2/D3.** The remaining concern about its shorter surge rating does not
disqualify it for the existing bounded prototype protection model. This is an
engineering recommendation, not an adopted BOM change, stock allocation or
manufacturing approval. Sixteen installed parts are needed; the old part's
diagnostic JLC requirement was 21 including allowance, which must be rechecked
for the new code.

## Existing requirements recovered and checked

The original archived brief and roof model were located in the first-run source
tree. Their exact SHA-256 values match entries in the published release's
`evidence/archive-manifest.json`; copies are retained under `source-evidence/`.
Their old quantities, stop-stage instructions and historical acceptance labels
are **not** current instructions. Only the unchanged protection/environment
basis is used; the present build remains two assembled carriers and eight pods.

The actual r10 native boards retain every required model dependency inspected:

- All 16 carrier isolation legs are 2.7 kΩ, 1%, between the respective port
  coupling and ADC nodes.
- Pod R9/R10 are 1 kΩ, 1%, from amplifier outputs to cable audio nets.
- Pod R14 is the required 330 Ω, 1%, 3V3-to-GND discharge/sink resistor.
- Both BAT54S footprints connect pin 1 to GND, pin 2 to 3V3 and pin 3 to the
  relevant amplifier output. They retain the expected SOT-23 lands.

The archived prototype model uses −20…60 °C local electronics air and explicitly
excludes 12 V/PoE signal miswiring, arbitrary external precharge and IEC surge
immunity. This is not a new relaxation introduced to accept a replacement.

## Electrical conclusion

The [candidate datasheet](https://assets.nexperia.com/documents/data-sheet/BAT54S.pdf)
defines the required numbered series-diode pinout, 30 V/200 mA ratings and
−55…150 °C ambient range. Its 600 mA surge condition is under 10 ms; that is not
equivalent to the original's longer condition. Its exact orderable identity is
listed by the [manufacturer](https://www.nexperia.com/chemical-content/BAT54S.html),
whose [product page](https://www.nexperia.com/product/BAT54S) states Production.

Replaying the retained model gives **3.895795 mA per carrier history branch**
and **2.596937 V off-pod rail**. The branch current is not a universal diode
transient maximum. A separate conservative screen bounds the source/history
voltage difference by 10.36 V across the pod's minimum 990 Ω isolation:

`10.36 V / 990 Ω + 20 µA = 10.484646 mA`.

Under those same passive-source/history and initial-cable-state assumptions,
the proposed diode does not rely on either part's 600 mA surge capability.
At the inherited 0.6 V clamp allowance, power is 6.2908 mW; using the candidate's
reference 500 K/W gives a 3.1454 °C rise. That is a reference thermal screen,
not this board's measured thermal resistance. The ambient range also covers the
existing −20…60 °C envelope. Thus the surge-duration and temperature differences
are resolved **for this conditional prototype model**, not for arbitrary faults.

The candidate's standard SOT-23 package and lead numbering match the native
layout at the footprint-screen level. Package limits, land observations and
normal electrical comparisons are in the preceding
[shortlist](../release-refresh-20261103/README.md). No new copper or firmware
change is indicated. Vendor-specific placement angle and physical assembly
inspection remain separate from this electrical recommendation.

Retain the existing first-article checks for cold/hot clamp voltage, leakage,
parasitic/filter-capacitor discharge and actual local transients. The 0.6 V
allocation is **not** a guaranteed all-temperature manufacturer maximum. Neither
the old design nor this replacement establishes lightning or miswire immunity.

## Independent review and tests

SOL 6.1 high independently reviewed the candidate on 3 November under task
`diode_conditional_review`. It reran the source/native checks and all five tests,
confirmed the numbered pinout and native lands, and found no candidate-specific
disqualifier within the stated model. It specifically distinguished the
3.896 mA carrier branch from the separate 10.485 mA pod-branch screen, and
retained waveform/thermal qualification and stock/placement holds.

Reproduce without changing native boards:

```sh
/usr/bin/python3 -B projects/crow-array/order-readiness/diode-review-20261103/check.py projects/crow-array/order-readiness/diode-review-20261103/checks.json
/usr/bin/python3 -B -m unittest discover -s projects/crow-array/order-readiness/diode-review-20261103 -p test_check.py
```

The five tests cover current native/source consistency, rejected historical
1.8 kΩ isolation, an inadequate sink, lost pod isolation and swapped diode pins.
Mutations are in memory only. KiCad prints its existing enum/image-handler
diagnostics; all tests complete successfully. This is a scoped substitution
review, not a replacement for whole-board release review.

## Next action and unchanged release holds

Check exact C47546 in the signed-in JLC job for immediate quantity, gross demand,
fees and eligibility. If that succeeds, implement the identity change in an
isolated next package and verify affected native schematic/BOM/PCB identity,
ERC/parity and vendor placement; do not relabel r10 as updated. C7507573 remains
the screened fallback, not a second adopted alternative. No further generic
diode search is needed unless these actual offers fail.

The goal's all-JLC wording also needs reconciliation with agreed home installs.
One exact-code recovery found microphone C3273770 and Pico C9900019762 not
orderable, with zero exposed overseas/presale pools. Their catalog reason says
no longer manufactured; **this is not adopted as a manufacturer lifecycle
determination**, particularly for the generic JLCPCB Assembly Pico listing.
The initial MPN misses were not proof of zero stock. The buzzer search still
found no exact JLC offer. The preserved recovery JSON records these limitations.
No home-install part or source was changed. The user subsequently confirmed
external sourcing for all agreed home-install parts on 3 November; see
[the recorded decision](../STATUS.md#user-sourcing-decision-on-3-november-2026).
The JLC-only requirement therefore applies to factory-installed parts.

TinyFish tools remain unavailable in this session. Saved pod test-C placement
is already verified; its actual loaded-model hash/outward mouth, carrier
connectors, required diode population and process acceptance remain open.
No purchases, vendor messages, reservations or production changes occurred.
