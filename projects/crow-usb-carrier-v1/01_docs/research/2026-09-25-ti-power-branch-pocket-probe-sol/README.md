# Sparse power branch pocket probe — incomplete

`python3 replay.py` reconstructs the accepted 13 occupied `quiet_power` cells on
the reviewed Q_PRE-moved TI board and calls the current native
`_branch_owner_pockets` validator with full-footprint singleton pockets. Inputs
are pinned by `replay.py`; `result.json` records the tested checker digest and
the native conflicts. Nothing in this packet changes canonical source or board.

The four full native power branch terminal denominators remain **42, 27, 68,
and 34 (171 total)**. A pocket has no route, capacity, or return credit. Its
geometry must contain the complete native body, both courtyards, and pads; a
pad-only rectangle cannot satisfy the current schema.

| Proposed pocket | First native checker failure | Consequence |
| --- | --- | --- |
| `U_AFE2` in `analog_ch2`, N3V3_ADC | Full envelope x=62.055–69.545 intersects `analog_ch3` starting x=69 | Moving that boundary to x=69.545 excludes native `R_IN3P` and `U_ESD3` from their owner region. |
| `U_AFE3` in `analog_ch3`, N3V3_ADC | Full envelope x=84.055–91.545 intersects `analog_ch4` starting x=91 | Moving that boundary to x=91.545 excludes native `R_IN4P` and `U_ESD4`. |
| `U_BUCK` in `input_buck`, N5V_BUCK | Full envelope overlaps same-owner `C_IN1` and `C_IN2`, so a singleton pocket is invalid | Rectangular native-envelope closure must add those, `R_BUCK_FB_TOP`, `C_IN_HF`, and `C_OUT1`; its hull then touches foreign-owner `C_PWR_CT2` in the accepted `quiet_buck_edge` cell. |

Thus the current sparse pocket mechanism does **not** safely clear either
remaining branch. The analog sites need a coupled, native-valid neighboring
region/member recut or physical movement. The buck site needs a physical
separation of the input cluster from `C_PWR_CT2`, or a separately reviewed
geometry model that can represent a nonrectangular complete native-envelope
owner pocket. Merely tagging the three pads would be a false acceptance path.
No P1 acceptance or realized route is claimed.
