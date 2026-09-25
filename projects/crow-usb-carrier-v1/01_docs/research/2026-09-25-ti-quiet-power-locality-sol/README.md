# Quiet-power branch locality screen (research only)

The exact 569-reference TI diagnostic board and unified floorplan are pinned in [`receipt.json`](receipt.json). This read-only screen addresses the two residual `eb439d58` branch witnesses: `N3V3_ADC` at `C_LDO_OUT_1.1` and `N5V_BUCK` at `R_PWR_TOP.1`. Both refs belong to `quiet_power`, whose primary rectangle is `[25,105,75,134]` mm. Neither witness is inside that rectangle. No placement, canonical source, copper, or acceptance state changed.

`C_LDO_OUT_1` has native body/courtyard envelope `[130.205,120.455,135.795,123.945]` mm, entirely in the broad foreign `adc_reference` rectangle. It is physically local to its LDO cluster: its envelope is 0.310 mm from `U_LDO`, 0.460 mm from each of `C_LDO_IN` and `C_LDO_OUT_2`; its N3V3_ADC pad center is 4.395 mm from `U_LDO.9` and 3.883 mm from `C_LDO_OUT_2.1`. The minimum axis-aligned shift into the present quiet-power rectangle is **60.795 mm west**. That projected full envelope `[69.410,120.455,75.000,123.945]` intersects `C_HOLD4`'s native full envelope over `[69.410,120.455,72.995,123.945]`. This is the first hard physical conflict; no further placement search was made. The move would also separate the output capacitor from its regulator by roughly 60 mm, contrary to the existing local output-cap arrangement.

`R_PWR_TOP` has full envelope `[74.475,90.725,77.525,92.275]` mm, overlapping `adc_reference` east of x=75. Its feedback pad `R_PWR_TOP.2` is only 2.427 mm from `U_PWR.1` and 3.338 mm from `R_PWR_BOT.1`; native-envelope gaps are 0.475 and 0.250 mm respectively. Merely fitting its full envelope inside the present quiet-power rectangle requires at least **2.525 mm west and 14.275 mm south**. That is not a tiny local adjustment, and this screen did not trial a move after the first `C_LDO_OUT_1` hard conflict.

The two electrically local clusters are sparse quiet-power-owned groups within broad `adc_reference` planning space. A source repair should represent validated local owner pockets at current native poses, coupled with an explicit region/foreign-occupancy treatment, or recut the relevant functional regions while preserving every existing owner and corridor. The current unresolved-branch rule tests `regions[block]` unless an endpoint names a fully validated `physical_cell_id`; simply naming a pocket or moving one pad cannot bypass native full-envelope containment and foreign-owner checks. Any such model needs its own complete ref/footprint and corridor census. This receipt provides no P1/P2/P3 credit.

Reproduce from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-quiet-power-locality-sol/screen.py > projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-quiet-power-locality-sol/receipt.json
```
