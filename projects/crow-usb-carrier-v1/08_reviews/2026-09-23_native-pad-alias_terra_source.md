# Terra review — native Crow pad aliases

**Input reviewed:** `f1d4524ab51e40dd961e19d1f340b605b5029b22` only, against parent `72cedc9cace3fa07ed142ae4ca1e04bdcdaa38ed`.

**Verdict: PASS.** I found no correctness defect in the alias-resolution change.

## What was checked

* `resolve_pad_aliases()` resolves only through the netlist component value using `load_parts()` identities, and rejects an unrecognised value when its FPID is one belonging to an alias dossier.  A recognised alias dossier must also name the exact non-empty netlist FPID.  Thus it does not borrow a mapping merely because some other part shares a footprint.
* Alias-map validation is reused from the pin-map gate.  Empty aliases, undocumented non-identity aliases, aliases for undeclared pins, and an unknown netlist schematic pin fail before placement.
* Several logical pins may collapse only when their declared functions agree and every non-identity member is explicitly `fused: true`; separately, two logical pins sharing one schematic number must resolve to one physical pad.  A second distinct net reaching a collapsed physical pad is rejected.
* `expected_alias_pads` holds all declared physical pads, including pins absent from `pad_net`; `place_parts()` compares that set to the loaded native footprint before assigning any nets.  This preserves and checks the two USB SBU/NC lands.  The normal `check_pads_present()` remains active for every connected resolved pad, and all observed consumers iterate the physical `pad.GetNumber()` after the translation.
* The Q_IN DMP6023 mapping is compatible with the fused drain footprint: logical 6/7/8 map via schematic 5 to physical 5 and therefore require one same-net result.  On the actual Crow netlist it resolves to pads 1–5, with physical 5 on `N12V_FUSED`.

## Executed evidence

Targeted test selection (four new cases):

```
/usr/bin/python3 tests/t1_generate_board.py --only='native USB4105 aliases preserve every logical contact and NC land|board alias resolver rejects unevidenced, missing and conflicting maps|board aliases leave identity parts unchanged|board generator refuses a missing unconnected alias pad'
```

Result: **4 passed, 0 failed**; both known-bad cases rejected their fixtures.

I also ran the committed resolver against the real Crow netlist (568 components, 1779 netlist nodes).  It returned 1779 physical assignments and two alias-constrained refs.  `J_USB` translated all logical 1–17 to exactly `{A1,A4,A5,A6,A7,A8,A9,A12,B1,B4,B5,B6,B7,B8,B9,B12,SH}`; A8 and B8 retained their source unconnected nets.  `Q_IN` translated to exactly physical pads 1–5.

Finally I invoked the committed generator with the actual Crow floorplan/netlist and an isolated temporary output directory.  It placed all **568** footprints and progressed past alias/footprint/net assignment; the first failure was the already reported unrelated baseline `thermal_vias.fields[0]` collision: emitted `U_LDO.11` via intersects different-net `U_LDO_EN.1`.

No review-packet source files or root worktree files were modified.
