# Digital-launch source handback — 2026-09-08

Outcome: bounded H2 digital source correction, pending root independent
adoption. NOT ROUTE-READY; no generated P-LAND/DRC/route/thermal/SI or physical
PASS. This author relinquishes the exclusive carrier writer lease on terminal
delivery. No child work continues after delivery and no commit was made.

## Identity, scope and exact delta

Repository `/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901`;
administrative HEAD `05a1eb52b5ea8bdc6bb38dccbdf3008ac38743ac`, source adoption
`6259f892bbee579cfc36c82fd2e6fc50e0c10799`. Deadline08:02Z; handback is early
on one coherent batch. Only H1 and H2 new geometry hypotheses were evaluated;
H1 had one conflict, H2 zero. No three-nonimproving threshold was reached.

Before edits, strict TaskEnvelope SHA256
`9bc35eb905d0fd74795dbc1bb3c22e0d47c6e2fe3897d949afbbf6c9f393d13a`,
canonical20-member packet SHA256
`2d137157213f939298e4e563aebe16757a239dd8a8a8304f5ee6959ed3e426d0`
and all409 source-census rows were verified. MEASURED07:25:47Z archive:
1289 actual files/127635305 bytes copied and rehashed before edits. Complete
before inventory and forensic copies are retained, not inferred from old claims.

Six existing files change: route.yaml, digital-only rules/nets.yaml, six new
named digital rule areas in floorplan.yaml, test_route_source_contract.py,
STATUS and append-only routing journal. Three new durable source/doc files:
test_digital_launch_source.py, ADR0011 and this report. New evidence is only
`06_build/tmp/digital-launches-20260908/` (called E below). No placement edit.
Terminal inventory lists exact before/after SHA256 and size for every changed
file and rehashes all unchanged/generated/checkpoint/review subjects. Only
three of409 original census rows differ: floorplan, route and nets source.

| Subject | Before SHA256 | After SHA256 |
|---|---|---|
| floorplan.yaml | `6dec722fc236fe3679a0b40d741fa3029f99bbfc9434dd5571bdef48b227511d` | `4dd2c876342d70edac1363a547c41ae6904778a369699a1014d1fea22f052bc1` |
| route.yaml | `2a064f923cf768dca9f17f6dc2fa49861fc47780446e03833fc4e8e5f83e8f0a` | `64576b9688ce0082e8b8265487a7fc9762c8b71d4c1f7cea1490dcc3c2d9625e` |
| rules/nets.yaml | `219f06fdf207b0f33268ff8b68f23995b130d748a410e4633004f7e77866da5b` | `7d51c9b92d90b959e82d6a19085acd31fa3b6691a540d6ed601aa8f2e91152eb` |

The exact final source assertions preserve all299 refs/868 native memberships/
205 nets/40 NCs, values/MPNs/pin/model/footprint bindings; all placement source,
including the three adopted capacitor poses;150x100 mm outline, mounting holes,
four layers,11 external datums, fab floors, original keepouts/zones, first nine
west-ADC seed banks and power-wave object. Stackup.yaml/rf.yaml, parts dossiers,
shared tools, primary worktree and configured dirty KRT are untouched.

## All twelve digital nets and all27 native endpoints

The initial uniform pad-only .25/.20 clearance sampler uses existing
escape_check.max_landable:48 directions,1 mm reach, capped2 mm width and actual
in-pad landing points, not pad centres alone. Eight endpoints miss .36/.25;
nineteen do not. CLK2/3/6/7 sample maxima are .15/.25 mm, ADC29/34 .10/.20 mm,
ADC24/25 approximately .30/.40 mm at .25/.20 clearance respectively. These
are finite source observations, not exact continuous optima or generated gate
results. Full new geometry is independently screened with native shapes.

