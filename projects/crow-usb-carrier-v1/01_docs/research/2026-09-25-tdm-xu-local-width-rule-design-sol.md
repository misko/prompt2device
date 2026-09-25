# XU316 TDM launch width: source-rule design, not route acceptance

**Disposition:** retain P1/P2 and the four-net TDM route as unaccepted. This is a
fab-only rule design based on the `7afc7102` isolated placement board
(`candidate.kicad_pcb`, SHA-256
`53e6fb7809910946c36053e7ceeb77e7fc866456ff77775ed4c59b3e49278555`).
That board has no TDM tracks, an unfilled In1.Cu reference zone, 724 native DRC
violations and 499 unconnected items. The separate one-track scratch replay
below is a predicate test, not a completed route or a new source rule.

## The physical contradiction and its exact subjects

On the coupled placement, `U_XU.107` (`TDM_DATA_1V8`) is centered at
`(200.8375, 97.6000)`. Its 0.25 × 1.475 mm F.Cu land ends west at x=200.1000.
Pads `.106` (`N0V9`) and `.108` (physical NC) are centered 0.400 mm above/below
it. A 0.200-mm track centered on the DATA land has only 0.175 mm nominal
edge-to-neighbor-pad clearance while running beside those lands; a 0.150-mm
track has 0.200 mm. The exact native scratch DRC reports the 0.200-mm DATA
stub versus pad `.108` as **required 0.2000, actual 0.1750 mm**. It also
reports the fixed `.106/.107` and `.107/.108` land gaps as **required 0.2000,
actual 0.1500 mm** because that scratch project lacks the source's separate
same-footprint, pad-to-pad rule. The proposed launch width rule must never
relax pad-to-track clearance or cover this pad-to-pad issue.

The same 0.4-mm pitch problem can occur at the other three exact TDM endpoints.
On this board, `.20` (`TDM_FSYNC_1V8`) is `(209.9000,107.4625)`, `.22`
(`TDM_BCLK_1V8`) is `(210.7000,107.4625)`, and `.23`
(`AUDIO_MCLK_1V8`) is `(211.1000,107.4625)`. Their 0.25-mm-wide lands end
south at y=108.2000. Pad `.21` is a physical NC between FSYNC and BCLK;
`.24` is GND beside MCLK. A straight centered 0.200-mm south departure also
has only 0.175-mm nominal lateral gap while adjacent lands are present.
All four endpoints require separate native route measurements before choosing
which local widths, endpoints, and areas are necessary. A DATA-only exception
does not establish the four-net lane.

## Manufacturing basis and limits

