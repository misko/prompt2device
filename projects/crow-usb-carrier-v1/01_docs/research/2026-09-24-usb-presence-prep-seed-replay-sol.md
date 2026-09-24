# Isolated `prep.seed_stubs` replay of the USB presence route

**Result: the existing emitter reproduces the reviewed disposable route; P1/P3
remain unaccepted.** This test used the isolated Q_VBUS-moved source board,
SHA-256 `60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17`,
and a copied `route.yaml`. The only recipe addition is the three banks in
[the research YAML](2026-09-24-usb-presence-prep-seeds-sol.yaml). The canonical
board, floorplan, and route file were untouched.

After `generate_rules_generic.py` restored the source netclasses and DRU on
the copied board, full `route_and_stitch_generic.py prep` passed the critical
USB-pair preflight and its collision-refusing emitter. It served **9/9** banks
(the six existing PLL banks plus three presence/return banks), placed **33/33**
primitives and vias, and refused zero. The prepared r0 board SHA-256 is
`88496643cd29fce51e995997c828546f890d82a23f68744d9dc8a29896e82909`.
Native `net/layer/endpoints/width/drill` signatures of all nine
VBUS_PRESENT_N primitives and all six new GND primitives match the prior
[hand-built probe](2026-09-24-usb-presence-south-pad-route-probe-sol.md)
exactly. The other eight GND primitives belong to the existing PLL seeds.

With the strict source `.kicad_pro`/`.kicad_dru` beside the board, the
unfilled source has 54 DRC violations (40 clearance, 14 dangling vias); the
prepared board has 60 (the same 40 clearance plus six dangling GND vias from
the existing PLL seeds and the two new return seeds). On saved filled copies,
both source and prepared boards have **40** violations, all pre-existing
clearances, with no new short, clearance, width, or dangling-via finding.
KiCad native connectivity places R_VBUS_PU.2, Q_VBUS.3, and U_XU.8 in one
component on the prepared board; the saved filled board's two presence return
via centers and B.Cu trunk midpoint lie in the same In1.Cu GND polygon.
The prepared board still has many other unconnected nets. This is repeatable
local copper and return geometry, not allocation-wide P1/P3 proof.

The optional generic `connected_pins` seed-bank check now closes the
all-terminal replay gap identified by the independent review. The isolated
VBUS_PRESENT_N bank declares `[R_VBUS_PU.2, Q_VBUS.3, U_XU.8]`; after all
banks emit, the shared checker requires each exact pad to exist on the bank
net and to lie in KiCad's connected component of `R_VBUS_PU.2`. The updated
isolated recipe passed full prep again with 9/9 banks, 33/33 primitives, and
zero collision refusals. Its r0 board SHA-256 stayed
`88496643cd29fce51e995997c828546f890d82a23f68744d9dc8a29896e82909`.
Generic positive and missing-pad, wrong-net, and disconnected-pad fixtures
pass; existing seed recipes without `connected_pins` retain their behavior.

Reproduction on the isolated Q_VBUS source board, with the same repository
checkout and collision checks enabled:

```bash
REPO=/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922
SOURCE=/tmp/crow-presence-B5uZxt/project
PROBE=$(mktemp -d /tmp/crow-presence-seed-replay.XXXXXX)
cp -a "$SOURCE/03_src" "$SOURCE/04_kicad" "$PROBE/"
mkdir -p "$PROBE/02_parts/TMUX4827YBHR"
cp "$SOURCE/02_parts/TMUX4827YBHR/part.yaml" "$PROBE/02_parts/TMUX4827YBHR/"
cp -a "$SOURCE/02_parts/TMUX4827YBHR/qualification" "$PROBE/02_parts/TMUX4827YBHR/"
python3 - "$PROBE/03_src/route.yaml" "$REPO/projects/crow-usb-carrier-v1/01_docs/research/2026-09-24-usb-presence-prep-seeds-sol.yaml" <<'PY'
import pathlib, sys, yaml
route_path, recipe_path = map(pathlib.Path, sys.argv[1:])
route = yaml.safe_load(route_path.read_text())
recipe = yaml.safe_load(recipe_path.read_text())
route['prep']['seed_stubs']['stubs'].extend(recipe['stubs'])
route_path.write_text(yaml.safe_dump(route, sort_keys=False))
PY
python3 "$REPO/skills/kicad-pcb/scripts/generate_rules_generic.py" "$PROBE"
python3 "$REPO/skills/kicad-pcb/scripts/route_and_stitch_generic.py" prep "$PROBE/03_src/route.yaml" --root "$PROBE"
```

The preflight requires the source board to be segment-free and carries its 14
source vias forward. The emitter checks exact source-pad/net ownership and
every authored segment/via against foreign copper; the command does not
bypass either check. Route prep deliberately relaxes some fabrication floors
on r0 for the later router, so the strict DRC comparison above used copied
source rules rather than r0's temporary rule files.
