# Four-part TI ADC analog boundary: 18-net endpoint accounting

**Research-only negative packet.** `build_trial.py` binds the exact four-part
ADC7 board SHA `046019a13094764baef313d62611b137e0f0af971079734c71ab050dbf46b3a0`,
the authoritative modular plan, the merged USB/VBUS research packet, the
unchanged access-only ADC7 portal, and the current checker. It changes no
canonical source/board/checker or stock record and is not a P1 attempt.

`adc_analog_boundary` covers **18 nets and 88 exact source/native F.Cu pad
members**: `ADC1N/P` through `ADC8N/P` have four terminals each (64 total),
while `VMID1_EXT` and `VMID2_EXT` have 12 each (24 total). Every native net
has exactly the declared terminal set. No net fails branch cardinality: all
18 have at least three members and cross source owners.

The old `analog_1_4` and `analog_5_8` ordinary nine-slot reservations and
their broad witnesses are removed. The 16 ADC N/P nets receive individual
geometry-free `unresolved_multiterminal_branches` with all 64 exact endpoint
rows, one P2 pad-to-tree obligation per terminal, a P3 connected-tree edge
lower bound, filled In1.Cu GND return debt, null capacity, and no bbox. The
branch validator accepts all 16. `ADC8N` records one foreign-region blocker:
`C_ADC_AC8N1.2` is inside its `analog_ch8` owner but also enters
`usb_vbus_sense`. This is placement debt, not a region waiver.

Both VMID nets are blocked by **native owner containment**, not endpoint
count. On `VMID1_EXT`, `R_B1P.2`, `R_B2P.2`, `R_B3P.2`, and `R_B4P.2` lie
0.24–0.78 mm east of the corresponding `analog_ch1`–`analog_ch4` east
boundary. On `VMID2_EXT`, the same is true for `R_B5P.2` through `R_B8P.2`
relative to `analog_ch5`–`analog_ch8`; `R_B8P.2` enters `usb_vbus_sense`.
The exact pad and owner bboxes are in `endpoint_ledger.json`. Red checker
trials reject the first offending pad of each VMID net with `branch pad
outside source owner region`. Both VMID nets therefore retain null capacity
and explicit P2/P3/return debt in the ledger, with no invented branch or
replacement signal reservation in the coarse contract.

The unchanged ADC7 access-only portal `[166,83.9,167.12,85]` mm remains a
**separate, null-capacity** local screen for ADC7N/P's eight pads. Its eight
pad-to-port obligations and filled-return debt are retained; it contributes
no branch reservation or route credit. The board's four-part placement and
portal are not generalized into ADC1–8 path capacity.

The full hash-bound evaluator reports **zero analog item diagnostics**, one
`INCOMPLETE` no-credit ADC7 portal, and no USB item diagnostics. Aggregate
P1 still **FAILS**: the analog allocation is missing per-net boundary
witnesses for the two unrepresentable VMID nets. Because allocation credit
is all-or-nothing, the 16 individually valid branch representative uses
also generate 16 global denominator errors. This is the expected fail-closed
schema/floorplan result: `p1_accepted=false`, no analog capacity or return
proof. It does not imply those branches are physically routed.

Reproduce from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-adc-analog-88-accounting-sol/build_trial.py
```
