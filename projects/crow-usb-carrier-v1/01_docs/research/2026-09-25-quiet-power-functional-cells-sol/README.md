# Quiet-power physical-cell refinement on reviewed TI board

**Research only; no route, current/return, capacity or P1 credit.**
`replay.py` pins the reviewed Q_PRE-repair TI board SHA-256
`e07ed8bc663fdfd4ce39477165b656b0dcf2bfbae54d84ec501bfccf326d22ef`
and the unified source/floorplan/modular-plan inputs. The candidate applies
Q_PRE's reviewed `(46,107.15,0°)` source pose in memory. It retains every
native pad/net, all **569** modular owners, and all fixed component poses;
canonical Crow files are untouched. Run `python3 replay.py` here to regenerate
[`result.json`](result.json).

One bounded functional partition refinement assigns all **69 `quiet_power`
references exactly once** to 13 occupied cells: PWR controller, LDO, buck
edge, dump timing, audio control, mid control, both hold banks,
and five small pre-switch/hold-control cells. Small occupied pockets are used
only where neighboring full native envelopes defeat a broad rectangle; this
is not a 69-singleton construction. The candidate tightens `adc_reference`
to its 65-member native hull, recuts `input_buck`, and splits affected
placement patterns. The *actual* `_physical_cells` checker accepts all cells,
including full body/pad containment, disjoint foreign occupancy, owner/ref
denominator and pattern checks. Cell IDs, member lists and exact bboxes are
in the result. This receipt does not prove copper or a connected route.

The reviewed Q_PRE move removes the old Q_PRE/C_IN3 envelope overlap: the
current native y gap is **0.260 mm**. The old collision was a stale-board
artifact and is not a blocker here.

For the four power nets, the candidate adds `physical_cell_id` to **all ten**
quiet-power endpoints outside the proposed primary `quiet_power` cell. The
only untagged quiet-power power endpoint is `R_PWR_TOP.1`, inside that primary
cell. `C_LDO_OUT_1.1` is tagged; `R_PWR_TOP.1` needs no tag because it lies
inside the primary cell. Nine additional endpoints need tags to retain the
full 171-terminal denominator:

| Net | Tagged quiet-power endpoints |
| --- | --- |
| `N3V3_ADC` (68 terminals) | `C_LDO_OUT_1.1`, `C_LDO_OUT_2.1`, `C_OPA_BULK.1`, `R_ADC_TOP.1`, `R_DUMP.1`, `R_LDO_PG_TOP.1`, `R_OPA_BLEED1.1`, `U_LDO.10`, `U_LDO.9` |
| `N5V_BUCK` (34 terminals) | `D_HOLD.2` |

The actual isolated unresolved-branch checker accepts `N1V8` **42/42** and
`N3V3X` **27/27** with the three previously validated XU tags. It rejects
`N3V3_ADC` at **`U_AFE2.8`**, whose pad x maximum is **69.25 mm** while its
`analog_ch2` primary region ends at **69.00 mm**. It rejects `N5V_BUCK` at
**`U_BUCK.10`**, whose pad y maximum is **100.70 mm** while the proposed
`input_buck` region ends at **100.50 mm**. Both failures are outside the
validated quiet-power cells; the checker stops at the first violation on
each net. The four branches preserve exact source/native terminals, all
P2 pad-to-tree and filled-return duties, P3 tree duties, and null capacity.

**Next action:** resolve these two newly exposed foreign-owner/source-region
failures in a separate coupled floorplan review, including all endpoints that
any recut would displace. This packet stops at that conflict set. Do not
promote its cells or infer P1 acceptance from their geometric validation.