JLCPCB's [rigid-board capability table](https://jlcpcb.com/capabilities/Capab)
publishes a 0.09-mm trace/space minimum for multilayer 1-oz copper and a
0.10-mm pad-to-track minimum; its [copper-weight guide](https://jlcpcb.com/help/article/jlcpcb-copper-weight)
also lists 0.09 mm for at least four FR-4 layers at 0.5/1 oz. A 0.150-mm
F.Cu launch is above those public etch floors for the source's selected
four-layer, 1-oz-outer stack. The [XMOS XU316 TQ128 datasheet](https://www.xmos.com/documentation/XM-014532-PC/html/rst/XU316-1024-TQ128.html)
confirms the 0.4-mm package pitch and directs land-pattern design to the PCB
process/IPC criteria. These sources support a **fab-only feasibility screen**;
they provide no TDM timing, crosstalk, return-path, mask, or complete-route
qualification for these specific necks. The nominal 0.200-mm copper clearance
remains the design rule; a 0.150-mm width merely makes it geometrically
possible at the named lands.

## Proposed two-layer source mechanism

The current `floorplan.yaml` already declares `design_rules.track_min_width:
0.15` and `min_clearance: 0.15`; the isolated scratch `.kicad_pro` instead has
Board Setup `min_track_width: 0.20`, `min_clearance: 0.0` and Default-class
clearance `0.20`. Rebuild and audit the *actual* generated `.kicad_pro` before
using an exception. [KiCad 10's manual](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html)
says Board Setup minima are absolute and recommends placing the fabrication
floor there, then using custom rules for stricter local requirements. Follow
that documented architecture: keep the physically justified Board Setup
track minimum at 0.150 mm; emit an explicit 0.200-mm general `track_width`
backstop; retain every stronger netclass rule, including USB_HS at 0.410 mm;
emit a later 0.150-mm rule for each *qualified* exact TDM net/area. Keep a
0.200-mm effective clearance for these tracks through an explicit four-net
TDM class (or an equivalent symmetric pair clearance rule), and retain the
separate, later exact-footprint pad-to-pad rule for the XU lands. The current
source Default clearance is 0.150 mm, so merely asserting a 0.200-mm router
clearance does not make it a native DRC floor. A Default netclass width is
only a router setting, not a DRC width minimum in KiCad.

The prospective source record needs one row per pad, not a TDM group waiver:
`{id, pad: U_XU.107, net: TDM_DATA_1V8, layer: F.Cu,
area: tdm_xu_107_launch, min_width: 0.150mm, exact_segments: [...],
max_thin_length_mm: <measured-and-reviewed>, evidence: <JLC/route review>,
why: <pad fanout geometry>}`. Corresponding rows for `.20/.22/.23` are
conditional on their own route trials. Reject missing or duplicate pads/nets,
areas, segment lists, length limits, and evidence. The generator must verify
the declared pad's exact net and class, rather than accept a free-text alias.

Native KiCad rule shape, *after* the general and stronger class rules:

```scheme
(rule "tdm_xu_107_launch_width"
  (layer F.Cu)
  (condition "A.NetName == 'TDM_DATA_1V8' && A.enclosedByArea('tdm_xu_107_launch')")
  (constraint track_width (min 0.150mm)))
```

KiCad documents `enclosedByArea()` as requiring the whole object inside the
area. The existing generic `scoped_floors` uses `insideArea()`, which accepts
any overlap and is too broad for this launch. Neither predicate proves that a
track starts at `U_XU.107`, exists at all, or is below an allowed cumulative
length. An independent realized-board audit must require the named source pad
and exact net/layer, enumerate **all** sub-0.200-mm tracks on the four TDM
nets, match only approved segment endpoints/widths within a tight tolerance,
check full copper-shape containment and continuous pad-to-nominal-width
connectivity, cap per-pad thin length, reject extra branches/vias, and fail if
any declared area or qualifying segment is absent. The ordinary 0.200-mm
width and clearance resume outside each exact launch. Check the generated DRU
order and native DRC on the realized board; do not infer compliance from an
area declaration alone.

## Isolated native predicate replay

The local scratch board `/tmp/tdm_local_neck.kicad_pcb` has one 0.150-mm
DATA diagnostic track from `(200.8375,97.6000)` to `(199.8050,97.6000)`,
length 1.0325 mm. Its rectangular rule area is
`[199.700,97.490,200.950,97.710]`; the entire track capsule fits. This is a
pad-centered *diagnostic*, with only 0.295 mm beyond the pad's west edge. It
has a dangling end and is not an accepted maximum neck length. The scratch
board SHA-256 is `b170afb31c8a86235bc23ab16e5efb4c4b656467b0d8d76ba67edd2ec69976e2`.

The checked-in [`width-rule probe`](2026-09-25-tdm-xu-width-rule-probe/replay.py)
replays KiCad 10.0.4 DRC from the SHA-bound candidate with a fixture
`.kicad_pro` whose Board Setup minimum is 0.150 mm, an unconditional 0.200-mm
`track_width` rule, and the exact-net F.Cu `enclosedByArea` rule above. Run
`/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-tdm-xu-width-rule-probe/replay.py /tmp/crow-tdm-rule-replay-sol`
from the repository root. The script writes each isolated board, `.pro`,
`.dru`, full DRC JSON and a compact summary under that scratch directory.
The
positive diagnostic has **no DATA track-width or pad-to-track clearance
finding**, only its expected dangling end. Three negative controls add exactly
one DATA `track_width` error attributed to the general 0.200-mm rule: rule
net changed to `N0V9`, track extended 0.305 mm beyond the area, and area
removed. Overall counts are 774 versus 775 violations, with 499 unconnected
items in all four cases; these are not board-pass counts. A separate 0.150-mm
`USB_DP` control with its 0.410-mm rule emits a `track_width` violation
attributed to `USB_HS_width`. The copied `.pro` SHA-256 is
`0fbab8b76154185e8a4dc44401b6b0756ee01f0acac9133515e3d9217326aa53`.

KiCad 10.0.4 also allowed a matching 0.150-mm custom rule against the
*scratch* Board Setup 0.200-mm track minimum, while the no-area and wrong-net
controls failed at that same board minimum. That observed behavior conflicts
with the manual's absolute-minimum statement and should not be used as the
source architecture. The two-layer replay above follows the documented
floor/backstop model and still has the necessary negative controls.

No canonical `nets.yaml`, generator, floorplan, route, or P1/P2 acceptance
state is changed by this note. The remaining gate is an actual connected
four-net route with native clearance/width, package exits, return continuity,
timing, and independent review.
