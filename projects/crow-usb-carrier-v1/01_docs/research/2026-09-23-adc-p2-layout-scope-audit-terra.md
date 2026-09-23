# ADC P2 layout-scope audit — 2026-09-23

## Verdict

**P2 ADC/reference placement is incomplete.** The accepted native input board
is `crow_carrier.p2_input_power_source_backtrack_r1.kicad_pcb`, SHA-256
`c3d906591a343aea8949687c05c0f5ff4372e982c5af70a04df4828b7409fd93`.
The final frozen source packet is
`/tmp/crow-p2-adc-reference-prep-20260923/projects/crow-usb-carrier-v1/03_src/floorplan.yaml`,
SHA-256 `467d41cef9e0478a7a8d039c48037eb628422891ad1493058ecbd50fbecaea90`.
Its native in-memory reopen is recorded by `census_predicted.json`, SHA-256
`405d0481a2e3c4b1145a8a2e54df15e8601f2673e68b551320483e8f289aa699`, as
**16/16 numeric rows passing with zero residuals**. Those rows cover 17
reset/VMID support refs. The `adc_reference` population is 64 refs, so 47
refs are intentionally outside that numeric support census. Most
consequentially, all 20 individually named ADC supply/reference capacitors
(ten per ADC) are outside P-ADJ/P-ADJ-PAIR measurement.

This is not a request to invent a manufacturer millimetre limit.  TI gives
qualitative close-placement and return-topology requirements, and P2 needs a
machine-checkable per-ref ownership/observation record for them.  The later
P3/FULL saved-board route proof must establish the direct VREF-to-AVSS copper,
ground-plane/thermal-via implementation, and any actual return path.

## Manufacturer requirements and present observation

TI SBAS992A §8.3.4 (PDF p.30) requires a **minimum 1 uF VREF-to-AVSS**
capacitor.  §11.1 (PDF p.116) says power decouplers must be close to their
device pins, VREF filter capacitors near pin 3, directly short VREF-capacitor
ground to AVSS pin 4 with **no via** in that trace, use ground planes between
device and decouplers, and connect all grounds directly to the central local
ground area; its exposed-pad instruction calls for a via pattern to ground
planes.  These are quantified only for capacitance, not distance.  The exact
local copy is `02_parts/TLV320ADC6140IRTWT/TLV320ADC6140-SBAS992A.pdf`; the
corresponding retained interpretation is `part.yaml:67-77`.

The following are pad-centre measurements on the SHA-bound accepted native
input board (capacitor non-GND pad to the nearest matching `U_ADC_*` pad).
They are diagnostic geometry, **not TI limits or pass/fail thresholds**.
Every listed capacitor has GND on pad 2; the frozen 16-row numeric census does
not grade any of them.

| Device / exact required capacitor | Owning pin | measured span (mm) |
|---|---:|---:|
| A AREG 100 nF / 1 uF | 2 | 8.310 / 6.029 |
| A AVDD 100 nF / 10 uF | 1 or 19 | 4.894 / 4.401 |
| A DREG 100 nF / 1 uF | 24 | 6.140 / 13.259 |
| A IOVDD 100 nF / 10 uF | 1 | 9.741 / 12.745 |
| A VREF 100 nF / 10 uF | 3 | 8.543 / 9.695 |
| B AREG 100 nF / 1 uF | 2 | 10.708 / 8.793 |
| B AVDD 100 nF / 10 uF | 1 or 19 | 4.894 / 4.401 |
| B DREG 100 nF / 1 uF | 24 | 6.140 / 12.324 |
| B IOVDD 100 nF / 10 uF | 1 | 9.341 / 6.547 |
| B VREF 100 nF / 10 uF | 3 | 6.002 / 9.906 |

The VREF 10-uF capacitors satisfy the stated minimum capacitance by nominal
value, but the P2 artifact does not show the required direct ground connection
to AVSS.  That topology cannot be inferred from a refdes-only proximity row.

TI TPS3839 SBVS193D p.15 calls for the optional 0.1-uF VDD/GND bypass
immediately at pins 3/1, and TI SN74LVC1G123 SCES586E p.16 calls for supply
bypass at VCC/GND and local timing R/C around pins 6/7. The frozen source
packet closes all 16 associated engineering-dossier rows. The earlier
`/tmp/crow-adc-source-analysis.json` residuals (including `U_RST2.8 ->
C_RST2.1` and `Q_RST1.3 -> R_RESET_PU.2`) were measured on an earlier,
stale read-only proposal and are retained only as historical diagnostic data;
they are not residuals against the frozen packet.

## What is missing from P2 and who owns it

| Missing P2 requirement | Population | Existing real check | Required source/backtrack action |
|---|---|---|---|
| Per-pin close placement of supply/reference capacitors | all 20 `C_ADC_[A/B]_{AREG,AVDD,DREG,IOVDD,VREF}_{100N,1U/10U}` | None: the placement report has 311 resolved numeric rows but no row naming any of these 20; P-LAYOUT only sees the IC dossier. | **ADC/reference source owner:** add an exact 20-row qualitative P2 placement/observation contract, tied to `U_ADC_A/B` physical pins and each C ref. Do not manufacture an mm maximum. Require a recorded measured span and a local-placement disposition; use the existing source P2 workflow to re-run placement. |
| VREF return topology | each device's VREF capacitor(s), `U_ADC_[A/B].3` and `.4` | None. P-ADJ excludes GND pours and cannot prove a direct trace or absence of via. | **ADC/reference owner, P3/FULL:** reserve the pad-2-to-AVSS direct-return corridor at P2, then verify saved copper: VREF C ground -> pin 4 direct without a via; ground/thermal-pad area connected to planes/via pattern. This must not be waived by a distance record. |
| Local ground-area / exposed-pad thermal return | `U_ADC_[A/B].4`, `.25` plus all decoupler ground pads | None in this P2 proposal; current board is a placement artifact, not a route proof. | **ADC/reference + route owner:** carry exact pin/return reservation into P3 and grade the routed board. Do not infer it from ratlines, zones, or the proposed 16/16 result. |
| Existing reset/VMID numeric closure | 17 proposed refs | Yes: frozen `census_predicted.json` reports 16/16 PASS, zero residual. The earlier three-residual result is historical and superseded. | Closed within the 16-row support-cell scope. This is independent of, and does not close, the ADC per-pin/return scope. |

## Acceptance boundary

`03_src/floorplan.yaml` already names the 20 capacitors and two ADCs in the
`adc_reference` region, and `03_src/modular_plan.json` says the block owns
local analog/digital decoupling and reference/VMID filter banks.  That
population ownership is useful but is not a proximity or return check.
`placement_policy_audit.md` only reports 33 layout blocks and the global
numeric P-ADJ families; a PASS/closure for the 16-row proposal therefore would
not establish the 20 TI requirements.

**Actionable gate:** do not promote ADC/reference P2 based solely on the
frozen 16/16 numeric support census. Backtrack to the ADC/reference source
contract to add the
20-ref qualitative P2 observation/reservation and its explicit P3 return-proof
handoff; then regenerate and measure the P2 candidate.  No board save or
source edit was made by this audit.
