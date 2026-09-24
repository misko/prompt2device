# Independent review — conditional TMUX4827 B2 POFV scope (2026-09-24)

**Verdict: PASS for source-bound native-DRC scoping; not a fabrication or P1
acceptance.**  This review covers the uncommitted conditional-profile changes
in the shared Crow worktree.  It does not make a JLC order, uploader, CAM, or
PCBA acceptance claim.

## What is bounded

The conditional declaration in `03_src/floorplan.yaml` is a closed mapping:
`TMUX4827_YBH_B2_POFV`, `CONDITIONAL`, and exactly `U_ISO1..U_ISO8`.
`tmux4827_pofv.activated()` requires that declaration and the one exact
assembly profile.  The profile binds all of the following before any local
rule is emitted:

* exact `TMUX4827YBHR`, Texas Instruments, and
  `crow_usb_analog:TI_YBH0009_C02_TMUX4827` identity;
* the native-footprint and coupon SHA-256 values;
* B2-to-pad-5 GND mapping, 3×3 pad map, 0.25-mm perimeter lands, and the
  0.35/0.20-mm B2 geometry;
* one centred, through F.Cu-to-B.Cu, filled-and-capped GND via at each of the
  eight sites; and
* eight tiny, placed-pad-derived rule areas.  A second 0.35/0.20 via, an
  offset/missing via, a changed pad/net/footprint, or an overlapping foreign
  via is rejected by the independent audit.

The generator lowers only KiCad's absolute floors to `.09` clearance,
`.25` via diameter, `.075` annulus, and `.10` hole clearance.  It then emits
the later `tmux_ordinary_via_floor` (`.45/.13`) and
`tmux_ordinary_hole_clearance` (`.25`) rules plus exact B2 pair rules.  The
producer and `via_process_check.py` require those advanced absolute floors,
the complete generated-rule block, and every ordinary netclass clearance to
remain at least `.15` mm.  Thus an offsite `.35/.20` via is still subject to
the strict `.45/.13` rule and the relaxed hole/clearance rules are limited to
the named B2 relationships.

## Native adversarial evidence

Ran, read-only against source plus temporary native boards created by the test:

```text
python3 -m unittest -v tests/t1_tmux4827_pofv.py
Ran 8 tests in 15.555s
OK
```

This uses KiCad native DRC and exercises:

* clean eight-site positive generation;
* wrong net, offset, missing fill/cap, missing via, wrong OD/drill;
* an extra filled/capped `.35/.20` via away from B2;
* changed reference, pad, neighbour position, area, footprint, and coupon
  hash;
* injected global/indented foreign relaxed DRU rules;
* an ordinary offsite `.35/.20` via, which native DRC reports against the
  restored ordinary via/annulus floor; and
* foreign track/pad and altered supply-net cases, which retain a stricter
  `.20` netclass clearance outside the exact same-footprint exceptions.

`git diff --check` was clean at review time.

## Public-process boundary

The source says `CONDITIONAL` and continues to require uploader confirmation.
That matches the public-only assessment in
[2026-09-24-jlc-public-pofv-tmux4827-assessment-terra.md](2026-09-24-jlc-public-pofv-tmux4827-assessment-terra.md):
JLC publicly describes filled/capped BGA via-in-pad and a compatible nominal
diameter range, but does not qualify this exact 0.4-mm-pitch,
0.35/0.20-mm, 0.075-mm-annulus site.  Exact vendor CAM/uploader and PCBA
approval remain an external hold.

No final Crow board generation or release/P1 acceptance was performed by this
review.
