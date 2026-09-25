# Independent review — compact XTAL architecture B

**Verdict: PASS, source-architecture evidence only.** Reviewed commit
`a43fb676ae4f66ab7b14a57c5fb5117cd31e8c96` and its generated, ignored board.
This is not P1/P2/P3 acceptance, a route result, or a release claim.

| Input | SHA-256 |
| --- | --- |
| `03_src/floorplan.yaml` | `0032b1202f5742b6575198d27ea50629826d49cf81cf12a31fead8a2929d9868` |
| `03_src/modular_plan.json` | `75c3a517cea50dd6b5745fae96b051d334debd48aac143becaca3d5fe3fc35dc` |
| `03_src/rules/p1_corridor_requirements.yaml` | `191e5580a6ddf56bc9670aff3593c9e9a02d91e75c0c79998b500955050e82a3` |
| `06_build/xtal_source_arch_b.kicad_pcb` | `000c6cee2e28c470b7cb49a4db863c7b1398a72a25f54e914b1d8035b3e3d152` |

The board has **569 unique references**, exactly matching the modular plan. All
five compact oscillator body-plus-courtyard envelopes are contained in
`clock_oscillator_local [214, 110.5, 219.1, 119.2]`:

- `Y_XU [214.155, 110.605, 219.045, 114.395]`
- `R_XTAL_FB [215.625, 114.885, 217.575, 115.915]`
- `C_XTAL_OUT [214.845, 116.495, 216.755, 117.505]`
- `R_XTAL_DRIVE [217.025, 116.485, 218.975, 117.515]`
- `C_XTAL_IN [217.045, 118.095, 218.955, 119.105]`

The ignored board contains no footprint, pad, or track intersecting the
`xtal_south_cap`, `qspi_gap`, or `jtag_strip` regions and faces. The exact
`qspi_gap` P2 denominator is **13/13** endpoints; `xtal_south_cap` is **7/7**.
Both retain `GND` / `In1.Cu` continuous-filled-reference obligations. Clock
ownership is partitioned as three main refs, five oscillator refs, and an empty
QSPI transit cell.

The board has no XTAL or QSPI signal tracks; its 14 zero-length F.Cu items are
GND. The source architecture therefore admits the compact placement only. It
does not repair the r2 finding that `Y_XU.2`, `Y_XU.4`, `C_XTAL_IN.2`, and
`C_XTAL_OUT.2` lack proven ground return. A fresh P2 candidate must prove those
egresses, local `XTAL_IN_R`, the seven cross-owner pad-to-face paths, filled
In1 return, clearance/DRC, and silkscreen. P1 remains `INCOMPLETE`.

Evidence: `01_docs/research/candidate_loop_xtal/xtal_r2_return_terra.json`,
`03_src/rules/ic_reference_research.yaml`, and
`06_build/xtal_source_arch_b.kicad_pcb`.
