# Independent review: revised XU14/XU17 local candidate (Terra)

Reviewed SOL commit `39a45b02`, retained isolated source/board at
`/tmp/crow-xu-southwest-revised-source-sol`, and retained XMOS XU316 guidance.
No canonical source or board was changed.

The isolated floorplan/board hashes reproduce. The helper declarations bind
only `U_XU.14/N0V9` and `U_XU.17/N1V8`, each to the stated cap pad, F.Cu
window and flare. The board has the stated 0.15-mm pad launches, 0.60-mm
continuations, and C14/C17 GND paths to ordinary 0.60/0.30-mm vias. The scope
is exact-pin and bounded; ordinary DIGITAL_POWER remains unchanged outside.

This local topology is geometry-feasible: six PLL seed banks remain separate,
C14/C17 supply and GND copper does not overlap them or the four diagnostic
timing strips, and `.42` return remains distinct from EP `.129`. TMUX reports
eight B2 areas and via-process reports 20 sites (14 protected, six ordinary,
zero partial). The correct DRC has four `track_dangling` findings, 499
unconnected items, zero parity issues, and no width/clearance/short/courtyard/
mask finding under correct rule order. It is not a complete routed board.

XMOS asks for local VDD/VDDIO decoupling and short/direct GND return, but
publishes no maximum capacitor distance, via distance, return impedance, or
ripple number. C14 is still a multi-segment ~4.22-mm supply route; plane/via
geometry does not prove loop impedance or return current. C17's GND via is
close to or within its capacitor courtyard, so absence of native DRC does not
prove assembly/mask suitability. Upstream N0V9/N1V8 and board-wide return
quality remain open.

Silk ownership regresses from current PLL placement 260 owned / 264 degraded /
44 unplaced to 258 / 266 / 44. Verdict: isolated geometry candidate only;
not admissible for placement, route, P1/P2, or release until decoupling/return,
assembly, silk, and complete-connectivity evidence closes.
