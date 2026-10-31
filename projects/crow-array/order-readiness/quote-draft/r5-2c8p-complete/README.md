# Complete 2-carrier / 8-pod quote-upload package — r5

**Complete files for quote upload, not production approval.** This revision adds
manufacturer-derived nominal body centers and explicit physical orientations for
all 11 unique through-hole placements. It preserves the released boards, Gerbers,
full BOMs and every inherited SMT CPL byte. It supersedes r4's incomplete CPLs.
No upload, purchase, reservation, supplier contact or manufacturing commitment
has been made. Publication to the remote branch is a separate step.

## Files and quantities

Use these pairs from `quote-draft/r5-2c8p-complete/`; never mix revisions:

| Board | Gerbers | BOM | Complete CPL | Assembled quantity | JLC placements per board |
|---|---|---|---|---:|---:|
| Carrier | `carrier-gerbers.zip` | `carrier-bom.csv` | `carrier-cpl.csv` | 2 | 137: 127 SMT + 10 THT |
| Pod | `pod-gerbers.zip` | `pod-bom.csv` | `pod-cpl.csv` | 8 | 29: 28 SMT + 1 THT |

BOM/CPL quantities describe **one board**. Set assembly quantity separately in
JLC. Candidate bare fabrication remains five carriers and ten pods; confirm
service minimums without silently populating all bare boards.

| Installation owner | Exact part | Carrier refs / per board | Pod refs / per board | Batch count |
|---|---|---|---|---:|
| JLC THT | Amphenol RJHSE-5080 | J101–J108 / 8 | J1 / 1 | 24 |
| JLC THT | Same Sky PJ-102AH | J1 / 1 | — | 2 |
| JLC THT | RECOM R-78E5.0-0.5 | U10 / 1 | — | 2 |
| Home | Raspberry Pi SC0915 Pico | U3 / 1 | — | 2 |
| Home | CMA-4544PF-W microphone | — | MIC1 / 1 | 8 |
| Home | CPE-203 buzzer | — | BZ1 / 1 | 8 |

Factory total: **478 SMT + 28 THT = 506 parts**. Home: **18 parts**.
`scope.csv`, `procurement-plan.csv` and `home-install-parts.csv` retain exact
identities/references. Counts are installed need, not purchase quantities or
attrition allowances. RECOM and PCM1864DBT have intentionally blank JLC codes
pending exact eligible Global Sourcing/private-inventory matching.

## Local placement verification

Native coordinates are mm, X right / Y down. The existing CPL datum is retained:
**CPL X = native X; CPL Y = -native Y**, without an added origin translation.
Negative Y values are intentional. Every added THT component is top-side.

The native anchors are pad 1, not body centers. The CPL uses nominal geometric
body centers calculated below. All native THT angles are zero. Added CPL angles
are **0 degrees in the explicitly defined CAD poses below**, not a claim that
JLC's selected library uses the same zero. Positive rotation convention is
counterclockwise. JLC's [CPL specification](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly)
covers SMT and THT and asks for component center, side and rotation; the final
library interpretation must be checked after matching. Do not blindly apply a
universal 90/180-degree correction or use pad-1 coordinates as centers.

| Exact part | Center offset from native pad 1 (X, Y), mm | Required physical pose, top view |
|---|---|---|
| RJHSE-5080 | (+3.556, -0.127) | Mouth toward native -Y (CPL +Y); pin 1 left of pin 8; locating pegs ahead of signal rows |
| PJ-102AH | (0, +6.500) | Mouth toward native +Y (CPL -Y); pin 3 to the right of pins 1/2 |
| R-78E5.0-0.5 | (+2.590, -2.250) | Pins 1 VIN, 2 GND, 3 VOUT left to right; body mainly toward native -Y from pin row |

`tht-placement-verification.csv` gives every absolute anchor, body center, CPL
coordinate and physical orientation. Example checks: carrier J101 =
(11.556, -8.373), pod J1 = (10.556, -8.373), carrier power J1 = (188, -8.700),
carrier U10 = (184.590, -35.750), all mm in CPL coordinates.

Source facts and derivation:

