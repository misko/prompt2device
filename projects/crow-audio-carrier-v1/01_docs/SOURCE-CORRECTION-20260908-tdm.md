# CARRIER-TOPO-001 source-author correction — 2026-09-08

Author evidence only: not an independent review, canonical TaskAttempt,
source acceptance, PCB acceptance, release, or physical qualification.
Baseline HEAD a17ede026cceabb821738884857e99b6823e056f; exact task and
immutable441-file scope-R1 packet live in06_build/verification/
tdm-source-correction-20260908-a17ede02. Original envelope is preserved.
Raw scope-R1 SHA256:
d60e3e9864e18d88376f5cf2350848c3a1c1d5f3c201c3b1bb21e32db66f3fa3.

## Source decision and limits

The old raw node truly lacked bias; U_TDM output disable did not define its
CMOS input. Source now inserts exact noninverting Nexperia74LVC1G17GV,125
U_TDM_SCH/C6076,10k R_TDM_PD and100nF supply C_TDM_SCH. The existing
TI1G125 output/OE/Ioff boundary and all four power-state intentions remain.
ADR0005's append-only amendment owns detailed primary facts, executable
resistor bounds, loading, slew, round-trip timing and qualification holds.

Stored Nexperia Rev16 primary PDF SHA256 is
3db133d57486306950ba1140ac13a8a0ea95509dcefb88db36c08423a819b163.
Its true Schmitt input accepts unlimited input rise/fall time. TI's retained
CMOS input has a10ns/V ceiling. The conditioner deliberately removes the
raw RC decay from that input; propagation delay is not an output-slew bound.
Manufacturer output-transition maxima are absent; final edge measurements
and remote setup/hold/duty information remain OWED, not silently guaranteed.

The20uA ADC-plus-PCB Hi-Z leakage,20pF raw capacitance,0.4mA ADC added load,
25uA clean-node load,6ns complete path allowance,5ns MCH setup and45percent
minimum clock phase are explicit engineering allocations. Cirrus INPUT
leakage and16mA drive setting are not output-leakage/loaded-level guarantees.
Under these assumptions: released raw0.2163V; high load0.372134mA;
high-to-Hi-Z decay to0.4V about600.165ns; device delays24.1ns and residual
setup margin1.521094ns at12.288MHz. This conditional prototype screen is
not a full-temperature timing or SI guarantee. Existing150mA rail allocation
is not raised;5mA is reserved inside it. Native power inventory charges the
new0.1uF. First-article card names failure/stop criteria and slow-input current.

## Exact additive ownership

Source299→302 components,868→877 pins and205→207 native nets (including
one added singleton NC). Every old component identity and geometry remains;
the sole old pin-net change is U_TDM.2 TDM_RAW→TDM_CLEAN. No old seed copper
changes:88banks/218segments/20vias remain. New anchors are U_TDM_SCH
[147.5,52,0],R_TDM_PD[144.25,52,180],C_TDM_SCH[150.75,51.05,0].

Digital nets12→13, ordered physical path segments15→17. Only old
U_ADC.25→U_TDM.2 is replaced, by ADC→conditioner and conditioner→U_TDM;
the real conditioner-input→pull-down leaf is added. All non-TDM endpoints,
all24 analog groups and report-only/no-via semantics remain. The existing
shared reader requires identical ordered path IDs within a group, so TDM
moves into the genuine main/pull_down group with MCH inputs; unbranched
buffered clocks stay together. No dummy leaf, deleted endpoint, reduced
denominator, shared checker edit, or routing permission was introduced.

## Actual author observations

Every command capture below is under the task's actual directory; raw runner
state timestamps govern timing, not earlier estimated commentary headings.

- red-old-source-checker: actual12tests/3expected failures before repair;
  all9 inherited tests still passed.
- green-source-screen:16/16 conditional arithmetic checks, six resistors and
  four exact primary PDF identities. Physical guarantee explicitly absent.
- full-suite-before-regeneration:105tests/4failures/11errors; old native
  cohort deliberately stale and real report-path schema issue then corrected.
- full-rebuild: stopped at a caught0.05168Ohm transcription discrepancy in
  the new lower-bound value; command/budget unchanged, value corrected.
