# Quiet-power functional-cell candidate and two-tag conflict

Research-only negative packet. `replay.py` pins the **reviewed Q_PRE repair**
board SHA-256 `e07ed8bc663fdfd4ce39477165b656b0dcf2bfbae54d84ec501bfccf326d22ef`,
the unified TI electrical source, floorplan and modular plan. It applies the
reviewed `Q_PRE` post-anchor `(46,107.15,0°)` in memory. All **569** native
references retain their exact modular electrical owners and original netlist;
the 27 fixed poses are unchanged. It writes `result.json`, never canonical
source or PCB. Reproduce with `python3 replay.py` from this directory.

The candidate partitions all **69 `quiet_power` references exactly once**
into ten functional occupied groups: PWR controller, LDO, pre-switch,
pre-gate, buck edge, dump timing, audio control, pre support, mid control,
and the two hold banks. Each group uses the hull of its members' native full
body/courtyard envelopes. It tightens `adc_reference` to the hull of its 65
members, narrows the broad `input_buck` planning rectangle, and rebinds the
affected placement patterns to their proposed cells. The group membership,
rectangles and full checker outcomes are in `result.json`. These are
*disposable candidate cells*; none are accepted source authority.

Actual `_physical_cells` rejects the candidate at
`quiet_pre_switch: unassigned native footprint/pad Q_DUMP enters physical cell`.
This first group conflict could be refined by repartitioning, so it is **not**
the impossibility proof. In particular, the previously reported native
`Q_PRE`/`C_IN3` overlap is repaired on this board: their full-envelope y gap
is **0.260 mm**. The earlier board's overlap must not be cited as a current
blocker.

The decisive full-denominator constraint is the instruction to tag **only**
`C_LDO_OUT_1.1` and `R_PWR_TOP.1`. The other nine `quiet_power` endpoints on
the four exact power nets remain untagged, so the branch checker requires all
nine pads inside the **single primary** `quiet_power` rectangle:

| Net | Untagged quiet-power pads |
| --- | --- |
| `N3V3_ADC` | `C_LDO_OUT_2.1`, `C_OPA_BULK.1`, `R_ADC_TOP.1`, `R_DUMP.1`, `R_LDO_PG_TOP.1`, `R_OPA_BLEED1.1`, `U_LDO.10`, `U_LDO.9` |
| `N5V_BUCK` | `D_HOLD.2` |

Their minimum enclosing pad rectangle is
`[21.72,106.85,138.45,122.48]` mm. It intersects **21 full native
`adc_reference` envelopes**, including `U_ADC_B`. Shrinking the ADC planning
region cannot remove those occupied bodies. Under the present fail-closed
`physical_cells` grammar, every occupied primary quiet-power cell would
reject the foreign ADC footprints. A source-only partition with exactly the
two requested branch tags is therefore impossible on this board without
moving or falsely reassigning components. This is independent of how the ten
candidate groups are subdivided or connected.

Using only the six already validated physical cells as branch authority,
the actual isolated four-net checker accepts `N1V8` (42/42) and `N3V3X`
(27/27) with the three existing XU tags. It rejects `N3V3_ADC` (68/68) at
the unvalidated `C_LDO_OUT_1.1` cell, and `N5V_BUCK` (34/34) at untagged
`D_HOLD.2` outside the proposed primary cell. The full 171-terminal
denominator, all P2 pad-to-tree, P3 tree, current/return and null-capacity
debt remain; no route or P1 acceptance is asserted.

**Next action:** either permit exact `physical_cell_id` tags for the additional
nine quiet-power power endpoints and validate a complete connected 69-member
cell partition, or move the blocking physical clusters before repeating the
two-tag constraint. Do not promote this candidate or infer capacity from its
planning rectangles.