- **Amphenol P-RJHSE-X080 Rev A, 2019-05-22**, user-supplied `rjhsex080.pdf`.
  Exact 5080 option is 50 microinch gold. Manufacturer source:
  [drawing](https://cdn.amphenol-cs.com/media/wysiwyg/files/drawing/p-rjhse-5080.pdf).
  Reviewed attachment SHA256:
  `e96d3f6cde115981be470e0edd3159dfda3ebe1a453db0c45d525e629668a756`.
  Primary units are inches. Body width/depth .620/.590; peg pitch .500;
  pin-to-peg lateral offset .110; front-to-peg .200; peg-to-pin-1 row .100.
  Center X = (.500/2 - .110) × 25.4 = 3.556;
  center Y = (.590/2 - .200 - .100) × 25.4 = -0.127.
  The component-side PCB pattern maps to the native footprint by a 180-degree
  planar rotation, **not mirroring**. Signal pitch .040, odd/even row separation
  .170 - .100 = .070; peg relative positions (-2.794, -2.540)/(9.906, -2.540).
  Native metric rounding differs by at most 0.004 mm; the verifier allows
  0.006 mm for that rounding, not as a fabrication tolerance. This source is
  Rev A, correcting the r2 review's unbound Rev J description.
- **CUI PJ-102AH Rev A, 2005-11-17**, manufacturer-authored drawing hosted by
  [Adafruit](https://cdn-shop.adafruit.com/datasheets/21mmdcjackDatasheet.pdf),
  SHA256 `74c35b925c9cbb3ded203afc33684eb76c538b0b99dc80e8500d5da8f1714e45`.
  Current Same Sky PDF access returned 403; the exact-part legacy drawing is
  identified rather than misrepresented as a current revision. Same Sky's
  [current catalog](https://www.sameskydevices.com/catalog/interconnect/connectors/dc-power-connectors/jacks)
  corroborates 14.4 × 9 × 11 mm body dimensions, not an independent new pinout.
  Front-to-pin-3 = 10.7 mm, pin-3-to-pin-1 along body = 3 mm, body length 14.4 mm:
  center Y = 10.7 + 3 - 14.4/2 = 6.5 mm. Width is symmetric about pins 1/2.
  Native pin 2 = (0,6), pin 3 = (4.7,3) relative to pin 1. Native pose is a
  180-degree rotation of the drawing's PCB top view. Pin 1 is center-positive
  VIN12, pin 2 GND sleeve; switched pin 3 is intentionally unconnected.
- **RECOM R-78E-0.5 Rev 9/2025, page I-3**,
  [manufacturer datasheet](https://recom-power.com/pdf/Innoline/R-78E-0.5.pdf),
  SHA256 `d3855b95007832c025518b4ee2073697aabee0b6be311484ea9a1aa7b3c53b96`.
  Body 11.6 × 8.5 mm; left edge to pin 1 = 3.21 mm; pin row to near edge = 2 mm.
  Center = (11.6/2 - 3.21, 2 - 8.5/2) = (2.59,-2.25).
  The recommended top-view pattern confirms pins 1/2/3 left-to-right at 2.54 mm.
  Manufacturer-derived center X is **0.10 mm right** of the KiCad F.Fab box
  center. Only the CPL body-center annotation changes: pads, footprint and
  released board remain unchanged. This is not a new mechanical-clearance
  acceptance or authority to waive retained fit/seating controls.

Dimensions above are nominal drawing values, not measured samples or a nozzle
pickup specification. PDF visual review plus read-only KiCad 10.0.4 checks
verify all 11 pin/peg constellations against native sources; labeled power pins
and existing SMT poses are checked. This is coordinator verification, **not an
independent adversarial review, new populated-3D acceptance, supplier approval
or a fabricated full-pipeline pass**. Original release acceptance is inherited.

## Validation and reproduction

From the repository root, portable verification needs only Python 3:

```sh
python3 -B projects/crow-array/order-readiness/complete_tht_quote.py verify
python3 -B projects/crow-array/publication.py verify
python3 -B -m unittest discover -s projects/crow-array/order-readiness -p 'test_*.py'
```

To reexecute native checks use Python with KiCad's `pcbnew` module (on this
server `/usr/bin/python3`) and append `--live-native` to the first command.
`build --output <new-directory>` regenerates the package and requires pcbnew;
it refuses to overwrite an existing revision. Manifest hashes bind sources,
the local native-audit record and every package file. Portable verification
checks retained evidence; it does not pretend to reopen KiCad on the MacBook.

## Next MacBook steps — quote only

1. After publication, sync the existing branch without disturbing local edits;
   run verification above. This package is currently local/unpushed. Record HEAD.
2. When browser upload is authorized, use only the r5 Gerbers/BOM/CPL pairs
   above. Set **2 assembled carriers / 8 assembled pods**, retaining candidate
   bare counts 5/10 until JLC confirms minimums. Do not multiply BOM quantities.
3. Match all **137 carrier / 29 pod** references, including the 28 batch THT
   parts. Keep exact MPNs, historical CUI/Same Sky naming reconciliation and
   Global/private-source exceptions. Home SC0915, CMA-4544PF-W and CPE-203 must
   remain absent; no extra assembly placeholders or unselected required parts.
4. Inspect both complete placement previews. For each THT instance, compare
   pin 1, all signal/terminal pads, peg holes, component center and the physical
   pose table above. RJ mouths face native -Y, power-jack mouth native +Y, RECOM
   VIN/GND/VOUT left-to-right. Compare ALL inherited SMT placements too.
   JLC library zero/center may differ: record any proposed corrections and
   return them for review; do not approve production or guess a rotation.
   If THT is omitted from the preview, obtain an explicit placement-reviewed
   THT operation quote rather than treating absence as approval.
5. Request/inspect a quote including all 506 factory placements and THT labor.
   Confirm safe supported installation method, original stack/stencil/seating/
   clearance controls, CTS handling and home-pad exclusions. Preserve released
   hand-solder constraints unless a different method receives engineering
   acceptance; JLC THT capability alone does not waive component limits.
   The retained assembly controls live under the release's `fab/` and
   `historical/` directories. Do not submit this README alone as the full
   manufacturing instruction package.
6. Resolve exact stock, gross quantities/allowances, source eligibility,
   sourcing/assembly fees, dates, shipping and tax. RECOM is JLC's responsibility
   again. Installed counts are not enough to authorize a parts purchase. If
   pricing requires a noncancelable pre-order/reservation, stop and report it.
7. Save quote and preview evidence, selected exact identities, corrections and
   remaining holds. No payment, reservation, substitution or manufacturing
   approval. Return the complete quote for a separate user decision.

If no complete quote can be produced without stock purchases, retain the
complete files and the explicit missing prices. Do not solve that by silently
omitting parts, moving THT home, or claiming this package is production-ready.
