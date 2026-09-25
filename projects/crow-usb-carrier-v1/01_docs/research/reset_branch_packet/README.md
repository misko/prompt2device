# Crow XU_RESET_N five-terminal branch declaration

**Disposition: reset source declaration `INCOMPLETE`; whole 59-net packet
`FAIL` at the next crystal witness.** This research packet extends the
fixed-pose JTAG packet on the unchanged QSPI-gap board SHA-256
`fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27`.
No canonical source, board, route, or acceptance state changes.

`XU_RESET_N` has five exact F.Cu terminals under three owners:

| Owner | Native terminal |
| --- | --- |
| `debug_connector` | `J_JTAG.10` |
| `digital_power` | `R_XU_RST_PU.2`, `U_CORE_OK.1`, `U_XU_3V3_OK.6` |
| `xmos_core` | `U_XU.38` |

The source-owned `unresolved_multiterminal_branches` record binds those five
source/native endpoints, five P2 native-pad-to-tree obligations, a minimum
four-edge connected-tree obligation for P3, and a separate P2 continuous
filled-GND-reference obligation on `In1.Cu`. It chooses **no tee, edge order,
trace, corridor, via, or area reservation**. The checker verifies the exact
interface denominator, net/layer, native pad identity and owner-region
containment. Its only `U_XU.38` witness uses that physical pad's exact bbox,
replacing the former nonlocal bbox `[215.405,91,221.02,104.345]` mm. The
matching `reset_unresolved_tree` record has no `bbox`, segments, pitch,
slots, or capacity credit. Source and contract hashes are in
[result.json](result.json).

The native pad bboxes reveal a separate source-region blocker. Both
`R_XU_RST_PU.2` and `U_XU_3V3_OK.6` lie inside `digital_power` **and**
`audio_clock_tdm`; `U_CORE_OK.1` lies only in `digital_power`. The checker
requires this exact foreign-region inventory in the declaration and reports
it on the unresolved reservation. This does not authorize shared ownership.
The physical regions need repair before P1 acceptance, and the actual branch
route, pad escape, four JTAG-lane coexistence, GND return, and DRC need later
native proof. The candidate board has zero reset tracks/vias and an unfilled
F.Cu GND-zone outline. It supplies no filled-return proof.

The full 59-net denominator remains: USB 4, XMOS service 13, ADC timing 15,
ADC analog 17, and power boundary 10. The generic checker withholds capacity
and P1/P2/P3 credit for `unresolved_multiterminal_branch`. After the reset
witness is replaced, the whole allocation reaches the existing nonlocal
`U_XU.34` crystal witness and fails there. The QSPI, JTAG, and reset endpoint
denominator errors are consequences of that allocation abort; they are not
claims that the named reset terminals are absent. `XTAL_IN`/`XTAL_OUT` remain
an independent source-cell and return problem.

Reproduce from the repository root with KiCad 10 `pcbnew` and PyYAML:

```sh
/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/reset_branch_packet/build_packet.py
/usr/bin/python3 -m unittest skills/kicad-pcb/scripts/tests/test_p1_coarse_capacity.py
```

The builder pins the JTAG packet, board, modular plan, alias part and checker
hashes. It writes only this research directory. The corrected checker adds a
generic fail-closed unresolved-branch record, with synthetic tests for the
exact terminal count, four-edge lower bound, blocker inventory and prohibition
of invented geometry.
