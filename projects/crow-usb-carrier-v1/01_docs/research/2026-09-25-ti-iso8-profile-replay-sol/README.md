# Exact TI U_ISO8 via profile replay

The integrated placement did **not** create or retain an ISO8 clearance error
under its governed native rules. The earlier 699-issue bare-board DRC omitted
the TI project `.kicad_pro`, `.kicad_dru`, and the post-generator
`TMUX4827_YBH_B2_POFV` rule-area producer. That incomplete harness evaluated
the intentional 0.100-mm B2 via-to-adjacent-pad gap against a generic
0.200-mm rule. Its shifted `U_ISO8.2`→`U_ISO8.4` issue identity is a harness
artifact, not a new production-rule clearance fault.

`replay.py` pins the frozen TI source and project-rule hashes and both
source-generated placement boards. In isolated temporary projects, it runs
the exact `generate_tmux4827_pofv.py` producer, which creates the eight
pad-bound native rule areas and re-emits the exact 0.100-mm conditional rules.
The independent `via_process_check.py` then passes all **14 protected vias**:
eight `U_ISO*.5` B2 sites at 0.35-mm copper/0.20-mm drill and six `U_LDO`
sites at 0.50/0.20 mm. The candidate's `U_ISO8.5` GND via is centred at
`(199.0,53.0)` mm. The baseline and union each have **213 DRC issues and 499
unconnected items**, no ISO8 clearance item, and *identical* issue identities
(+0/−0). The [receipt](receipt.json) binds the input and project-rule hashes,
native rule-area names and bounds, via process census, and exact delta.

No via relocation is justified. The exact source profile requires one
0.35/0.20-mm GND via centred on each `U_ISO*.5` pad within 0.0015 mm; an
off-pad via with a short GND neck would fail its independent authority check
and add unproved return geometry. A smaller via would violate the exact
qualified geometry and require a new process/footprint review. The valid
0.100-mm conditional clearance applies only to the named B2 via and four
adjacent signal pads; ordinary board clearances remain governed separately.

This removes only the *claimed ISO8 DRC blocker* from the integrated placement
assessment. The 0.005-mm ADC8 cap owner margin, 28 source-unencoded F.Fab
reference-field moves, unfilled In1.Cu return, 499 opens, and vendor/CAM/PCBA
acceptance remain. There is no route, return, P1, or P2 acceptance here.

The producer creates fresh KiCad UUIDs for the eight rule-area objects on
each run, so byte hashes of the augmented temporary boards are not stable.
The replay pins the input board/project/source hashes and checks the emitted
area names and native bounds, centred via geometry, exact generated `.dru`,
process census, and DRC issue identities. Two consecutive replays produced
the same receipt SHA-256 `9417ca44def604e5142988c1efb5b27e561c0fa027b6a082f291e12410e35484`.

Reproduce from this directory with `python3 replay.py`.
