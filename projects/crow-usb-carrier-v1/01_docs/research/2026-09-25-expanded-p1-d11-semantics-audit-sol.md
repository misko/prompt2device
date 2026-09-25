# Expanded-board P1 coarse result versus D11 — read-only audit

Subject: expanded-locked private 7628G board
`fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16`,
the complete `2026-09-25-ti-expanded-locked-p1-sol/result.json`, and accepted
[D11](../decisions/0011-p1-floorplan-and-p2-placement-admission.md). No
board, source, contract or checker was changed. The result is `INCOMPLETE`,
five of five allocations `INCOMPLETE`, zero global errors and zero independent
diagnostics, with `routing_realized=false` and `p1_accepted=false`.

D11's P1 test is **fixed anchors, outline/regions/service axes, reserved
corridors and capacity, pin/net parity, native P1-class defects, and
fitted-body/courtyard/model coverage**. It explicitly assigns local-placement
gaps to P2 and does not require a routed board as P1 proof. The current
schema-2 checker deliberately does not implement that engineering acceptance:
its `p1_corridor_capacity.py` header says it cannot accept P1 alone; each
unresolved branch and integration reservation is emitted `INCOMPLETE`, the
allocation row is always `FAIL` or `INCOMPLETE` (never PASS), and its final
result hardcodes `routing_realized: false`, `p1_accepted: false`. The copied
`p1_requirements.yaml` also requires `p1_accepted_must_remain_false: true`.
No floorplan edit, or even adding copper, can make this coarse evaluator
issue P1 acceptance. The five labels must be read as conservative debt,
not five independently proved floorplan failures.

| Allocation | P1 floorplan admission still owed | Properly deferred P2/P3 evidence |
| --- | --- | --- |
| `usb_device_pair` | Exact `USB_DP/DN` linked stages have rough slots 2/2 at `usb_edge_access` and 3/2 at `usb_frontend_xmos`, but effective 7628G 0.410/0.150-mm launch fit at 0.4-mm XU.59/.60 pitch and the complete connector/ESD path remain unproved. `VBUS_USB` and `VBUS_PRESENT_N` have exact branch endpoints but no physical capacity reservation. The unqualified D15 3313A screen cannot fill this gap. | Final pad fan, route topology, impedance/skew, filled In1.Cu return and the 8-terminal VBUS/3-terminal presence trees. |
| `xmos_service_escape` | Source names JTAG trunk `[221,65,226,84]`, four segmented J_JTAG accesses, QSPI gap `[219.2,110.5,223.2,118.5]` and XTAL handoff `[217.2,107,218.95,110.5]`. They pass topology/geometry checks but have no effective six-QSPI/four-JTAG/two-XTAL capacity lower bound; five-terminal `XU_RESET_N` has no physical reservation. An independent capacity/ownership review is still P1 work. | Native pad-to-face access, local oscillator/reset placement, connected nets and filled reference under realized routes. |
| `adc_timing_xmos_bundle` | All 14 nets/54 terminals are exact, including four two-terminal crossings and 11-terminal `AUDIO_EN`, but all 14 reservations are geometry-free unresolved branches. The direct TDM/XU west band previously measured only three 0.45-mm slots for four nets; an alternate `[188,94,190,99.84]` neck measured five raw slots but lacks typed ownership/admission. The P1 four-net corridor capacity remains unproved. | Five source-region conflicts on movable audio/quiet-power pads (`R_ADC_DATA_PD.1`, `R_ADC_I2C_SCL_A_PU.1`, `R_ADC_I2C_SDA_A_PU.1`, `U_ADC_CLOCK_OK.1`, plus `R_AUDIO_PD.1`, `R_AUDIO_PU.2`, `U_AUDIO.6`) are measured P2 placement debt unless they foreclose the selected corridor. Complete trees, endpoint access and filled return are P2/P3. |
| `adc_analog_boundary` | Eighteen exact analog/VMID branches are geometry-free, so no N/P corridor-capacity lower bound is established. The ADC7 access-only portal `[166,83.9,167.12,85]` is deliberately null-capacity; channel 8 lacks an exclusive north-face interval in the documented bounded search. A P1 floorplan must reserve feasible channel 7/8 handoffs or independently justify a different corridor. | Local cap/ADC pad-to-face access, P-ADJ budgets, VMID tree routing and filled reference under the actual analog routes. |
| `power_boundary_windows` | All ten named windows are geometrically preserved (nine electrical power/enable windows plus CHASSIS), but their reported reason is `current, return, thermal, or mechanical capacity unmeasured`. P1 needs a bounded current/thermal/mechanical reservation rationale and fixed-hole/connector-envelope review, not a completed rail route. | Detailed copper/IR/thermal/return realization, via/trace sizing and final fixture reaction after local placement. |

The expanded board's native DRC is zero violations with 499 unrouted items;
count parity is 569/569 and pin-map parity covers 799 physical identities.
Those are useful P1 inputs. The packet's original DRC did **not** perform
schematic parity; the later hash-pinned native parity probe did perform it
with zero issues on the same frozen board. The result still lacks an
independent D11 capacity/model/connector-neighbor admission review, so no P1
claim follows from a clean coarse result.

**Smallest governance path:** retain the no-credit coarse source/checker
unchanged and add a separate, exact-board, independently reviewed D11 P1
engineering admission receipt only after the listed true P1 capacity and
coverage gaps have evidence. It should explicitly carry the measured P2/P3
debts forward rather than trying to turn every coarse reservation into PASS.
This is a new decision/receipt, not an `INCOMPLETE` relabel. Moreover D11
independently requires connector FULL before **any** route preparation/import
or routing, and D13/D14 restrict the present TI diagnostic. To conduct a
private USB route experiment before FULL/P1 admission, the narrow
[draft exception](2026-09-25-private-usb-route-experiment-decision-draft-sol.md)
would require an explicit new accepted project decision and independent
preflight; D11's existing authorization does not allow it.
