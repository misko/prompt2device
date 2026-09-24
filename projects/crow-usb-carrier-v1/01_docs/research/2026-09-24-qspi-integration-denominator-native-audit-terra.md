# QSPI integration-corridor denominator and native audit

**Scope:** independent source/native input audit for a future schema-2 QSPI
integration-corridor packet.  This note is not a route, capacity proof, P1
acceptance, or release claim.

## Pinned inputs

- Crow source branch commit: `57e816c7a554ae0d4303067af4a4ee3af340ccb9`.
- Regenerated QSPI-gap board SHA-256:
  `fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27`.
- Corresponding QSPI-gap floorplan SHA-256:
  `cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925`.

Authoritative source rows agree: `03_src/rules/p1_corridor_requirements.yaml`
(`xmos_service_escape`/`qspi`) and `03_src/modular_plan.json` interfaces.
There are no QSPI pad aliases: every source endpoint below is its native
identity and the native board pad net matches its listed net.

## Exact denominator

The demand is six F.Cu nets, six 0.45-mm slots, and a stated 2.70-mm width:

| Net | `xmos_core` native endpoint | `clock_flash_debug` native endpoint(s) |
| --- | --- | --- |
| `QSPI_CLK` | `U_XU.4` | `U_FLASH.6` |
| `QSPI_CS_N` | `U_XU.2` | `R_QSPI_CS.2`, `U_FLASH.1` |
| `QSPI_D0` | `U_XU.127` | `U_FLASH.5` |
| `QSPI_D1` | `U_XU.128` | `U_FLASH.2` |
| `QSPI_D2` | `U_XU.1` | `U_FLASH.3` |
| `QSPI_D3` | `U_XU.3` | `U_FLASH.7` |

This is 13 source/native endpoints (six XU-side and seven clock/flash-side),
so a conforming handoff packet needs 13 exact `affected` entries and 13 ordered
P2 pad-to-face obligations.  The two
participants are exactly `xmos_core` and `clock_flash_debug`; the integration
owner is `board_integration`, which is an authority string, not a third
participant block.

## Geometry interpretation

The regenerated source declares a disjoint empty region
`board_integration_qspi = [199.8, 110.5, 223.2, 118.5]` mm, with
`xmos_core = [190, 84, 232, 110.5]` and
`clock_flash_debug = [190, 118.5, 232, 136]` mm.  Therefore the only correct
cell-face directions for this corridor are `xmos_core` **south** at `y=110.5`
and `clock_flash_debug` **north** at `y=118.5`; its participants must not be
reversed or include `board_integration`.

Native inspection confirms the named QSPI nets: XU pads 1--4 are at
`y=107.6625` mm and pads 127/128 at `y=105.8/106.2` mm; flash pads are at
`y=125.295--129.105` mm and `R_QSPI_CS.2` at `y=123.4` mm.  Thus the faces
are source-cell boundaries rather than pad access claims.  The required
packet must retain explicit P2 F.Cu pad-to-face and In1.Cu GND filled-reference
return obligations for all endpoints.

## Result

No source owner, endpoint, net, face-direction, or native-pad mismatch was
found that prevents an exact packet.  The result is still **INCOMPLETE**:
the 5.00-mm raw face does not prove six usable lanes, any pad escape, return
continuity, native rule-area preservation, routing, or P1 acceptance.
