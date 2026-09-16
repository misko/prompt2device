# Carrier source correction — 2026-09-07

This is a source-author engineering record, not an independent review or a
release. ADR0006/0007 authorize a public-information prototype design, not
ordering, field installation, or ignoring known source errors.

## Corrected source defects

CAR-F11: CS5308P DS1314F1 Table1-2 p6 requires unused SPI_CS to VDD_IO,
unlike SPI_SDO/SCK/SDI which go to GND. U_ADC.38 now connects3V3_ADC;
the other three remain GND. Exact source regression and E-INV pin assertion
prevent restoring the old ground tie. [Primary Cirrus PDF](https://statics.cirrus.com/pubs/proDatasheet/CS5308P_DS1314F1.pdf).

CAR-F10: TI SLLSEG9C p4 specifies normal VIO0..5.5V and component IEC
contact25kV/air30kV. Its12.4V value at5A is typical100ns TLP, not a
guaranteed8/20us clamp. No14V absolute semiconductor rating exists in the
table. Those two invented limits were removed. The schema2 audio path
now checks normal voltage selection over24 explicit parts/eight arrays,
while separately retaining board transient survival as UNQUALIFIED.
The actual isolated12V clamp proof remains required, six exposed parts.
This does not prove the sixteen audio conductors, coupling caps, buffer
inputs or ADC survive any board-level ESD event.
[Primary TI PDF](https://www.ti.com/lit/ds/symlink/tpd2e2u06.pdf).

The power page moves the fuse bank away from C_BUCK_IN3 and separates
J9/F_IN/Q_IN. Q_IN is explicitly drain-left/source-right/gate-bottom;
its pin/net topology is unchanged. OE uses genuine Schmitt inverter
U_OE with local C_OE; ADR0005 records exact authority and limitations.

## OPEN source blocker: 3V3_ADC regulator, load banks and both-direction ramp

TPS7A24 SBVS386E Table6-4 gives DBV reference-board thetaJA167.8C/W;
recommended TJ ceiling is125C. At the retained85C ambient and150mA rail
allocation, `(5.15-3.25875)*0.15=283.6875mW` and reference-board
`TJ=132.6028C`. The corresponding reference thermal budget is238.38mW,
not the old400mW. The authored budget is corrected to238mW, with the
failure explicit; actual board thetaJA is not guaranteed by this metric.
The rail allocation and ambient have NOT been silently reduced.

CS5308P Table3-7 current is typical only, including74.1mA for mid-impedance
48k operation. It does not establish a maximum permitting an arbitrary
smaller rail budget. A hardware power or regulator correction is required.

TPS7A24 section8.1.3 p14 recommends effective output capacitance no greater
than50uF; the p5 nominal range accounts for approximately50% derating.
The local4.7uF minimum check says nothing about the two470uF reference
banks behind low-ohm resistors:940uF nominal/752uF at minus20%, before
parallel ceramics. Series resistors mean these are not simply940uF
directly across the output at every frequency, but they cannot be ignored
in startup, loop stability, supply collapse or reverse-current analysis.
Section8.1.4 explicitly warns about reverse current when a large output
bank remains charged while VIN collapses.

CS5308P Table3-2 p9 requires every supply ramp UP AND DOWN in0.01..10ms.
The LDO current-limit minimum is specified at one output-voltage condition;
it is not a full-ramp charging-current guarantee. Typical ADC current is
not a guaranteed discharge sink. No valid all-corner charge/discharge proof
has been established for this source. Do not mark it a bench-only debt.

`03_src/check_power_source.py` independently reopens both primary PDF
hashes, derives the thermal failure from live rail values, and exits1 with
OPEN_SOURCE_FAILURE. Its tests discriminate the thermal predicate and
retain the unproven startup flag. The general E-CAP minimum gate can still
pass; that is not source acceptance. This dedicated finding must be closed
by source analysis/redesign before further source approval or release.
A larger suitable low-noise regulator is a research direction, not an
adopted or qualified replacement. Any replacement also needs a deliberate
rail-discharge solution; greater sourcing current alone cannot prove ramp-down.
[Primary TI PDF](https://www.ti.com/lit/ds/symlink/tps7a24.pdf).

## Additional confirmed reference-source defects for the next D-BACK

The author independently reopened DS1314F1 section4.5.6 p31 after the
coordinator identified a mode-specific conflict. Its three bullets explicitly
require the input-buffer VMID reference from external components in
hardware/default mid-impedance mode (Fig2-2). The current U_AFE9 follows
the ADC_VMID outputs, the source offered only for high-impedance mode.
This is a known source defect, not a bench-only common-mode uncertainty.
The generic buffered-VMID example does not override this device/mode rule.

Fig2-1 p7, independently viewed, connects ADC_FILT1N/2N directly to GND;
the current source inserts1Ω ground-leg R_FILT1N/2N. The next reference
author must correct/rederive those returns with the external VMID and
power-bank changes as one coherent source revision. Do not reduce470uF
merely to fit the regulator without accounting for the locked distortion
requirement. Existing `check_analog_filter_topology.py` asserts the current
network topology, including the wrong VMID source; its PASS is not evidence
that the hardware-mode manufacturer's requirement is satisfied. Update that
checker and hostile tests alongside the actual reference-source correction.

## Outcome and preserved subjects

Two full producer runs were performed. The first stopped on a checker
representation mismatch: native unconnected U_OE.1 appears as an empty-net
entry. The source was already NC. The exact checker now includes that entry
and a hostile case rejects tying it to GND. The first power-page visual
inspection also led to a more compact4x2 fuse grid, separated from the
input-capacitor bank. Both iterations are preserved.

The second run generated six pages/206 components/603 pins, M-FRESH9/9,
133/133 surviving labels,185/185 pin maps, E-INV66/66, and logic9/9.
It deliberately stopped at shared E-TOPO:284mW against238mW, exit1.
No new source acceptance, catalog checkpoint, ERC acceptance, independent
review, placement, route or release followed. Circuit JSON has zero hard
errors and1347 advisory warnings, not a clean producer census.

Final Circuit JSON SHA256:
`816900b829a750eb3d7e1da6ed7118934b8aaf300fec324ee09c5a1b1ccfac7a`.
Final PDF SHA256:
`ef71de43cb2ad798f3583c4f76a5a9227934a91e80c99e29c384133cf5e2e7eb`.
Final native netlist SHA256:
`6fe02cda1bd075055a44081bf0f0004587a22fafa06c10afe6e8db432c69af46`.

Preservation root: `/tmp/carrier-dback-source-20260907.aOuRpq` contains
the previous build/dist/04_kicad/06_build, current-source snapshot, first
iteration subject, both conductor logs, and four recoverably withdrawn
old request/response/checkpoints. No authenticated receipt existed.
Prior generated verification/catalog/review artifacts not overwritten by
this run are stale historical evidence, not witnesses for the new subject.

Parent-owned renderer correction resolves the project-frozen dependencies
and materializes actual Noto Sans font baselines because librsvg2.58 ignores
dominant-baseline. This run materialized1094 text baselines. Parent reports
renderer12/12, documentation15/15, progressive-disclosure14/14 and
SKILL-AUTH PASS. Source-author tests:30/30 project and42/42 shared early
design (31 hostile fixtures); G-ORPHAN830/830 and ADR-bound PASS.

## Ownership and verification scope

The verified frozen TaskEnvelope remains unchanged. Root explicitly extended
this author's scope to shared E-SURGE checker, its existing tests and the
normative contracts.md schema. The parent separately owns the shared renderer
fix and tests. Prior DEFECTIVE reviews remain unchanged. New generated subjects
must be independently reviewed; no author-run test converts a verdict to SOUND.

## Coordinator verification and next architecture boundary

MEASURED by the coordinator on the final subject above: native-netlist
comparison with the archived predecessor finds 206 to 206 components and
601 to 603 pins. Only Q_TDM_EN/R_TDM_OE_PU were removed and U_OE/C_OE
added; the only common-component pin change is U_ADC.38 to 3V3_ADC, and
no common-component value changed. Normalized electrical SHA256 is
`fd3e1660ae21b04d3c7cf0c330e60c11427c0f7298aa18059038d545e2f67f2b`.

MEASURED seven executable suites: 30 project, 42 early-design, 12 renderer,
15 documentation, 14 progressive-disclosure, 4 crow governance and 36
pipeline acceptance tests pass (153 total). The disclosure suite includes
two deliberately reproduced blind spots; test counts are not board approval.
The coordinator viewed all six final PDF pages at 2200-pixel raster scale;
the prior text-baseline and power-fuse collisions are locally corrected.
This author/coordinator inspection is not a fresh independent SOUND review.

The next D-BACK reopens the power/reference architecture as a coherent unit,
not another cosmetic schematic iteration. Preserve the load/ambient and audio
requirements. The exact retained Cirrus layout-guideline record remains
`evidence/cs530x-effective-capacitance-source.md`: section 1.9 explicitly
permits smaller reference bulk capacitors only at increased low-frequency
THD. It does not authorize silently reducing the performance requirement.
The existing public evaluation schematic also uses zero-ohm ground links
R351/R434 versus one-ohm positive feeds R352/R435 (PDF p17); generic examples
do not override the mode-specific external-VMID rule in DS1314F1 p31.

The four old prelayout request/response/checkpoint files were withdrawn,
not lost: the temporary archive and predecessor Git commit retain them.
No new sourcing request, authenticated allocation, ERC acceptance, placement
or release was produced. Old cached stock and schematic checkpoint are stale.
Known source errors need source corrections; physical prototype measurements
remain a separate later qualification boundary under ADR0007.
