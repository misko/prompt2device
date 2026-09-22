# USB realized-copper net-contract repair — 2026-09-22

`03_src/rules/nets.yaml` now owns one `USB_DEVICE` realized-copper group with
`max_spread_mm: 1.0` and `no_vias: true`. It preserves the accepted routing
geometry authority in `rf.yaml` and `route.yaml`; it adds no conductor, board,
placement, or fabricated-impedance claim.

ADR 0008 explicitly adopts the complete three-path ceiling and the F.Cu-only,
continuous-In1.Cu, no-signal-via policy. ADR 0002 remains the endpoint and
power-boundary decision; it is no longer cited as the source of these SI rules.

The member nets are ordered P/N members `USB_DP` and `USB_DN`, each modeled as
a tree. A chain would be false because each net contains two reversible Type-C
contacts plus the signal pin of a shunt ESD clamp. The TPD2EUSB30A is not a
series boundary and therefore does not split either member into another net.
Three identical path IDs make the independent copper audit compare like paths:

| path | P endpoints | N endpoints |
|---|---|---|
| `type_c_a_to_phy` | `J_USB.4` (A6/DP) → `U_XU.60` | `J_USB.5` (A7/DN) → `U_XU.59` |
| `type_c_b_to_phy` | `J_USB.12` (B6/DP) → `U_XU.60` | `J_USB.13` (B7/DN) → `U_XU.59` |
| `esd_shunt_to_phy` | `U_USB_ESD.1` → `U_XU.60` | `U_USB_ESD.2` → `U_XU.59` |

The `octilinear_endpoints` pair uses the A-contact path solely for the
pre-route move-set lower-bound check. All six declared electrical paths are
independently measured after a board exists, and the path reader rejects any
physical copper edge not used by a declared path. No `congruent_pads` claim is
made.

The exact current source circuit, SHA-256
`3b34d5ccd5586f5e2b40a2ae169b5fe1e06a065b1739ed6615846cc6852c6dc3`,
contains all eight named ref/pad/net bindings. The shared R-LEN loader accepts
one group and six paths. The schema-reader audit reports 64 proven, zero bad
rows for the `nets.yaml` family; its whole-project FAIL is from pre-existing
unrelated source-schema findings.

Decision admission now reports one current length group and one current
`no_vias` group, instead of the prior zero denominator. Admission remains FAIL
as required: there are no independently accepted route/nets snapshots yet,
and the separate U_ADC/Y_XU assembly-owner findings remain. This repair does
not create or refresh accepted locks.

Evidence is retained in
`06_build/verification/usb-net-contract-repair/{schema-check.json,source-endpoints.json,admission-summary.json,admission-without-locks.json}`.
