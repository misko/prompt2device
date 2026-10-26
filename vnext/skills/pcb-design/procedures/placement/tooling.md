# Local placement producer and review contract

Run with `/usr/bin/python3` (KiCad pcbnew installed). The placement producer does
not author copper. No external services, purchases or library downloads are involved.

```
/usr/bin/python3 tools/placement.py build --project PROJECT --inputs INPUTS --plan PLAN --output OUTPUT
/usr/bin/python3 tools/placement.py verify --project PROJECT --inputs INPUTS --plan PLAN --output OUTPUT
/usr/bin/python3 tools/placement.py issue --project PROJECT --review REVIEW
/usr/bin/python3 tools/placement.py check --project PROJECT
```

All named paths except PROJECT are project-relative. Build refuses an existing
output; use a new candidate directory. A failed geometry check still leaves
native boards/previews and the findings; it does not produce acceptance.
`issue` and `check` optionally take `--receipt RELATIVE_PATH` for a versioned
successor receipt; both still execute the same owning certificate and refuse
overwriting on issue. The default historical path is unchanged. A downstream
consumer must explicitly bind the selected receipt; merely writing another
receipt does not advance routing or replace the old release.

## Author interface

INPUTS is coordinator-owned JSON, version1, `boards` mapping to each accepted
`intent`, native exported `netlist`, `footprints` map (library:name to retained
file) and independent `rules`. Authors may not weaken INPUTS to fix a candidate.

PLAN JSON version1 has `boards` with exactly the same board keys. Each board:

- `outline`: [width_mm,height_mm], origin top-left [0,0], x right, y down.
- `layers`: 2 or 4; `layer_plan`: nonempty explanation of roles and returns.
- `placements`: every physical schematic ref maps to [x_mm,y_mm,angle_deg].
  Angles are KiCad degrees, one of 0,90,180,270 (positive counterclockwise).
- `mounts`: list of [x,y,drill_diameter,keepout_diameter], all positive sizes.
- `blocks`: list of {id,members}; every physical ref occurs in exactly one
  block, while proximity and other relationships may cross block boundaries.
- `notes`: short assumptions and unresolved placement risks.
- Optional `board_keepouts`: unique physical references whose existing footprint
  rule areas become board-owned at the exact placed geometry. The producer keeps
  each owner and its areas in a native group, preserving curves, layers and all
  prohibitions. This explicit representation change requires placement/mating
  review; it does not allow free-form keepouts or routed copper at placement.
- Optional `edge_notches`: radiused recesses in a rectangular board edge. Each
  row has `edge` (north/east/south/west), `start_mm`, `end_mm` measured clockwise
  from that edge's starting corner, inward `depth_mm`, inside `radius_mm`,
  `overhang_refs`, `reason`, and retained `evidence` paths. Recesses cannot touch
  corners or overlap. Native arcs preserve machining radii. Geometry rejects
  pads, mounts, reservations and undeclared bodies in the conservative removed
  rectangle; `overhang_refs` permits only named body overhang, never pads.
  Evidence and source recipe are review-bound. A body exception is not mating
  approval: recheck actual 3D engagement, edge/copper/web tolerances and access
  independently, then renew placement and affected downstream acceptance.

Shared rules, per board, may contain `envelopes` keyed by ref with local
[xmin,ymin,xmax,ymax] mechanical courtyard rectangles; these need an evidence
source in the input manifest. Otherwise native footprint courtyard geometry
is observed conservatively as a bounding rectangle. Missing geometry fails.
Pad geometry is never changed by envelope refinement.
For a source-owned mechanical repair, optional `npth_revisions` maps a physical
reference to `{reason,evidence:[paths],holes:[...]}`. Each hole row contains local
`at:[x,y]`, `before_mm`, `after_mm`, `before_clearance_mm` and
`after_clearance_mm` (`before_clearance_mm:null` means no local override, distinct
from an explicit zero). The existing accepted library stays immutable. The producer
requires exactly one unnumbered, netless circular NPTH at that location with the
declared baseline diameter and clearance; only diameter and local clearance may
change. No moves, new holes, numbered pads or electrical edits are supported.
Recipe, original library, evidence and regenerated native output are bound by
the ordinary placement review. This is an engineering revision requiring fresh
placement review and downstream mating/routing/layout checks, not a cosmetic
exception or automatic approval. Independently review affected copper clearance,
board web, tolerance and fit. Downstream native/library exports must match the
reviewed geometry; recipe support alone does not adopt an existing routed board.
Courtyard bounds use the drawn boundary, excluding graphical stroke thickness;
component clearance already belongs in that boundary. True boundary overlap and
out-of-board geometry still fail. Drawing line width must not change acceptance.

