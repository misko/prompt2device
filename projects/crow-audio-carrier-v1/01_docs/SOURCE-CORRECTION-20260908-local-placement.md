# Local placement source correction — 2026-09-08

Disposition: **SOURCE-ONLY HANDOFF FOR INDEPENDENT ROOT ADOPTION.** The authored
intent is coherent under the bounded calculations below. It is not generated
placement, P-ADJ, P-MODEL, DRC, routing, fabrication or physical acceptance.
The saved PCB remains stale/unaccepted. **DO-NOT-ORDER; first-power HOLD.**

Author: fresh exclusive `carrier_local_placement_source_20260908` source task.
Repository: `/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901`;
branch `codex/crow-roof-array-board-dev-20260901`; unchanged HEAD
`6545d7d15bda7645fe9424723583f865afd521e9`. Final source assessment observed
2026-09-08T05:18:21.202798Z; final checks ran 05:23:52–05:23:58Z.

## Execution boundary and provenance

The complete immutable TASK/TaskEnvelope and selected PCB-design/KiCad
lifecycle, runtime, placement/proximity, source/prep and project contracts
were read before source actions. JLCPCB-fab guidance was read; no public
sourcing, account, vendor, allocation or purchase action occurred. The strict
11-member packet and 407-file before-source census were verified. Envelope
SHA256 `4ea2d3132831c3da71de4fd29aed5e652e3742f42fdead91a0db680cd8cd32e2`;
packet SHA256 `7ebdbbab5d3bde10ce85ba635d4449c6d28058c9132c0b9eb776d6f48eb39a1e`.
The packet, its copied diagnostic whitespace and literal `+by` are untouched.

Root subsequently withheld both optional producer arms so separately observed
route-source defects can be batched before regeneration. That narrower boundary
governed this attempt: **producer commands `[]`; public resumes `[]`; retired
targets `[]`; new schematic-review requests `[]`.** There is no producer exit
code, watchdog attempt or fresh producer boundary to report. The actual stopping
boundary is source-only handoff before root adoption/regeneration. No checkpoint
was re-stamped, deleted or retired. No new PCB was built, moved or saved; no
commit, push, shared-tool modification or delegation occurred.

Before source edits, 722 files / 97,764,814 bytes were copied and rehashed at
04:25:40.934914Z beneath
`06_build/tmp/local-placement-20260908/archive/`. The sibling
`archive-inventory.json` SHA256 is
`3cf4c772adf775ccf96cc173d4d178d4816ad7fc7f6849f1f3320e735ad83f53`.
All 722 archive copies were reverified in the final assessment; no original
target is missing. The archive includes authored sources, generated schematic
bundle, sourcing request/evidence, all three checkpoints, PCB/project/rules
and prior reports. Nothing material was deleted. All prior reports, including
the model-source and authority-batch handbacks, remain verbatim.

## Exact authored delta and whole-inventory coverage

Of the frozen 407 authority inputs, exactly **20 changed and 387 remain
byte-identical**: `03_src/floorplan.yaml` and the following 19 `part.yaml`
dossiers, with changes restricted to their `layout` subtrees:

`1812L035-60MR`, `2920L260-33DR`, `2N7002K-7`, `74LVC1G14GV,125`,
`AO3400A`, `AO3401A`, `AP63205WU-7`, `BLM21PG600SN1D`, `CS5308P-DN`,
`DMP6023LFG-13`, `OPA1656IDR`, `SN74LVC1G123DCTR`, `SN74LVC1G125DBVR`,
`SN74LVC3G34DCUR`, `TMUX2821DSGR`, `TPD2E2U06DRLR`, `TPS3839K33DBZR`,
`TPS389001DSER`, `TPS7A9201DSKR`.

Every dossier's non-layout YAML projection is identical to its archive copy.
All MPNs, values, physical pins, native memberships, electrical topology,
footprints, model files/bindings/overrides and datasheet bindings are preserved.
The separate source regression changes are
`03_src/tests/test_local_placement_source.py` (new, 11 tests) and
`03_src/tests/test_ldo_region_selection.py` (preserves the historical regional
fallback test after removing only the now-explicit LDO-cap anchors in that
fixture, and expands existing repeats). Documentation changes are STATUS,
the placement journal and this new report: 25 total Git-delta paths.

