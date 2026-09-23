# P2 input/quiet-power qualitative-scope audit — 2026-09-23

## Verdict

The 47/47 `p2_input_power` numeric result on accepted native board
`c3d906591a343aea8949687c05c0f5ff4372e982c5af70a04df4828b7409fd93` is
valid **for its declared P-ADJ/P-ADJ-PAIR rows**. It is not complete
input/quiet-power placement acceptance. Of the 89 owned refs, 48 appear in
one or more numeric rows and 41 do not. The unscored set contains the entire
TPSM63603 main-buck bypass/control/current-loop cell, plus fixed hold-bank and
LT3045 qualitative-return items.

Prior P2 language should therefore say: **“47/47 declared numeric rows PASS;
qualitative buck/return/thermal placement and later saved-copper proof remain
open,”** rather than “input/quiet-power placement accepted.” No passed numeric
fact is invalidated.

## Population disposition

| Disposition | Refs | Count | What is proven / still required |
|---|---|---:|---|
| Numeric P2 coverage | 48 refs including entry protection, precharge/dump, supervisors, timing, LT3045 input/output/ILIM/PGFB pairs | 48 | 47 declared rows pass (6 P-ADJ, 41 P-ADJ-PAIR). This proves only those named non-ground spans. |
| Main-buck qualitative cell, no numeric row | `U_BUCK`; `C_IN1/2/3`, `C_IN_HF`; `C_OUT1/2/3`; `C_VCC`, `C_VLDO`; `R_BUCK_FB_TOP/BOTTOM`, `R_RT`, `R_AGND_JOIN`, `J_PWR` | 15 | Must be treated as one local buck cell: input/output capacitor current loops, VCC/VLDO bypass, FB sense/AGND return, RT and PGND/thermal implementation. |
| Hold/LDO qualitative or later-physical items, no numeric row | `C_HOLD1..16`, `C_LDO_NR4/5`, `C_OPA_BULK`, `C_PWR_CT2/3`, `R_LDO_PG_BOT_A/B`, `R_LDO_SET`, `R_OPA_BLEED1/2` | 26 | Hold capacitors are intentionally fixed-bank anchors; they need storage-path/thermal/copper proof. LT3045 SET/NR/PGFB-return topology and downstream bulk are not established by the passed local rows. |

The counts reconcile exactly: 48 numeric-covered + 15 main-buck qualitative +
26 hold/LDO qualitative = 89 owned refs. This is a coverage classification,
not an assertion that the 41 parts are electrically incorrect.

## Exact authority and measured diagnostic geometry

TI TPSM63603 SLVSFS5A §7.3.11 requires a high-quality **1-uF VCC-to-AGND**
capacitor close to the device and permits a 0.1–1-uF VLDOIN capacitor for noise
immunity (p.22). Sections 7.3.2–7.3.4 require the FB divider at the regulation
point and account for input/output capacitor behavior; §10 supplies the layout
example. The retained dossier
`02_parts/TPSM63603RDHR/part.yaml:12-19` preserves these requirements but has
no `keep_short` or `adjacency` row, so the policy census cannot observe them.

These accepted-board pad-centre spans are diagnostics only, not manufacturer
distance limits:

| U_BUCK relation | Pads | span mm |
|---|---|---:|
| VCC bypass | `U_BUCK.23 -> C_VCC.1` | 10.383 |
| VLDOIN bypass | `U_BUCK.22 -> C_VLDO.1` | 8.520 |
| FB divider upper / lower | `U_BUCK.25 -> R_BUCK_FB_TOP.2` / `.25 -> R_BUCK_FB_BOTTOM.1` | 10.936 / 12.042 |
| Input capacitors, VIN terminals | nearest `U_BUCK` VIN pads to `C_IN1/2/3/C_IN_HF.1` | 3.692 / 3.266 / 6.209 / 5.512 |
| Output capacitors, VOUT terminals | nearest `U_BUCK` VOUT pads to `C_OUT1/2/3.1` | 3.495 / 9.670 / 7.891 |

Because switching-loop validity also depends on the return path, layer and
actual copper, these centre-to-centre values cannot close or fail the TI
qualitative requirements. They demonstrate why the ungraded cell must remain
visible. In particular, the 10.383-mm C_VCC diagnostic is not evidence for
the required close bypass.

ADI LT3045 Rev. D pp.11–22 requires Kelvin OUTS to the output capacitor/load,
direct COUT/SET ground association, low-ESR/ESL output capacitance and
appropriate input capacitance. The existing dossier correctly scores the
chosen `C_LDO_IN`, `C_LDO_OUT_1/2`, ILIM and PG-top relationships, but its
own notes identify the unscored CSET/NR and return/EP concerns:
`02_parts/LT3045EDD-PBF/part.yaml:36-40`. The complete return and EP11-via
implementation remains a P3/FULL saved-board check, rather than a new P2 mm
budget.

## Required qualification boundary

1. Keep the 47/47 result as the numeric P2 receipt.
2. Before describing the 89-ref power block as electrically placed, add a
   source-owned qualitative P2 observation/reservation for the 15-ref buck
   cell: C_VCC at pin 23, C_VLDO at pin 22, input/output capacitor banks,
   FB divider to pin 25/AGND, PGND/thermal-pad and switch-current corridors.
   It must record observed pairing/return reservation without inventing a
   manufacturer millimetre maximum.
3. Retain the 26 fixed-bank/LDO refs as explicit qualitative dispositions;
   P3/FULL must verify actual copper returns, Kelvin topology, thermal vias,
   high-current loop area and capacitor connection topology.

No source, board, policy, or generator was modified.
