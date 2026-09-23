# USB4215-03-A source candidate

This is the public-only source candidate for `J_USB`. GCT drawing A sheet 1
(`GCT_USB4215_A.pdf`, SHA-256
`1659ba00769b9b774a033fac72cb2f3bfc481a3272c53f34e87520f33635a9e1`)
identifies a top-mount horizontal USB 2.0 Type-C receptacle with 16 logical
contacts. Its recommended PCB layout is viewed from the component side. The
contact row remains 12 physical SMT lands: A1/B12 and A12/B1 share GND lands;
A4/B9 and A9/B4 share VBUS lands. A6/B6 are distinct D+ contacts and A7/B7
distinct D− contacts. The existing 17-port logical identity including `SH`
therefore remains intact.

The drawing shows **no locating peg** and instead four plated shell slots at
X=±4.32 mm. Relative to the contact-row centre at footprint Y=−3.680 mm,
the source places the upper shell-slot centres Y=−3.105 mm and the lower
centres Y=+0.895 mm (4.00-mm vertical separation). This uses drawing A's
5.15-mm contact-leading-edge-to-lower-slot-centre dimension and its
1.15-mm-long contact lands: `5.15 − 1.15/2 = 4.575 mm` from contact centre
to lower slot centre. The upper-to-lower 4.00-mm dimension gives the upper
offset `0.575 mm`. The drawing also places the dashed front component outline
2.10 mm beyond the lower shell-slot centre, hence front Y=`+2.995 mm`. A
6.50-mm body depth gives back Y=`−3.505 mm`; the contact solder lands extend
0.750 mm behind that body edge. F.Fab and the simple model use these outline
datums, while the courtyard includes the rear lands and a nominal 0.50-mm margin. Contact X coordinates, widths (eight 0.30 mm plus four
0.60 mm) and 1.15-mm length are from the same layout. The mirrored shell
centre spacing is 8.64 mm. Plated lands are 1.00 mm wide with 0.60-mm slot
width; upper length 1.80 mm land / 1.40 mm hole, lower 2.20 / 1.80. This
preserves 0.20-mm annulus on straight sides and ends. Outer contact-to-shell
copper horizontal gap is `1.12 − 0.30 − 0.50 = 0.32 mm`; contact-to-slot
gap is `1.12 − 0.30 − 0.30 = 0.52 mm`. These are nominal drawing calculations,
not supplier DFM acceptance or a complete tolerance stack.

The connector's shell still needs through-hole stake assembly; the signal
contacts remain SMT. Drawing sheet 2 is packaging evidence: 1,200 pieces per
reel, tape unreeling/peel direction and carton quantities. It provides **no**
board assembly method or shell-stake solder-process approval. A public JLC catalog response on 2026-09-23 identified C37616412 for this exact MPN.
The volatile raw response (SHA-256
`d4694044864b9b9f64567008ab9cabe6f32085e5f0e86ac4eade50bb7ae9e993`)
is retained only in the ignored `06_build/cache/` snapshot; stock and assembly
availability require a fresh check.

The source VRML model is a **drawing-derived envelope**, not GCT CAD. It marks
the +Y mouth side, rear contact direction and the four downward shell-stake
directions. Its simplified body is 8.94×6.50×3.16 mm from the drawing/product
page, without cavity detail, tolerance sweep, precise mating plane, or
registered board edge. The selected cable, mouth exposure, assembly process,
PCB-mounted model registration, neighboring connector operation and all 19
physical targets remain open. The source-only candidate makes no P1/DRC,
routing, full connector, or JLC order claim.

The earlier USB4105 board-edge anchor is not transferred to this candidate.
The +Y mouth marker and body outline are source-model cues only; the exact
PCB edge, shell-stake seating, mating datum and installed orientation need an
independent registration before any island or floorplan proposal is adopted.

The connector assembly contract carries the existing board-level **intended**
service direction `[0, −1, 0]` from the dated connector placement intent.
That intent explicitly says all connector orientations await native placement;
it does not establish this footprint's board rotation, mouth-to-edge datum,
or installed mating geometry. The local model mouth points to footprint +Y,
which would point board −Y only after an independently accepted 180° placement.

A separate source-only native alias fixture used this exact dossier and the
source footprint with the current `part_identity` and schematic converter
(`06_build/verification/usb4215_alias_fixture/`, ignored). Its reproducible
script SHA-256 is
`4a2c53dcd064a9752038c9fa84183e23e4baa4e8fb1d28fa09992317fb9c91f5`;
the result JSON SHA-256 is
`cf709cfb9a2b254f7a35311975debfc287c29ad1ae47b6e17cfa5e4744465402`;
the native KiCad DRC/parity JSON SHA-256 is
`712b081b612805ebff6bd1da28b5f4ed21196f685728cff1d774e6dc0844d4ef`.
For geometry commit `3cd02b44940eb9aca8879d56f47796f7d4365cfa`, it verified
17 logical A/B/SH pins, 12 physical SMT locations, four shell PTH slots and
zero NPTH; four fused VBUS/GND pairs share both copper and net, A8/B8 SBU
remain no-connect, A6/B6 and A7/B7 carry D+/D− respectively, and
SH shares GND with the current authored `crow_carrier.tsx` caller. The
single-footprint net-assigned board produced **zero native schematic-parity
issues and zero DRC violations**; eight unconnected items reflect the small
unrouted fixture and its explicit SBU no-connects. This is not full Crow
schematic/PCB parity or route proof.

A separate four-case negative fixture forced one pad in each manufacturer-fused
pair to the opposite GND/VBUS net. The native checker reported
`shorting_items` and `solder_mask_bridge` in every case; no conflicting fused
pair escaped. Its ignored script SHA-256 is
`8b2e181d02f71f4cfc252ceb4886fc85e73c40ee194364cde514102e1e966649`,
and the results SHA-256 is
`fc60c565e02f329bbf4de5a058394e6af113ab8814cef45517ad55215172dbd5`.
The fixture establishes this exact part/net mapping only, not general
connector or full-board parity.
