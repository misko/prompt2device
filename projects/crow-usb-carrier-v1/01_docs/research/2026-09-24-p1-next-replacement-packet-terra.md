# P1 next replacement packet: XU service-cell ownership

**Research review only — no P1 acceptance, task dispatch, canonical source or
board edit.**  This selects one testable prerequisite for the distinct active
root `p1_floorplan_569_after_native_evidence_abort`; it does not spend that
root's single attempt.

## Exact subject and conclusion

This review is bound to `main` commit `9c73181c432b51558003a8be7e496cc8c6757d5a`:

| Input | SHA-256 |
| --- | --- |
| `03_src/floorplan.yaml` | `a882f87682484c37c5766a9e37c5a0d93b38a8e5a775fb1ab4425011da40a275` |
| `03_src/modular_plan.json` | `7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e` |
| `03_src/rules/p1_corridor_requirements.yaml` | `9ef85e5f4918dea0378203a97fa631ce2e73a690170235902a97a6c8e30527d8` |

The single next governed action is to author and independently review **one
read-only XU-service-cell ownership variant packet**.  It must replace the
overlap between `xmos_core [185,72,232,128]` and
`clock_flash_debug [185,112,232,136]`, whose shared rectangle is 47 x 16 mm.
The prior straight y=112 boundary is already rejected because it crosses full
XU-decoupler bounds.  The packet may use either a staggered disjoint boundary
or one explicit source-owned shared service zone, but must name the selected
alternative; it cannot retain overlapping aliases.

This is the narrowest useful replacement action because the current
`xmos_service_escape` allocation already names its exact QSPI and JTAG/reset
endpoints and declares 2.70 mm and 2.25 mm F.Cu demands respectively, while
its geometry remains `null`.  It can therefore prove or reject internal source
ownership without a connector sample, vendor-private record, or USB launch
claim.

## Packet contents and test

Freeze a disposable source-floorplan variant and its netlist/interfaces,
requirements, aliases, generator/checker versions and input hashes.  Retain
the exact 27 `p1_fixed_refs` from the requirements file: J1--J8, `J_PWR`,
`J_USB`, `J_JTAG`, and C_HOLD1--C_HOLD16.  XU, flash/debug, crystal and local
support remain P2-movable; their collision is recorded as P2 relocation debt,
never corridor capacity credit.

The review must produce machine-readable measurements for the selected QSPI
and JTAG/reset service faces:

1. each source cell/service zone and reservation is exclusive, bounded, inside
   the outline, and does not cross another source region;
2. full component bodies, pads, courtyard fallback, fixed references and rule
   areas do not intersect the new boundary or reservation;
3. each declared face has nonzero, non-overlapping F.Cu width against its
   stated demand, with exact endpoint and owner names; and
4. every movable endpoint has an explicit `P2_REQUIRED` pad-to-face and local
   return obligation.

An intersection, inadequate width, missing endpoint, or missing P2 obligation
rejects the variant.  A clean result is still **INCOMPLETE research** for the
independent schema-2 admission packet; it is not a coarse-contract receipt,
native P1 attempt, P2 authorization, or route permission.  The separate
ADC/timing and analog ownership debts remain deliberately outside this one
packet and must be resolved before any complete P1 corridor proof.

## External USB qualification is separate

`usb_device_pair` remains geometry-null and its ESD-to-XU F.Cu diagnostic is
explicitly limited evidence.  Connector FULL is also `INCOMPLETE` with 19
physical unknown paths.  Those facts do not prevent preparing or testing this
internal source packet, but they still prevent P3, route preparation/import,
P5 promotion, release and order.  This packet supplies no connector fit,
impedance, return-path, SI, decoupling, or USB qualification evidence.

The active graph's root has `max_attempts: 1` and no dependencies.  Its prior
native campaign is terminal and non-creditable due to the mixed board SHA
recorded in finding `USB-P1-native-evidence-failure-replacement`; this review
neither resumes nor resets it.

Primary current sources: `03_src/floorplan.yaml` (regions and ownership),
`03_src/rules/p1_corridor_requirements.yaml` (fixed references, endpoints and
demands), `03_src/modular_plan.json` (active root),
`01_docs/findings.yaml` (replacement finding), and
`01_docs/research/2026-09-24-p1-fresh-candidate-admission-audit-sol.md`
(connector-FULL boundary).
