# Independent review — strict TMUX P-LAND reader admission (Terra, 2026-09-24)

**Reviewed change:** `2f7280a1` (`land_witness.py`, `t1_tmux4827_pofv.py`,
`t1_escape_tier.py`).  This is a reader-only review; it makes no Crow board,
route, or P1 claim.

## Verdict

**No material implementation issue found.**  The former reader blocker is
cleared narrowly for a board that has the verified TMUX POFV contract.  This is
not evidence of full Crow P-LAND closure.

## Boundaries verified

`BoardContext` now supplies the actual board path to the reader.  The exception
is available only when all of these are true:

- the DRU is that board's companion `.kicad_dru` file;
- the active assembly is discovered for that same board and carries the active
  TMUX contract;
- one, ordered marker pair contains byte-exact output of
  `tmux4827_pofv.dru_rules()`; and
- `via_process_check` passes on that board and assembly, then the raw board and
  DRU bytes still equal their pre-check values.

Only that generated POFV block is removed before P-LAND parses the remaining
rules.  Its contents concern the selected TMUX vias/holes and Pad--Pad or
Via--Pad relations; P-LAND's hypothetical object is a Track--Pad launch.
The shared via-process gate remains the authority for the excluded annular,
drill, hole-clearance, area, pad/via identity, and process-selector facts, and
native DRC remains the physical enforcement.  A raw DRU reader still rejects
these constraints, and an external or altered annular rule remains unsupported.
No generic annular-width interpretation or global relaxation was added.

## Reproduced tests

- `python3 tests/t1_tmux4827_pofv.py`: **12 passed**.  It rejects altered
  annulus/diameter/drill/net/area/markers, duplicate or absent blocks, forged
  track rules inside the block, an external annular rule, and a foreign via in
  the protected area.
- `python3 tests/t1_escape_tier.py`: **51 passed, 0 failed**.  The new fixture
  confirms that a foreign annular rule outside a verified TMUX block still
  produces `unsupported physical constraint annular_width`.

The focused tests substantiate the same-board prerequisite, exact generated
text, exclusion boundary, and strict negative path.  They do not themselves
exercise a hostile concurrent writer; the production reader's before/after raw
byte comparison is the implemented guard for that condition.

## Release interpretation

The recorded post-fix isolated run in
`2026-09-24-p-land-tmux-verified-reader-sol.md` admits the ordinary rules after
via-process verification, but its all-pad Crow P-LAND run hit the 240-second
bound.  It is therefore neither a full pass nor a full failure.  Its focused
`U_XU.14`, `U_XU.17`, and `C14.1` searches are limited positive witnesses;
`U_XU.18` still reports `NO_VALIDATED_WITNESS` under ordinary rules.  Those
coverage and finite-witness results remain release work after the parser
blocker has been cleared.