The native inventory resolves **299 fitted references, 868 numbered pin
memberships and 920 physical pad objects**. The 205 parsed nets include 40
no-connect pseudonets; equivalently there are 165 connected nets including
GND, or 164 non-GND connected nets. No added or missing component exists.

Coverage is enumerated, not inferred from the old 41-cap diagnostic:

- [all-299-source-coverage.csv](../06_build/tmp/local-placement-20260908/evidence/all-299-source-coverage.csv)
  lists every reference, value, footprint, final source pose, ownership roles
  and relationship count. All 128 capacitors appear. 297 references participate
  in the 325 explicitly derived relationships; J10/J11 are the two additional
  reviewed fixed external interface datums, not omitted support components.
- [all-325-before-after-relationships.csv](../06_build/tmp/local-placement-20260908/evidence/all-325-before-after-relationships.csv)
  enumerates owner/ref/partner/net/physical-pin selection, engineering centre
  budget, old saved-board centre/gap and proposed source centre/gap. The full
  pad/courtyard coordinates are in `evidence/candidate-geometry.json`.
- [final-source-assessment.json](../06_build/tmp/local-placement-20260908/evidence/final-source-assessment.json)
  retains every changed/unchanged census path, all 325 relationships and the
  actual 287 adjacency / 64 keep-short declaration evaluations.

The floorplan now provides **147 direct anchors plus 152 anchors from the
existing two four-channel repeat banks**, all pinned, with `require_anchor`.
There are no regional-centre floaters. Existing placement patterns, model
override patterns, region definitions, legalization settings and pinning
semantics are preserved. The board remains four layers, outline
(20,20)–(170,120) mm; mounting datums (25/165,25/115) mm and fiducials are
unchanged. All 11 external connector poses and their external labels are exact.

Each repeated cell owns 19 members: AFE, entry fuse/ESD, two coupling caps,
local bypass, paired input/feedback/output resistors and capacitors,
differential capacitor, isolation switch/bypass and output pulldowns. North
AFE origins are `(40.5 + 32k,47,0°)` and south origins
`(40.5 + 32k,93,180°)`, k=0…3. South member offsets are negated and rotations
advanced by 180°, preserving electrical identities rather than swapping P/N.
Film-cap input pads face the connectors; biased pads face the amplifiers.
The 16 ADC common-mode capacitors are explicitly placed at ADC-side pins,
not inherited from the remote AFE cells. U_ADC remains `(96,70,0°)`.

Power/reference support is explicitly owned around U_BUCK `(42,66)`, its
unchanged inductor `(47,66)`, U_LDO `(64.5,70)` and U_AFE9 `(78,70)`.
Clock/TDM local support follows U_CLK `(147,59)` and U_TDM `(154,54)`;
the TDM source resistor and bypass are next to their actual owner near J10.
Hold-cap positive pads face the common feed; C_HOLD2 rotates 180°.
Eight stale static P1–P8 captions were removed in favor of repeat-owned fuse
captions. MAIN moves to `(32.5,81.2)` beside F_IN `(32.5,77)`.
Generated silkscreen fit/ownership remains a later gate.

## Local obligations, metrics and quantitative before/after

All numerical maxima here are **engineering placement budgets**, not vendor
specified trace lengths. The repository ≤5 mm bypass/BST and ≤10 mm feedback
guidance informed the plan; most feedback pairs are held to ≤5 mm. The
unchanged XGL switch-pad budget remains 3 mm, measured 2.6775 mm both before
and after. Trace resistance, loop inductance and routed length are not measured.

