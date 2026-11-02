# Inspection inputs

JSON format version1: `label`, `connectors`, optional `model_notes`. Each connector
is keyed by native reference and contains `mpn`, `source`, `limitations`,
`expected_pads` (number to local XY; duplicate numbered module pads are allowed),
`expected_pegs` (unnumbered local XY list), `tolerance_mm`, `mouth_direction`
(local native XY), `intended_direction` (absolute native XY), and `solids`.
Use enough asymmetrical independent pin/peg witnesses to constrain orientation;
listing only a body center is inadequate. Sources must identify maker/revision
and drawing view. Intent must come from the brief/mechanical requirement, not
be copied from the calculated direction just to obtain PASS.

Coordinates are mm, footprint local X right / Y down / Z above PCB top. Angles
come ONLY from the actual native footprint, and are converted once into the
right-handed render frame X,-Y,Z. Bottom-side connector models are currently
unsupported and fail explicitly. General bottom-side envelopes remain shown.

Solids are drawing-derived inspection shapes, not exact manufacturer models:

- `box`: `bounds: [xmin,ymin,zmin,xmax,ymax,zmax]`.
- `cylinder`: `base: [x,y,z]`, `axis: [x,y,z]`, `radius`, `length`.
- Either may have `cuts` (primitive shapes subtracted), and `color: [r,g,b]`.
- Optional `tag` labels a primitive's purpose, e.g. housing, contact, peg, mouth.

Nominal housings/pins/pegs must be distinguished from illustrative mouth cavities
and latch details. Without verified private cavity dimensions, do not claim plug
fit from them. `expected_pads` checks coordinate witnesses only, not electrical
connectivity or finished hole/slot shape. Include explicit limitations in the
connector entry and investigate mismatches rather than expanding tolerance.

Non-overridden populated components are marked `unqualified_footprint_envelope`:
their XY bounds come from native F.Fab or pad geometry, with illustrative1mm
height. They are never clearance evidence. `missing_connector_reviews` lists
unreviewed native J/P references; module connectors must be declared explicitly.
TP/test pads are not automatically sockets. Review the inventory for other
non-J/P devices containing connectors before claiming completeness.

The output binds native board, inspection JSON, helper/extractor/kernel code
and each PNG, and records camera vectors. Any source change requires a new
output folder. Do not change hash-bound release manifests to attach previews.
