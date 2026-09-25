# Exact power-branch endpoint location in existing physical cells

Research-only checker replay on Terra's `82893c37` 171-terminal power overlay. No canonical Crow source or PCB changed; P1/P2/P3 remain unaccepted.

The opt-in branch endpoint field `physical_cell_id` selects a previously validated occupied `physical_cells` region while retaining the exact modular `block` owner. It is admitted only when the cell owns the endpoint's full reference, native pad and physical envelope, agrees with the source region and placement pattern, and passes existing cell foreign-body/region checks. An untagged endpoint still has the legacy primary-owner-region requirement. A missing tag for a remote pad, wrong cell owner/ref, clipped body/pad, or wrong pattern fails closed. The exact source/native terminal denominator, P2 pad-to-tree duties, P3 connected-tree lower bound, filled-return debt, and null-capacity rule are unchanged. Cells owned by the same modular block are not inventoried as foreign electrical regions.

On board SHA-256 `d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`, exactly three XU power pads need the existing `xmos_core_east` physical cell: `C_XU_VDDIO_35.1`, `C_XU_VDDIO_56.1`, and `C_XU_USB33.1`. The replay tags those three only and retains all **171** exact power terminals across `N1V8` (42), `N3V3X` (27), `N3V3_ADC` (68), and `N5V_BUCK` (34). Isolated checker validation accepts the `N1V8` and `N3V3X` unresolved branches with their full obligations. `N3V3_ADC` still fails at `C_LDO_OUT_1.1` outside `quiet_power`; `N5V_BUCK` fails at `R_PWR_TOP.1` outside `quiet_power`. The full checker stops at `C_LDO_OUT_1.1`, with `FAIL`, `routing_realized=false`, and `p1_accepted=false`. [receipt.json](receipt.json) pins all replay inputs, overlay hashes and exact outcomes.

Reproduce from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-power-branch-physical-cell-sol/replay.py
python3 -m unittest discover -s skills/kicad-pcb/scripts/tests -p 'test_p1_*.py' -q
```

The separate `AUDIO_EN` problem has sparse local owner pockets amid broad overlapping primary planning regions. This extension intentionally applies only to already-declared complete `physical_cells` partitions. A future, separately validated sparse `owner_pockets` branch-location model would be needed there; a pocket name alone must not waive native body/pad containment, foreign occupancy, or route/return obligations.
