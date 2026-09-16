# ADR-0007: shielded RJ45 factory-cord spoke

Status: proposed source integration; independent full-source review pending (2026-09-12)

## Decision

Use Wurth 615008160221 at pod J1 and Weidmuller 8909650150 factory-terminated
15 m shielded Cat6A straight-through cords. Pins 1/3/7 carry `12V_POD`, pins
2/6/8 carry `GND`, pin 5 is `AUDIO_P`, and pin 4 is `AUDIO_N`. Shell tabs 9/10
form the local `POD_SHIELD` island and have no pod signal-ground connection.
The carrier owns the low-inductance shield-to-chassis bond at cable entry.

U3 is the sole bottom-side component. Its two exposed-line prefixes are
J1.5-to-U3.3 and J1.4-to-U3.5, each exactly B.Cu, via-free, no more than 4.0 mm
pad-centre distance and no more than 4.2 mm realized copper. Every downstream
path must include the complete prefix. Other governed critical paths retain
their exact F.Cu requirements.

The old Micro-Fit promoted route remains immutable history and is ineligible
for replay after this topology and placement change. `route.import_source` is
`build`, so import fails unless a future routing run creates a fresh
`06_build/route/FINAL`; promotion follows full independent acceptance.

## Qualification boundary

Exact-product manufacturer STEP establishes the nominal complete-end geometry:57.98mm axial, including rear sleeve and raised latch. Independent native BREP containment supports a22.986mm nominal grip diameter about the documented cable axis. Keep manufactured radial/axial tolerance, installed exposure, full latch motion and populated service unknown in the existing phase contract. Primary cable OD is6.1..6.5mm; retain67mm bend planning floor, exceeding10D at maximumOD. The former HARTING approximate-dimension SOURCE hold is superseded by this evidence, not by an invented manufacturing maximum.

UV is unestablished and remains an explicit environmental qualification hold before outdoor deployment. PUR is not a UV rating. Exact power-off1:1 T568B, shield continuity, contact resistance/current and2.2ohm finished hot-loop tests remain owed in FIRST_ARTICLE_TEST_PLAN. Source and physical admission remain separate; no release or order authority follows from nominal geometry alone.

Assembler DFM must accept bottom U3 beside later-soldered J1 tails, including
bottom paste/CPL rotation, mask web, fillets, inspection, rework, and the
nominal 0.40 mm courtyard-to-annulus clearance. The J1 manual soldering profile
is not published and remains an assembler qualification item. First article
must also prove POD_SHIELD-to-GND isolation and the complete ESD/noise tests.

The pod J1 surge-coordination ceiling is a proposed project 28.5 V DC
insulation limit (57 V PoE application divided by a 2x engineering reserve),
not a re-labelled 150 VAC rating. The exact jack appears on Würth's PoE++
compatible range page. The part source record separates that application
inference from its published AC specifications and retains first-article
qualification; independent source review must accept this assessment.

## Source adoption follow-through — 2026-09-12

The independently accepted 95-file source was adopted at commit8a2d3620,
as recorded in the carrier schematic journal at20:08 UTC. The initial
proposed/pending wording above is the original handback. Exact native
schematic review and subsequent PCB/routing/release gates remain separate;
no stale generated board or prior sealed release gains acceptance here.
