# USB4215 final source/mechanical review — Terra

**Review binding:** clean `/tmp/crow-usb4215-source-20260923` commit `3cd02b44940eb9aca8879d56f47796f7d4365cfa`, compared with `723d2746`. This replaces the prior review file collision. No project file or generated board was changed.

## Verdict

**Mechanical source correction: PASS. USB4215-focused alias/native fixture: PASS. Source-package adoption can proceed subject to the normal fresh composed-source checks; physical/placement adoption is not established.**

The initial review failure is retained as history: the first USB4215 commit placed the body/Fab/model mouth at `+2.245 mm`, 0.760 mm behind the sheet-1 front outline, and the courtyard ended 0.255 mm short of it. Commit `3cd02b44` corrects the published `5.15 mm` contact-edge-to-lower-slot relation, slot centers, Fab outline, drawing-derived VRML and courtyard. The correction resolves that specific defect.

## Drawing-to-source check

| Item | Final implementation | Review |
|---|---|---|
| Upper/lower shell-slot centers | `y=-3.105` / `+0.895 mm`, four slots total at `x=+/-4.32 mm` | Matches the source derivation: 1.15-mm contact land and sheet-1 5.15-mm contact-leading-edge-to-lower-slot-center dimension give 4.575 mm center separation; the 4.00-mm slot separation gives the upper coordinate. |
| Slots and lands | upper 0.60 x 1.40 drill in 1.00 x 1.80 land; lower 0.60 x 1.80 drill in 1.00 x 2.20 land | Correct. Minimum annulus is 0.20 mm and there are no NPTH locators. |
| Body/mouth | front `y=+2.995 mm`, back `y=-3.505 mm` | Correct arithmetic: lower slot `+0.895` plus explicit 2.10-mm front-outline dimension; 6.50-mm body depth establishes the back. VRML and F.Fab agree. This is a nominal component front/mouth datum, **not** a mating-plane or PCB-edge datum. |
| Courtyard | `x=-5..+5`, `y=-4.76..+3.50 mm` | It contains the contact lands at the rear and body front with nominal 0.50-mm margin. This corrects the prior front exclusion. It remains a source courtyard, not installed-service clearance. |
| Contacts/aliases | 16 logical A/B contacts, 12 SMT locations, four declared fused same-function GND/VBUS pairs, plus `SH` on four PTH shell slots | The MPN, dossier, TSX, native footprint, parity map, route lanes and RF launch agree. A6/B6 retain D+, A7/B7 D−; CC1/CC2 remain separate; SBU remains NC; VBUS remains sense-only; shell identity remains retained. |

The drawing-derived model is properly labelled non-GCT CAD. Its corrected `+Y` mouth direction supports later orientation work only. The board-edge/mating-plane registration, a board rotation, exposure, cable clearance, shell-stake assembly method and physical fit remain owed.

## Source-contract and fixture status

The committed USB4215 connector-assembly receipt is **INCOMPLETE**, with 45 evidence facts: 14 exact + 12 conservative = **26 evidenced**, and 19 unknown. Its USB row correctly retains the intended board `-Y` service direction as an intent only and says an accepted 180-degree footprint rotation is needed to map the local `+Y` mouth there. This is appropriate disclosure, not placement approval.

The older dedicated native test remains hard-coded for USB4105 and is not evidence for this part. It is superseded for USB4215 scope by the retained, actual-source fixture at `06_build/verification/usb4215_alias_fixture/`, bound to `3cd02b44940eb9aca8879d56f47796f7d4365cfa`. Its `run.py` SHA-256 is `4a2c53dcd064a9752038c9fa84183e23e4baa4e8fb1d28fa09992317fb9c91f5`; `result.json` is `cf709cfb9a2b254f7a35311975debfc287c29ad1ae47b6e17cfa5e4744465402`; parity DRC is `712b081b612805ebff6bd1da28b5f4ed21196f685728cff1d774e6dc0844d4ef`.

The fixture proves the exact dossier/footprint/converter path for all 17 aliases: 12 unique SMT locations, four SH PTH pads, zero NPTH, correct same-net fused pairs, A8/B8 unconnected, D+/D− A/B pairs and `SH=GND` as actually composed in `crow_carrier.tsx`. Native KiCad reports zero violations and zero schematic-parity issues; its eight unconnected items are the expected un-routed/NC fixture items. The negative fixture (`negative_fused.py`, SHA-256 `8b2e181d02f71f4cfc252ceb4886fc85e73c40ee194364cde514102e1e966649`) forces the partner in each fused pair to the opposite rail. Each of four cases produces both `shorting_items` and `solder_mask_bridge` findings (results SHA-256 `fc60c565e02f329bbf4de5a058394e6af113ab8814cef45517ad55215172dbd5`). This closes the previously identified alias-fixture gap. A fresh full composed-source expansion remains a separate normal adoption check, and the connector receipt's 26/45 evidence count remains physical-contract disclosure rather than electrical parity proof.

## Evidence

* Primary drawing: `02_parts/USB4215-03-A/GCT_USB4215_A.pdf`, SHA-256 `1659ba00769b9b774a033fac72cb2f3bfc481a3272c53f34e87520f33635a9e1`.
* Final footprint: `03_src/lib/crow_usb_carrier_v1.pretty/GCT_USB4215_03_A.kicad_mod`, SHA-256 `64d46bb6685897b550f76af541711d607a9b51b4ddc0c6421cab608ef9c6cb80`.
* Final drawing-derived envelope: `03_src/lib/3dmodels/derived/GCT_USB4215_03_A_envelope.wrl`, SHA-256 `80854b13500ee9b552bc974fb52d0028c85a2bb05b76e02f519d5d2ff93db027`.
* Connector receipt: `06_build/verification/connector_assembly_contract_usb4215_candidate.json`, status `INCOMPLETE`, 26/45 evidenced facts.
