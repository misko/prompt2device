# One scratch P1 reset reservation candidate — checker stop

**Result: FAIL, no P1 admission.** `build.py` made exactly one private
source/floorplan/contract candidate in
`/tmp/crow-reset-two-corridor-single-candidate-sol/`. The native board stayed
SHA-256 `fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16`.
The frozen inputs were P1 source `e8ff456de1868386890dbb5413bb20dc054b5d711b7c9b97d8b02a6b4695ae92`,
floorplan `8a805d92d4f57c3a0db00a45d1c9aef57958eb0c219d44f9ca89e5531021d8b4`,
contract `9faaed39333c0db45c188003d2ac6bacc69562f259f8332d0d6a79db7d25037f`,
modular plan `02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8`,
and aliases `a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e`.
The script asserts these digests before creating the scratch directory.

The candidate retained all **13 service nets**, including the same five
`XU_RESET_N` ref.pad identities, and changed only scratch planning data. It
added `J_JTAG.10` fixed access with the previously measured two 0.15-mm
segments, added reset as the fifth JTAG-strip net with exact connector/XU
endpoints and P2 obligations, and placed a disjoint one-net reset window
`[185,100,190,110.5]` between `digital_power` and `xmos_core`. It removed
the geometry-free reset reservation in the scratch copy so the two physical
reservations could be tested honestly. Scratch hashes: source
`309217715caf72145a26866a0fd218b46bce0df4ac00e7d1fcc65297b2d83d80`,
floorplan `fd6f9149f2ffe2cecd86cbbf59d8510a33553fc0f34feaac076764f5ce272f62`,
contract `79f5aff51c6d4636bdac7b12581927e2c21c507f63560b25b29708756f3320d6`.

The existing P1 checker accepted the scratch global source/region/native
integration-corridor construction far enough to evaluate allocation
witnesses. Its first service failure was
`R_XU_RST_PU.2: witness bbox is a nonlocal bridge across source region`;
the same independent diagnosis applies to `U_CORE_OK.1` and
`U_XU_3V3_OK.6`. Their 10.2-mm-tall digital-power face exceeds the
checker's one-quarter-local-span limit (34.16/4 = **8.54 mm**). This is a
specific source-face blocker, not evidence of native copper obstruction.

The checker also reports `jtag_strip: integration net double reservation
credit in xmos_service_escape` and twice the same error for
`reset_power_gap`. Its current integration-corridor contract forbids the
same reset net in the JTAG and digital-power physical reservations; the
fixed reset access adds another same-net reservation relative to the other
corridor. A narrower face alone therefore cannot admit the complete
five-terminal, two-corridor tree. A reviewed branch-aware source model or
checker representation is needed before another candidate. The reported
`integration affected endpoint/layer denominator mismatch` errors for
existing QSPI/XTAL/JTAG and reset follow the service allocation's early
abort; they are not new native-pad findings.

The exact [summary](summary.json) records overall `FAIL`, service `FAIL`,
the three locality diagnostics and seven global accounting errors. No route,
refill, current-rule DRC, P2 pad access, P3 connected reset tree, filled
return, or P1 receipt was produced. Stop here under the one-candidate bound.

To reproduce, choose a fresh scratch path (the script refuses an existing
directory):

```sh
/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-reset-two-corridor-schema-probe-sol/build.py --out /tmp/crow-reset-two-corridor-replay
```
