# Crow audio carrier v1 — v0.1.7 first-article order release

**DESIGN: SOUND**

**PUBLIC SOURCING: CLEAR — exact public observations clear quantity plus the configured 150-unit surplus**

**ASSEMBLY FULFILLMENT: LIVE UPLOADER CHECK REQUIRED**

**ORDER VERDICT: AUTHORIZED FOR FIVE SUPERVISED FIRST ARTICLES**

**QUALIFICATION: FIRST-ARTICLE-ONLY**

This archive authorizes a five-board first-article order under the exact controls below. It is a partial PCBA package: JLC places 300 top-side references per board; 33 physical references per board are installed afterward. A board assembled only from the uploaded BOM/CPL is intentionally incomplete. Missing U_ADC is a hard stop before power.

## Upload only these files

- `fab/crow_audio_carrier_v1_gerbers.zip`
- `fab/bom.csv`
- `fab/cpl.csv`

Do not mix these files with another release. Public stock observations are not a JLC allocation; save and inspect the live resolved BOM before payment.

## Fabrication selections

- JLCPCB Standard PCBA, quantity 5.
- FR-4, four copper layers, 1.6 mm finished thickness, JLC04161H-7628.
- 1 oz outer copper and 0.5 oz inner copper.
- Green solder mask, white silkscreen, ENIG 1 microinch.
- Controlled impedance selected to bind the named stack; retain submitted artwork.
- Enable production-file confirmation.
- Epoxy fill and copper cap only the twelve 0.60 mm copper / 0.30 mm drill via-in-pad sites named in `fab/order_notes.txt`: nine under U_ADC EP49, two under U_LDO EP15, and one in C_ADC_CM6P pad 2. Keep all 589 ordinary 0.50/0.20 mm vias and every component lead hole unfilled.

## Assembly controls

1. Confirm exactly 300 CPL placements, all on the top side.
2. Compare every resolved BOM row with `fab/bom_echo_gate.txt`. Any substituted MPN, redirected LCSC code, unresolved row, or automatic substitution stops payment.
3. Review all 21 placements in `fab/rotation_human_gate.txt`: U_RST2, U_CLK, U_BUCK, U_AFE1–U_AFE8, U_ISO1–U_ISO8, U_LDO, and D_HOLD.
4. Confirm JLC's stencil treatment for the six excluded SMD references. Either omit paste on those lands or have the qualified manual assembler accept cleanup and later rework after JLC reflow.
5. Fit all 33 declared physical exclusions on every board: U_ADC; F_IN; C_FILT1_470U, C_FILT2_470U, C_HOLD1, C_HOLD2; C_A1P/C_A1N through C_A8P/C_A8N; J1–J11. U_ADC requires qualified QFN reflow or hot-air work and exposed-pad inspection.
6. Reconcile each serialized board to 300 JLC placements plus all 33 manual references before first power.

## Stop before payment if

- any upload file differs from this archive's manifest hash;
- a resolved BOM row is substituted, redirected, or unresolved;
- a placement is on the bottom or any listed rotation is unconfirmed;
- CAM shows anything other than 12 filled/capped and 589 ordinary vias;
- qualified QFN/manual assembly or the excluded-SMD stencil plan is unavailable;
- production files change the outline, drill families, copper, or layer stack.

Retain the final selections, resolved BOM export, placement preview, CAM production files, quote, and order number and bind them to this release in an external order receipt. The eight RJ45 connectors carry proprietary balanced analog audio and isolated DC over factory Cat6 patch cords. They are not Ethernet or PoE and must never be connected to network equipment.

## First power and limits

Use a current-limited isolated 12 V source and follow `verification/first_article_test_plan.md`. This release authorizes first-article purchase; it does not claim electrical, thermal, cable, mechanical, EMC, environmental, production, or roof-deployment qualification.

## Docs-only successor

v0.1.7 keeps every v0.1.6 fabrication, source, PDF, 3D, BOM, CPL, render, and review byte unchanged. It replaces the blanket no-order wording with the user-authorized five-board order profile and preserves every live uploader and post-delivery qualification hold.