`proximity` rows: {id,a:[ref,pin],b:[ref,pin],max_mm,reason}; measure native pad
centres (not a routed-length guarantee). `access` rows: {ref,point:[localx,y],
direction:[dx,dy],max_gap_mm,width_mm,depth_mm,reason}; point must face an edge,
ray to that edge stays clear of other bodies/mounts. `reservations` in PLAN
may describe route regions as {id,rect:[x1,y1,x2,y2],layer,owner_refs,reason};
check non-owner pads and incompatible same-layer reservations. These are
proposed routing space, not copper. The reviewer checks sufficient coverage.
Unknown input/geometry applicability must not be presented as a zero-row PASS.

## Independent review

One JSON block in a dated `08_reviews/*-placement.md`: schema1,
stage KICAD-PLACEMENT, distinct author/reviewer, verdict PASS or FAIL,
`inputs`, `plan`, `output` paths, `subjects` map of exact file SHA256s, and
`checks` mapping completeness,mechanical,electrical,routability,reproducibility,
applicability to {verdict,evidence:[bound paths],rationale}.
PASS must cover all required producer input/output subjects exposed by verify.
The coordinator issues the receipt, never the producer or reviewer alone.

The project `01_docs/placement-contract.json` binds phase authority, the
accepted schematic receipt, upstream toolchain archive and all archive file
hashes. Verify runs that exact archived verifier against current schematic
subjects, then checks new placement artifacts using current placement tools.
Old receipts are retained without replacement or review-hash rewriting.

## Version2 critical-route admission

New `issue`/`check` requires placement contract `version:2` with `critical_routes`
pointing to coordinator-owned JSON `{version:1, boards:{BOARD:{reason, duties}}}`.
Every board is present. Each duty has a unique `id`, `terminals:[{ref,pin},...]`
and nonempty `requirements` strings describing applicable current/drop, return,
timing, sensing or thermal obligations. Include cross-block/shared connections
affected by a proposed change, not just the moved components. The independent
reviewer owns scope sufficiency; no tool infers electrical intent from net names.

The review adds `critical_routes`, a trial manifest path:
`{version:1, boards:{BOARD:{native:{source,project}, duties:{ID:{verdict,evidence,rationale}}}}}`.
Bind the scope, trial, native board/project and all engineering evidence in the
ordinary review `subjects`. `source` is a separate native scratch trial, with the
same full placement/pad/net/outline identity as the placement under review.
Do not add copper to the placement producer or require a routing-stage receipt.
Explicitly empty duties require both the coordinator's applicability reason and
the review trial's `not_applicable_reason`; unknown applicability fails review.

`tools/critical_routes.py` replays refill/DRC with current native settings, rejects
physical faults, stale fills and unsupported solder-land bores, and walks physical
copper connectivity for all declared critical terminals. Unrouted noncritical
connections remain visible in native DRC but do not require completing the board.
Independent review must still establish actual electrical/thermal margins, return
quality, shared-copper preservation and adequate scope; connectivity is not those
proofs. Use the adopted native-authoring boundary for changes to existing copper.

New admission cannot downgrade to version1. Continue checking historical receipts
with their exact archived toolchain; adopt this upgrade explicitly, with new trial
evidence and independent review. It does not silently migrate a live project.

Current geometry support deliberately excludes bottom-side assembly, rotated
nonrectangular collision polygons, flex/rigid-flex, RF qualification and external
model/enclosure collision claims. Native footprint pads/net identity, geometric
checks and readable PCB plots are measured; feasible routing remains separately
reviewed. Unrouted pads at placement are expected, not final DRC acceptance.
