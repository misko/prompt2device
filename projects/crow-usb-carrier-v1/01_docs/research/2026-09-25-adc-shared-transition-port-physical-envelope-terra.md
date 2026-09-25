# ADC shared-transition-port physical-envelope probe

Scope: research-only evaluation on the TI unrouted diagnostic board. This note
neither changes the canonical Crow source contract nor supplies P1 evidence.

The shared-transition-port occupancy check used
`FOOTPRINT.GetBoundingBox(True, True)`. That includes movable reference/value
text. On the exact board, `C_ADC_A_IOVDD_10U` therefore appeared to occupy
`[138.721750, 91.256192, 149.898572, 99.661600]`, although its physical body is
`[140.245, 93.375, 142.255, 96.825]`; its courtyard is
`[140.225, 93.355, 142.275, 96.845]`. The claimed ADC/audio port at
`[148.9, 92.1, 149.0, 92.3]` is physically clear.

The generic checker now uses its pre-existing `_physical_envelope(fp)` for
shared-port occupancy. That keeps the body and F/B courtyards, and separately
keeps pad checks, while excluding movable text. Focused tests prove a
text-only overlap passes and physical body, pad, and courtyard overlaps fail.

The isolated candidate is retained under
`01_docs/research/2026-09-25-ti-adc-shared-port-probe/` and remains outside
canonical source:

- candidate: `candidate.json`, SHA
  `801cf1662da36dc704458df194889fee23098aa0f1e317cd5cf1a4dc19eabed5`;
- source requirements: `requirements.yaml`, SHA
  `62c8e8f9b3e2a264a76c30fcc68107e4de28d98c00f5ee4f7a3be863d059c648`;
- floorplan: `floorplan.yaml`, SHA
  `c2f107c315a3a1750f700dcbadbe556ae8206b7e99937d044c62def4104a6b21`;
- exact board SHA: `8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`;
- result: `result_physical_envelope.json`, SHA
  `a36f2a055cf8b5c3c2f478eaacb2c0990933a65c36163fa1a84d0463a79110f9`.

The bound `--diagnose-all` run reports `INCOMPLETE` with no global errors. It
has no `adc_timing_xmos_bundle` diagnostic; the shared trunk and its exact P2
and filled-reference obligations remain incomplete. Independent diagnostics
remain ADC analog (18), USB (10), and power (9). No route, acceptance, or P1
credit follows from this screen.
