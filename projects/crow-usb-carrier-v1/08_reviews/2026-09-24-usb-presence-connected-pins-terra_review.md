# Independent review: generic seed `connected_pins`

**Verdict: sound generic all-terminal binding for the isolated USB research
replay.** I reviewed SOL `1554b0fe` and replayed the isolated Q_VBUS-moved
Crow input with the declared `VBUS_PRESENT_N` set
`[R_VBUS_PU.2, Q_VBUS.3, U_XU.8]`. `prep` served 9 banks, placed 33
primitives, refused none, and produced r0 SHA-256
`88496643cd29fce51e995997c828546f890d82a23f68744d9dc8a29896e82909`, the
same byte-identical result as the prior reviewed replay.

The implementation is fail-closed. A claim must be a nonempty unique
`REF.PAD` list including the bank `pin`; every identity resolves to an
existing footprint pad and every resolved pad must be on the bank net. After
all banks emit, native `BuildConnectivity` requires every target pad UUID in
the source pin's component. Deferring that check until the end correctly
allows a later same-net bank to finish the component while still rejecting an
unconnected target.

`python3 tests/t2_route_stitch.py --only='seed_stubs (bonds|is IDEMPOTENT|connected_pins)'`
passed all seven focused tests, including the three existing negative fixtures
for absent target, wrong net, and disconnected target. Additional isolated
hostile probes confirmed refusal of a duplicate claim identity, missing source
pin, malformed identity, and an unconnected second physical pad bearing the
same `U2.1` number; resolving all native pads with that number makes the last
case fail rather than silently choosing one. A legacy bank without
`connected_pins` still passed, preserving old recipes.

This check is an exact local-copper contract, and the USB research YAML
remains isolated. It does not alter a canonical Crow route or establish P1 or
P3 acceptance.
