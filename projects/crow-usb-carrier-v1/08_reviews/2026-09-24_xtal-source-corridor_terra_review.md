# Independent review — XTAL source corridors

**Verdict: PASS, source-only.** This review covers commit
`391696ea86a08faf2af26c8912d08ff3cd3aaed0` against parent `558c751c`.
It accepts the allocation record only. P1 remains non-passing: the corridor
contract is `INCOMPLETE`, no P1 receipt exists, and no native board, routed
copper, filled return, DRC, P2/P3 completion, or release is implied.

## Reviewed source

| File | SHA-256 |
| --- | --- |
| `03_src/floorplan.yaml` | `01a9cef20cd71b8503a2420da439f00b74e66ce9e08789a531e2a7b1599a47ff` |
| `03_src/modular_plan.json` | `75c3a517cea50dd6b5745fae96b051d334debd48aac143becaca3d5fe3fc35dc` |
| `03_src/rules/p1_corridor_requirements.yaml` | `9fbf8a5e8a015c6c0166343096476a9ceb1ba12fc1dd1f818222610e0b7a9ea9` |

The source declares 569 unique references and 59 modular interface nets. It
preserves the USB (4), XMOS service (13), ADC timing (14), ADC analog (18), and
power (10) allocations. The new XTAL handoff remains empty at
`[217.2, 107, 218.95, 118.5]`; the five oscillator parts belong in
`clock_flash_debug [190, 118.5, 232, 136]` in a fresh source-generated P2
candidate. The cross-owner contract covers seven pad endpoints on `XTAL_IN` and
`XTAL_OUT`; `XTAL_IN_R` remains a local P3 obligation.

## r2 compact poses cannot be adopted

The five r2 body-plus-courtyard envelopes are not wholly contained in the new
clock region. Three also occupy the intentionally empty handoff.

| Part | r2 envelope | conflict |
| --- | --- | --- |
| `Y_XU` | `[214.155, 110.605, 219.045, 114.395]` | outside clock region; intersects handoff |
| `R_XTAL_FB` | `[215.625, 114.885, 217.575, 115.915]` | outside clock region; intersects handoff |
| `C_XTAL_OUT` | `[214.845, 116.495, 216.755, 117.505]` | outside clock region |
| `R_XTAL_DRIVE` | `[217.025, 116.485, 218.975, 117.515]` | outside clock region; intersects handoff |
| `C_XTAL_IN` | `[217.045, 118.095, 218.955, 119.105]` | straddles clock boundary; intersects handoff |

They remain deferred evidence, not source anchors or an accepted placement.

## Fresh P2 obligations

A fresh source-generated P2 candidate must keep all five physical envelopes
inside `clock_flash_debug` and keep `xtal_south_cap` empty. It must prove the
seven declared cross-owner pad-to-face endpoints, local `XTAL_IN_R`, direct
ground egress for `Y_XU.2`, `Y_XU.4`, `C_XTAL_IN.2`, and `C_XTAL_OUT.2`, and a
continuous filled `GND` reference on `In1.Cu`. Native connectivity, clearance,
silkscreen, filled-return, and XMOS local clock validation remain required.

## Evidence

- `01_docs/findings.yaml` (`USB-XTAL-native-realization`): capped r1/r2 history and reassessment state.
- `01_docs/research/candidate_loop_xtal/r2_result.json`: r2 placement and routing result.
- `01_docs/research/candidate_loop_xtal/xtal_r2_signal_audit.json`: signal audit.
- `01_docs/research/candidate_loop_xtal/xtal_r2_return_terra.json`: return audit.
- `03_src/rules/ic_reference_research.yaml`: XMOS XIN/XOUT proximity and short ground-return requirements.
- `03_src/XTAL_SOUTH_CAP_HANDOFF.json`: source handoff geometry and non-acceptance limits.
