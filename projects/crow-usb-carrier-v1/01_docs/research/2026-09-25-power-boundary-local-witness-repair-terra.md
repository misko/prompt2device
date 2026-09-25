# Isolated power-boundary local-witness repair packet, 2026-09-25

Status: **INCOMPLETE**. This packet proposes source/contract geometry only.
It supplies no copper, current, thermal, return, or route-capacity credit.

The exact TI board measured for this packet is
`06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project/04_kicad/crow_carrier.kicad_pcb`,
SHA-256 `8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
All listed pads are on `F.Cu` and have the declared nets. `J1.10` CHASSIS is
unchanged: it remains the one P1-fixed physical witness.

## Five expressible local replacements

The generic checker can express these five as `virtual_block_face` witnesses.
Each proposed witness lies within its owner source region and touches exactly
one face; its separate `power_or_mechanical` reservation lies in an unowned
gap and has no slot demand. Every row needs the shown exact P2 obligation.

| Net | Source / owner | local witness bbox | owner face | exterior reservation bbox |
| --- | --- | --- | --- | --- |
| GND | `C_ADC_3V3X_OK_VDD.2` / adc_reference | [75, 107.20, 75.50, 107.80] | west | [70, 107.20, 75, 107.80] |
| N12V_PROTECTED | `C_SPOKE_IN1.1` / analog_ch1 | [36.30, 83.50, 37.40, 84] | south | [36.30, 84, 37.40, 85] |
| N0V9 | `C_CORE_FF.1` / digital_power | [184.50, 116.50, 185, 117.30] | east | [185, 116.50, 190, 117.30] |
| N5V_LDO_HOLD | `C_ISO1.1` / analog_ch1 | [33.60, 83.50, 34.30, 84] | south | [33.60, 84, 34.30, 105] |
| PWR_EN | `U_ADC_PWR_BAD.2` / adc_reference | [75, 105.30, 75.50, 105.70] | west | [70, 105.30, 75, 105.70] |

For each row the contract witness must use `kind: virtual_block_face`, the
opposite outside-facing `face`, its local `region_id`, and this exact shape:

```yaml
p2_obligation:
  status: P2_REQUIRED
  source_pad: <source above>
  native_pad: <source above>
  net: <net above>
  block: <owner above>
  region_face: <owner face above>
  layer: F.Cu
  to_reservation: <new local reservation id>
```

`C_CORE_FF.1` was remeasured at [160.24, 116.59, 160.80, 117.21]; its old
box was stale. The local face witness intentionally does not pretend that this
pad itself lies on the face: P2 must prove pad-to-face access.

## Four handoffs the present schema cannot safely encode

`N1V8`, `N3V3X`, and `N3V3_ADC` need the adc_reference east face, immediately
adjacent to the digital_power region. `N5V_BUCK` needs the digital_power west
face, immediately adjacent to adc_reference. A generic exterior reservation
there would overlap the other source region, and `_virtual_region_clearance()`
correctly rejects it.

The existing `integration_corridors` model cannot be assigned to
`power_boundary_windows`: it requires `allocation_id` to name a row in source
`allocations` with a declared matching demand, whereas power boundary coverage
is a separate top-level source object. A `shared_transition_port` may be able
to model an explicitly designed, empty, jointly owned union zone, but it needs
the exact participant/endpoint/return contract and native foreign-obstacle
screen; none is currently source-declared. This is a deliberate schema gap,
not an excuse to draw another cross-region witness strip.

The safe source change is therefore two-phase: adopt only the five local rows
above after a hash-bound checker run, then add a power-specific integration
handoff schema or a fully specified shared transition port for the remaining
four. Keep all ten power nets in the denominator, preserve `INCOMPLETE`, and
require P2 pad-to-face/port, filled-return, current, and thermal evidence.
