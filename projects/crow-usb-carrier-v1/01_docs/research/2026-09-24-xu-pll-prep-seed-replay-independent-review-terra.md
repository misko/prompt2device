# Independent review: XU PLL `prep.seed_stubs` replay (Terra)

Reviewed SOL evidence commit `7b8c6182`, retained source/boards in
`/tmp/crow-xu-pll-seed-replay-sol`, and current Crow `03_src/route.yaml` and
live netlist. No canonical route or board was changed.

## Copper and native evidence

The retained r0 SHA-256 is
`395446f15c79967ac0f41500c8d31e4bda558fe76347606b187c4d06db8700ea`;
the strict saved board and DRC JSON hashes match the SOL note. I compared its
local copper with the earlier diagnostic board. The complete 18-item native
signature matches: 7 `PLL_0V9` 0.20-mm F.Cu segments, 3 `N0V9` 0.60-mm F.Cu
segments, 4 GND 0.20-mm F.Cu segments, and 4 GND 0.60/0.30-mm vias. The six
pin-owned banks are exactly `U_XU.41`, `FB_PLL.1`, `C_PLL_100N.2`,
`C_PLL_1U.2`, `U_XU.129`, and `U_XU.42`.

This supports deterministic reproduction of that *local* diagnostic copper.
It does not establish complete N0V9 supply, PLL return impedance/current
quality, assembly clearance, the diagnostic TDM exits, or full routing.

TMUX reports eight B2 areas/rules. Via-process reports 18/18 sites: 14
protected and 4 ordinary 0.60/0.30-mm vias, with no partial process state.
Those are geometry/process checks; they do not change the connectivity verdict.
The strict DRC JSON has zero `violations` and zero schematic-parity entries,
but 499 `unconnected_items`; those items begin with ordinary open nets such as
`PRE_GATE` and `N5V_LDO_FEED`. The zero-violation field is therefore not a
route acceptance result.

## Current-source preflight findings

All three `ADC_MCLK`, `ADC_MCLK_RAW`, and `ADC_MCLK_SAFE` members remain in
`prep.waves.groups.audio_timing` at route.yaml lines 108-110 and are absent
from the live `crow_carrier.net`. `wave_nets()` rejects exactly this condition,
so it is a real current-source preflight blocker.

The `route.common.fab_overrides` value is repository-relative
`projects/crow-usb-carrier-v1/03_src/rules/route_fab_overrides.txt`, while the
actual project-local file is `03_src/rules/route_fab_overrides.txt`. The shared
resolver finds the former in the canonical checkout through its repository
fallback, but it fails when replay is run from a standalone copied project
root, as the retained log shows. This is a source portability/preflight defect
for isolated replay, not evidence that canonical-checkout resolution itself
failed. It should be corrected separately with the ADC wave members; neither
defect invalidates the measured seed emitter signature.

No material contradiction in the replay evidence found. The retained 499
unconnected items prevent route, P1, or PLL supply/return acceptance.
