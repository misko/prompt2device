# Connector physical qualification plan

Status: source-stage plan only. This plan selects procedures and evidence targets; it records no realized geometry, service clearance, installed cable route, tolerance bound, or physical PASS.

## Bound candidate and hardware

The future qualification subject is the exact candidate PCB produced from `03_src/floorplan.yaml`, with connector refs J1-J8, J_USB, J_PWR, and J_JTAG populated with the contract-selected receptacles. Authored orientation authority is `01_docs/research/2026-09-22-connector-placement-intent.md`; it explicitly binds each ref to intended board-frame mating and lateral axes for generation. Its status is planned, so realized orientation remains unknown until the saved PCB and outline are measured. Test with the exact selected mates and cables. J_JTAG uses Samtec FFSD-05-D-06.00-01-N as both the selected keyed IDC mate and cable assembly identity. No alternate plug, boot, wire termination, or cable may be substituted without a separate profile.

## Procedure

1. Freeze and hash the candidate PCB, connector contract, phase policy, floorplan, population list, connector lots, mates, cables, and enclosure/coupon configuration. Record ref-to-profile identity for every sample.
2. Populate the exact connectors on a coupon or first article made with the candidate footprint, board thickness, edge/outline registration, and mounting process. Record seating and connector rotation before loading.
3. Establish a repeatable board restraint outside component and trace keepouts. Apply insertion and withdrawal by hand at the selected mate while reacting the load through the restrained PCB and connector mounting features. Do not use neighboring connector bodies, cables, or their solder joints as the counter-hold. The operated connector carries its own reaction through the selected mounting load path. Observe board flex, connector rotation, latch/polarization engagement, and solder-joint distress.
4. For each profile, perform the required service operation with every member of its declared simultaneous group populated in the declared state. Exercise J1-J8, J_USB, and J_PWR in `normal_service`; exercise all eleven refs including J_JTAG in `bench_service`. Record the target ref, neighboring population, start/end state, hand access, grip/release access, interference, and result for every operation.
5. Install each exact selected cable in its intended enclosure state. Record the as-installed exit direction, unobstructed straight segment, first controlled bend, bend radius, strain relief, and all contact/interference with board, enclosure, and neighboring populated hardware. J_JTAG's lateral ribbon exit must be measured as installed. Before its cable target can enter source deferral, extend the owning schema/compiler with an optional board-frame exit vector (including unit-vector and non-axial validation) or select and evidence an actually axial cable assembly. Schema 1 permits only `along_mating_axis`, `opposite_mating_axis`, and `none`, so this plan does not encode the lateral route falsely.
6. Across the required sample lot, measure the installed mating-plane/board-outline relationship and each applicable contributor to exposure setback. Record raw observations per sample and derive any future one-sided allowance from those observations and cited manufacturing tolerances. Do not infer a zero contributor from a missing observation.
7. Repeat mating and unmating for the project-approved cycle count, then repeat seating, rotation, flex, solder-joint, latch/polarization, simultaneous-service, and cable-route inspections. The cycle count and any numeric load or displacement limits require separate cited engineering authority before grading.

## Load cases and reaction paths

| Assembly | Load cases | Selected reaction method and load path |
| --- | --- | --- |
| `spoke_rj45` / J1-J8 | plug insertion; latch release and withdrawal; installed cable bend/strain; service with both groups populated | Restrain the PCB at its mounting features adjacent to the operated bank. Carry hand insertion/withdrawal reaction from the Wurth through-hole shell and pins into the PCB, then through the PCB restraints. |
| `usb_device` / J_USB | plug insertion and withdrawal; overmold grip; installed cable bend/strain; populated-neighbor service | Restrain the PCB at adjacent mounting features. Carry reaction from the GCT shell stakes and SMT mounting into the PCB and restraints; do not use the USB cable or neighboring connectors as a counter-hold. |
| `external_power` / J_PWR | latch engagement; latch release and withdrawal; wire/cable strain; populated-neighbor service | Restrain the PCB at adjacent mounting features and support only the PCB. Carry reaction from the Molex through-hole header into the PCB and restraints; do not react through the wire pair or latch. |
| `debug_jtag` / J_JTAG | polarized insertion and withdrawal; ribbon lateral exit/bend; bench group populated | Restrain the PCB at adjacent mounting features. Carry reaction from the Samtec SMT header joints into the PCB and restraints while gripping the keyed socket body; do not pull the ribbon as the withdrawal grip. |

The method above selects the support concept and load path. Its physical adequacy remains unknown until the governed candidate is exercised. No numeric force or deflection acceptance bound is invented here.

## Acceptance evidence

Each stable target below requires observations for every governed sample and connector ref. A target passes only when its exact identity and candidate binding are complete, every required observation is present, and the stated qualitative criterion is met. Any interference, loss of seating, damaged latch/polarization, connector rotation, board or joint damage, or inability to complete a required operation is a failure. Missing measurements, calibration, sample identity, or approved numeric limits remain `INCOMPLETE`.

| Stable target | Required evidence and acceptance criterion |
| --- | --- |
| `spoke_rj45.interface`, `usb_device.interface`, `external_power.interface`, `debug_jtag.interface` | Realized orientation and mating plane measured against the exact PCB/outline; the exact mate fully engages without collision, cross-mating, latch damage, or loss of seating in the intended enclosure state. |
| `*.reaction` | Video/photographs plus before/after seating, rotation, flex, and joint inspection for every load case; load follows the selected path and causes no visible damage, permanent movement, or unintended neighbor loading. Numeric force/deflection claims require separately approved bounds and calibrated measurements. |
| `spoke_rj45_service`, `usb_device_service`, `external_power_service`, `debug_jtag_service` | Per-ref operation record with declared group populated; required start-to-end transition completes by the selected hand method, with grip/latch/polarization access and no interference or neighbor disturbance. |
| `*.cable` installed route | Exact cable identity and installed route record showing exit, straight segment, first bend, strain relief, and neighbor/enclosure clearance. Any required dimension remains incomplete until measured against an approved bound. |
| `spoke_rj45_registration`, `usb_device_registration`, `external_power_registration`, `debug_jtag_registration` | Raw per-sample mating-plane/outline and process-contributor measurements. Future allowance must conservatively contain the observed/cited stack; no value is admitted from this plan. |

This plan is suitable as a source-phase evidence reference. It cannot approve placement, routing, enclosure service, release, fabrication, or first article.
