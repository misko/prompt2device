# ADC8 coupling cap southwest source-pose replay

This is a **research-only** full-board replay of Terra's
[`C_ADC_AC8N1` pocket proposal](../2026-09-25-ti-adc8-pocket-adjustment-terra.md)
on the exact TI integrated placement union. `build.py` starts from the pinned
frozen TI source, parts, library and netlist; it reapplies the reviewed Q_PRE
anchor and all 45 prior research placements, then changes only
`C_ADC_AC8N1` from `(198.20,60.25,0°)` to **`(198.00,60.05,0°)`**. The native
board SHA-256 is
`0b9d017706845ad4d77c2b579dd36f2e34c0ecf55a7b699ace4fca97465c5b93`.
No source region, route, or canonical artifact was edited.

`analyze.py` confirms exactly one changed footprint pose across 569 refs;
all 27 P1-fixed poses and every pad number/net/layer/shape/drill/local
position are preserved. The cap's full checker envelope is now
`[195.205,58.305,200.795,61.795]` mm. Its east margin to the
`analog_ch8` owner and its south gap to the `usb_vbus_sense` rectangle each
increase **0.005→0.205 mm**. It intersects no other native full envelope or
pad. The nearest full-envelope gaps are `C_A8P` **0.360 mm**, `R_B8P`
**0.480 mm**, and `C_FILTER8N1` **0.780 mm**. That 0.360-mm support gap is
narrower than the former 0.560-mm cap-to-C_A8P gap and still needs a real
signal/return escape review. Related pad-center distances improve:
`C_ADC_AC8N1.1`→`U_ISO8.6` **7.846177→7.742254 mm** and
`C_ADC_AC8N1.2`→`C_ADC_CM8N.1` **13.957539→13.870865 mm**.

The global 569-ref census remains unchanged: **zero cross-owner native
interaction pairs**, 115 refs outside their primary owner rectangles, and
139 refs entering foreign planning rectangles. `profile_compare.py` reuses the
hash-pinned exact TI POFV replay, including `.kicad_pro`, `.kicad_dru`, eight
source-generated B2 rule areas, and independent via-process grading. Prior
union and southwest trial have **213 identical native DRC issue identities**
(+0/−0), **499 opens**, and no ISO8 clearance finding. The source generator's
silk-ownership warning count remains 275. The
[geometry receipt](receipt.json) and [profile receipt](profile_receipt.json)
pin the exact evidence.

The minimal eventual source delta is one `placement.post_anchors` entry:

```yaml
C_ADC_AC8N1: [198.0, 60.05, 0]
```

That line is **not** a standalone canonical placement change: current
canonical source does not contain the other 45 research poses, including the
nearby ADC8 supports. Independent review would need a complete source-level
union replay, cap/`C_A8P` pad escape and GND return routing with filled In1.Cu
reference, whole-module owner/foreign-cell containment, and a verified
silkscreen/F.Fab source mapping. The existing 28 timing reference-field moves
to F.Fab are not source-encoded. Conditional B2 POFV vendor/CAM/PCBA
acceptance, the TI/ordinary-source USB ESD pad-shape rebaseline, 499 opens,
and all P1 corridor and P2 electrical tests also remain. This pocket
adjustment has **no P1/P2, route, return, or production acceptance**.

Reproduce from this directory:

```sh
python3 build.py > /tmp/crow-cap-integrated-build.log 2>&1
python3 profile_compare.py
python3 analyze.py
```
