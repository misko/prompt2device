# OPA2320 and retained-reference source correction — 2026-09-09

Author checkpoint, not source engineering acceptance, native review, routing
or release. Base commit4885a4a9; exact observations and source hashes are in
`SOURCE-CORRECTION-20260909-opa2320-outcome.json`, SHA256
`6126a3d4a060e6907108e3aeddfd1b6107e2cd795fca685d9f7da4f23773c083`.

## Implemented

ADR0023 adopts nine OPA2320AIDR/C2863402 packages on existing5V_OPA, adds
two10k reference input limiters, and changes two reference output isolators
to1k RC0402FR-071KL/C106235. Capacitors remain divider-side of the input
limiters; follower feedback remains raw-output-side of the output isolators.
All signal-filter values, eight channels,1.2Vrms differential, eight0.10A
spokes, external datums and pod source remain unchanged. Source population
is325 parts,923 physical pin occurrences,228 nets including41 NC names.

Source wiring/presentation, inventory, floorplan, routing/net classes,
electrical invariants and first-power population agree. Two new exact
dossiers bind unchanged primary PDFs. The retired carrier OPA1656 dossier
had no sealed carrier dependency; its PDF was moved to the temporary
adoption workspace and remains recoverable in Git and the frozen review
packet. Other boards and the still-used100ohm bleed-resistor dossier remain.

## Measured verification

| Check | Result and scope |
|---|---|
| Pre-change source suite |250/250PASS; actual run20:31:23..20:33:04Z, not inherited |
| New tests on actual4885a4a9 |10 tests;8 semantic failures including subtests,3 missing-function errors; raw-feedback hostile already passed |
| First attempted RED |Import error only; explicitly not credited as defect reproduction |
| Final focused tests |14/14PASS;21:06:50..21:06:54Z |
| Final full source suite |264/264PASS;21:07:41.727345..21:09:30.437841Z;108.396s test runtime |
| Source power topology |40 exact pin maps/39 values;25 conditional arithmetic checks pass; generation_admitted remains false |
| Changed reference placement |Native-library pads/courtyards checked against the full325-component source geometry;15 exact-net adjacency pairs pass; not a generated PCB |
| Protected prior inputs |478/503 unchanged;25 intentional carrier source/dossier changes; native PCB and pod inputs unchanged |
| Fresh reviewer frozen inputs |18/18 rechecked; source-review recommendation only, not PR-REVIEW SOUND |
| Structure audit |2891 existing findings,0 added/0 removed against the retained prior postcommit log; still FAIL |
| Global ADR bound audit |15 CITED,3 ESTIMATED,38 OWED against37 ceiling; still FAIL, no floor change. ADR0023 adds no derived inequality; carrier ADR0021 remains named debt |

The initial full run exposed stale census/preservation fixtures. Only the
two new reference nets/anchors are projected out of historical comparisons,
after exact assertions. The new geometry test then caught two courtyard
clashes and an overlong divider connection; moving only the added input
resistors fixed them without relaxing clearance/adjacency limits. Actual
final new anchors are R_VMID1_IN[73,70.6,0] and R_VMID2_IN[80.9,73.5,180].
Nonfatal KiCad PROPERTY_ENUM and existing parser ResourceWarnings remain.

## Review, sourcing and claim boundaries

The actual fresh reviewer returned IMPLEMENT_WITH_EXPLICIT_SOURCE_OBLIGATIONS
on the frozen4885a4a9 candidate. The outcome retains a clearly labelled
coordinator-condensed transcription, not a verbatim full response or invented
canonical TaskAttempt. It is not approval of the subsequent source patch.
Its five obligation groups remain explicit in that record and ADR0023.

Both new MPNs passed public two-distributor sourcing BEFORE adoption; details
and dated observations are in sourcing/parts-selection-2026-09-09.md.
This is targeted2-part evidence, not current whole-board availability or
JLCPCB PCBA allocation. No account, upload, supplier contact, purchase or
credential extraction occurred.

The reference arithmetic gives0.568421mA positive-input and5.684211mA combined
OUT/-IN return-current screens for the assumed5.4V resistor differential and
5percent resistance reserve; output resistor power is0.030695W against the
series-derived0.051471W85C screen. Nominal output RC is4.7ms. These are
MEASURED SOFTWARE ARITHMETIC, not physical readings, proof of reachable node
voltage or an output-pin overdrive rating. The source explicitly says so.

## Next engineering work

Close the correlated cold/start/restart and reference/filter charge argument:
TMUX partial supply, independent ADC voltage/current limits, CT and NR
retention, output backdrive, reference leakage/loading/settling, actual
common/differential filter loops and feed-current duration/thermal envelope.
OPA2320 is not Cirrus noise/THD-performance-equivalent; qualification scope
and unchanged acceptance limits are explicit. Do not restart a catalogue
search or another scalar delay sweep. No perfect proprietary silicon model
or new valid-audio-during-shutdown requirement is introduced.

The BRIEF hash rebind is only an ADR register addition and historical T4
implementation annotation; all requirements, directives, investigation
milestones, four attempts, six-attempt budget and one non-improving count
remain. choose_source_correction is not credited. CAR-F12 stays open.
After source admission, use the full conductor and fresh native reviews,
then placement/routing and final release gates. No generated files, route,
release tag, publication or physical acceptance changed at this checkpoint.
