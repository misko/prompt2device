# Expanded-locked P1/P2 single-experiment no-go — 2026-09-25

## Scope and exact inputs

This is a read-only research finding. It evaluates the frozen expanded-locked
placement reference required by D18, not a new board, route, source admission,
or release claim.

| Input | SHA-256 |
| --- | --- |
| expanded-locked `crow_carrier.kicad_pcb` | `fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16` |
| its `03_src/floorplan.yaml` | `2f7843ada9eb08d19d268f0d6671079a8cf367629b2b3331119088927415b634` |
| its `03_src/rules/nets.yaml` | `18033487a097b6d29abe3f9d8517879931cf80d278d8973adcf276010a5b7190` |
| its `03_src/route.yaml` | `f49ca740665ce4cfdceb1c82701ddae548f140c8ee1735746040c523c96c8608` |

## No-go

There is no single frozen-placement pad-access/return/ownership experiment
that can supply meaningful positive P1 or P2 admission evidence.

The four direct timing nets are `AUDIO_MCLK_1V8`
`U_TDM_XLATE.6`→`U_XU.23`, `TDM_BCLK_1V8`
`U_TDM_XLATE.4`→`U_XU.22`, `TDM_DATA_1V8`
`U_TDM_XLATE.7`→`U_XU.107`, and `TDM_FSYNC_1V8`
`U_TDM_XLATE.5`→`U_XU.20`. They are only eight terminals of the
14-net/54-terminal `adc_timing_xmos_bundle`. The existing two-terminal record
is `FAIL` and grants neither routing nor P1 credit; `AUDIO_EN` remains an
ownership blocker. The complete timing inventory is `INCOMPLETE`, so a clean
four-net result could not meet the bundle's all-or-nothing P1 denominator.

The frozen local data escape cannot close P2 either. A 0.20-mm F.Cu trace from
`U_XU.107` has 0.175 mm clearance to the adjacent XU pad under the native
0.20-mm requirement. The later 0.15-mm, 1.0325-mm scratch neck is only a
local fabrication geometry probe: it has no source-backed XMOS electrical
allowance and identifies the nearest GND plane transition as 39.2442 mm away.
The In1.Cu GND zone is unfilled. Thus it does not demonstrate lawful
source-owned access and continuous local return. The MCLK/BCLK/FSYNC common
mouth remains unproved for three simultaneous legal exits.

USB cannot replace the missing evidence. The fixed-access screen fails
`J_USB.4` for an undeclared corridor, and a synthetic corridor then fails
because the pad lies outside its source owner region. The reviewed unadopted
3313A controlled-pair replay proves the exact DP/DN clearance policy only. It
does not prove the reversible four-leaf merge, ESD-to-XU transition, connector
ownership, or a filled In1.Cu return.

## Existing receipts

| Receipt | SHA-256 | Relevant outcome |
| --- | --- | --- |
| `2026-09-25-ti-two-terminal-timing-sol/result.json` | `5da4e85b606c5c13f16bef2e578400e67f245193b24e3f361fb8829ae0b31276` | `FAIL`; no P1 or routing acceptance |
| `2026-09-25-ti-adc-timing-complete-probe-sol.json` | `1bf05f9767a1e5a9fba840c5552d78bcbac4d36ba268ff2c3d784c63139b459f` | `INCOMPLETE`; 54-terminal denominator and lane failure |
| `2026-09-25-ti-timing-data-neck-fab-probe-sol/result.json` | `af8a9a1eb557df722e4d55b531f12dc5f3e1ed93bb949a71db1bb6e27251b671` | geometry-only local neck; return access unproved |
| `2026-09-25-ti-usb-fixed-access-evaluation-sol.json` | `fd3a04d5f0e1a7b34302e58a7e0dba6c13c32e171c499441b247c434df95576c` | `FAIL`; fixed connector access not source-owned |
| `2026-09-25-unadopted-3313a-controlled-pair-sol/native-replay-full-sidecar-20260925.json` | `ec9cfedff7b1c6d408e71355c53f87686ed3d1150120d515467ead1e15a589fd` | clearance controls pass; no topology/return admission |

The smallest useful next work is therefore a prerequisite, not a route test:
either source-owned USB edge-cell/corridor modelling, or coupled timing
neighbour placement with a local GND-return design. Both change the conditions
that this frozen-placement question holds fixed.

D18 permits a prospective bounded private route investigation only **after**
actual independent P1 engineering admission and the affected P2 placement
review. It expressly says current P1/P2 admissions are missing and authorizes
no route. This finding provides no exception to that boundary.
