# Measurement matrix and non-credit boundary

This matrix instantiates the 19 target families in the connector physical
qualification plan for the hash-bound geometry manifest. Every row remains
`INCOMPLETE`: this packet contains no fabricated article, population, fixture,
mate, measurement, limit, or observation.

| Target family / count | What a separately authorized unpowered, full-field article could record | What it cannot qualify from this packet |
| --- | --- | --- |
| `spoke_rj45.interface` (1, J1--J8); `usb_device.interface`; `external_power.interface`; `debug_jtag.interface` (3) | Exact mate engagement, polarization/latch condition, seating and immediate populated-field interference. | Mating-plane tolerance, enclosure fit, process registration, or interface PASS. |
| `spoke_rj45.reaction`; `usb_device.reaction`; `external_power.reaction`; `debug_jtag.reaction` (4) | Before/after seating/rotation/flex photographs and visible negative failure observations, using an approved restraint. | Reaction PASS, force/deflection/cycle margin, joint integrity, or a fixture load path without approved hardware and limits. |
| `spoke_rj45_service`; `usb_device_service`; `external_power_service`; `debug_jtag_service` (4) | Intended normal/bench service transitions with the declared simultaneous group installed; access/interference observations. | Installed enclosure access, reproducible hand force, service clearance PASS, or an unobserved group state. |
| `usb_device.cable`; `external_power.cable`; `debug_jtag.cable` (3) | Exact cable identity, initial exit and immediate cable-to-neighbor collision observations. RJ45 cable behavior stays in the spoke-profile observations. | Installed straight length, first controlled bend/radius, strain relief, far-end support, enclosure clearance, or cable PASS. |
| `spoke_rj45_registration`; `usb_device_registration`; `external_power_registration`; `debug_jtag_registration` (4) | Raw per-sample board-edge/mating-plane/seating measurements and shell/stake inspection. | Finished-process tolerance allocation, exposure/setback allowance, or registration PASS until limits and uncertainty are approved. |

The earlier fit-only prototype gives the same non-credit lesson: a complete
connector field can reveal an interference failure, but it closed zero FULL
targets because it lacked governed mounting, enclosure, process, and limits.
The present full-outline screen adds the six existing mounting-hole poses and
nominal adjacent-footprint screen; it still lacks the fixture, hardware, and
physical observations required to interpret any reaction or service test.