| Physical-pin centre-span obligation | Rows | Centre budget mm | Old saved-board maximum mm | Proposed source maximum mm |
| --- | ---: | ---: | ---: | ---: |
| Local IC bypass, including repeated AFE/ISO and control | 26 | 5 | 44.392 | 4.070 |
| ADC supply/LDO/VMID pin bypass | 12 | 5 | 61.742 | 4.974 |
| ADC common-mode input caps | 16 | 5 | 12.308 | 4.891 |
| ADC FILT reference ceramics | 4 | 5 | 12.460 | 4.500 |
| Local feedback at AFE input/output pins | 48 | 5 | 53.820 | 3.615 |
| Differential filter interconnect | 32 | 10 | 17.195 | 8.669 |
| LDO input/output physical pins | 4 | 5 | 23.309 | 3.915 |
| LDO NR capacitors | 5 | 5 | 24.681 | 4.342 |
| LDO feedback resistors | 2 | 5 | 24.606 | 1.824 |
| Buck VIN bypass | 3 | 5 | 13.703 | 4.915 |
| Buck bootstrap at BST and SW pins | 2 | 5 | 11.950 | 3.332 |
| Timing capacitors/resistor | 7 | 5 | 28.833 | 4.792 |
| Entry ESD P/N ownership | 16 | 5 | 61.307 | 3.376 |
| Clock/logic/gate/control local relationships | 23 | 5 | 39.007 | 4.973 |

No proposed row exceeds its stated budget. The complete 35-role, 325-row
inventory includes coupling, bias, series output, isolation, reset/strap,
power entry, fuse and reference/bulk obligations omitted from this short table.
For example, ADC pin 7→C_LDO_A improves 54.338→1.687 mm; ADC pins
32/33→C_LDO_D improve 61.742/61.719→2.310/2.412 mm. Supervisor VDD
pin 4→C_PWR is 30.492→1.420 mm; pin 4→C_AUDIO is
15.980→2.453 mm; U_DUMP VCC pin 5→C_DUMP_LOGIC is
20.854→4.070 mm. U_RST2 timing pins 6/7→C_RST_T are separately
measured at 3.337/2.995 mm; its supply owner is pin 8, not a tied-high input.
VMID1 pins bind to ADC pin 1 and VMID2 to pin 12; VDDA1/VDDA2 pin-specific
owners 5/9 are not interchangeable caps on a shared 3V3_ADC rail.

Necessary non-bypass exceptions are explicit, not silently treated as 5 mm:

- Film input coupling: 10 mm centre budget, maximum 7.773 mm, retaining
  the actual 5 mm pitch body and its entry-to-bias orientation.
- Reference dividers: 6 mm, maximum 4.936 mm. External-reference 10 µF
  and buffer bulk: 10 mm, maxima 7.770/7.893 mm, with separate local 1 µF
  bypass maximum 2.632 mm. These bulk/quiet-node paths still require short,
  quiet routing and the manufacturer trace-resistance check.
- FILT 470 µF reservoirs: 15 mm to the ADC reference pin, maximum
  12.495 mm; separate 1/10 µF ceramics are ≤4.500 mm. The resistor-to-bulk
  feed is independently bounded to 10 mm, measured maximum 6.353 mm.
- Hold-up bulk: 20 mm from the local C_LDO_IN feed, actual
  C_HOLD1/C_HOLD2 17.703/19.991 mm. These are low-frequency reservoirs,
  not substitutes for the local LDO input capacitor. This deliberate area
  tradeoff worsens their old centre spans (12.041/17.845 mm); current-path
  width, transient impedance, return path and effective hold-up remain open.
- Secondary buck output capacitors use 10 mm; the raw hold reservoir uses
  15 mm. The nearest output capacitor is 2.242 mm from the inductor output;
  fixed-output FB sensing is 9.600 mm under its 10 mm budget and must route
  from the quiet output side, not through SW. Entry feed/fuse paths use
  separate 10/15 mm budgets and require current-capacity review.

Machine-readable enforcement uses the **existing** `policy_audit` consumers:
287 new `layout.adjacency` rows bind exact reference pairs and explicit real,
non-GND nets. Their metric is copper-pad axis-aligned bounding-box gap,
not pin-centre span. Individual limits are recorded in the dossiers and final
assessment; engineering gap ceilings include geometric slack rather than
pretending a centre budget equals an edge budget. The 63 new `keep_short`
rows bind physical `anchor_pins` and exact `partner_refs` on owners whose
footprint-ID selection is unique; the existing inductor row makes 64 total.
Their actual metric is physical pad-centre span. The final calculation invokes
the existing `physical_pin_keep_short_spans` helper on isolated footprints.

