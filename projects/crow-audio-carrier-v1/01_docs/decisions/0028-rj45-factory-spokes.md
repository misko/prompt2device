# ADR-0028 — Factory RJ45 analog and power spokes

Status: proposed implementation; user direction and source architecture selected.
Date: 2026-09-12. Authority: carrier D8, pod D6 and parent D3.

Use Würth 615008160221 nonmagnetic, shielded 8P8C jacks and Weidmuller
8909650150 factory 15 m Cat6A PUR patch cords. Contacts 1/3/7 carry
+12 V, 2/6/8 carry return, 5 carries AUDIO+ and 4 carries AUDIO−. Shield
pads 9/10 connect to CHASSIS on the carrier and isolated POD_SHIELD on the
pod. Label the ports “POD AUDIO +12V / NOT ETHERNET OR POE”. Mate with power off.

The compact jack requires the entry clamps on the bottom, between its
4 mm contact rows. Independent source architecture review supports this
arrangement. Native footprint measurement gives 1.935073 mm pad-centre
spans for the pod candidate. The review's earlier 1.514 mm estimate is not
a native measurement. Full carrier transforms, copper, bottom assembly,
THT tails, paste, service access and protection order require fresh checks.

At 15 m, the published 290 Ω/km pair-loop DCR, three parallel power pairs,
1.25 hot multiplier and an unmeasured 0.300 Ω contact allocation give
2.1125 Ω and 10.58875 V at the pod for 0.10 A from 10.8 V. The finished
cord's resistance and current capability still require qualification.

Exact-product manufacturer STEP establishes the nominal complete-end geometry:57.98mm axial, including rear sleeve and raised latch. Independent native BREP containment supports a22.986mm nominal grip diameter about the documented cable axis. Keep manufactured radial/axial tolerance, installed exposure, full latch motion and populated service unknown in the existing phase contract. Primary cable OD is6.1..6.5mm; retain67mm bend planning floor, exceeding10D at maximumOD. The former HARTING approximate-dimension SOURCE hold is superseded by this evidence, not by an invented manufacturing maximum.

UV is unestablished and remains an explicit environmental qualification hold before outdoor deployment. PUR is not a UV rating. Exact power-off1:1 T568B, shield continuity, contact resistance/current and2.2ohm finished hot-loop tests remain owed in FIRST_ARTICLE_TEST_PLAN. Source and physical admission remain separate; no release or order authority follows from nominal geometry alone.

Retire the spoke's Micro-Fit crimps, joins and pigtails from the new assembly.
J9 power and J10/J11 module interfaces retain their separate contracts.
Prior sealed releases and every failed review remain historical evidence.
LAYOUT-001 remains closed with three spent attempts; this change grants no
additional diagnostic allowance. The generated carrier remains the old,
unrouted Micro-Fit subject until a normally admitted regeneration succeeds.

The source owns sixteen 0.20 mm B.Cu jack-to-clamp prefix seeds. Shared
`critical_path_check.py` reopens saved copper and enforces 4.0 mm pad span,
4.2 mm path length, no vias, B.Cu only, and complete-prefix dominance before
any AC-coupling branch. Both conductors invoke this through the existing
analog path gate. Failure is a route/placement finding, not a waived branch.
CHASSIS has an explicit 0.60 mm outer-layer routing owner, joining all sixteen
shell lands while each connector's EMI fingers bond locally to the panel.
There is no CHASSIS-to-GND tie, no inner-plane assignment, and no protective
earth or lightning-current rating. Panel contact remains a first-article test.

## Source adoption follow-through — 2026-09-12

The independently accepted 95-file source was adopted at commit8a2d3620,
as recorded in the carrier schematic journal at20:08 UTC. The initial
proposed/pending wording above is the original handback. Exact native
schematic review and subsequent PCB/routing/release gates remain separate;
no stale generated board or prior sealed release gains acceptance here.
