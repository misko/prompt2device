# Two remaining power-branch pads: source-cell lower bound

Research only. `analyze.py` pins the unified TI board, source, floorplan and
modular-plan hashes, uses the native body/courtyard envelope function, and
checks all **569** native references against their modular owners. Run it from
any directory with `python3 /absolute/path/to/analyze.py`; it regenerates
`conflict_graph.json`. It changes no canonical source, board, or checker.

The exact pads are `C_LDO_OUT_1.1` (`N3V3_ADC`),
`[134.1,120.75,135.5,123.65]` mm, and `R_PWR_TOP.1` (`N5V_BUCK`),
`[74.775,91.025,75.575,91.975]` mm. Both are electrically owned by
`quiet_power`. The **minimum one-rectangle owner region** containing both
pads is `[74.775,91.025,135.5,123.65]`. It intersects the full native
body/courtyard envelopes of **58 `adc_reference` footprints**, including both
ADC ICs. The minimum rectangle containing the two *whole footprints* is
`[74.475,90.725,135.795,123.945]`; the existing `adc_reference` and
`hold_bank_right` source regions intersect it. A direct `_physical_cells`
trial of that rectangle fails on the first foreign native ADC footprint,
`C_ADC_B_AVDD_10U`. Thus a single source-only rectangular `quiet_power`
physical cell admitting both pads is impossible on this board while retaining
all electrical owners and foreign occupancy. Declaring the 58 ADC bodies as
quiet-power members would falsify the modular owner map.

The local clusters themselves are physically clear of foreign native
envelopes: the U_PWR cluster hull is `[71.175,90.725,79.475,97.275]`, and
the U_LDO cluster hull is `[126.255,114.405,140.955,126.775]`. Both currently
intersect only the broad `adc_reference` source region. Its 65 native members
fit a tighter `[90.455,87.505,142.275,112.255]` hull with **zero foreign
envelopes**. That recut is a necessary local source-region step, but it does
not by itself admit the two branch pads.

**Correction to the original packet:** the current checker already accepts an
endpoint `physical_cell_id` in an unresolved branch, while preserving the
electrical `block`. The earlier
[`ti-power-branch-physical-cell-sol`](../2026-09-25-ti-power-branch-physical-cell-sol/README.md)
replay proves this for three XU pads and admits complete `N1V8`/`N3V3X`
branches. The remaining barrier is **absence of a validated, complete
quiet-power cell partition**, not missing checker syntax. An untagged pad
still uses `regions[block]`. Simply naming two new local cells is insufficient:
after recutting `adc_reference` to the native 65-member hull above and making
the U_PWR hull the `quiet_power` primary cell and U_LDO hull a second cell,
the real `_physical_cells` checker rejects the trial with
`quiet_power: physical cell ref denominator incomplete`. It requires an exact,
connected partition of **all 69** quiet-power references, including the hold
banks and U_LDO_EN, before either pad can use `physical_cell_id`. The broad
`quiet_power`, `input_buck`, and hold-bank source regions must be reconciled
with that disjoint partition. These are lower bounds, not a claim that the
entire connected partition is feasible.

**Next action:** design and native-check a connected 69-member quiet-power
cell partition together with the tighter ADC region and adjacent input/hold
region boundaries, then tag the two branch endpoints with their validated
cell IDs. Retain null branch capacity and all P2/P3/current/return debt. A
*single common rectangular cell* remains impossible on this board because of
the 58-body obstruction; separate cells are supported but not yet completely
modeled or admitted. No route or P1 credit is claimed here.