The consumer resolves dossier owners by footprint ID, not MPN/reference.
Repeated AFE/ISO and shared small-logic/supervisor footprints therefore use
exact-pair adjacency rather than a shared-rail nearest-cap keep-short shortcut.
Adjacency still cannot distinguish two same-net pins on one owner: for example
U_PWR/U_AUDIO VDD4 and tied MR3. The source inventory explicitly measures
VDD4; later physical review must retain that pin ownership. Poured GND is
excluded by adjacency, so none of these rows proves the return loop.

## Geometry, primary authority and ground/thermal limits

Source-only calculations load exact isolated library footprints, apply the
existing repeat/initial-pose mechanisms and compute pad/courtyard coordinates.
They do not call a board builder, add footprints to a new Board or save a PCB.
The old PCB is loaded read-only solely for the before measurements and policy
negative control. Scripts and four diagnostic SVG/PNG views are retained under
`06_build/tmp/local-placement-20260908/evidence/`; each view says SOURCE ONLY.

The complete 44,551 reference-pair courtyard-box screen has no gap below
0.30 mm; minimum is R_BCLK↔U_CLK, 0.30 mm (floating-point representation
0.29999999999998). All 920 pad boxes lie within their own courtyard boxes.
The minimum foreign-component copper-box gap is 0.59 mm, C_AUDIO.2↔
R_AUDIO_PD.1. The nearby foreign-copper to F.Fab body-graphic box screen also
has positive minimum 0.59 mm; F.Fab text is excluded from body geometry.
The minimum copper-to-preserved-board-edge distance is 1.325 mm, J10.11.
These orthogonal bounding-box measurements are conservative spacing screens,
not exact 3D bodies, generated courtyard DRC, keepout/service access or routing.

Retained primary layout authorities, reviewed alongside native topology:

| Local authority | Used layout evidence |
| --- | --- |
| [OPA1656 SBOS901C](../02_parts/OPA1656IDR/OPA1656_SBOS901C.pdf), pp.27–28 §8.4/Fig.8-13 | Local V+ bypass, compact feedback, quiet input separation and ground-plane guidance; preserved the existing non-inverting topology. |
| [TPS7A92 SBVS318B](../02_parts/TPS7A9201DSKR/TPS7A92_SBVS318B.pdf), pp.22–23 §10.1/Fig.42 | Same-side CIN/COUT, wide power return, quiet NR/lower-feedback return and EP/thermal-via obligations. |
| [AP63205 DS41326 Rev.3-2](../02_parts/AP63205WU-7/AP63205_DS41326_Rev3-2.pdf), p.15/Fig.25 | Compact VIN/BST/SW/output loop and quiet feedback. Its copper recommendation was not used to change the adopted fab/stack floors. |
| [CS5308P DS1314F1](../02_parts/CS5308P-DN/CS5308P_DS1314F1.pdf), pp.7–8/Fig.2-2 | Actual supply, VMID and FILT connections, including directly grounded negative filter pins. |
| [AN0556R1](../02_parts/CS5308P-DN/CS530x_Input_Buffer_Filter_Circuits_AN0556R1.pdf), p.4/Fig.2 | Local input buffer/filter relationships; the adopted component values/topology remain exact. |
| [July 2025 CS530x layout guidelines](../02_parts/CS5308P-DN/CS530x_Schematic_Layout_Guidelines_202507.pdf), pp.10–12/Figs.8–10 | VMID/filter grounding, separate GND_A/GND_D plane connections, finite digital-side ground cutout, matched input pairs, ≤0.5 Ω buffer-to-ADC trace DC resistance and controlled 50 Ω digital routing. |

All six exact PDF hashes are retained in
`evidence/primary-layout-authorities.json`. In particular, guidelines SHA256
is `a97e3cfbe311caf603bd56b7aeab189dd38727104168c26bb67dd24add07b62f`;
DS1314F1 is `6ca42cc09ac47ebdacacaee435f05e3f9c34b83d5692e52a2d8a26533e810e57`.
Relevant retained supervisor, single-gate, triple-buffer, switch and ESD
datasheet layout sections were also read for near-VCC/timing/entry ownership.
No public source was newly fetched or represented as fresh allocation evidence.

The FILTN wording in the guidelines is not a reason to alter topology:
root independently examined DS p.8 and evaluation E0 p.17, whose R351/R434
are explicitly 0 Ω. Separate GND_A/GND_D vias may join the same GND plane.
The finite digital-side moat is a physical routing/zone reconciliation, not
evidence for isolated schematic ground nets. All zones remain unchanged.
Historical CS5308P-DN `notes.md` wording “unlike current carrier one-ohm
negative returns” is stale and flagged for a separately authorized correction.

