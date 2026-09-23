# Current-source JLC public-stock refresh — 2026-09-23

Read-only public-catalog snapshot for source HEAD ee1de6b0. Scope is the current
exact-parts.csv census: 509 references and 89 exact MPN rows. Exact CSV
SHA-256: 4b4977e99d52d972db2bf6f8bab5fa240bcb2f30293deb148480229d6fe5f61c. This is an inventory screen only; observations
are dated and become stale. Sufficient public stock is not JLC PCBA reservation,
uploader acceptance, attrition confirmation, or purchase authority.

## Method and census

Exact-code queries used the existing jlc_stock_check endpoint:
https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList
They ran serially with a 1.21-second minimum inter-request delay. Raw
timestamped JSON response envelopes are in raw/ and each per-row timestamp and
SHA-256 is in manifest.json.

- 86 coded current populated lines queried: all 89 current MPN rows less the
  two D9 manual-THT MPN rows and uncoded U_ADC.
- D9 excluded exactly 24 manual references: J1-J8 / 615008160221 and
  C_A1N/P through C_A8N/P / R82DC4100CK60J. No query or JLC verdict is made
  for them in this screen.
- U_ADC / CS5308P-DNR has no selected LCSC code and remains unresolved.
- J_PWR / 43650-0200 / C192562 is not D9-excluded and was included. It
  observed stock 3,886 against threshold 155, exact normalized identity
  436500200, at 2026-09-23T04:48:25.812623Z; raw SHA-256
  f8563d25ddcbf3dec32c36ed804364a09b6642d534420bbc2f2e381adb57c749.
- Build quantity is five and D7 buffer is 150. Each threshold is
  5 times aggregated refs per board plus 150.

Receipt manifest: manifest.json. It lists 90 raw files/results: 86 current
populated selected exact codes and four research-only candidate codes.
manifest-initial-generic-labels.json preserves the preliminary proposal-label
attempt. Two candidate expected-input labels were corrected locally from
generic family names to exact returned MPNs, using retained responses only;
no network query followed and no stock observation changed.

## Selected-source result

84 of 86 coded populated current lines clear the public-stock threshold and
have exact returned-model identity agreement. Two current selected SMD lines
fail D7; U_ADC is separately uncoded:

| Current selected exact part / code | Qty per board; threshold | Observation timestamp; stock | Result |
|---|---:|---:|---|
| TMUX2821DSGR / C53283916 | 8; 190 | 2026-09-23T04:47:39.762158Z; 16 | LOW_STOCK. Exact returned model/brand: TMUX2821DSGR / Texas Instruments. Raw 072_selected_C53283916.json SHA-256 2a0720e67cb58ccab40144946c84ffd7da2a300f8724faa63b677f425c195eb5. |
| XU316-1024-TQ128-C24 / C6362698 | 1; 155 | 2026-09-23T04:48:00.768983Z; 46 | LOW_STOCK. Exact returned model/brand: XU316-1024-TQ128-C24 / XMOS. Raw 085_selected_C6362698.json SHA-256 2eee961ca010e21b02a94a691a72351c088fd37c5a21b08d87a3d25895d4f050. |
| CS5308P-DNR / no code | 1; 155 if a code were selected | not queried as exact selected-code lookup | UNKNOWN / unresolved. Current CSV and source retain no selected JLC code. D5 still requires a JLC-populated SMD ADC; this screen cannot assign a substitute. |

No selected coded row returned a model-identity mismatch. The raw manifest is
the complete exact-code audit trail for passing rows as well as these failures.

## Distinct research-only proposal screen

These four records were deliberately queried as proposals, not current BOM
lines. Their quantities are the requested prospective per-board quantities,
not inferred current selection counts.

| Exact proposal / code | Qty per board; threshold | Returned exact model; stock | Screen result |
|---|---:|---|---|
| TLV320ADC6140IRTWT / C1852023 | 2; 160 | TLV320ADC6140IRTWT; 188 | Exact identity and public threshold pass. Raw 086_candidate_C1852023.json SHA-256 68b7e7299126930efc71ae62213e859aac9f1165886a2a864888266061fcb8f8. |
| TMUX4827YBHR / C22428234 | 8; 190 | TMUX4827YBHR; 5,437 | Exact identity and public threshold pass. The preliminary generic expected label TMUX4827 was corrected against the retained response, without another network request. Raw 087_candidate_C22428234.json SHA-256 6c145687553c6925732f0e2ede92c3972f22bc124f94855d199d03c74870a2f6. |
| TCA9406DCUR / C840107 | 1; 155 | TCA9406DCUR; 16,905 | Exact identity and public threshold pass. The preliminary generic expected label TCA9406 was corrected against the retained response, without another network request. Raw 088_candidate_C840107.json SHA-256 7ca5ca9e9b2ec706caab29ce2440c0f89ca43f6fb1f4066eabf151172e426987. |
| Murata GRM32ER71A476KE15L / C84494 | 42; 360 | GRM32ER71A476KE15L; 56,458 | Exact identity and public threshold pass for this distinct 42-per-board proposal. It does not change the selected current 10-per-board line. Raw 089_candidate_C84494.json SHA-256 94b89775a5e6fa882410af257228f2844850ade5a54bc0242d2035fb74fac241. |

A catalog pass above is necessary supply evidence only. It does not approve
any candidate's electrical/mechanical architecture, alter the selected 89-MPN
BOM, reserve stock, or establish JLC placement/process availability. Recheck
the actual selected BOM in JLC's uploader at order time.

