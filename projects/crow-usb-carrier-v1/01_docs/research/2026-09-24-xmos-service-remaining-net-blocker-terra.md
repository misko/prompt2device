# Remaining XMOS-service nets after QSPI handoff

This is a bounded native/source audit of the regenerated QSPI-gap board
`fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27` and the
existing unified coarse candidate.  It does not change the 59-net denominator
or claim P1 acceptance.

With QSPI replaced by an exact 13-endpoint integration corridor, the first
remaining `xmos_service_escape` failure is `U_XU.51` (`JTAG_TCK`).  Its legacy
candidate witness `[215.405, 91, 221.02, 99.145]` is 8.145 mm tall, exceeding
the regenerated `xmos_core` local-span guard of 6.625 mm.  The checker
therefore rejects it as a nonlocal source-region bridge before it can become a
coarse handoff.  The companion JTAG/reset XU witnesses and XTAL XU witnesses
are likewise long bridges, rather than local source faces.

The `jtag_north` reservation `[221, 65, 226, 91]` also enters the regenerated
`xmos_core` cell (`[190, 84, 232, 110.5]`), so shrinking or relabelling the
old witness cannot make it a legitimate virtual handoff.  Native endpoints
confirm the actual external continuation: XU JTAG/reset pads are at
`x=216.1625`, `y=99.0..105.0` mm, while `J_JTAG` pads are at
`x=225.46..230.54`, `y=47.965` mm.

The bounded next repair is a separate source-owned JTAG handoff/corridor
model, beginning by resolving the overlapping `usb_frontend`
`[200,35,236,70]` and `debug_connector` `[218,35,238,65]` regions that cover
the JTAG continuation.  Until that ownership/region work supplies a
non-overlapping corridor and its own P2 pad/return obligations, retain all 13
`xmos_service_escape` nets and the allocation as **FAIL**.  Do not convert the
legacy bridge into a nominal local witness merely to obtain `INCOMPLETE`.
