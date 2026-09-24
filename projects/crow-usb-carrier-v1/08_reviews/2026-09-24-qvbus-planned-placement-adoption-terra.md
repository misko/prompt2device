# Q_VBUS planned-placement adoption review

**Verdict: accepted as source-only, unaccepted P2-movable placement intent.**

The canonical floorplan adds only `Q_VBUS: [212.0, 74.5, 0]` to
`placement.post_anchors`; the canonical `03_src/route.yaml` is byte-unchanged.
The comment correctly prevents a placement-acceptance interpretation.

`Q_VBUS` belongs to `usb_vbus_sense` and is absent from the 27
`p1_fixed_refs`.  This conforms to `p1_corridor_requirements.yaml`, which
reserves P1 immutability for the connector/hold-bank set and leaves other
anchored electronics P2-movable.  The current graph is unchanged: both
`p2_usb_service` and `p2_digital_power_core` remain downstream of the active
P1 root, while `p3_usb_pair` additionally requires `connector_full`.

SOL's isolated source-only generation reports one moved footprint (`Q_VBUS`),
with the remaining 568 poses, all 1,872 `(ref,pad,net)` identities, 14 source
vias, and all 27 fixed poses unchanged.  Its saved filled native receipt is
0 DRC violations, 499 unrouted items, and zero schematic-parity mismatch.
Those findings support the planned pose but are not a P1/P2/P3 acceptance or
route result.

All pre-adoption board hashes and board-bound capacity/placement receipts are
historical for this floorplan.  A future frozen candidate must regenerate the
board and rebind its fixed-ref, native DRC/parity, model/courtyard, and coarse
P1 receipts to the post-save board SHA.  No task was dispatched or consumed by
this source-only edit.