`evidence/ground-pocket-proposals.json` records **86/86 ground-bearing
capacitor return-space candidates**, outside their own courtyard, with direct
stub candidates ≤3 mm, plus 12 EP egress-space proposals for ADC/LDO/eight
isolation switches. These are uninserted geometric reservations, not vias or
ground traces. The hypothetical via is 0.50/0.20 mm: annulus 0.15 mm meets
the preserved 0.13 mm floor. The screen uses 0.25 mm hole-to-copper and
0.50 mm hole-to-hole clearance, with 0.15 mm test stubs at the preserved
0.127 mm fabrication copper-clearance floor. It does **not** qualify the
unchanged router's 0.25 mm clearance or the current GROUND class 0.30 mm
track width. The four configured 0.45/0.20 mm
route/stitch via sites remain untouched; root independently found their
0.125 mm annulus is below the 0.13 mm floor. No blind EP/paste vias were added.
Bulk return ampacity, local loops, heat spreading and separate ADC analog/
digital ground connections remain physical route-owner obligations.

## Tests, evidence and unchanged subjects

Final commands ran from the named worktree; complete stdout/stderr, UTC
start/end, arguments and return codes are in `evidence/final-checks.json`
and its four log files. Exact commands:

```sh
/usr/bin/python3 -m unittest discover -s projects/crow-audio-carrier-v1/03_src/tests
/usr/bin/python3 skills/kicad-pcb/scripts/policy_audit.py projects/crow-audio-carrier-v1 --skip-drc --phase source --output /tmp/carrier-local-placement-20260908.gn0FFQ/policy-source-after.md
/usr/bin/python3 skills/kicad-pcb/scripts/policy_audit.py projects/crow-audio-carrier-v1 --skip-drc --phase placement --output /tmp/carrier-local-placement-20260908.gn0FFQ/policy-stale-board-negative-control.md
git diff --check
```

- 05:23:52.858–05:23:53.748Z: **95/95 tests PASS**, rc0. New regressions
  prove complete pinned coverage, repeat mirroring, unchanged datums/models,
  all-cap/actual-net declaration coverage, ADC physical-pin ownership,
  unique-footprint keep-short owner semantics and corrected fuse captions.
  A hostile common-rail case proves that an unrelated near capacitor cannot
  satisfy a physically bound far intended capacitor's keep-short check.
- 05:23:53.748–05:23:55.382Z: source policy **PASS=2**, rc0 (P-LAYOUT,
  P-PREC). This phase does not grade source-proposed proximity as a board.
- 05:23:55.382–05:23:58.431Z: unchanged stale-board negative control,
  **expected rc1**, FAIL=2/PASS=3: 53/64 keep-short and 269/287 exact-pair
  constraints reject the old board. All **351/351 declarations are reached**.
  This is deliberate known-bad rejection, not a new placement gate result.
- 05:23:58.431–05:23:58.440Z: diff whitespace check rc0. Existing KiCad
  PROPERTY_ENUM and legacy unittest ResourceWarning diagnostics are preserved
  in raw logs; no shared code was edited to suppress them.

The 30-file non-gate evidence package is inventoried by
`06_build/tmp/local-placement-20260908/evidence-inventory.json`, SHA256
`420a4dfaa19452f03c50f588c19030e067d285587b65748c6af1b8c485b70d3a`.
Its source calculations are bounded diagnostic scripts, not a production
generator or alternative acceptance checker. Root's independent interim
04:56-candidate screen is useful corroboration only and predates final digital,
caption and hold-cap changes; it cannot approve this final source implicitly.

Final authored/source subjects:

