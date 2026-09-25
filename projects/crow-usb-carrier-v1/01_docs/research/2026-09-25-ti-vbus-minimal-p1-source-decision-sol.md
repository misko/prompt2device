# Minimal honest P1 source model for TI-board VBUS_USB

**Decision: declare one unresolved VBUS tree, without a VBUS corridor or
capacity claim.** This is a research recommendation for the exact unrouted TI
board SHA-256 `8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
It changes no canonical source, board or checker. The existing
`unresolved_multiterminal_branches` schema already carries the needed
fail-closed debt; no new generic branch DSL is needed to record it.

The smallest source/contract delta would keep the present three modular
owners and all eight `VBUS_USB` endpoints. Declare a VBUS branch with exact
`source_pad/native_pad/net/block` rows, `terminal_count: 8`,
`minimum_tree_edges: 7`, one P2 native-pad-to-tree obligation per row, an In1.Cu
filled-return obligation, and a P3 connected-tree obligation. Set
`capacity_slots: null`, provide no bbox, and use one representative physical
pad witness (for example `J_USB.2 → J_USB.A4`) plus one geometry-free branch
reservation. Remove both old `vbus_entry` and `vbus_sense_entry` VBUS witnesses
and reservations so there is no second capacity claim. Keep the independent
DP/DN linked path and `VBUS_PRESENT_N` accounting separate. Alias authority
remains `J_USB.2→A4`, `J_USB.15→B9`, `J_USB.10→B4`, `J_USB.7→A9`.

An in-memory call to `_unresolved_branches` on that exact board accepted the
eight source/native terminals, their three owners, the empty source-region
blocker list, P2 obligations, filled return, and P3 tree lower bound (**8/8**).
This validates the debt declaration only. A temporary whole-packet attempt
still failed: the current DP/DN source copy declares one raw slot for two
nets, below the updated checker minimum, and after that scratch value was
raised to two the unrelated `Q_VBUS.3` movable-pad witness stopped the USB
allocation. The consequent branch representative denominator error is a
linked effect of that allocation abort, not a VBUS branch pass. P1 remains
failed/incomplete.

`shared_transition_ports` can name the exact endpoints and a P2 return debt,
but its single empty port/reservation does not prove two physical launch sites,
a tree, VBUS current capacity, or access from the four connector aliases.
Its union also cannot overlap the already declared DP/DN integration corridor.
`physical_cells` partitions whole footprint refs; it cannot split `J_USB`
between A4/B9 and B4/A9. It also requires full native footprint containment,
while J_USB's body/courtyard projects beyond the board edge. Neither feature
turns the present VBUS launches into a valid positive P1 corridor.

For a later *geometric* VBUS claim, source/checker authority would need a
small fused-pad-site declaration: preserve four logical aliases, bind A4/B9
and B4/A9 to their two exact coincident native pad boxes, permit one shared
same-net access per site, and require a connected power tree with current,
width, fault and return evidence. The allocation must also account for both
the DP/DN path and VBUS tree without duplicate credit. On the current board,
the proposed `[227,28,233,29]` edge corridor/front face intersects native
`U_USB_CC_ESD` (body `[232.075,29.01,234.525,31.195]` mm). A physical
candidate would first have to move that body clear of the x=227.1–232.9,
y=29–29.2 face, or establish a different source-owned route topology; a
southward shift greater than 0.19 mm clears this one body/face intersection
mathematically but does not prove neighbor clearance, CC protection routing,
connector access or a filled return. No placement move is authorized by this
note.
