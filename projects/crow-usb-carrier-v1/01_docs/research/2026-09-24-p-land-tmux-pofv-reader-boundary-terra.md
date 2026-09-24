# P-LAND and TMUX POFV: reader-boundary audit (Terra)

**Observed blocker.** On the isolated Crow board, exact `escape_check.py --board` stops before pad search with `rule tmux_ordinary_annular_floor: unsupported physical constraint annular_width`. This is a `land_witness.read_rules()` language boundary, not a native DRC, pad-launch, annulus, or fabrication verdict.

## What P-LAND actually needs

P-LAND constructs hypothetical **tracks** from a copper pad and evaluates:

- declared `track_width` minima, including their applicable layer/area conditions;
- `clearance` between that hypothetical Track and foreign pads, plus native netclass/board clearance when no custom rule applies;
- board netclass assignments, board minimum track width/clearance, copper shapes/layers and KiCad DRC epsilon.

It inventories existing incident tracks but does not use their width as a witness. It has no hypothetical vias or holes. `hole_clearance` is already parsed only as a validated downstream-native-DRC obligation. `annular_width`, `via_diameter`, and `hole_size` cannot affect a Track–Pad launch witness. The TMUX POFV clearance rules are Pad–Pad or Via–Pad predicates, so they cannot match P-LAND's synthetic Track–Pad pair. Conversely, an arbitrary clearance or track-width rule still can affect its result and must remain fully parsed and enforced.

## Existing annulus/process boundary

The generated TMUX block deliberately applies a 0.13-mm ordinary annulus floor and permits 0.075 mm only for exact GND vias in the eight pad-derived `tmux4827_b2_pofv_U_ISO*` areas. `tmux4827_pofv.audit()` checks the eight exact area geometries and rejects a foreign via overlapping one. `via_process_check.py` independently requires exact expected POFV rule text, rejects residual foreign clearance/via/hole constraints, binds each B2/5 pad to its realized via/geometry, checks native fill/cap flags and drill-family selection, and retains the fabricator order selector. Native KiCad DRC then enforces the emitted annulus/via/hole constraints on the board. These are the annulus authorities; P-LAND must not replace them.

The public process boundary is also distinct: JLCPCB describes via covering/filled-capped options and ordering as a manufacturing choice, while the project assembly record requires the complete 0.20-mm drill family to be selectively filled/capped with uploader confirmation. Neither public record changes the limited meaning of a P-LAND launch witness.

## Narrow handling recommendation

Do **not** make `annular_width` generally meaningful to P-LAND and do not drop the entire DRU. Admit only a structurally verified generated TMUX POFV block as an *excluded physical-via namespace* after all of these conditions hold for the same board/DRU bytes:

1. `tmux4827_pofv.audit()` verifies the exact eight pad-derived areas and no foreign via overlap;
2. `via_process_check.py` passes the exact expected block, residual-rule, B2 identity, geometry, flag, selector and order-remark checks;
3. P-LAND reads all non-POFV rules normally and retains any Track–Pad `track_width`/`clearance` rule. Within the verified block it may record `annular_width`, `via_diameter`, `hole_size`, `hole_clearance`, and provably Pad–Pad/Via–Pad clearances as downstream scope, never as a launch relaxation;
4. an altered/missing/duplicated marker or generated rule is a hard failure, never a silent exclusion.

This implies the TMUX producer/process verification must run before P-LAND or be invoked as a same-byte prerequisite; current generic flow lists P-LAND before its post-board via-process stage, so merely relying on a later gate is not sufficient for a P-LAND exclusion.

## Required negative tests

- Exact board: P-LAND proceeds to a normal finite-witness verdict rather than `UNSUPPORTED`; native POFV/process checks still pass.
- Change either B2 annular value, via diameter/drill, GND condition, area name/bounds, block marker, or duplicate a rule: POFV/process prerequisite fails and P-LAND refuses the excluded block.
- Add any foreign via whose disc intersects a B2 area: prerequisite fails.
- Add `annular_width`, `via_diameter`, `hole_size`, or an unparseable condition outside the verified POFV block: P-LAND remains fail-closed.
- Add a Track–Pad `clearance` or `track_width` rule, including inside a forged POFV block: it must be parsed/applied or cause verification failure; it may never be silently omitted.
- Remove the POFV block: native DRC/via-process fails the advanced B2 geometry even if a P-LAND launch search runs, proving P-LAND cannot clear annulus/process obligations.

This is a reader compatibility change only. It cannot clear P-LAND, DRC, POFV manufacturing acceptance, or any XU placement/return condition.
