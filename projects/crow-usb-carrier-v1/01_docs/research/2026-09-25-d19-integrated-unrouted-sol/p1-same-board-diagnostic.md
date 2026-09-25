# D19 exact-board P1 coarse diagnostic — independently reviewed

**Terra reviewed the exact board, source, rule, contract and result hashes and passed this as diagnostic-only evidence on 2026-09-25.** All five allocations are `INCOMPLETE` with zero checker errors or diagnostics. No P1/P2 or route credit follows.

The unchanged D19 board SHA-256 is `ffb51cc31c5b1b0caada7e360c727848a1117b9cd94f6160fde2ca18ceb8625f`; generated `.kicad_pro` and `.kicad_dru` are `2d0bf4d9c14fedee82e1ba22f06d05a4ba97e7b7fe39a66e086ec1c48b408c1a` and `32a4dbacf8b1b2b8be93aa0a8308de483f183344bed98f42209ed62f82920992`. The [replay script](p1_same_board_diagnostic.py), SHA-256 `09e23aa7479fbe83fdc4ab3a9eeec1d97660407abee9c9e4298fe61761b12717`, bound those outputs to the 3313A native floorplan `71293463b6470d209997f6e6d97ec34962c239fb501ee45f7346c547a05e108a` and rules source `80681405a4a4692896bb9cf355d36e348bc482cb5658dad264a6f564eb4ba37a`. The linked five-terminal reset P1 requirements are `8f619b1b4a532682cae81cf6471182f11662d274fb4e88be45fec3013b483300`, with C105 and 3313A matched P1 floorplan `57388e5079f53a70d070fb074ce60bf8292e8512204bce2f3f3f4ce25105464c`. The generated project/rule hashes and current checker `c6609198e3daa5fc9718436194945f4cb0f39f4e9095ec991674479f798e7b46` are fixed inputs, not inferred acceptance.

One newly rebound, exact-board [coarse contract](../../06_build/prototype_board_diagnostic/d19-p1-coarse-diagnostic-20260925/coarse.json) is SHA-256 `c70591086ad77f1c2ed915b231bf55a7293dab1118fda19d5a9743249849ed3f`. Its [full result](../../06_build/prototype_board_diagnostic/d19-p1-coarse-diagnostic-20260925/full_result.json) is SHA-256 `cce8e5cee3c091b7a2a72f719acdb0a071818764121437032c68f92dcdec3d37`; the [summary](../../06_build/prototype_board_diagnostic/d19-p1-coarse-diagnostic-20260925/summary.json) is `6aa5ba2e5202be9d3b20128b79b90ccfe316e94d08d440768291b10c760f7b0c`. All five allocations are `INCOMPLETE` with zero checker errors or diagnostics:

| Allocation | Coarse status | Remaining physical obligation |
| --- | --- | --- |
| `usb_device_pair` | `INCOMPLETE` | USB edge and frontend-to-XU stages have only rough 2/2 and 3/2 slot counts; four-leaf merge, ESD tap, pad entrances and In1.Cu return remain unproved. |
| `xmos_service_escape` | `INCOMPLETE` | Shared four-JTAG-plus-reset stage has rough 11/5 slots; the five exact reset terminals, U_XU.38 handoff, P2 pad access and filled return remain unproved. |
| `adc_timing_xmos_bundle` | `INCOMPLETE` | All 14 timing reservations and 54 nested P2 pad duties remain; C105's moved pose does not prove connected timing paths or return. |
| `adc_analog_boundary` | `INCOMPLETE` | 18 reservations and 88 nested P2 pad duties remain unproved. |
| `power_boundary_windows` | `INCOMPLETE` | Current, return, thermal and mechanical capacity remain unmeasured, with 9 top-level P2 duties. |

This is a read-only, schema-2 coarse screen on the **same generated D19 board**. It offers no P1/P2 admission, no D18 routing and no change to D19's historical `FAILED_RESEARCH` receipt. Connector FULL, prototype-only TI ESD, production stack, fabrication, release and order holds remain.
