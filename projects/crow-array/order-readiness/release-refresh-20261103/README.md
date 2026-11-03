# Crow release inventory refresh and diode alternatives

3 November 2026. **Release remains on HOLD.** This review covers the agreed
two assembled carriers and eight assembled pods, on five/ten fabricated boards.
It preserves all native files, r10 production-intent files and browser drafts.
The saved pod trial-C coordinates are verified by the MacBook evidence; its
loaded model and outward mouth, carrier connectors and final process acceptance
remain open. No purchases, reservations or vendor messages were made.

## Inventory outcome

The [38-identity inventory table](INVENTORY.md) includes every r10 procurement
line and home-install part. Initial public results: 33 exact InStock badges with
unknown immediate quantity, one BAT54S lookup failure, one Panasonic spelling
mismatch and three home-part identities not located. None proves a complete,
allocated PCBA job. The aggregate index returned no usable numeric stock for
the 38 original lines; those nulls are not zeros. The preserved lookup results
carry dated URLs and response hashes.

A single exact-code recovery for BAT54S-7-F / C83574 succeeded: its exposed
overseas pool is four and presale is zero. The more specific signed-in draft
reported four available against **21 gross required**, including allowance.
Installed need is **16 = 2 per pod × 8 pods**. Do not replace that confirmed
shortage with the public page's generic InStock badge or add overlapping pools.

The portable CLI used for this pass was present in another existing worktree,
not in this shared branch's vNext tree. Its exact two source modules are retained
under `sources/` for reproducibility; this does not migrate the tool into vNext
or change any skill acceptance rule. Rerun from the repository root with a new
output path, never overwrite the retained observation:

```sh
python3 projects/crow-array/order-readiness/release-refresh-20261103/sources/jlc_stock.py bom projects/crow-array/order-readiness/quote-draft/r10-2c8p-outward-power/procurement-plan.csv --mpn-column mpn --code-column catalog_locator --quantity-column installed_2c8p --jobs 2 --format json --output /absolute/new-observation.json
python3 projects/crow-array/order-readiness/release-refresh-20261103/summarize.py
```

## Bounded diode shortlist

Three alternatives were screened. None was adopted into CAD, BOM or JLC drafts.
Public pool counts below are **not immediate PCBA allocation or lead times**.

