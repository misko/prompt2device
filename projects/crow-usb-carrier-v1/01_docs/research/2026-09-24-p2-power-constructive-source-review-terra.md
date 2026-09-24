# Independent power source-placement review

review_verdict: SOUND

source_patch: ELIGIBLE

native_admission: NOT_REVIEWED

## Identity and completeness

This is a fresh, source-only judgment of patch
`3e58a56094c91a5fdbac59744ff52d012f5c772f872b103217efa4954239ad03`
against base floorplan
`934673990bbcfb6f1d0c163fef6e082830eb613fa22ae2ef2117e1ecce34fb3d`.
The parsed patched floorplan hash is
`f1a59fbbdce6ee9e325fb0e797ff43bbe6884684aa30da80262d9c69de41bef8`.

I computed the envelope SHA-256 as
`6b8e723c7a0c8e715944bf58589d3bb796021195dcb9ba002c9704cd79ec3f6d`
and the manifest-file SHA-256 as
`035150de0993da7ddcad8a804d8201e7b91d32a15b5d49f6944d4a1f3159aab6`;
both equal the required values. The envelope has 103 inputs, all of whose
actual bytes, sizes, and hashes agree with their records. Its 90 selected
`inputs/02_parts/*/part.yaml` records agree one-for-one with the manifest's
90 files (`selected_count: 90`): 90/90 raw dossiers verified, with zero
missing, size, hash, or envelope-manifest mismatches. This is not a
zero-denominator result.

Duplicate-rejecting YAML parsing passed for base and patched floorplans plus
the supplied `nets.yaml` and `route.yaml`. A parsed recursive comparison
finds exactly 18 differences, all under `placement.post_anchors`; the key set
is unchanged and there are no other source-key differences. The supplied
patch applies to the base with `patch --dry-run --fuzz=0`. The 18 changed refs
are `C_IN1`, `C_IN2`, `C_IN3`, `C_IN_HF`, `C_OUT1`, `C_OUT2`, `C_OUT3`,
`C_VCC`, `C_VLDO`, `D_HOLD`, `Q_PRE`, `Q_PRE_EN`, `R_AGND_JOIN`,
`R_BUCK_FB_BOTTOM`, `R_BUCK_FB_TOP`, `R_PRE`, `R_PRE_G`, and `R_RT`.

All 48 current `post_anchors` whose names contain `ADC` remain byte-for-byte
unchanged. The `adc_reference` modular block's 65 refs are still present in
the supplied source representations; no ADC source entry was deleted or
altered.

## P0/P1/P2 findings and geometry evidence

P0: none. The source diff, YAML integrity, and supplied clearance predicates
have no finding.

P1: `C_OUT1` is the one worsened functional-pad diagnostic. Its distance to
TPSM63603 VOUT pin 15 moves from 6.910 mm to 7.275 mm (+0.365 mm). This is a
real local tradeoff and must not be hidden by the aggregate result. It is
acceptable for this source reservation because the moved group materially
improves the VIN/VCC/VLDO/FB/RT/AGND neighborhoods, all stated geometric
predicates pass, and this number is a diagnostic rather than a manufacturer
maximum or a routed-length claim. No other row in the supplied before/after
functional-pin table worsens: C_IN1/2/3/HF, C_OUT2/3, C_VCC, C_VLDO, both FB
resistors, RT, and AGND_JOIN all improve. This does not establish any actual
converter loop, return, Kelvin connection, EMI, or thermal behavior.

P2: the evidence remains placement/reservation evidence only. It has no
native P2 board, no realized copper, and no physical/assembly proof. The
owner ledger retains 26 saved-copper obligations. Those limitations are
admission boundaries, not a defect in the narrowly stated source patch.

I reviewed all 47/47 numeric P-ADJ/P-ADJ-PAIR observations. Their 47 unique
IDs and budgets agree with the corresponding selected-dossier layout rules:
14 for `74LVC1G14GV,125`, 2 for `AO3400A`, 4 for `AO3401A`, 4 for
`DMP6023LFG-13`, 11 for `LT3045EDD-PBF`, and 12 for `TPS389001DSER`.
All are reported passing with no failed row. The measurement record is not a
copy of the original candidate census: its six LT3045 `keep_short` results
changed on remeasurement (for example 4.937 -> 3.210 mm and 3.272 -> 1.316
mm), while preserving the declared 5.0 mm budgets. That is consistent with
the supplied claim of pad-geometry/copper-gap remeasurement rather than
echoed center distances.

The governing clearance is **0.20 mm**, from the applicable power classes in
`nets.yaml` and the route contract. The 0.09 mm value is only the
`jlc_4layer_advanced` fabrication capability floor and is not used to grade
this candidate. At 0.20 mm, the reported full-board predicate covers 568
footprints, 1,805 pads, 161,028 footprint pairs, 1,615,827 inter-footprint
pad pairs, and 2,959,002 paste pairs, with no scope finding. The evidence
also reports: exact transformed courtyard separation of 0.25 mm with no
finding; assembly envelope to foreign effective copper at 0.10 mm with no
finding; a 19.025 mm minimum moved-pad boundary margin; and no 0.25 mm
courtyard finding for any of the 18 moved refs versus all 16 hold-bank caps.
The precharge four-row check remains passing at 1.950/2.000, 3.675/4.000,
1.780/2.500, and 3.000/3.500 mm (measured/budget). Pad/paste and
courtyard/body/boundary/hold-bank denominators are therefore stated and
nonzero.

