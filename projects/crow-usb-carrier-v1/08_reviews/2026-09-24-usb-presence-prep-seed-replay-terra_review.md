# Independent review: USB presence `prep.seed_stubs` replay

**Verdict: reproducible isolated P2/P3 research input; not promotable from
this record alone.** I replayed SOL `204cf514` from the retained isolated
Q_VBUS-moved source in a fresh temporary project. The source board SHA-256 is
`60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17`; replay
served 9 banks, placed 33 primitives, refused none, and produced r0 SHA-256
`88496643cd29fce51e995997c828546f890d82a23f68744d9dc8a29896e82909`, exactly
matching the retained prepared board.

Native records establish that this is the reviewed route rather than a merely
similar connection. All nine `VBUS_PRESENT_N` primitives agree exactly with
the prior hand-built probe in net, layer, unordered endpoints, width, and via
drill: six F.Cu segments, one 37.200437-mm B.Cu segment, and the 0.60/0.30-mm
vias at `(214.5,74.5)` and `(204.75,110.4)`. The two GND return vias and their
attached stubs at `(215.5,75.6)` and `(203.85,110.4)` also agree. After
`BuildConnectivity`, each of `R_VBUS_PU.2`, `Q_VBUS.3`, and `U_XU.8` has the
same three-pad component: `{Q_VBUS.3, R_VBUS_PU.2, U_XU.8}`.

The retained strict source-rule boards reproduce their recorded native DRC
comparison under a fresh `kicad-cli pcb drc --severity-all`: unfilled source
is 54 rows (40 clearance, 14 dangling vias), replay is 60 (the same 40 plus
20 dangling vias), and the saved filled source and replay boards are both 40
clearance rows. Thus the replay adds no filled DRC category or count. The
unfilled six-dangling delta is expected: four carried PLL-seed returns and the
two presence-return vias become connected only when the GND plane is filled.

The emitter has adequate collision and supplied-pin binding for this replay:
it checks each bank's declared `pin` belongs to its declared net, refuses
foreign-copper collisions for every segment/via, and verifies that copper
reaches that declared pad. It does **not** declare or verify target pads beyond
that one `pin`. In particular, the VBUS bank names `R_VBUS_PU.2`; its contacts
to `Q_VBUS.3` and `U_XU.8` are proven here by board connectivity and geometry,
not by the seed schema. That is not a replay defect, but it bars controlled
promotion of this research YAML by itself. A future owned source change needs
the seed bank in canonical `03_src/route.yaml`, an explicit all-terminal
`{R_VBUS_PU.2,Q_VBUS.3,U_XU.8}` contract check, and the strict source-rule/
filled-plane receipt bound to the candidate board. No canonical board, P1, or
P3 state is promoted by this review.
