# P1/P2 admission audit: XU launches and connector FULL (Terra, 2026-09-24)

**Scope:** read-only review of the current `03_src/modular_plan.json`, ADR
0011, P1 source contract, and terminal P1 receipts.  No P1 was dispatched.

## Finding

The active graph has exactly one P1 root,
`p1_floorplan_569_after_native_evidence_abort`, with `max_attempts: 1`, zero
recorded attempts, and all seven P2 work items depending on it.  The modular
checker passes ownership (569/569 components and 59/59 crossings) and reports
the root as graph-`READY`; this is explicitly diagnostic, not geometry or
acceptance evidence.

**The 22 unresolved XU power-pad P-LAND witnesses are not an explicit P1
acceptance gate.** ADR 0011 assigns local decoupler placement and measured
local distances to `p2_digital_power_core` / `xmos_core`; P1 must record that
P2 debt rather than call it passed.  P1 must not enable a broad power rule or
claim any of the 22 launches, their capacitor returns, or PLL topology.

**Connector FULL is also deliberately not a P1 gate.** ADR 0011 permits an
accepted P1 floorplan and bounded, isolated P2 placement while the 19 physical
FULL targets remain incomplete.  FULL stays base `PASS`, zero unknowns, before
P3 critical-local routes, route preparation/import/other routing, P5
promotion, release, and order.  `rebuild_all.sh` still stops at step 3c on
FULL, so it cannot be used to imply a canonical P1/P2 continuation.

However, **the active P1 is not safely dispatchable or acceptable yet.**
`03_src/rules/p1_corridor_requirements.yaml` is `INCOMPLETE`, has null
geometry for every declared allocation and for `power_boundary_windows`, and
sets `p1_accepted_must_remain_false: true`.  The current P1 owner reassessment
also requires nonzero explicit corridor/ownership denominators.  The research
corridor diagnostic confirms that a fresh native candidate needs connected
reservation geometry, per-lane capacity/pocket/reference evidence, and
independent review before P1 can pass.  This is a P1 predicate defect separate
from the XU 22-pad local-launch debt.

## Prior-attempt boundary

The two immediately prior one-attempt roots are terminal, consumed history:
`p1_floorplan_569_after_launch_abort` failed before handback because of the
relative project path, and `p1_floorplan_569_after_relative_path_abort`
delivered a mixed-hash routability receipt.  Neither identifies a board result
for the active root nor replenishes its single attempt.  The latter is why the
new P1 packet must require candidate-board SHA equality in every receipt.

## Safe preflight before spending the active attempt

1. Freeze a clean source packet and use absolute resolved project/work paths;
   run a no-spend worker fixture that verifies every copied source directory,
   output directory, and required handback member before board generation.
2. Preserve and bind the two terminal archives; verify graph singularity,
   current root ID, `max_attempts: 1`, its seven P2 dependency/backtrack edges,
   and the accepted schematic/source receipts.  Re-run the modular ownership
   check against the frozen circuit JSON.
3. Replace the null P1 reservation facts with source-owned connected geometry
   for every allocation, including power boundaries; bind exact endpoint
   pads/nets, nonzero demands/capacity, outline/rule-area/pour and continuous
   reference evidence.  Run the hash-bound `p1_corridor_capacity.py` on the
   newly saved board.  A raw slot screen remains incomplete unless its required
   rule-area/pour/pocket evidence is present.
4. Require a single candidate-board SHA in every native DRC, parity,
   corridor, model/courtyard, and capacity receipt.  Missing or unequal hashes
   fail the packet.  Classify `P-ADJ`/`P-ADJ-PAIR` and the 22 XU pad launches
   as explicit P2 debt, never as P1 pass, waiver, or route credit.
5. Record the connector base's 19 unknown physical targets as the later FULL
   blocker.  Do not require them for P1, but do not run the normal canonical
   driver past its intentional step-3c stop or allow any P3/routing result.

## What may proceed

Before P1 acceptance, the graph blocks every active P2 item; only read-only or
isolated research may continue.  After a genuine P1 pass, ADR 0011 allows the
non-promoted `p2_digital_power_core` scope to place/review the XU decouplers,
PLL and exact 22-pad dispositions while FULL remains incomplete.  The other
six P2 scopes may likewise perform their defined placement work.  That does
not admit `p3_power_loops`, `p3_timing_boot`, `p3_usb_pair`, any route import,
or P5; each remains behind unchanged connector FULL.
