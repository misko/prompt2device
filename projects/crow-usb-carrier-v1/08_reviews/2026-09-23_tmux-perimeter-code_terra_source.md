# TMUX4827 perimeter clearance code review — PASS

**Reviewed working diff:** `/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922`,
against `1f96485ab1f1fc60db68d6efd30fe67dda9d82d8` (uncommitted at review time).
Read-only review; no Crow PCB was generated or changed.

## Verdict

PASS.  The implementation is bounded to the two defensible intrinsic package
pad pairs and preserves the ordinary `QUIET_POWER` clearance everywhere else.

* Profile geometry adds the exact `perimeter_pad_gap_mm: 0.15` value.  The
  strict schema rejects any changed value.
* The contract binds the retained dossier functions `7=S1B`, `8=VDD`, and
  `9=S2B`.  The live-board checker then requires `U_ISOn.7=FILTERnP`,
  `.8=N5V_LDO_HOLD`, `.9=FILTERnN`; changed identities fail closed.
* Native DRC rules require both items to be pads on the same exact `U_ISOn`,
  with only `7/8` and `9/8` pad numbers and their exact signal/supply net
  identities, in both operand orders.  They cannot match a track, via, zone,
  other footprint, other pad pair, or general power/GND relation.
* The focused native fixture uses a `.20` `QUIET_POWER` class on
  `N5V_LDO_HOLD`: all 16 intended package pad pairs pass with the local rules;
  deleting the 16 local rules produces 16 `.2000 mm` clearance violations;
  a foreign track and foreign-footprint pad remain `.2000 mm` violations.

## Independent verification

`/usr/bin/python3 -m unittest tests.t1_tmux4827_pofv -v` passed **8/8**,
including the new native DRC scope test. `git diff --check` reported no
whitespace defects.

This is a source/native-fixture verdict only.  It does not constitute actual
Crow-board DRC acceptance, CAM/PCBA acceptance, a routing-width waiver, or a
general low-voltage/power-isolation relaxation.
