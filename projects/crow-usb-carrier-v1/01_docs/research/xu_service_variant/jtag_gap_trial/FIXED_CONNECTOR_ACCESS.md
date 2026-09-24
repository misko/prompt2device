# Fixed connector access checker trial

The coarse checker now accepts a `fixed_connector_access` boundary witness for
an endpoint already listed in a source-owned `integration_corridors[].affected`
denominator. The ref must remain in `p1_fixed_refs`, with its native pose and
ref.pad/net identity validated as before. The witness boundary contains the
native copper pad on the named layer. It points to a separate single-net
`fixed_connector_access` reservation inside the connector's source region.
That rectangle must touch the physical pad boundary and the named corridor at
its declared source face; same-layer reservations cannot overlap it. The
source corridor's P2 pad-to-face and filled-return obligations remain exact.
Both reservations report `INCOMPLETE`, with no slot or route credit.

The existing JTAG trial illustrates why this is a useful schema distinction.
Its four `J_JTAG` terminals are P1-fixed, so a virtual
`integration_corridor_handoff` remains forbidden. Native `J_JTAG` pads 2, 4,
6, and 8 are at x ranges 230.17–230.91, 228.90–229.64, 227.63–228.37,
and 226.36–227.10 mm respectively, all at y 46.57–49.36 mm. The declared
`jtag_gap` starts at y=65 mm and spans x=221–226 mm. This work does not claim
four disjoint physical access rectangles from those pads to that gap; their
escape, effective clearance, intervening native objects, and filled return
have not been proven. The original `build_trial.py` and its fail-closed
receipt remain unchanged. A future source/contract trial can add four access
reservations using this schema without reclassifying the connector as movable.

The synthetic native fixture exercises one valid fixed endpoint and rejects a
movable ref, an incorrect physical pad box, a detached access rectangle, an
unknown corridor, and an overlapping reservation. The prior test requiring
fixed refs to be rejected from virtual integration handoffs still passes.

Validation: `python3 -m unittest skills/kicad-pcb/scripts/tests/test_p1_coarse_capacity.py`
passed 49 tests. No P1 acceptance, physical routing, native DRC, or board
change follows from this checker extension.
