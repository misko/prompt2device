# WSLP model source closed; coupled power analysis remains open

Source subject: `f04370b66f829ca85ae108009b0e678cf51f8358` plus the
model-only change set described here. No electrical, placement, rule, generated
schematic/board, pod, checkpoint or release bytes changed in this sub-batch.

## Source change and primary authority

Added the tenth reproducible VRML model and attached it to the authored
`Vishay_WSLP1206_50m_Exact` footprint with identity transform. The other nine
producer outputs are byte-identical to the committed baseline. A parsed
non-model footprint comparison proves all pre-existing geometry is unchanged.

The existing archived Vishay30122 revision09-Sep-2024 PDF p2 was rendered and
visually inspected. Its exact0.006..0.050ohm row supplies nominal overall
3.20x1.60x.635mm and terminal lengthT=.508mm; these are not generic1206
dimensions or the1.65x1.93mm copper land. All four tolerances are+/-.254mm.
[Manufacturer drawing](https://www.vishay.com/docs/30122/wslp.pdf).
PDF SHA256: `36e35aeb3d41f110442de6690ef220a8a20c720118a40abb0fa8eedbf7308edb`.

Model SHA256: `b11845f0e20c69fec2b29a2b1a5f13ee76a6d37b32aefcc31be140f6edd96c6c`.
`03_src/lib/3dmodels/provenance.md` records the omitted underside relief,
coating/weld/marking detail and unswept production maxima. This is a nominal
visual envelope, not manufacturer CAD, solder geometry or a thermal model.

## Observed RED/GREEN and isolated-coupon evidence

- Actual pre-fix model suite:8 tests,3 failures and2 errors,rc1. Missing
  model bytes, missing attachment and nine-versus-ten inventory were exposed.
- Corrected model suite:8/8 PASS. Independent expected dimensions, terminal
  coordinates, four footprint rotations and KiCad reopening are checked.
  Wrong relative90degree rotation,2.54x scale and negativeZ are rejected by
  the same terminal registration predicate used on the corrected geometry.
- Full affected source suite:241/241 PASS,93.497s; actual bounded elapsed
  93.809163s,06:38:50.777151–06:40:24.587758Z,rc0.
- Native isolated coupon:seven successful renders covering0/90/180/270,
  matched-camera populated/bare top, and normal/inverted front/right views.
  Four model-minus-bare body envelopes:4/4 within.06mm, worst edge error
  .027681661mm at57.655860px/mm. Each body contributes15664 measured pixels.
- Signed mount-side fraction:normal1.000000; deliberately inverted model
  .055112 versus.75 minimum, rejected. The wrong-side top render is exactly
  byte-identical to the bare image; renderer success alone proves no body.
- Model/digest inventory:12/12 SHA256SUMS entries verify, including the
  unmodified external capacitor model and its licence.

Full-suite log SHA256:
`72f641f6e1cd2ff75c348a0cd52adc394c6b90c33f47045d8bff04765af0140c`.
The [source-correction outcome record](../SOURCE-CORRECTION-20260909-wslp-model-outcome.json) retains actual command metadata,
logs, coupon measurements and diagnostic scripts. All coupon boards/images are
temporary evidence, not candidate carrier generation or P-MODEL-REG acceptance.

For this end-contact resistor, the generic `all_pad_centres`-inside-body
predicate is not the right physical datum: copper centres+/-1.725mm correctly
extend beyond the nominal body+/-1.600mm. The terminal footprints lie inside
the actual copper at all four rotations. No body, copper or tolerance was
changed to make an inapplicable predicate pass; the shared gate was not edited.

## Remaining release work

The separate fresh electrical task studies the unchanged coupled raw/OPA/held
network, qualified precharge timing, repeat histories and current duration.
This model sub-batch does not accept those electrical assumptions. The previous
source-regression closure report still owns the unresolved engineering list,
except its WSLP missing-model item is now closed at source-file level.
Full native regeneration, current-board registration, fresh independent reviews,
routing and release sealing remain ahead. Physical/order/publication holds and
the existing pod seal are unchanged. No JLC upload or purchase was performed.

The fresh study is now terminal INCOMPLETE; its decisive findings and next
engineering calculation are in [the coupled-power report](2026-09-09-coupled-power-findings.md).

## Model folder contract correction

The repository-wide present-file audit exposed two pre-existing omissions:
the model folder allowed nested provenance/checksums but not its top-level
`3dmodels/provenance.md` and `3dmodels/SHA256SUMS`. Added those two exact entries
after the electrical worker released its scope. The same audit rejects both
before and accepts both after; no numeric gate, debt ceiling or unrelated
folder was changed. The whole audit still fails on inherited findings:
2893 to 2891 repository violations, 18 to 16 carrier violations. This is not
a claim of a clean repository-wide audit. The in-flight untracked count is
separate and is resolved by committing this source batch, not an ignore rule.
Actual before/after log SHA256 values:
`a83e9946ac0199dee94e6fb8a131e81c6a10459c99a6f412a7649b3ecfa62dc9`,
`8424e45df1f4041dff6fd447083de99cb6e60cde86e0bd6ff7be78cdb4991cc5`.
