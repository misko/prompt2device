# Independent review: prototype-only schematic adopter

**Reviewed immutable implementation:** `7cb829e9e0cf68b671da67ba4ef246363a5008eb`.
This is an implementation review only.  I did not run the adopter against the
Crow canonical project or promote any artifact.

## Disposition

**PASS for its intentionally narrow transaction.**
`03_src/adopt_prototype_schematic.py` can only adopt a complete private
`PROTOTYPE_ONLY` TI producer bundle into these four schematic-stage paths:

1. `03_tscircuit/build/circuit.json`
2. `04_kicad/crow_carrier.kicad_sch`
3. `06_build/netlists/crow_carrier.net`
4. `03_tscircuit/build/schematic.pdf`

It has no board, router, release, order, ordinary checkpoint, or pinned-reuse
promotion path.  The resulting private receipt explicitly says
`SCHEMATIC_ONLY`, `ordinary_checkpoint: NOT_REFRESHED`, and
`pinned_reuse_schematic: NOT_PROMOTED`.

## Admission and stale-data controls reviewed

- It accepts only the exact `U_USB_ESD` selection
  `TPD2EUSB30ADRTR`, whose suitability is `prototype_only`; an ordinary PASS
  selection is rejected.  It also verifies the unchanged pause-state
  checkpoint binding.
- The private bundle must be below `06_build/prototype_only`, have a complete
  four-artifact receipt, bind every governed source input by SHA-256, contain
  569 unique components, 1,787 pad/net tuples, 428 nets, and the exact TI
  DRT footprint/value/pad map.  It re-exports the bundle schematic and rejects
  a native-netlist mismatch.
- Before plan, after the staged gates, and immediately before the marker and
  replacements, tracked destinations must be Git-clean.  The caller must
  provide the intact `--plan` JSON and a new private backup directory.  The
  four observed hashes are rechecked before promotion; changed contents abort
  before replacement.
- The staged E-FAULT, P-PREC semantic-review, and ERC checks run on an
  independently copied temporary view.  The source copy uses `shutil.copy2`,
  so a defective gate cannot mutate canonical source through a hard link.
- Artifacts are staged, backed up, then replaced as a set.  A pending marker,
  post-write hash check, receipt staging, and rollback of every replaced
  artifact fail closed on a partial-write error.

## Verification

From the repository worktree, I ran:

```sh
git show --check 7cb829e9
python3 -m unittest \
  projects/crow-usb-carrier-v1/03_src/tests/test_adopt_prototype_schematic.py -v
python3 -m py_compile \
  projects/crow-usb-carrier-v1/03_src/adopt_prototype_schematic.py
```

All commands passed.  The focused suite is **11/11**, including rejection of
dirty tracked and untracked destinations, stale or partial bundle data, an
ordinary selection, failed staged gates, a late competing workstream edit,
and a simulated gate-side source edit.  KiCad emitted three pre-existing
`PROPERTY_ENUM` assertions while importing its Python bindings; the tests
nevertheless completed successfully and none exercises a board flow.

## Residual operational limit

The native netlist is intentionally ignored by Git, so Git cannot identify
its editor.  Its exact bytes remain plan-bound and are copied to the private
backup before any replace.  As with any multi-file filesystem transaction,
another process writing in the tiny interval after the final recheck and
before `os.replace` is outside the process's locking authority.  Run an actual
adoption only while owners have quiesced these four destinations; do not treat
this review as authorization to perform that adoption.
