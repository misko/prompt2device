# Crow microphone pod v3 — v0.2.7 first-article order release

**DESIGN: SOUND**

**PUBLIC SOURCING: CLEAR — all 22 machine-BOM rows clear quantity plus the configured 150-unit surplus**

**ASSEMBLY FULFILLMENT: LIVE UPLOADER CHECK REQUIRED**

**ORDER VERDICT: AUTHORIZED FOR TEN SUPERVISED FIRST ARTICLES**

**QUALIFICATION: FIRST-ARTICLE-ONLY**

This archive authorizes a ten-board first-article order under the exact controls below. JLC places 31 top-side references. J1 and the off-board MK1 capsule remain controlled manual operations; TP1–TP7 remain bare probe pads.

## Upload only these files

- `fab/crow_mic_pod_v3_gerbers.zip`
- `fab/bom.csv`
- `fab/cpl.csv`

Do not mix these files with another release. Public stock observations are not a JLC allocation; save and inspect the live resolved BOM before payment.

## Fabrication selections

- JLCPCB Economic PCBA, quantity 10.
- FR-4, two copper layers, 1.6 mm finished thickness, 1 oz copper.
- Green solder mask, white silkscreen, ENIG 1 microinch.
- Standard two-layer construction, no controlled-impedance service, ordinary tented vias.
- Enable production-file confirmation.

## Assembly controls

1. Confirm exactly 31 CPL placements, all on the top side.
2. Compare every resolved BOM row with `fab/bom_echo_gate.txt`. Any substituted MPN, redirected LCSC code, unresolved row, or automatic substitution stops payment.
3. Confirm U1 and U2 in `fab/rotation_human_gate.txt`; also visually inspect D1, D2, and U3 polarity/pin 1 in the final preview.
4. Keep J1, MK1, and TP1–TP7 excluded from machine assembly.
5. Fit exact Würth 615008160221 at J1 and exact AOM-5024L-HD-R at MK1 after PCBA. Inspect all J1 contacts, shield tabs, guide posts, mouth direction, capsule polarity, wiring, and strain relief.

## Stop before payment if

- any upload file differs from this archive's manifest hash;
- a resolved BOM row is substituted, redirected, or unresolved;
- a placement is on the bottom or U1/U2 orientation is unconfirmed;
- J1 or MK1 appears in machine assembly;
- production files change the outline, drills, copper, or stack.

Retain the final selections, resolved BOM export, placement preview, CAM production files, quote, and order number and bind them to this release in an external order receipt. J1 uses straight-through factory Cat6 patch cord with Crow-specific analog/DC wiring. It is not Ethernet or PoE and must never be connected to network equipment.

## First power and limits

Use a current-limited isolated supply and follow `verification/first_article_test_plan.md`. This release authorizes first-article purchase; it does not claim cable, audio, thermal, mechanical, EMC, environmental, production, or roof-deployment qualification.

## Docs-only successor

v0.2.7 keeps every v0.2.6 fabrication, source, PDF, 3D, BOM, CPL, render, and review byte unchanged. It replaces the blanket no-order wording with the user-authorized ten-board order profile and preserves every live uploader and post-delivery qualification hold.