| Exact net | All native endpoints | New source copper and owner |
|---|---|---|
| MCH_MCLK | J10.9, R_MCH_MCLK_PD.1, U_CLK.1 | No seed; all three full-width witnesses; generic |
| MCH_BCLK | J10.10, R_MCH_BCLK_PD.1, U_CLK.3 | CLK3 partial .18→.36; other two full-width; generic |
| MCH_FSYNC | J10.12, R_MCH_FSYNC_PD.1, U_CLK.6 | CLK6 partial .18→.36; other two full-width; generic |
| MCLK_BUF | U_CLK.7, R_MCLK.1 | CLK7 partial .18→.36; resistor full-width; generic |
| BCLK_BUF | U_CLK.5, R_BCLK.1 | No seed; both full-width; generic |
| FSYNC_BUF | U_CLK.2, R_FSYNC.1 | One .18 seed reaches both pads; complete prep owner |
| ADC_MCLK | R_MCLK.2, U_ADC.34 | ADC34 partial .18→.36; resistor full-width; generic |
| ADC_BCLK | R_BCLK.2, U_ADC.29 | ADC29 partial .18→.36; resistor full-width; generic |
| ADC_FSYNC | R_FSYNC.2, U_ADC.24 | ADC24 off-centre .36 corner; resistor full-width; generic |
| TDM_RAW | U_ADC.25, U_TDM.2 | ADC25 off-centre .36 corner; buffer full-width; generic |
| TDM_BUFFERED | U_TDM.4, R_TDM.1 | No seed; both full-width; generic |
| ADC_TDM | R_TDM.2, J10.2 | No seed; both full-width; generic |

MEASURED after-change full-source witnesses for the other19 endpoints include
every final foreign pad and old/new seed, hole/seed-via/keepout and edge, using
.36 mm copper/.25 mm clearance and1 mm reach. R_FSYNC.1 also has such a witness
but needs no generic routing: it is already reached by its complete source
seed. The two corner ADC starts [98.29,73.1] and[99.1,72.29] touch actual copper
despite not being pad centres; neither was unnecessarily narrowed.

Reaching means native full-copper contact with the declared same-net pad and
a connected primitive chain. Eight banks touch their declared pads; only CLK2
also touches another same-net pad. Seven banks remain partial. No other net
topology, pull-down branch or complete path endpoint changed.

## Geometry, exceptions and ownership

E/candidate-h1.json retains H1's full-source C_CLK.1 conflict: CLK7 .36 mm
extension [149.5,58.55]→[149.95,58.4] has .11 mm nearest-pad gap at required
.25. H2 changes only the end to[149.95,58.55], giving .26 mm. It also retains
the corrected inherited CLK3/CLK6 widened entries; hostile tests prove the
old [144.8,59.35]/[149.2,59.25] .36 discs conflict with CLK4/CLK5 at .25.

MEASURED H2 and final live-source geometry:18 new primitives,868 native pads,
111 physical-hole/mounting-head shapes,18357 checks and zero findings:
15582 foreign-pad,1998 hole,18 track-keepout,18 edge,36 existing seed-via,
36 seed-hole,661 old/new foreign-seed comparisons and8 declared-pin checks.
All full round ends and widened entries are included. Native quantization
tolerance is2 nm, not a manufacturing waiver. Nearest gap values are separately
calculated polygon observations; they are not DRC certificates.

| Bank | Narrow length mm / count | Closest initial foreign-pad gap mm | Widened exit gap mm |
|---|---:|---:|---:|
| CLK2 / FSYNC_BUF | 1.400000 / 1 | .235 | none; complete |
| CLK3 / MCH_BCLK | 1.430278 / 3 | .235 | .295 |
| CLK6 / MCH_FSYNC | 1.020000 / 1 | .235 | .303073 |
| CLK7 / MCLK_BUF | 1.142443 / 2 | .235 | .260 |
| ADC29 / ADC_BCLK | .900000 / 1 | .210 | .395265 |
| ADC34 / ADC_MCLK | .900000 / 1 | .210 | .422738 |
| ADC24 / ADC_FSYNC | 0 / 0 | .210 at full .36 | .586803 |
| ADC25 / TDM_RAW | 0 / 0 | .210 at full .36 | .884288 |

