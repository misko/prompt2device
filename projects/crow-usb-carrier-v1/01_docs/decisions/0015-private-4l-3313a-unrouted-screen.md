---
id: 0015
date: 2026-09-25
status: accepted
---
# D15 — one private, unrouted 4L 3313A stack screen

**Accepted project decision (2026-09-25).** The continuing release-design
instruction authorizes this reversible private diagnostic. This decision
supersedes only the narrow D11/D13/D14 boundaries stated below. An independent
hash-bound preflight remains required before generation. No board generation
or routing is authorized outside the one named experiment.

## Decision

Allow **one** ignored, private, **unrouted** native diagnostic derived from the
current TI prototype subject, changing only a copied four-layer stack/rule
contract to evaluate special `JLC04161H-3313A` and the exact-net USB pair
geometry. This extends [D13's](0013-usb-esd-prototype-boundary.md)
schematic-only and [D14's](0014-private-native-diagnostic.md)
current-stack sidecar boundary solely for this named experiment. It supersedes
[D11's](0011-p1-floorplan-and-p2-placement-admission.md)
connector-FULL bar **only** for a private stack and USB pair-rule preview on
this one unrouted copy, since rule generation may count as route preparation.
Route import, track/via/arc/teardrop creation, and ordinary P3 or routing
remain barred until connector FULL. The
`prototype_only` TI ESD and `DESIGN_CLEAN` holds remain. This creates no
engineering board, test article, fab candidate, accepted stack, or stage
admission.

## Frozen subject and permitted private delta

The pose/outline reference is the exact ignored expanded TI board
`06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925/04_kicad/crow_carrier.kicad_pcb`, SHA-256
`fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16`.
Its project/rules sidecars are `.kicad_pro`
`7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094`
and `.kicad_dru`
`00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a`.
The copied TI circuit JSON is
`580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d`,
netlist `a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd`;
the exact schematic is pinned by the [native parity probe](../research/2026-09-25-ti-expanded-native-parity-probe/replay.py).
The copied floorplan is
`2f7843ada9eb08d19d268f0d6671079a8cf367629b2b3331119088927415b634`,
`rules/nets.yaml` is
`18033487a097b6d29abe3f9d8517879931cf80d278d8973adcf276010a5b7190`,
`rules/rf.yaml` is
`833a8c022648859e65ba3b727bffd14c868214936a9751f12c5a15ecd3ea376c`,
and `rules/route_fab_overrides.txt` is
`d8285ec77a25583b21afa136de614faa4257008250f370e2b5d08d359ef6a1d9`.
The [JLC fixed-geometry packet](../research/2026-09-25-jlc-3313-uniform-usb-solve-sol/README.md)
and [Terra's exact edit map](../research/2026-09-25-private-4l-3313a-unrouted-diagnostic-terra.md)
are research inputs, not stack acceptance. Freeze their hashes and the
generator, library tree, KiCad version, connector contract and rule seed in
the independent preflight receipt; any drift stops the attempt.

Work only in a fresh ignored `06_build/prototype_board_diagnostic/` child
containing private copies. Change its copied floorplan to the JLC special
1.58-mm nominal/±0.158-mm thickness, L1–L2 and L3–L4 composite 3313
dielectric 0.2064 mm/Er 4.1, 1.065-mm core/Er 4.38, with four layers and
existing finished copper thicknesses retained. Change only the private
USB_DP/USB_DN **F.Cu pair** contract to 0.180-mm width and 0.100-mm
*intra-pair* gap, retaining 0.150-mm clearance to every foreign pad/net/via/
zone, no USB vias, and all other netclass rules. The pair-clearance preview
must use a tight named rule area with exact `nets_a: [USB_DP]` and
`nets_b: [USB_DN]`; retain generic `USB_HS` 0.150-mm clearance. A disposable
synthetic KiCad DRC check must prove precedence and foreign-net negative
controls before the Crow preflight. A private RF/route-contract
copy may replace only the 7628G cross-section facts with the named 3313A
**hypothesis** and no-credit marker. A private process-note copy may update
only drill aspect-ratio explanation. The sole new rule geometry allowed is one
F.Cu-only permissive area named `usb_pair_xu_launch`, rectangle
`[215.3, 95.0, 217.1, 95.8]` mm around U_XU.59/.60. On the frozen board,
their native pad boxes are respectively `[215.425,95.475,216.9,95.725]` and
`[215.425,95.075,216.9,95.325]` mm; adjacent pads 58 and 61 remain outside
the area's y bounds. The preflight must reopen those native boxes and reject
any drift. This area previews only the XU launch, not the full connector-to-XU
path. No other source, part, placement, pad, hole, outline, net, rule or
geometry change is permitted.

The private copied-file/field allowlist is: `floorplan.yaml` stackup entries
named above plus exactly one `keepouts` entry
`{name: usb_pair_xu_launch, layers: [F.Cu], deny: [], rect: [215.3, 95.0, 217.1, 95.8]}`;
`rules/nets.yaml` USB_HS width/gap plus one exact `nets_a`/`nets_b`
scoped-clearance declaration for that area; `rules/rf.yaml` named
cross-section inputs and research status, plus only the `USB2-CLAIM-ZDIFF`
text/evidence/acceptance fields needed to retract the old 7628G claim and
label the 3313A result as an unqualified research hypothesis; and
`rules/route_fab_overrides.txt`
aspect-ratio explanatory text only. Each resulting generator output is compared
against the frozen board by object class and exact geometry. Any other copied
source or generated-board difference is a stop.

The experiment may regenerate only its private `.kicad_pcb`, `.kicad_pro`,
`.kicad_dru`, TMUX POFV areas, parity/DRC reports and a hash-bound research
receipt. Do not add conductor tracks, arcs, vias or teardrops; retain the
baseline 14 GND vias, eight rule areas and one GND zone, saved **unfilled**.
Do not route, create fabrication/assembly exports, run the ordinary
`rebuild_all.sh` past connector FULL, alter canonical `03_src`/`04_kicad`,
accepted pointers/contracts, modular work status or release manifests.

## Independent gates and stop rule

Before generation, a reviewer verifies every frozen hash, the exact TI
schematic/netlist receipt, copied source diff against the allowlist above, and
the hash-pinned [native parity replay](../research/2026-09-25-ti-expanded-native-parity-probe/replay.py):
KiCad 10.0.4, zero violations, **499 opens**, zero *performed* schematic
parity issues on the 7628G reference. The reviewer also verifies the JLC
packet's provenance limits: the 89.9172598796-Ω 0.180/0.100-mm value is a
public fixed-geometry output, not an authenticated production impedance or
approved stack. No generation starts before this decision and its independent preflight are
reviewed and signed.

After the single generation, an independent reviewer checks exact 569
electrical poses, 1,810 electrical pads, six holes, eleven connector poses,
outline, pin/net identities, all non-USB rules and existing copper against
the reference; only declared stack/rule/POFV changes may differ. Run count,
native pin/net and **performed** schematic parity, V-PROCESS, and full
zone-refilled native DRC on a disposable copy. Preserve full violations and
unrouted count rather than calling an empty parity list a pass. Screen the
XU.59/.60, TI ESD and both Type-C leaf envelopes, 0.150-mm foreign
clearance, mask-dam clearance and pad-to-pair fan. This unrouted screen can
reject a geometry hypothesis; it cannot demonstrate the complete pair,
return continuity, skew, impedance, assembly fit or connector FULL. Stop and
record `FAILED_RESEARCH` on any hash mismatch, unexpected object/source
delta, added saved copper/zone fill, parity failure, new native defect, or
unverifiable screen. No retry or automatic alternate candidate is included.

The final receipt must say `RESEARCH_UNROUTED_STACK_SCREEN`, name all exact
inputs/results, and set P1/P2/P3/P5, connector FULL, route, fabrication,
assembly, release and order credit **false**. Further source selection would
require separate stack/price/Standard-PCBA confirmation, exact-route/return
and SI work, full stack-dependent power/TMUX/thermal/mechanical revalidation,
connector FULL and ordinary project admissions. This decision confers none of those later admissions or credits.
