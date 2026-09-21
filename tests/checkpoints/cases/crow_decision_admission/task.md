# Admit settled Crow design decisions before placement and routing

Continue from this synthetic Crow-inspired coupon. It preserves three failure
classes from retrospective anchors R04-R07, R11, and R20: a connector migration
left a retired physical pad anchor, U1 is required to be machine assembled but
has no machine owner, and
the current `MCH_INPUT_SECTIONS` declaration relaxed an independently reviewed
`no_vias: true` constraint. The coupon is not the complete historical board and
does not establish production readiness or incident cost.

Repair the authoritative editable sources. Generate the current Circuit JSON
from `03_tscircuit/src/components.json` with:

```bash
/usr/bin/python3 build_circuit.py
```

Then run the native design-decision admission command from `START.md`, using
the current route/nets sources and both independent reviewed snapshots under
`03_src/reviews/`. Preserve the reviewed snapshots and the native board. Do not
delete the protected group, loosen its membership, replace machine ownership
with manual fitting or silence, broaden the adopted top-only SMD policy, or edit
generated evidence to claim success. This reduced case independently requires
U1 to resolve to exact machine placement and all fitted SMD to remain top-side;
those Crow-specific facts do not create a universal ban on manual SMD projects.

Record the repair and exact admission result in `HANDOFF.md`. A passing result
only admits these pre-placement decisions. The grader runs a disposable route
command recorder after admission; it must remain absent whenever admission
fails and does not mean routing or the board is complete.