Six exact named F.Cu areas and their net lists/rectangles are recorded in
ADR0011 and live source. Four gain .18 width floors; all six gain .20 local
clearance. Total scoped rules become5 floors/7 clearances including the
untouched west-ADC rules. Every narrow capsule is wholly contained, not merely
overlapping; two corner first capsules are contained in clearance-only areas.
All widened exits are independently screened at ordinary .25 even where
item-overlap semantics might permit .20. Class ADC_CLOCK stays twelve/.36/.25.

Existing clocks realized_width contract is .36 nominal/.18 minimum,1.44 mm
maximum subnominal length and3 primitives per net. These are explicit authored
source discontinuity allocations, not solved SI limits. Durable tests additionally
require exact lengths/counts above and reject an overextended overlapping item,
fourth segment and .17 floor. Final generated same-bound remeasurement remains
mandatory after all producers, including excluded FSYNC_BUF's exact1.40 mm/1.

The exact partition is162 generic (clocks11,analog96,references10,power8,
pod_power11,control25,bootstrap1), two complete deterministic nets LDO_A_FILT
and FSYNC_BUF, one GND and40 NCs =205. All class counts remain11/8/25/1/11/
96/12/1. Source wave/width consumers and shadow compile/verify reconcile it.
Existing O-DOUBLE preflight only checks many-pad power, not this two-pad clock;
the retained hostile test shows that limitation and requires exact shadow
compilation to reject a duplicate FSYNC deterministic/generic owner. No checker
was weakened or modified to hide this gap.

## Reproducible checks and retained failures

All finite runs use E/run.py NAME SECONDS followed by the exact argv. Each
NAME.run.json retains cwd, argv, real UTC start/end, timeout, elapsed time,
rc, cancellation status and full raw-log SHA256; NAME.log retains stdout/stderr.
Heartbeat is10 seconds. No run timed out or was cancelled.

| Run | UTC start–end | Finite bound / rc | Result |
|---|---|---|---|
| endpoint-census | 07:27:47–07:27:53 | 120s / 0 | 27 endpoints,8 shortfalls |
| candidate-h1 | 07:36:03–07:36:07 | 120s / 0 | Diagnostic completed, one geometry conflict; REJECTED |
| regression-before-source | 07:36:30–07:36:34 | 90s / 1 | Five tests:1pass,3fail,1missing-bank error before source patch |
| candidate-h2 | 07:37:35–07:37:39 | 120s / 0 | Zero source-geometry findings |
| full-project-tests | 07:46:03–07:46:12 | 120s / 1 | 122/123; hostile expected O-DOUBLE outside its applicability |
| rules-source | 07:46:18–07:46:18 | 40s / 0 | Source classes8/8 |
| net-references | 07:46:18–07:46:18 | 40s / 0 | 334/334 references,0ghost/0unreached |
| final-source | 07:47:50–07:47:55 | 45s / 0 | Live H2 equality/full geometry/preserved source/shadow205 |
| full-project-tests-final | 07:47:50–07:48:00 | 120s / 0 | 123/123 after correct shadow consumer binding |
| after-endpoints | 07:49:43–07:49:46 | 45s / 1 | First diagnostic incorrectly treated own PTH drill as foreign; four J10 false failures retained |
| after-endpoints-final | 07:50:14–07:50:17 | 45s / 0 | Exact own plated-hole exception; all19 full-source witnesses |
| full-project-tests-terminal | 07:50:14–07:50:24 | 120s / 0 | 124/124, including ten digital source tests |
| replay-candidates | 07:55:57–07:56:04 | 45s / 0 | Archived before-source + saved H1/H2 point lists reproduce exact checks/findings |

Exact terminal test argv: `/usr/bin/python3 -m unittest discover -s
projects/crow-audio-carrier-v1/03_src/tests -v`; terminal full-log SHA256
`41a92d4dbd0b15107ac8e756c0a49f7905aab0a4171a63f8befb182912d2771b`.
Source consumer argv: `/usr/bin/python3 skills/kicad-pcb/scripts/rules_audit.py
projects/crow-audio-carrier-v1 --phase source` and `/usr/bin/python3
skills/kicad-pcb/scripts/net_reference_audit.py projects/crow-audio-carrier-v1`.
Source tests call existing wave_nets/check_wave_widths/audit_config,
compile_source_prep_authority/verify_authority and copper_length_audit.load_groups.
No real realized_track_width_guard was run because it loads a BOARD; only its
authored configuration and exact source extents were checked here.

