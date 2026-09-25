# Shared JTAG/reset linked-path scratch check (2026-09-25)

`build_linked.py` pins the expanded-locked, unrouted native board and its P1
inputs, copies the P1 source/floorplan/contract to one isolated scratch
candidate, then evaluates that candidate with `p1_corridor_capacity.py`. It
does not edit canonical Crow inputs. Reproduce with
`python3 build_linked.py --out /tmp/new-crow-reset-linked-scratch` from the
worktree root. The builder rejects checker drift from SHA-256
`c6609198e3daa5fc9718436194945f4cb0f39f4e9095ec991674479f798e7b46`;
the builder's own SHA-256 is
`69f064a7185accb2868926fc88fcb4fd0d03fd78d0751fe03e8b1a7f8d6611aa`.
The frozen board SHA-256 is
`fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16`;
the original source, floorplan, and contract pins are in the script. The
scratch source/floorplan/contract SHA-256 values are respectively
`8f619b1b4a532682cae81cf6471182f11662d274fb4e88be45fec3013b483300`,
`fd6f9149f2ffe2cecd86cbbf59d8510a33553fc0f34feaac076764f5ce272f62`,
and `6b8281cb6284d333a624cf9566803ef954d02ec18f790b2fdb6d2771fbcf555a`.

The first linked stage shares the exact ordinary `jtag_strip_trunk` physical
reservation with its four disjoint JTAG nets. Its J_JTAG.10 reset access is an
ordered two-segment envelope. The second stage spans the separate
digital-power/XMOS window, with U_XU.38 as the single interstage join. The
scratch declaration covers all five native XU_RESET_N terminals and requires
at least four connected tree edges; it has one P3 tree obligation. The checker
preserves the original four JTAG, six QSPI, and two XTAL reservations. The
audited first-stage rough receipt lists all five JTAG/reset nets, with 5
demand slots against 11 current rough slots; the reset power stage has 1
demand slot against 23 rough slots. This is one joint rough-capacity screen,
not duplicate credit for the shared host.

Replay result: overall `INCOMPLETE`, zero errors; `xmos_service_escape`
`INCOMPLETE`; linked reset `INCOMPLETE`. P2 pad-to-face and filled-reference
proofs remain owed for both stages, including U_XU.38 about 20 mm from the
JTAG-stage XMOS face. P3 native route/tree realization remains owed. The
rough counts are P1 structural evidence only, not admission or route proof.
Focused linked-path tests: 25/25 pass. The tests cover host identity and
geometry, disjoint nets and joint demand, branch declaration, terminal/tree
denominators, P2 and return obligations, and segmented access geometry.

The captured concise receipt is `linked-summary.json` in this directory
(SHA-256 `5fd498e74fd113911c4d673b689f33f6bf01df30f3cec5ec0f64baacb01f1733`).
The exact replay's full scratch receipt is
`/tmp/crow-reset-linked-shared-capture-sol/result.json`. These are research
evidence, not release receipts.