## Functional and scope review

The 90 raw dossiers support the limited functional coherence judgment. The
input path reserves the fuse and reverse-polarity/protection neighborhood:
the 0451004.MRL has IN/OUT, the DMP6023LFG has source pins 1--3, gate 4, and
common drain 5--8, and the B340A has K1/A2. The TPSM63603 dossier identifies
VIN 3/4/18/19, VOUT 7--10/12--15/30, VLDOIN 22, VCC 23, AGND 24/27, FB 25,
and RT 1. The moved satellites consequently reserve a coherent source
neighborhood for the named VIN, VOUT, VCC/VLDO, feedback, RT, and AGND
functions; it does not prove copper topology. The precharge pose preserves
the AO3401A SOT-23 G/S/D role and the D_HOLD/Q_PRE/Q_PRE_EN/R_PRE/R_PRE_G
relationship. The quiet-power source facts identify LT3045 IN 1/2, ILIM 5,
PGFB 6, SET 7, GND 8/11, OUTS 9, and OUT 10, supporting its retained
input/output/SET/OUTS reservation but not a Kelvin or low-noise result.

I read all 89/89 qualitative ledger rows. Their per-reference classifications
are complete:

- Patched pose (18): `C_IN1`, `C_IN2`, `C_IN3`, `C_IN_HF`, `C_OUT1`,
  `C_OUT2`, `C_OUT3`, `C_VCC`, `C_VLDO`, `D_HOLD`, `Q_PRE`, `Q_PRE_EN`,
  `R_AGND_JOIN`, `R_BUCK_FB_BOTTOM`, `R_BUCK_FB_TOP`, `R_PRE`, `R_PRE_G`,
  `R_RT`.
- Fixed power anchor (2): `J_PWR`, `U_BUCK`.
- Hold/fixed reservation (16): `C_HOLD1` through `C_HOLD16`.
- Preserved unowned/existing reservation (53): `D_IN`, `D_QIN_GS`, `F_IN`,
  `Q_IN`, `R_QIN_G`; `C_AUDIO`, `C_AUDIO_CT1`, `C_AUDIO_CT2`,
  `C_DUMP_LOGIC`, `C_DUMP_TIME1` through `C_DUMP_TIME8`; `C_LDO_EN`,
  `C_LDO_IN`, `C_LDO_NR4`, `C_LDO_NR5`, `C_LDO_OUT_1`, `C_LDO_OUT_2`,
  `C_OPA_BULK`; `C_PWR`, `C_PWR_CT`, `C_PWR_CT2`, `C_PWR_CT3`; `Q_DUMP`;
  `R_ADC_BOT`, `R_ADC_TOP`, `R_AUDIO_PD`, `R_AUDIO_PU`, `R_DUMP`,
  `R_DUMP_PD`, `R_DUMP_TIME1`, `R_DUMP_TIME2`, `R_DUMP_TIME3`,
  `R_LDO_ILIM`, `R_LDO_PG_BOT_A`, `R_LDO_PG_BOT_B`, `R_LDO_PG_TOP`,
  `R_LDO_SET`, `R_OPA_BLEED1`, `R_OPA_BLEED2`, `R_PWR_BOT`, `R_PWR_PU`,
  `R_PWR_TOP`, `U_AUDIO`, `U_DUMP`, `U_LDO`, `U_LDO_EN`, `U_PWR`.

Each row separately retains a P3/FULL saved-copper obligation. For input
protection that includes the actual high-current path, gate clamp/return, and
fuse/diode/FET thermal behavior; for the buck it includes VIN/VOUT/quiet
return copper, switching loops, ground association, thermal, and EMI; for
precharge/hold it includes copper, gate return, sharing, pulse, and thermal
behavior; for LT3045 it includes input/output/SET/OUTS/EP copper, Kelvin
return, load path, and thermal behavior. The other preserved groups retain
their named dump, hold-bank, or local-reservation obligations. Thus the
numeric 47 result is explicitly not treated as sufficient source-suitability
evidence by itself.

## Disposition and exact next boundary

The 18-pose patch is eligible for later source adoption after the **569
schematic checkpoint**, subject to this review's scope. It does not admit a
native board. The next boundary is to regenerate native P2 from the adopted
source and obtain an independent native-P2 review that rechecks actual pad,
paste, courtyard, body/envelope, boundary, hold-bank, and functional-pin
geometry. Only after that may the separate saved-copper P3/FULL work address
current loops, return paths, Kelvin connections, EMI, thermal behavior,
precharge/hold sharing, and physical/assembly qualification. P3, FULL, and
release remain blocked by this review.