| Part and supplier page | Class | Observed sourcing | Disposition |
| --- | --- | --- | --- |
| [Nexperia BAT54S,215 / C47546](https://jlcpcb.com/partdetail/C47546) | Same-footprint candidate | InStock; overseas 210,932; presale 207,940; immediate count absent | Preferred exact-job availability check; manufacturer lists exact orderable part |
| [Nexperia BAT54S-QR / C7507573](https://jlcpcb.com/partdetail/Nexperia-BAT54SQR/C7507573) | Same-footprint candidate | InStock; overseas 25,277; presale 25,269; index also 25,277 | Fallback; exact suffix-to-maker ordering identity still needs reconciliation |
| [onsemi BAT54S / C258194](https://jlcpcb.com/partdetail/onsemi-BAT54S/C258194) | Rejected for present sourcing objective | OutOfStock; overseas and presale zero | No further engineering work in this pass |

The QR public object also exposed pre-purchase minimum 86. Do not interpret that
as an assembly minimum, place a pre-order, or promise that 21 can be purchased
without checking the applicable route. Its aggregate count equals the exposed
overseas count; it is not an independent second pool.

## Circuit and substitution checks

Read directly from the unchanged r10 native pod:

| Component | Pin 1 | Pin 2 | Pin 3 | Role |
| --- | --- | --- | --- | --- |
| D2 | GND | 3V3 | AMP_P | Clamp U2A output to rails |
| D3 | GND | 3V3 | AMP_M | Clamp U2B output to rails |

R9/R10 are 1 kΩ between these outputs and the cable-facing AUDIO_P/AUDIO_M
nets. D2/D3 use native `SOT-23` footprints: pads 1/2 at x −0.9375 mm,
y −0.95/+0.95 mm; pad 3 at x +0.9375, y 0; each pad 1.475 × 0.6 mm.

The [Nexperia BAT54S datasheet](https://assets.nexperia.com/documents/data-sheet/BAT54S.pdf)
specifies pin 1 anode, pin 2 cathode and pin 3 the series midpoint. It therefore
preserves the rail-clamp polarity. Its SOT23 uses 1.9 mm lead pitch and a
2.8–3.0 × 1.2–1.4 mm body, consistent with the existing SOT-23 layout at the
package-screen level. The manufacturer [ordering/lifecycle listing](https://www.nexperia.com/chemical-content/BAT54S.html)
includes BAT54S,215 and BAT54S,235; the [product page](https://www.nexperia.com/product/BAT54S)
states Production. This is not a vendor CPL-orientation acceptance.

The [original Diodes datasheet](https://www.diodes.com/datasheet/download/BAT54.pdf)
and [Nexperia BAT54S-Q datasheet](https://assets.nexperia.com/documents/data-sheet/BAT54S-Q.pdf)
support comparison with the ordinary Nexperia version. Key nominal limits agree:
30 V reverse, 200 mA forward, 2 µA leakage at 25 V, 10 pF at 1 V and 5 ns recovery;
the tabulated forward-voltage maxima at 0.1/1/10/30/100 mA are
0.240/0.320/0.400/0.500/0.800 V. Conditions and board-dependent thermal ratings
still apply. Primary documents were read online; the Diodes PDF is retained
locally, while Nexperia's direct shell downloads returned HTTP 403.

Important differences prevent claiming a universally identical substitute:

- Nexperia's 600 mA surge rating is for less than 10 ms, versus the original's
  less-than-one-second condition. Confirm the existing clamp fault envelope
  does not depend on the original longer pulse before adoption.
- Nexperia lists ambient −55…150 °C and storage −65…150 °C. Do not transfer a
  −65 °C operating claim from the original to the candidate.
- The QR family has the required pinout, but its exact JLC `R` suffix has not
  been tied to a manufacturer ordering record in this pass.

Engineering disposition: **credible replacements, not yet accepted**. Next
electrical check is limited to the existing clamp fault/temperature envelope
and land-pattern acceptance; do not restart the whole architecture. Exact
stock, placement convention and affected BOM/source review remain separate.

## Next browser and release actions

TinyFish discovery on 3 November returned not installed; a reconnection was
offered. No signed-in browser task is live. This is an access dependency, not
evidence that the JLC draft is unavailable.

1. **Diode availability:** look up C47546 first, C7507573 second in the signed-in
   parts picker, without selecting a substitution. Retain exact manufacturer,
   MPN, package, immediate available quantity, exact-job gross need and any
   sourcing/lead-time restriction. Do not start a noncancelable preorder.
2. **Pod model:** in the existing new C diagnostic draft
   `c11ad98ea0534ce78a6c3bc004515ffc`, capture J1's loaded footprint/model UUID
   and cached OBJ hash; compare with the expected model in
   [the numerical review](../quote-tests/r10-connector-mapping/LOADED-J1-REVIEW.md).
   Capture an oblique cable-entry view showing the native −Y edge. C stays
   loaded on HOLD; do not restore A in this separately created C draft.
3. **Carrier:** after pod acceptance, verify J101–J108 individually and power
   J1 independently. Do not infer power-jack mapping from an RJ result.
4. **Release:** after reviewed substitution and connector corrections, build an
   isolated next package, reconcile all required BOM rows including D2/D3,
   recheck affected CAD/CPL/DFM evidence and saved fabrication settings, then
   obtain complete itemized quote/placement evidence before release sealing.

The agreed home-install split remains two Picos, two oscillators, eight
microphones and eight buzzers. On 3 November the user explicitly confirmed
external sourcing for these parts; the JLC availability requirement applies
to factory-installed parts. See [the recorded decision](../STATUS.md#user-sourcing-decision-on-3-november-2026).
External exact-part availability and handling checks remain required. An
overseas JLC oscillator offer does not establish home-delivery eligibility.

Previous goal turn classification: progress, because the new saved-coordinate
evidence was inspected, matched to inputs and replayed successfully. This turn
adds a complete public refresh and a bounded substitution shortlist. The goal
remains active; no final-release claim is made.
