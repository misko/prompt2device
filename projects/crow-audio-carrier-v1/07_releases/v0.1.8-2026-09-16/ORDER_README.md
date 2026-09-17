# Crow audio carrier v1 — v0.1.8 first-article order release

**DESIGN: SOUND**

**PUBLIC SOURCING: CLEAR — exact public observations clear quantity plus the configured 150-unit surplus**

**ASSEMBLY FULFILLMENT: LIVE UPLOADER CHECK REQUIRED**

**ORDER VERDICT: AUTHORIZED FOR FIVE SUPERVISED FIRST ARTICLES**

**QUALIFICATION: FIRST-ARTICLE-ONLY**

This archive authorizes a five-board first-article order under the exact controls below. JLC places all 306 fitted SMD references on the top side, including U_ADC, F_IN, and the four polarized bulk capacitors. The 27 through-hole references are installed afterward. A board assembled only from the uploaded BOM/CPL is intentionally incomplete until those through-hole parts are fitted.

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

1. Confirm exactly 306 CPL placements, all on the top side.
2. Compare every resolved BOM row with `fab/bom_echo_gate.txt`. Any substituted MPN, redirected LCSC code, unresolved row, or automatic substitution stops payment.
3. Review all 26 placements in `fab/rotation_human_gate.txt`: C_FILT1_470U, C_FILT2_470U, C_HOLD1, C_HOLD2, U_ADC, U_RST2, U_CLK, U_BUCK, U_AFE1–U_AFE8, U_ISO1–U_ISO8, U_LDO, and D_HOLD.
4. Require the resolved uploader row for C42457798 to identify exact CS5308P-DN. If JLC cannot supply it, consign exact CS5308P-DN for JLC placement; do not move it to manual post-assembly work.
5. Fit the 27 declared through-hole exclusions on every board: C_A1P/C_A1N through C_A8P/C_A8N and J1–J11.
6. Reconcile each serialized board to 306 JLC SMD placements plus all 27 through-hole references before first power.

## Stop before payment if

- any upload file differs from this archive's manifest hash;
- a resolved BOM row is substituted, redirected, or unresolved;
- a placement is on the bottom or any listed rotation is unconfirmed;
- CAM shows anything other than 12 filled/capped and 589 ordinary vias;
- JLC will not place the exact U_ADC, F_IN, four polarized bulk capacitors, or any other fitted SMD reference;
- production files change the outline, drill families, copper, or layer stack.

Retain the final selections, resolved BOM export, placement preview, CAM production files, quote, and order number and bind them to this release in an external order receipt. The eight RJ45 connectors carry proprietary balanced analog audio and isolated DC over factory Cat6 patch cords. They are not Ethernet or PoE and must never be connected to network equipment.

## First power and limits

Use a current-limited isolated 12 V source and follow `verification/first_article_test_plan.md`. This release authorizes first-article purchase; it does not claim electrical, thermal, cable, mechanical, EMC, environmental, production, or roof-deployment qualification.

## Release change

v0.1.8 moves U_ADC, F_IN, C_FILT1_470U, C_FILT2_470U, C_HOLD1, and C_HOLD2 into the JLC BOM/CPL, so every fitted SMD is placed by JLC on the top side. The copper geometry is unchanged and was fully rebuilt, routed, and requalified. Fresh public observations cover the five-board quantity plus the configured 150-unit surplus; final JLC mapping, allocation, consignment acceptance, rotations, and CAM selections remain supervised order-time checks.
