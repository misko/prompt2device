# Regulator source correction — 2026-09-08

Proposed source-only H3 handback under the exclusive regulator writer lease.
NOT ROUTE-READY; DO-NOT-ORDER. No native PCB, conductor, generation, prep,
router, import, checkpoint/review write, shared-tool change, commit or release
was performed. Root independently adopts after explicit writer handback.

## Authority and preserved subjects

Worktree: /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901.
Source adoption a8e8ac31d591ae1bf8aa985f7d272ccff597ca7f; administrative
HEAD1602a507cc20f63a1980b6605784c918b5ece10c. Strict envelope SHA256
b2863f4796fa56e83577a6d1266d51a445b1fc0770cba781e05b5861ecf64716;
canonical 22-member packet SHA256
afc4c481961849051b5749db5271b91f872aa3bd051e9910ce9442d4489c161c.
All packet members and all 410 census rows were individually verified before
editing. At 08:12:03Z, 1,412 actual subjects/131,740,120 bytes were copied
and independently rehashed, including existing generated/checkpoint/review
subjects. The new evidence directory is regulator-source-20260908 only.

PCB-design/KiCad lifecycle, native geometry, layout-precedent and source
authority instructions required this bounded source continuation, explicit
quiet-pour handling, archive-first discipline and no generated acceptance.

Preserved by executable terminal comparisons: all electrical identities,
299 refs, 868 pin memberships, 205 nets, 40 NCs, 150x100 mm outline/mounting,
four layers/stackup, 11 external connector datums, all but one pose, all
original keepouts/GND zones, all classes/scoped clearances, 17 seed banks and
three previous ADC capacitor poses. Dossier fields other than layout_refs and
gotchas are exact. The 1.20 mm/2.5 A bulk bound and old ADC 5.05 mm/eight-item
subtotal are unchanged; the combined guard adds only real regulator items.

## Actual source delta and rationale

See ADR0012 for manufacturer URLs, hypotheses, exact resistance model and
limitations. Move only C_LDO_OUT from [62,74.15,270] to [61,66.5,180]; do not
move R_LDO_TOP or alter its load-sense topology. Add 15 banks/37 F.Cu straight
primitives, six 0.50/0.20 mm off-pad GND vias, five width-only rule areas and
five top pour/via exclusions. No new clearance exception or power pour.

Five off-centre starts are inside actual native pad polygons. Independently
measured fixed-centreline width ceilings against native foreign pads/holes
and all simultaneous foreign seed segments are OUT1 1.109506, IN10 1.112455,
OUT2/IN9 0.450004 and SW5 0.800004 mm; selected widths are 1.10/0.40/0.75 mm.
These are diagnostics of these specific paths, not a global escape optimum;
normal full-screen and exact-area admission remain separate. The original
centre/bulk collisions are durable hostile tests. New source main paths
include real 1.20 mm entries; the broad input-cap landing is independently
screened at 1.20 mm. No “only centre launches are possible” assumption remains.

NR1–5/lower feedback/GND4 return to EP is explicitly protected from top
pour/via bypass, while common inner GND stays unsplit. SS6 connects to EP;
two EP drops are separate from the four power-cap return drops. All intended
destinations are reached through actual F.Cu contact without invented plane
edges. SW reaches the inductor but not bootstrap, preserving generic ownership
of the remaining real branch. Partition stays 162 generic + two complete
deterministic nets + GND + 40 NCs. Nothing is removed from an owner by hope.

New subnominal 3V3 copper is 2.7200609733428465 mm/five items; adding the
original 5.05/eight yields 7.7700609733428465/13. The guard rounds upward to
7.770061 mm. New input subtotal is 3.075 mm/four, SW 0.90 mm/one. Each net's
exact subtotal is separately tested, beyond the uniform wave allowance.

## Measured evidence and rejected attempts

Evidence root: 06_build/tmp/regulator-source-20260908/.

| Run | Actual result |
|---|---|
| archive-before | 22 packet members, all 410 census rows, 1,412 archived subjects verified |
| hypothesis-1 | Native-circle SWIG overload error; raw output retained, no source accepted |
| hypothesis-1-native-overload | 44,008 comparisons, one real west EP/PG collision; rejected |
| hypothesis-2 | 44,839 comparisons, clear after vertical-first EP escape |
| hypothesis-3-wide | 44,839 comparisons, clear after widening main IN/OUT to 1.10 mm |
| regression-native-before-source | New engineering tests fail original source, retained |
| full-project-post-source | 132/133 pass; sole hostile used tangency rather than overlap |
| full-project-terminal | 134/134 pass after definite hostile overlap and added entry/edge tests |
| full-project-terminal-freeze | 134/134 pass, 08:44:44–08:44:58Z, final engineering source |
| rules-source | 8/8 classes, zero failures; no board opened |
| net-references | 339/339 resolved, zero ghost/unreached |
| final-source-terminal | 44,882 regulator + 19,239 digital comparisons, zero failures; shadow authority verifies |

The moved capacitor passes 298 courtyard comparisons, 866 moved-body/foreign
pad checks, 596 reverse checks and 1,732 distinct-footprint pad pairs, including
same-net copper. Physical OUT1/2-to-cap pin spans are 2.648703/3.125000 mm;
the original exact-owner placement ceilings remain unchanged. All 19 other
digital full-width witnesses still pass in the complete project suite.

The failed tangency expectation was a test defect, not a source geometric
failure: the revised hostile deliberately overlaps the quiet stem and is
rejected. All candidate source snapshots and full bounded stdout/stderr,
timestamps, return codes and log digests remain. No nonimproving source loop,
replacement, delegation or unauthorized producer was used. Benign installed
KiCad enum warnings and inherited ResourceWarnings remain visible in logs.

Terminal integrity records both 410-row before/after censuses, every changed
existing subject and every new durable source file; all archived subjects
are independently rehashed again. evidence-inventory.json additionally binds
new evidence bytes and explicitly names its own recursive-log exclusions.
Do not substitute this evidence for a checkpoint or independent review.

At 08:47:52Z the terminal preflight rehashed all 1,412 original archive copies
and current subjects: 1,404 existing subjects unchanged, eight permitted
existing changes, three new durable files. Exactly five of 410 census rows
change: route/floorplan/nets and the two permitted dossier metadata records.
All other census rows and all original generated/checkpoint/review evidence
remain byte-exact. Final metadata is rehashed again after this report freezes.

## Remaining gate and handback

Nominal 35 um copper/rho85 DC losses are explicitly evaluated at the full
2.5 A for every new narrowed power branch, without assumed parallel sharing.
No finished-copper/plating allocation, allowable fault duration, temperature
rise, barrel ampacity or achieved thetaJA is claimed. AP's 2 oz EVM thermal
precedent and TI's 1 A family EVM do not qualify this carrier. Two thermal and
four power-ground vias are geometric proposals, not proven series banks.

Fresh filled-board quiet-return topology, no generic/stitch pre-EP shortcuts,
post-import exact widths/extent, current-transfer, loop impedance, thermal,
startup/stability, native DRC and digital SI are mandatory later evidence.
This source batch does not close other ADC supply/ground or low-current IC
egress. All TOP77, ADR0007/0009 prototype limits, first-power 0.20 A HOLD,
mechanical/service/sourcing/publication and physical qualification obligations
remain. The writer relinquishes its exclusive lease only with explicit terminal
delivery; root then owns independent adoption. Absolute deadline 08:55Z.
