# JLC public POFV evidence for TMUX4827 B2 — 2026-09-24

## Question and fixed geometry

This is a public-document review only.  It assesses the proposed GND B2 escape
at each of `U_ISO1` through `U_ISO8`, all exact TI `TMUX4827YBHR` 0.4-mm-pitch
YBH DSBGA-9 footprints.  The retained coupon and part dossier define:

| Feature | Nominal value |
|---|---:|
| Eight perimeter ball lands | 0.25-mm circular, 0.40-mm pitch |
| B2 GND POFV | 0.35-mm OD / 0.20-mm through drill, filled and capped |
| B2 annulus before fill/cap | 0.075 mm |
| B2 copper to adjacent perimeter land | 0.100 mm |
| B2 drill edge to adjacent perimeter-land copper | 0.175 mm |

The geometry is independently reproducible from the retained [exact part
dossier](../../02_parts/TMUX4827YBHR/part.yaml) and [native coupon
README](../../02_parts/TMUX4827YBHR/qualification/README.md).  TI SCDS457B
establishes the 0.4-mm package grid and nominal land pattern; it does **not**
qualify a JLC filled/capped process.

## What JLC's public material supports

JLC's current [PCB Manufacturing & Assembly
Capabilities](https://jlcpcb.com/capabilities/Capab) states the following:

* Multilayer minimum via is **0.25-mm diameter / 0.15-mm hole**; a 0.20-mm
  hole is preferred, while a 0.20- or 0.25-mm hole with a sub-0.45-mm via
  diameter costs more (capability table, lines 172–173 when reviewed).
  Therefore the proposed 0.35/0.20 via is within the published size range,
  subject to the paid/order option.
* For 1-oz multilayer boards, trace/space is **0.09/0.09 mm** and 3 mil is
  described as acceptable in BGA fan-outs.  A BGA pad of 0.20–0.25 mm requires
  ENIG; BGA-pad-to-trace clearance is 0.10 mm, locally 0.09 mm on multilayer;
  and filled/plated-over vias may be placed in BGA pads (lines 189, 198, 205).
  The coupon's 0.25-mm perimeter lands and 0.09-mm outward launches fit those
  published BGA statements.
* The same page lists epoxy-filled/capped and copper-paste-filled/capped
  via-in-pad, compatible with via diameters **0.15–0.55 mm** (line 217).  This
  range includes the proposed 0.35-mm via.
* JLC's [Five Via Finishes guidance](https://jlcpcb.com/blog/five-via-finishes)
  says epoxy or copper-paste fill followed by copper capping is suitable for
  via-in-pad, calls out a maximum fillable hole of 0.5 mm, and instructs the
  customer to identify required epoxy/copper-paste vias by size range or order
  note.  It also says ordinary ink plugging cannot be used for a via-in-pad or
  one within 0.35 mm of another soldermask opening.  Thus the eight B2 sites
  require the filled-and-capped process; tenting or ink plugging is not an
  equivalent substitution.

The project tier record is consistent with the public broad capability: it
records `jlc_4layer_advanced` as 0.09-mm track/space, 0.25/0.15-mm via and
POFV-capable.  It is a retained interpretation, not a vendor acceptance:
[fab_tiers.yaml](../../../../skills/kicad-pcb/references/fab_tiers.yaml).

## Limits, contradictions, and ambiguity

Public JLC pages do **not** publish a specific annular-ring or hole-to-adjacent-
BGA-land rule for a filled/capped BGA via.  The generic page gives a multilayer
1-oz **PTH-pad** annular-ring minimum of 0.15 mm, but also lists a 0.25/0.15-mm
minimum **via** (a nominal 0.05-mm ring) and says via diameter should exceed
hole diameter by 0.10 mm.  Those different entries cannot be collapsed into
one rule for B2's 0.075-mm via ring.  The page's 0.20-mm **inner-layer**
via-hole-to-copper and via-hole-to-**track** values do not explicitly govern
the 0.175-mm drill-edge distance to a neighbouring **outer-layer BGA pad**.
They also do not establish that distance as accepted.  The exact B2 geometry
therefore remains unspecified in public guidance rather than conclusively
contradicted by the PTH-pad or inner-layer entries.

Likewise, the published BGA **pad-to-trace** 0.10-mm value is not a published
**via-to-adjacent-pad** minimum.  It supports the eight 0.09-mm perimeter
launches, but not the B2 0.10-mm copper gap as a production guarantee.  The
generic SMD pad-to-pad value is 0.15 mm, whereas the native 0.25-mm, 0.4-mm
pitch ball lands yield 0.15 mm exactly.  The proposed B2 exception is narrower
and has no public tolerance margin.

The public [JLC Q&A example](https://jlcpcb.com/help/answers/detail/599-Via-in-pad-Manufacturing-Question)
is an unanswered customer question containing superficially similar 0.4-mm
pitch / 0.2-mm-hole numbers.  It is not manufacturer approval and is not used
as evidence.

## Decision boundary

Public JLC material supports selecting paid filled-and-capped POFV in principle
and supports the nominal 0.35/0.20 diameter/drill envelope.  It does **not**
close the DRC process exception for the eight `.075`-annulus, `.175` drill-to-
neighbour, `.100` via-to-adjacent-BGA-land sites.  No public document reviewed
establishes registration tolerance, CAM treatment, ENIG/mask/paste behavior,
or PCBA yield for this exact stack-up and footprint.

Consequently, the only defensible source disposition remains a *conditional,
exact-eight-site POFV profile* plus an external vendor CAM/uploader and PCBA
acceptance gate.  It must not relax global annulus, hole-clearance, via-size,
or copper-clearance rules.  A vendor response must explicitly address the
0.35/0.20 filled/capped via in the 0.4-mm BGA, the 0.075-mm pre-cap annulus,
the 0.10-mm adjacent-land copper gap, and the 0.175-mm drill-edge gap; a generic
"via-in-pad supported" statement is insufficient.

No order attempt, private uploader interaction, or claim of fabrication
acceptance was made for this review.
