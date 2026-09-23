# TPSM63603 D-BACK allocation v2 — terminal result

Status: **NO COMPLETE LEGAL POSE IN THE V2 CENTER BANDS; ALLOCATION BACKTRACK REQUIRED; NO GLOBAL IMPOSSIBILITY CLAIM**.

The v2 allocation differs materially from the preserved v1 search: it separates VIN, VOUT, and quiet-control pose-center bands and admits same-owner relocation of `C_PWR_CT2`. The exact allocation is recorded in `/tmp/crow-power-dback-allocation-v2.md` (SHA-256 `a5a6d9fc9794d4cca6c98af59cd29407f5fb1fae8bb58e2e2e4fc291397d0bfd`).

The one bounded constructive solve ended after 379,400 joint states. It moved/rotated all 13 TPSM63603 satellites plus `C_PWR_CT2`, held `U_BUCK`, `J_PWR`, every other post anchor, the fixed 27, all 16 hold capacitors, and every unowned reference invariant, and used transformed courtyard polygon collision with 0.25 mm clearance. The terminal JSON is `/tmp/crow-power-joint-cell-candidate-v2.json` (SHA-256 `c321f141c350c403de28c1244cc6c5b76f6005cf76f5defa17138a9e0e23f2d3`). No complete assignment was found. No source patch is emitted from a partial packing.

The v2 bands constrain footprint **centers**, not full-courtyard containment. Therefore their gross rectangle area is not an impossibility proof and is not used as one.

## Exact neighborhood boundary and next owner decision

The right/east continuation of the VOUT band is occupied by the same-owner dump cell: `C_DUMP_TIME1/5/6/7`, `R_DUMP_TIME1/3`, and `U_DUMP`. Moving east would therefore require a broader quiet-power source-owner change plus revalidation of those existing numeric rows.

The south continuation is different: an exact fixed-footprint courtyard census finds **no fixed or unowned footprint** in x 48–61, y 78–88 mm. The next source-allocation decision is to expand only the VOUT pose-center band south from y 86.5–92.5 to y 82.5–92.5 mm while retaining x 50.5–58.5 mm, keep the dump cell invariant, and reserve a northbound U_BUCK VOUT-current corridor into that bank. This is an analytic space-allocation proposal, not a third search or a claim that it will pass.

`C_PWR_CT2` has no owned row in the 47-row census, but any later move must still be followed by the complete 47-row regrade. The v2 run found no accepted geometry, so the baseline 47/47 numeric receipt remains attached only to baseline bytes; it was not reissued or weakened.

The remaining-26 qualitative ledger remains binding at `/tmp/crow-power-remaining26-obligations-terra.md`, SHA-256 `6143119c7db4f012b23736dc83494d1b2565137475e4efd60c37b902f63c057e`. Those hold-bank, LDO, timing, OPA, return, Kelvin, and thermal obligations remain ungraded. Geometry alone cannot close them, and P3/FULL still owns saved-copper proof.

No board was saved or generated, no repository/source file was changed, and no routing or copper work was performed.
