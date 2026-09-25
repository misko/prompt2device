# Review: physical-cell unresolved branches

Reviewed checker commit `eb439d58` on checker SHA-256
`b4ece816b23bcc1f213a6e66253d4aa2dfe1a1358a5a74aaaea40fd8a36bab95`.
This is research only; P1 remains unaccepted.

The supplied exact-board replay passed its intended positive case.  It tags
only `C_XU_VDDIO_35.1`, `C_XU_VDDIO_56.1`, and `C_XU_USB33.1` with existing
`xmos_core_east`, while retaining their modular owner `xmos_core`.  It keeps
all 171 power terminals.  Isolated `N1V8` and `N3V3X` branches are accepted;
`N3V3_ADC` remains blocked at `C_LDO_OUT_1.1` and `N5V_BUCK` at `R_PWR_TOP.1`,
both outside `quiet_power`.  The full replay remains `FAIL`,
`routing_realized=false`, and `p1_accepted=false`.

`UnresolvedBranchPhysicalCellTest` ran 4/4 successfully.  Its missing-cell,
wrong-cell, wrong-owner/ref, clipped body/pad, wrong-pattern, extra-field, and
undeclared-native-pad cases all fail closed.  The checker also continues to
ban `bbox` and `capacity_slots` from unresolved branches, so the physical-cell
extension grants no geometry or capacity credit.

## Blocking defect: aliased native pad duplication

The branch validator still accepts two distinct source terminals that alias
one native pad.  A synthetic four-source `TREE` branch with `J_USB.A1` and
`J_USB.B1` both mapped to native `J_USB.1` returned success.  It validates
unique source-pad keys, then collapses `expected_native` to a set before the
native-board census; no source-to-native one-to-one check remains.

This violates the exact terminal denominator: two declared obligations can
stand for one physical pad.  The physical-cell change neither causes nor fixes
it, but a full-native-identity branch admission cannot be relied on until it
uses the linked-pad collision rule (or an equivalent check) before its native
census.  Do not admit the 171-pad power branch overlay as an exact native
denominator proof until that correction and a negative alias-collision test
land.

The executable
[`unresolved_branch_duplicate_native_alias_fixture.py`](2026-09-25-unified-power-boundary-replay-terra/unresolved_branch_duplicate_native_alias_fixture.py)
is the exact regression fixture.  It exits unsuccessfully under the reviewed
`eb439d58` checker because that checker accepts the alias collision.  During
this review, the subsequent uncommitted correction visible in the shared tree
rejected the same fixture with `branch source/native terminal alias collision`.
That later observation is not a review of a committed fix; it only confirms the
fixture exercises the intended guard.