| Subject | SHA256 |
| --- | --- |
| floorplan.yaml | `f5a897ea3afac77b7ef1291ebc3220a01495c0921f6728a2f4dbf3ef73b41d58` |
| Official parts digest (relative-path/NUL/content/NUL algorithm) | `74b185decaf546b1230474ee1692c82d4c4d8e52b9add00f67a49c3740967c33` |
| Unchanged semantic netlist | `b6da08f18cecc93d43eb7b5ccd87ccbca01ed3c97c450add1e75ad9d6c88d369` |
| Unchanged design-rules digest | `e5087b6b49a592e47d04c784df48db6806325dfc9f8be06e40a728055f7736a2` |
| Unchanged raw native netlist | `3b2bba539a61e279c3111a80d01087f6978fc4c498a74f194fbb2512c0aea63f` |
| Unchanged Circuit JSON | `22db91c1bf52ee3a709e8121b9a85e0102f55064ea1efa141d73d6ef5130f1f2` |
| Unchanged schematic PDF | `339ecaddadc094d08f3efa6317aa57fa2a738d2417a94d1da3967a1cc18cbab2` |
| Unchanged 04_kicad schematic | `544999412cdc87aab91ce4c56a98f8b65ddae5ae9d6c4130468c68757469dec8` |
| Unchanged stale PCB | `72f4b136f2c5477167b06861b2636e48be955a6500a27cac867bd267cb4f0abb` |
| Unchanged sourcing request | `0062b752250bfba1e95ae3940accdf619dc57d7515729bd93753a51eaaa05ce8` |
| Unchanged prelayout-inputs checkpoint | `029fbdff9e256a473e16f171a477f5b2a2ce41b25cd1a6e545fde314fdb0b4c1` |
| Unchanged prelayout checkpoint | `3eaff08ee5c56d33d92201a6e72bbf260703dcc0dd2e6cb8c93a4972e0b9a7fd` |
| Unchanged schematic checkpoint | `f11c43a958506e7fdaf0c4a59a0da5e155568cff566867508a115e314d8cd445` |

All other exact saved project/rules/build-provenance/secondary schematic hashes
remain those in the immutable packet `subjects.json`; final assessment rehashed
every listed subject. The old parts digest
`aca88a2ea82cf15bc5f4e4371a0382b009801ca1d6ef9800547e2f2bd4a99904`
is no longer current. Preserving checkpoint bytes is not preserving their
validity: source/layout changes stale those boundaries, requiring a future
governed source reopen and fresh request-bound reviews, never re-stamping.

## Explicit unresolved checklist and handback

- [ ] Independent root adoption of this exact source, declarations, final
  footprint poses and evidence. Author calculations are not independent review.
- [ ] Separately authorized route-source correction: exact-net wave groups,
  missing net classes, class/wave widths, 0.45/0.20 via-annulus defect and
  fine-pitch launch **clearance as well as width**. Root's read-only ADC screen
  found sampled maximum launch width 0.20 mm at 0.20 mm clearance and
  0.10 mm at current 0.25 mm clearance; unchanged 0.8 mm POWER_TRANSIENT
  floors and absent scoped neckdown rules cannot be assumed routable.
- [ ] Physical 50 Ω digital impedance/stackup and matched-input route review;
  actual buffer-to-ADC trace resistance ≤0.5 Ω. Source centre spans prove
  neither trace length nor resistance. Nominal stackup thickness remains
  ungraded; no stack/fab floor was changed here.
- [ ] Quiet NR/feedback returns, distinct ADC GND_A/GND_D plane connections,
  finite digital-side moat, ground-loop/current paths, hold-up reservoir
  impedance and legal thermal egress. The existing legalizer 0.30 mm spacing
  warning versus the 0.65 mm via-pocket guideline is not globally waived.
- [ ] Authorized full-source producer, fresh public-only sourcing boundary and
  fresh exact schematic review after root's batched source corrections. No
  review/producer permission transfers from this exhausted writer lease.
- [ ] Eventual generated-board P-ADJ/P-COLLIDE/DRC, pin/connector/caption
  ownership, silkscreen fit, all-model registration/height/service clearances,
  via/paste/thermal legality and actual route gates on the new saved subject.
- [ ] Preserve TOP77-Q1–Q5/N1, first-power HOLD and all physical prototype,
  enclosure/service, exact supplier CAD, sourcing/allocation and publication
  qualifications. ADR-0007 supersedes the former physical-coupon stop but
  does not imply any physical measurement or production qualification.

The source author stops at this bounded handoff and relinquishes the exclusive
writer lease in the terminal message. Root owns independent adoption and all
subsequent authorization. No approved result follows from silence.
