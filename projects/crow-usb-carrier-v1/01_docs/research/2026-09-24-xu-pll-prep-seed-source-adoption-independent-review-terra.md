# Independent review: XU PLL seed-source adoption (Terra)

Reviewed route-source adoption `9f4bfb1a` against its parent, the prior PLL
diagnostic board, and retained isolated replay at
`/tmp/crow-xu-pll-seed-replay-sol`.

The route diff is bounded to six `prep.seed_stubs` banks, removal of only the
three absent ADC MCLK wave names, and the project-local fab-overrides path.
It changes no canonical board, floorplan, graph, P1 input, or full route
artifact. Current `route.yaml` SHA-256 is
`f49ca740665ce4cfdceb1c82701ddae548f140c8ee1735746040c523c96c8608`,
matching the adoption note.

The YAML expands to exactly 18 primitives: seven `PLL_0V9` 0.20-mm F.Cu
segments from `U_XU.41`; three `N0V9` 0.60-mm F.Cu segments from `FB_PLL.1`;
and four one-segment/one-via GND banks at `C_PLL_100N.2`, `C_PLL_1U.2`,
`U_XU.129`, and `U_XU.42`. I compared net, layer, endpoints, widths, and
drill for all 18 against the earlier diagnostic board: they match. The four
TDM diagnostic strips are absent, as intended.

`fab_overrides: 03_src/rules/route_fab_overrides.txt` names the actual
project-local file. The three removed ADC MCLK names are absent from the live
netlist and no longer occur in a wave group. Thus both replay preflight
defects are corrected without a broader route-plan change.

Retained source adoption evidence is consistent: route ownership reports
PASS/0 findings, schema reader reports 1047/1047 declared keys and 0 orphan,
and strict native DRC for the saved isolated r0 reports zero violations and
zero schematic-parity issues. It also reports 499 unconnected items. TMUX's
eight B2 areas/rules and via-process's 14 protected plus four ordinary vias
verify geometric/process state, not route completion.

No material adoption issue found. The 499 opens, upstream N0V9 supply gap,
return current/impedance and assembly proof, imported full conductor, and
P1/P2 acceptance remain open.
