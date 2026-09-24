# Isolated exact-net XU power neck-down rule proof — 2026-09-24

**Result: native rule precedence and the two local flares work on this one isolated board. This is a rule/geometry proof, not an adopted rule, current-capacity approval, complete route, or P1 acceptance.** No canonical source, rules, board, P1 attempt, or graph was changed. The positive saved board is `/tmp/crow-xu-width-exception-sol/04_kicad/crow_carrier.kicad_pcb`, SHA-256 `8c618b3c93f9a464a243b50674b68696baee0c58726a835e30fb4a22f80a6e5a`; its isolated `.kicad_dru` is SHA-256 `22e83ba08c0a235b2d6437960dbeb76da63f53cf1e5c93ba8f89dcd0aa891974`.

The unchanged ordinary `DIGITAL_POWER_width` rule requires 0.60 mm on `N0V9`, `N1V8` and the other class nets; the existing class clearance is 0.15 mm. Two **F.Cu-only**, exact-net, rule-area-scoped width rules were placed after that width rule in the isolated `.kicad_dru`:

```scheme
(rule "xu14_local_neck"
  (layer "F.Cu")
  (condition "A.Type == 'Track' && A.NetName == 'N0V9' && A.insideArea('xu14_neck')")
  (constraint track_width (min 0.15mm)))
(rule "xu17_local_neck"
  (layer "F.Cu")
  (condition "A.Type == 'Track' && A.NetName == 'N1V8' && A.insideArea('xu17_neck')")
  (constraint track_width (min 0.15mm)))
```

The native F.Cu rule areas are rectangles `xu14_neck=[207.25,107.40,207.75,109.00]` and `xu17_neck=[208.45,107.40,208.95,109.00]` mm. No clearance constraint was relaxed. The two 0.15-mm tracks run from `U_XU.14` `(207.5,107.6625)` and `U_XU.17` `(208.7,107.6625)` to `(207.5,108.95)` and `(208.7,108.95)`, respectively, **1.2875 mm each**. From y=108.95 they flare to 0.60 mm: N0V9 continues 0.25 mm to `(207.5,109.2)` and then follows the prior 0.60-mm C14 path; N1V8 continues 0.37 mm to `C_XU_VDDIO_17.1` `(208.7,109.32)`. Both total supply path lengths remain 4.952891 mm (C14) and 1.657500 mm (C17). The four TDM diagnostic strips and three prior ordinary GND return vias remain in place. The first flare at y=108.72 mm failed clearance to adjacent XU pads because the round 0.60-mm track end reached back toward the pad tips. Moving only the junction to y=108.95 mm removed those findings.

The TMUX POFV producer passed after the local rules were added, retained both exact-net rules, and emitted its eight B2 areas/rules. Full saved-board native DRC with `--severity-all --refill-zones --all-track-errors --save-board --schematic-parity --format json` reports **four violations, all the four original intentional `track_dangling` TDM ends; zero track-width, clearance, short, mask, or other findings; 499 unconnected items; zero schematic-parity findings**. DRC JSON SHA-256 is `814b7e5e6783398623599a98f693e2421982071482349bfee18bb758ea2e4585`. `via_process_check.py` passes 17/17 graded vias: 14 protected via-in-pad sites and three ordinary 0.60/0.30-mm GND vias, no partial sites; JSON SHA-256 `73137adc8418ad8b25067ce17c05da50dcad99a405f18925ed70f4966332de3f`. Exact netlist parity passes 282/282 nets, 1,641 connected nodes, 146 no-connects.

The deliberate negative board `/tmp/crow-xu-width-exception-sol/offsite-negative/crow_carrier.kicad_pcb`, SHA-256 `635e3130a59ae0200050cefed68e9871c8708712c0c295311caa67092b74e401`, adds one floating 0.15-mm F.Cu `N1V8` track from `(180,115)` to `(181,115)`, far outside the two XU areas. Native DRC reports **one `track_width` violation on that exact track citing `DIGITAL_POWER_width` minimum 0.6000 mm**, plus its new dangling end and the four original dangling ends; 499 unconnected items and zero parity findings. Negative DRC JSON SHA-256 is `3733ba5ba7b621e07707d4797914fcb9f013a8d0b7e411c5dc75015b1b9cac1b`. This proves the local rule does not globally lower the N1V8 width floor.

This hand-added `.kicad_dru` rule is not source-owned; `generate_rules_generic.py` may replace it on a normal rebuild. The 0.15-mm necks still need governed source authority, exact regeneration, conductor-current/voltage-drop and transient review, mask/assembly review, completed surrounding power/PLL routes, full return extraction, and independent acceptance under the [VDDIO17/PLL contract](2026-09-24-xu-vddio17-pll-acceptance-contract-terra.md). No PLL copper was added in this bounded proof.
