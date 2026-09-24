# XU local-power rule producer seam — 2026-09-24

**Finding:** Crow's normal drivers generate generic rules and TMUX POFV before `route_prep`; `route_and_stitch_generic.py prep` then writes the seed-bearing `06_build/route/r0.kicad_pcb` and rides the `.kicad_pro`/`.kicad_dru` sidecars along. That freshly prepared **r0** is the first legal board on which `xu_local_power_launches.py` can audit the two contiguous 0.15-mm pin exits and emit the exact-net rule areas. The track-free `04_kicad` board before prep must not be passed to this helper: missing copper is correctly an error. The final `generate_rules_generic.py` → `generate_tmux4827_pofv.py` pair after stitch is the second required producer seam, now on `04_kicad/$BOARD.kicad_pcb`, because pcbnew saves and rules regeneration can change sidecars. Relevant driver positions are `rebuild_reuse.sh` lines 232–244 and 266–267, and `rebuild_all.sh` lines 482–500 and 526–527. No canonical source or board was changed for this audit.

A minimal **atomic promotion patch**, conditional on independent placement/return review and source adoption of the four poses plus four XU seed banks, is two explicit calls in *each* Crow driver:

```sh
# Immediately after run_stage route_prep (before pre_route_review_check/import):
$PY 03_src/diagnostics/xu_local_power_launches.py \
    "06_build/route/r0.kicad_pcb" 03_src/rules/xu_local_power_launches.yaml \
    --emit-dru "06_build/route/r0.kicad_dru" \
    --save "06_build/route/r0.kicad_pcb"

# Immediately after the final generic-rules and TMUX POFV producers, before rules_audit:
$PY 03_src/diagnostics/xu_local_power_launches.py \
    "04_kicad/$BOARD.kicad_pcb" 03_src/rules/xu_local_power_launches.yaml \
    --emit-dru "04_kicad/$BOARD.kicad_dru" \
    --save "04_kicad/$BOARD.kicad_pcb"
```

Keep each call under `set -e` so an invalid window, absent launch, wrong net/pad, or changed ordinary rule stops the driver. The four calls are not safe to add alone while canonical `xu_local_power_launches.yaml` still lacks windows and canonical prep has no XU copper: the helper would deliberately fail. The normal full drivers should run generic rules → POFV → helper in that order at the post-prep and final seams; a later generic-rules invocation must again be followed by POFV and helper. A direct low-level `route_and_stitch_generic.py prep` remains a producer of copper and ordinary sidecars, not an invocation of the project-specific helper. If direct prep must be self-contained, a separate opt-in post-seed producer hook and route schema change are required; that is broader than this minimal Crow-driver patch.

In `/tmp/crow-xu-producer-seam-sol`, the isolated [shared-return source recipe](2026-09-24-xu17-outside-courtyard-shared-return-sol.md) produced r0 with 10/10 seed banks, 28 primitives, and zero refused. Its r0 DRU already carried ordinary `DIGITAL_POWER_width` and eight TMUX B2 rules. Running the exact post-prep helper command emitted two XU areas/rules and returned `PLACEMENT_REVIEW_REQUIRED`; repeating it returned the same result with a **byte-identical DRU SHA-256** `60593deeb18805231e00140abd2a9795b343cb8e509934908cbe1b124656266c`. Both area names remained singular. Removing the XU14 window caused exit 1, `XU_VDD14_LOCAL: invalid window`; removing its one 0.15-mm segment caused exit 1, `XU_VDD14_LOCAL: missing narrow launch`. Neither failure altered the DRU. The saved positive r0 PCB SHA-256 is `d7ebbc8bb55bee39469f573cb7fa0c7885e4b71b04668106f00d26449cad3310`.

For an end-to-end native gate, that emitted r0 board/DRU was placed in an isolated project-layout copy with the actual `fp-lib-table`, schematic, and project file at `/tmp/crow-xu-endtoend-seam-sol`. Full `kicad-cli pcb drc --severity-all --refill-zones --all-track-errors --save-board --schematic-parity --format json` reports **zero violations, 499 unconnected, zero parity issues**; JSON SHA-256 `40c924c6944cb984f16c4b2f8dca65554e2408b8f7b42acc7a5311aba0cd7f2a`. A bare `r0` copied outside that project layout reported 199 `lib_footprint_issues` from missing local library resolution, so the project-layout DRC is the valid native result. The [previous final-board replay](2026-09-24-xu17-outside-courtyard-shared-return-sol.md) separately proved correct final-rule order, four intentional dangling TDM strips only, POFV eight, via-process 19/19, and exact parity 282/282.

The helper deliberately requires `status: placement_review_required` and returns `PLACEMENT_REVIEW_REQUIRED` on success. This permits a **conditional source candidate and isolated prep proof** without claiming P1 acceptance, provided work stops before the full import/route-acceptance path. The status string itself is **not a P1 gate**: once these calls are wired into the full drivers, a successful helper exits zero and later gates still determine placement/route acceptance. A separate full-rebuild blocker is visible even on the isolated candidate: `escape_check.py` exits `P-LAND UNSUPPORTED` on the existing `tmux_ordinary_annular_floor` annular-width rule before route prep. This audit does not claim an end-to-end `rebuild_all.sh`/`rebuild_reuse.sh` pass or resolve that unrelated gate.