Existing test suite warnings (KiCad property-enum initialization and unclosed
read-only parser handles) remain in raw logs; rc0 is not a warning-free claim.
The old west-ADC engineering/negative tests still run against their exact nine
banks; new tests separately compare all digital copper with those old banks.
No source correction was made in response to the own-hole diagnostic false
failure, and no rejected source geometry was counted as improving via rerun.
Original candidate programs read the then-current source; after source adoption
use E/replay_candidates.py, which explicitly loads the archived baseline and
the saved point lists instead of accidentally appending duplicate live seeds.

## Retained primary authority and unchanged subjects

Primary public files were read from the verified local dossiers, not replaced:

| File | SHA256 | Applied authority |
|---|---|---|
| SN74LVC3G34_SCES366L.pdf | `d541afbccf6270522f5ba33b86ca31da0ec6bbf497c0d1f8ba265e9ac2e1faec` | pp3/10 exact DCU pinout and bypass/unused-input layout |
| CS5308P_DS1314F1.pdf | `6ca42cc09ac47ebdacacaee435f05e3f9c34b83d5692e52a2d8a26533e810e57` | pp4–5 exact physical digital/ground/supply pins |
| CS530x_Schematic_Layout_Guidelines_202507.pdf | `a97e3cfbe311caf603bd56b7aeab189dd38727104168c26bb67dd24add07b62f` | pp10–12 digital50 ohm/near-source-series/ground/decoupling intent |

U_CLK uses native Package_SO:VSSOP-8_2.3x2mm_P0.5mm; U_ADC uses the exact
project-local Cirrus QFN48/0.4 mm/4.6 mm EP footprint. All299 isolated native
footprints are loaded at source-expanded poses, with actual effective pad/hole
shapes. No BOARD constructor/load/save or alternate PCB is involved.

E/before-inventory.json and E/archive retain all original subjects.
E/terminal-integrity.json rehashes1289 archived files and current counterparts:
1283 unchanged existing files, six allowed changes, three new durable files.
All20 packet members remain exact;406/409 census rows unchanged. Generated
board SHA256 remains `72f4b136f2c5477167b06861b2636e48be955a6500a27cac867bd267cb4f0abb`;
native netlist remains `3b2bba539a61e279c3111a80d01087f6978fc4c498a74f194fbb2512c0aea63f`.
Every generated/checkpoint/review byte is preserved and remains stale/unaccepted.
E/evidence-index.json binds terminal evidence members; it excludes itself and
the already separately hash-bound archive. Root must independently rehash/adopt.

## Next boundary and unresolved obligations

PCB-design/KiCad skills caused strict lifecycle source backtracking, finite
source-only checks, exact ownership/extent boundaries and refusal to promote
local geometry to generated acceptance. No Board, conductor, prep/router/import,
checkpoint retirement/resume, route exploration, generated review impersonation,
commit/release/tag/push/account/upload/vendor contact/purchase occurred.

Root independent source adoption is next, then remaining source current/
ground/thermal/SI work before any combined authorized generation. Local seeds
do not prove generic routing will avoid re-entry, preserve every final primitive,
or retain all pull-down branches. Reopen generated source admission/P-LAND,
final widths/extent/clearance/land contact/connectivity/DRC, exact full paths
and filled-plane return continuity after all producers. The .36 mm public-stack
hypothesis remains unsolved, especially local discontinuities and real edge
rates/source-series/receiver/package delays; no invented50 ohm or skew PASS.

Preserve1.20 mm bulk power/2.5 A, the exact5.05 mm/eight-segment3V3 exception,
all three adopted capacitor poses, independent GND_A/VMID paths and common
inner planes. Genuine series-current transfer/current sharing, fault/startup,
ground/paddle/thermal spreading, realized return and SI proof remain open.
TOP77, first-power0.20 A HOLD, DO-NOT-ORDER, ADR0007 prototype scope, ADR0009
independent-power-state limits, physical/service/sourcing/publication obligations
all remain. This handback grants no physical or publication authorization.
