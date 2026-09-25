# XTAL + QSPI + fixed JTAG source packet — reset is next blocker

**Research-only result: FAIL, no P1 or P2 admission.** This packet combines
the hash-pinned XTAL physical-cell packet with the reviewed four-net segmented
JTAG access packet on the same native board. The four fixed `J_JTAG` pads stay
at the reviewed connector pose `(228,50,90)`. Source validation accepts all
three disjoint integration corridors (`qspi_gap`, `xtal_south_cap`,
`jtag_strip`), and direct native checks accept all eight exact JTAG witnesses.
The whole 59-net contract advances beyond the former `U_XU.51` JTAG failure
and stops at the unchanged reset witness:

`U_XU.38: witness bbox is a nonlocal bridge across source region`

The QSPI, XTAL and JTAG `integration affected endpoint/layer denominator
mismatch` errors follow from this allocation abort. They do not indicate that
their source-declared endpoint sets are missing. The USB allocation is also
`INCOMPLETE`: shrinking `usb_frontend` to give the fixed JTAG connector its
own source region exposes `J_USB.4: witness bbox is a nonlocal bridge across
source region`. These are the next independently visible source-model debts;
this packet does not repair reset or USB.

The JTAG strip is `[221,65,226,84]` mm on F.Cu. The fixed connector keeps
its four exact native pads and ordered segmented access chains from the
reviewed [JTAG packet](../../jtag_segmented_packet/README.md):

| Net | Fixed pad | XU pad |
| --- | --- | --- |
| `JTAG_TMS` | `J_JTAG.2` | `U_XU.44` |
| `JTAG_TCK` | `J_JTAG.4` | `U_XU.51` |
| `JTAG_TDO` | `J_JTAG.6` | `U_XU.37` |
| `JTAG_TDI` | `J_JTAG.8` | `U_XU.36` |

The XU north face is `[221.1,84,223.9,84.3]` mm, bound to the existing
`xmos_core_east` physical cell while each XU pad's modular endpoint owner
remains `xmos_core`. The face's 2.8 mm raw span exceeds the four-net 1.8 mm
source demand, without proving effective capacity. The other two XU physical
cells, retained `C_XU_VDDIO_35` pose, QSPI and XTAL geometry, all 29 XU-owned
refs, and seven XTAL endpoint owners remain as in the pinned XTAL packet.
The JTAG source carries exactly eight `P2_REQUIRED` pad-to-face obligations
and a separate filled `In1.Cu` GND-return obligation. No checker capacity
credit, physical copper route, filled return, DRC, connector service or
crystal performance is established.

The full allocation statuses are:

| Allocation | Status | First checker reason |
| --- | --- | --- |
| `usb_device_pair` | INCOMPLETE | `J_USB.4` nonlocal bridge |
| `xmos_service_escape` | FAIL | `U_XU.38` nonlocal reset bridge |
| `adc_timing_xmos_bundle` | INCOMPLETE | `U_ADC_A.22` needs virtual P2 face |
| `adc_analog_boundary` | INCOMPLETE | `C_ADC_AC1N1.2` nonlocal bridge |
| `power_boundary_windows` | INCOMPLETE | `C_ADC_3V3X_OK_VDD.2` nonlocal bridge |

From this worktree root, reproduce with KiCad 10 `pcbnew` and PyYAML:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/xu_service_variant/p1_xtal_jtag_packet/build_packet.py
```

The builder pins both parent source/floorplan/contracts, the native board,
modular plan, alias part, and checker SHA-256; it demands the exact FAIL
outcome. [validation.json](validation.json) records the full input/output
digests and all allocation results.

| Generated artifact | SHA-256 |
| --- | --- |
| `p1_source_xtal_jtag.yaml` | `265d6c710d76769814ae61feeacbbf1a2eb54c5289190859180114420ca0364e` |
| `floorplan_xtal_jtag.yaml` | `31558a45a34a2817cb3211a55d5bcf8dc2e866b63d7e0e6f933f548d64da624b` |
| `coarse_xtal_jtag.json` | `8b0460ea93b6d5a0dfbde2a7a17b491eb118ccae905dbaf96d905f5cb539bf3c` |

No canonical source or board, governed task state, P1 attempt or release
artifact was changed.
