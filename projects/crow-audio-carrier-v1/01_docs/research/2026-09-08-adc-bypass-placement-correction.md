# ADC bypass placement correction

Status: **SOURCE TESTED / SCHEMATIC REGENERATED / VISUAL REVIEW OWED / DO-NOT-ORDER**.

The generated placement failure at `003a8bff` is retained in
[the preceding adoption record](2026-09-08-generated-placement-adoption.md).
This correction changes only C_LDO_A's authored pose, from
`[89.8, 70, 180]` to `[89.93, 70.05, 180]`. All other floorplan fields,
301 other fitted poses, connector datums, parts, electrical limits, route
seeds and routing rules are unchanged. No generated PCB was hand-edited.

## Source evidence

MEASURED with isolated native footprints, not a constructed or saved BOARD:
the corrected ADC pin7/bypass copper-box gap is 1.495 mm, below the unchanged
1.5 mm engineering ceiling. The earlier candidate probe measured the nearest
foreign via gap as 0.259098 mm against 0.25 mm. These are nominal source
geometry screens, not manufacturing-tolerance or physical qualification.

The new `test_adc_bypass_placement.py` checks both constraints together,
all 877 source pads, 218 seed segments, 20 source vias, foreign drill clearance,
body/courtyard separation, and the existing two-pin filter contact graph.
It also compares the entire floorplan against the committed failed subject,
allowing exactly one pose delta. Historical preservation tests admit only
this explicitly asserted new pose before comparing every unaffected field.

MEASURED regression sequence, all bounded with 10-second heartbeats:

- Before the source fix, five tests ran: three hostile tests passed and two
  positive tests failed, including the actual 1.625 mm adjacency defect.
  The old pose still passes the broad 5 mm centre-distance test. Red log SHA:
  `b0b102a24b51d89c7638f194495cca1832d3f4162cbda494192ecb4c5b79f02b`.
- After the fix, all five tests passed. Three blind east shifts still fail
  ground-via clearance; a missing filter seed still fails native contact.
  Green log SHA:
  `208109e511ab39fa90e6d28dff617f63d56f25fc5711b0f66f13c096baea2ecb`.
- First complete suite: 201/202 passed; the sole failure was an additional
  historical regulator-placement equality still expecting the old pose.
  That test now admits only the same asserted capacitor delta, retaining
  all its regulator and other-placement comparisons. Failed log SHA:
  `0bcefbeb9fbe73d4e2b7436c081e63c873d3801e9d310bda28508de07951662c`.
- Final complete suite: **202/202 PASS**, actual 16:58:00–16:59:13 UTC,
  73.240 seconds, exit0, no timeout/cancellation. Log SHA:
  `ebd163613e01d09fd80e24ac9c8c2c05f7c2f0a5b05a6f0d3266e670ebdddc77`.

Captures are under `/tmp/carrier-fresh-build-20260908.4RBsSy/`, with copies
retained in `06_build/verification/bypass-correction-20260908-003a8bff/captures/`.

## Exact regeneration boundary

MEASURED `prelayout_input_checkpoint.py verify`: exactly one changed input
among 421, `03_src/floorplan.yaml`; exit1 at 16:56:52 UTC, log SHA
`3e9cd056c4b542901740e99e98c6e3afd19076b7165235fdb52f0f7802cbd719`.
The reuse conductor requires this complete census before generated writes.
It has no layout-only refresh arm. Both the full conductor and 06_build
contract require deliberate archive-and-restart after this drift. Do not
re-stamp the old census, rewrite review hashes, or invoke the board generator
directly to bypass that boundary. Preserve the old cohort together, then run
the full conductor and grade the bytes actually produced.

The old PCB remains unaccepted and unrouted. Current-board DRC, placement
reviews, routing, silk cleanup and carrier release are still owed. The pod
seal is unchanged. Public catalog evidence is not PCBA allocation or order
authority; all physical, TOP77 and 0.20 A first-power holds remain.

## Regeneration and actual review boundary

Source correction commit: `aaef8512f572a354196882b4fb17235167009bd5`.

MEASURED archive at 17:03:13 UTC: 516 files / 89,419,015 bytes copied and
rehashed, including all 421 original checkpoint inputs. The old floorplan
was recovered from committed `003a8bff` and matched its frozen digest.
Eight checkpoint/catalog files were moved recoverably into `prior/`; no
operator fields were populated and no authenticated receipt existed.
Archive manifest SHA:
`8efdf54672b995cc883863bee03318013fdf75b984827015b842950e09033064`.

MEASURED full conductor, 17:05:23–17:06:34 UTC, 71.288 seconds, exit2 at
the deliberate pre-layout pause. Electrical closure9/9, request52/52,
new input census421/421 and pre-layout checkpoint11/11 passed. Log SHA:
`3788c846ae96fc271a5424a2ab4d7bfa5b6bc1318f4004e4fb4398f0168ed50f`.

MEASURED independent archived/current comparison: all302 component identities,
values and footprints, all877 pin-net entries and207 native nets unchanged;
normalized electrical review hash remains
`83b1c3510e0b08d9d4f390fac59403374073615f7bfcc8f6361308b51ce84c73`.
Rules hash remains
`e33aea9d2b4136aee98781dc592ba4df6c7f7fec99353af5f3703cc4d1c72036`.
All516 archived files were independently rehashed again. Only the one
authored floorplan and six regenerated checkpoint inputs differ. Old review
files, old PCB and pinned schematic are byte-unchanged. Census log SHA:
`8329ad03e038669aef6aa9a14f19a0494bdb44a3adbd47e564f1951e77b964f9`.

MEASURED public catalog, 17:07:52–17:09:22 UTC, 89.854 seconds:52/52 exact
codes pass the unchanged five-board quantity screen, zero uncoded rows.
Log SHA `1c64bcf5ad5f2216f71162bb06ef877efa0271440d27071765d4f6ae07402732`.
This is public stock only, not assembly allocation, price or order authority.

MEASURED explicit public-prelayout continuation, 17:10:01–17:10:05 UTC,
3.070 seconds: checkpoints reverified, manufacturing prelayout4/4, ERC0errors
with2100 warnings baselined, new schematic checkpoint7/7. PR-REVIEW grades2/2
and fails exactly the changed PDF hash; the existing topology witness passes
its unchanged electrical/parts/rules subject. Resume log SHA:
`9bcc0d58235bb4e4a24cfdff8ddc08a92444b14b16b3e5cb66e968a6b12fa951`.

The new19-page PDF SHA is
`6191dc89803e2b2c2f16f104252fda01226fad86da649907c80c52592e5f87cf`;
Circuit JSON `1d5379e263fbc7582190d118656bc782dd685c65f4057db2108a050aa033b969`;
native schematic `424732575f968e17f740200fc2db93c7034624c595b88dc3affef060b5078e5f`.
All202 source tests passed again against these regenerated bytes at17:10:48UTC,
72.422seconds, log SHA
`25d7d7789ab40e12288ae4bc55f8e25c42a6c7f71df593db28673d31b1ec8631`.

Next: commit the new frozen subject and commission a fresh bounded visual
review of all19 pages. Do not repeat the unchanged topology lens or re-stamp
the prior visual witness. Accepted schematic review then requires the fresh
placement handoff before regenerated PCB work. No carrier release yet.