- full-rebuild-r2: expected prelayout exit2,302-way source parity,
  E-CLOSURE9/9,selection2/2,52-code request,421/11 input/checkpoint pins.
- full-suite-after-regeneration:195tests/10failures, all historical additive
  census/preservation expectations. Updated exact owned delta only; retained
  all old authority comparisons and added explicit original299/88/path tests.
- full-suite-additive-expectations:197/197 PASS,59.889s, zero failures/errors.
- tdm-native-geometry:302refs/877pads;8211 new-pad/foreign-pad+hole checks,
  no failures. Native copper gaps0.690306/0.670164/2.986816mm clear dossier
  ceilings1.5/1.5/5mm;22/22 digital launches and73/73 power landings pass.
  Isolated native source shapes are not realized body/courtyard, DRC or SI.

The exact old eight-file checkpoint/request/blank/public-stock cohort was
copied and moved recoverably as one unit. The later r2 cohort was similarly
reopened after additive test corrections: five present members retained;
three not-yet-produced members explicitly absent. Both operator worksheets
remain blank except their exact Requested LCSC column. No authenticated
receipt, reviewer restamp, PCB generation, commit, order or upload occurred.

Final conductor/public-screen/review-boundary results and exact changed-file
inventory will be appended to this author record at handback. All original
TOP77,first-power0.20A,THT,connector,thermal/current/SI and publication holds
remain; independent schematic review must be newly commissioned on final bytes.

## Final author boundary — actual clock2026-09-08T15:36:20Z

Full-rebuild-r3 completed in75.282s,exit2 at the intended prelayout boundary.
It produced302refs/877pins/207nets,19pages,165/165 surviving labels,
209/209 pin-map assertions,115/115 electrical invariants,5/5ADR links and
E-CLOSURE9/9. Build diagnostics:0embedded errors/1688advisory warnings.
M-BOUND remains15CITED/3ESTIMATED/0UNVERIFIED,37OWED; the three inherited
ADC bounds now execute successfully inside their budgets but retain their
ESTIMATED classification. No debt floor or ceiling was changed.

Full-suite-final-r3 passed197/197 in56.550s,zero failures/errors/skips on
these regenerated bytes. Native geometry v2 adds6234courtyard/body-to-pad
checks at0.1mm without failures; all302 native courtyards were present.
The diagnostic still does not certify a realized board. Live-power-screen
passed15/15 conditional checks, with1061.08uF actual charge inventory;
150mA3V3 allocation is unchanged. The author visually inspected delivered
page18's11parts and clear wiring/labels; this is not the fresh PDF review.

Public-stock-r3 completed109.509s,exit0:52/52 exact codes pass five-board
quantity with zero required absolute surplus. C6076 was observed at3136
catalog units. The tightest stock ratio remains C53283916 at60units/40
required. Raw stdout is copied verbatim as the stock.txt companion; no
operator response fields or allocation receipt were filled.

Public-prelayout-resume-r3 completed2.996s,exit1 at PR-REVIEW, not a producer
failure:421/421input census,11/11prelayout checkpoint, exact request and
readiness4/4 were verified before writes. ERC0errors/2100warnings are fully
retained. New schematic checkpoint7/7 is recorded. PR-REVIEW graded2/2 old
artifacts and found8issues: seven stale hashes plus the prior DEFECTIVE
topology verdict. Neither old review was edited/restamped. Fresh independent
topology and delivered-PDF reviews are required on this final source.

Detailed before/after changes, generated artifact/review hashes, actual runner
UTC timestamps, warning-class counts and immutable packet verification live
in the task's actual/final-inventory.json. The task terminal-result-r1.json
is an author handback, not a canonical TaskAttempt or acceptance receipt.
The exact board and historical pinned schematic remain unchanged;
no PCB generation, promotion, placement, routing, release or Git commit ran.

Next executable read-only check from repository root:
`/usr/bin/python3 -B skills/kicad-pcb/scripts/stage_checkpoint.py verify projects/crow-audio-carrier-v1 schematic`.
Root must inspect/commit the exact source and commission fresh independent
reviews before any schematic-review continuation. Do not rerun the full
producer or use the placement-capable resume arm while those reviews are stale.
