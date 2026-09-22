# Four-layer design and cost posture

Decision date: 2026-09-22. Scope: reversible design, with no purchase or fabrication authorization.

Adopt the vendor-supported JLC04161H-7628G ordinary four-layer, nominal1.6mm construction with1oz outer and0.5oz inner copper. Keep the continuous inner ground reference beneath the USB pair and reserve the other inner layer for power/return distribution. Existing source rules bind the exact vendor-solved cross-section; see [impedance evidence](../research/2026-09-22-usb-impedance-evidence.md).

Four layers are the baseline for this489-component, eight-channel carrier because the USB return path, digital/power distribution and analog neighborhoods must coexist. Two-layer construction has not been shown to satisfy those requirements. Additional layers, heavier copper, blind/buried vias and selective filled/capped via-in-pad are not selected here. Any need for them must arise from actual escape, routing or thermal evidence and reopen the owning decision.

The assembly source selects standard service, top-side SMD placement and a five-board evidence quantity. These are design/quotation inputs, not an order. Existing manual/consigned/THT population dispositions remain in assembly.yaml. Required fine-pitch local fiducials and exact paste/via realization must be resolved before layout acceptance.

No price or budget ceiling is claimed. A production quote depends on the final outline, stack, drill/via process and populated BOM; those artifacts do not yet exist. Compare qualified vendor quotes before spending and preserve the user's separate purchase authorization. This decision chooses the least complex currently supported design baseline; it does not assert a lowest market price.
