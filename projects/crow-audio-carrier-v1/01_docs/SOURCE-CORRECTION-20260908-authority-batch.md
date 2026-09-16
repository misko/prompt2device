# Source correction handback — authority batch 2026-09-08

Author status: COMPLETE WITH THE COMMISSIONED SCHEMATIC-REVIEW STOP.
Recorded 2026-09-08T04:10:59.187397+00:00. This is author execution
evidence, not independent source adoption, a TaskAttempt, P-AUTH acceptance,
manufacturing allocation, or a release/seal. Root retains independent adoption.

## Outcome and hard boundary

The three authorized source fixes are complete: 25 exact local manufacturer
PDF bindings cover 191 refs; F_IN is corrected from unsupported
2920L260/33MR to manufacturer-documented 2920L260/33DR; the first-match region
fix changes exactly C_LDO_A and C_LDO_D out of 299 source refs. All other
electrical values, pins, footprints, placement anchors, models, pad overrides,
and rule numerics are unchanged. The 33 previously bound used dossiers/PDFs
(108 refs) remain byte-identical. Overall: 77 dossiers, 58 used MPNs, 299 refs,
58/58 used MPNs now locally PDF/SHA-bound. No additional electrical/package
mismatch was found by this bounded inspection.

The existing full producer ran once and reached intentional prelayout exit2.
The fresh public screen passed 51 exact codes / 265 refs / build5, with all
51 returned MPNs matching the requested component identities and 34 excluded
manual refs unchanged. The public-only resume ran once, revalidated prelayout,
recorded the new schematic checkpoint and stopped at PR-REVIEW exit1: seven
stale-binding findings across the two old topology/render witnesses. They were
not edited, rebound, commissioned, or adopted. No schematic-review resume,
board generation, routing, seal, commit or push occurred. HEAD remains
`896dc0ee2c02b09b3e3701bdade06d2e4fcf9186`.

## Authority and recovery

This FRESH exclusive source batch consumed the immutable task envelope
`48ceab6e16435cf1b2ff1ade6c57c024a876880079b466bb7694ebfc80ab3062`
and canonical 15-member packet
`a6cf915d8f1189a467c206ded0859abd6fea41ec343d92795dc8a18e17446c27`.
At 03:46:40.015142Z the exact 382-file before-source census, all 25 candidate
PDF hashes, and 33 existing bindings passed. Packet bytes still pass at handoff,
including its two inherited cosmetic whitespace warnings; no packet was edited.

Before any source or generated mutation, the complete affected project and
external census authority were archived to
`/tmp/carrier-authority-source-20260908.HOlRp3/archive/`.
All 1,045 files / 94,411,104 bytes were rehashed successfully. The archive
manifest SHA-256 is
`9550ae936725e2a35201823b9b65fdeff11b5279d7714486a5399fd01c79e9f2`.
It includes old request/blank response, all three checkpoints, Circuit JSON,
PDF/native/netlist/provenance, PCB/pro/dru, generated evidence and old reviews.
The old MR dossier was recoverably moved to
`/tmp/carrier-authority-source-20260908.HOlRp3/retired/02_parts/2920L260-33MR/`;
the verified archive also retains it. Nothing material was irrecoverably deleted.

At 04:01:31.546063Z exactly the five existing boundary files below were moved
to corresponding `retired/` paths, after byte comparison to the archive. No
receipt existed; none was fabricated. The newly generated 51-row response
remains completely unanswered except its prefilled requested-code column.

| Retired live file | SHA-256 |
| --- | --- |
| `06_build/sourcing/prelayout_request.json` | `6f218d35dadc11a630dc8288ac9056c6b59b2d3ae7a8c824d935d624cfc34f12` |
| `06_build/sourcing/prelayout_response.csv` | `a6c00ed1b8fb438bdcb99cf1f13d9195cd9621a29bfbd3342ee2c1e22232264c` |
| `06_build/checkpoints/prelayout.json` | `92cb9215c69d039c8101b3f34b1bef34869134e6e72b8658a6f6221d4f3ca07e` |
| `06_build/checkpoints/prelayout-inputs.json` | `17cb1a35722e7afb4f5444fb63d7aa13cb5a913a98dd6b82171ae680cff606f3` |
| `06_build/checkpoints/schematic.json` | `7e5afa77c1e71d760752e5e9891fdcd2bf01b88768d9414871c76f6964fa0e4c` |

The public probe writer initially refused its pre-existing output. That exact
old probe was also byte-compared to the archive and recoverably retired; the
existing `probe-bom` command then generated the canonical probe from the new
request. Both probe hashes are identical:
`0d533bb0d036a59c098689fddc83569c5bbfa40d47a120a97246e4b0726f5c4b`.
The one fresh public-stock process had already loaded those identical bytes;
its complete actual output is retained. No old stock verdict was reused.

## Independently inspected PDF bindings

Every listed binary was rehashed, parsed with pdfinfo/pdftotext, and inspected
on the rendered identity/rating/ordering page(s), independently of the capture
author's assertions. Each dossier records the original public URL, actual
local filename/hash/revision/page count, page sections and provenance. The
two Molex rows share the same one-page drawing; the Panasonic binding names
the FK family document rather than the MPN of the source folder.

| Exact used MPN after correction | Refs | Revision; PDF pages | SHA-256 |
| --- | ---: | --- | --- |
| [12105C106K4Z2A](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/12105C106K4Z2A/part.yaml) | 3 | 2025-08-12; 3 | `a0c8f8cbf9da904596c7e5423238ff21f926400eefe9bea7f454bae22a7ebd56` |
| [1812L035/60MR](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/1812L035-60MR/part.yaml) | 8 | GD06/10/24; 8 | `a18b5ceec6d56cd31b20da55341ed1b35a48184f1f7fff8ca8bc6948cd8fb974` |
| [2920L260/33DR](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/2920L260-33DR/part.yaml) | 1 | GD02/13/25; 6 | `e475d42720b26ca785d54a72ad608748af40b8a55fa3d311e6577f485ca4b121` |
| [43650-0200](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/43650-0200/part.yaml) | 1 | D8; 1 | `b8942b95bc3fe4c02171de9e714d99b2688055e249ba1524e3c2a8c3cf78eaa3` |
| [43650-0400](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/43650-0400/part.yaml) | 8 | D8; 1 | `b8942b95bc3fe4c02171de9e714d99b2688055e249ba1524e3c2a8c3cf78eaa3` |
| [CL05B103KB5NNNC](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/CL05B103KB5NNNC/part.yaml) | 2 | 2020-07-17; 38 | `dd7aeac014da7235d687bc41a30cc1bf1366e0b03c81ee46135de1202cb06008` |
| [CL05B104KO5NNNC](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/CL05B104KO5NNNC/part.yaml) | 28 | 2024-04-09; 38 | `4f5a2dcf3dcb4c183cd55320ac4b1b050bbc89f066a0ce86353ece3e56294afd` |
| [CL10A475KO8NNNC](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/CL10A475KO8NNNC/part.yaml) | 2 | 2024-05-09; 38 | `b2081b0b0d43033ef3aca53f8c56f782c170ac3913a91aa847b74e5f7e6557a9` |
| [CL10B224KA8NNNC](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/CL10B224KA8NNNC/part.yaml) | 1 | 2023-01-31; 38 | `00c61e295f03297000302fb2c7b2e5d5557edba7ca3dd0989e872718e9aa89c2` |
| [CL10B474KA8NFNC](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/CL10B474KA8NFNC/part.yaml) | 2 | 2020-07-17; 38 | `30d447eb2ed3b4820d743724c3edea06e58a9327f8a56d12c14f8bdba401f029` |
| [EEEFK1V4R7R](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/EEEFK1V4R7R/part.yaml) | 2 | ABA0000C1181 2026-02-10; 12 | `b36857d089adaddf3042b33bf11d0f7d83bf70734e983f33b7827152e11854e3` |
| [GCM1555C1H681JA16D](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/GCM1555C1H681JA16D/part.yaml) | 16 | 2026-04-05; 32 | `60c98e61fbcb539527be8601d71edea758b1622b3be792f3d2df46f228d6ab00` |
| [GRM188Z71C475KE21D](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/GRM188Z71C475KE21D/part.yaml) | 4 | 01A / 2026-06-19; 33 | `7cf6195efe2cab32c91ce2f768ab63d9d47ebee1677bd7a9c03e7f09e1b81dab` |
| [GRM2195C1H153JA01D](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/GRM2195C1H153JA01D/part.yaml) | 12 | 2026-06-24; 33 | `bbac4b8492989790f1e2223c4f47fb18c9f8fc3731973990a40dcfa70db85b33` |
| [GRM32ER71A476KE15L](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/GRM32ER71A476KE15L/part.yaml) | 6 | 04CA-EN / 2026-06-26; 33 | `fd44194fdabc476650301c34e6e10eeb64d0c7cba90253b20af2371a07fd5ea8` |
| [RC0402FR-070RL](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-070RL/part.yaml) | 1 | generated2026-09-08; 1 | `86e35763f809c9aa780f4e8ad0d3d6f71b57a3d3afdeb5f523837e5a29da9813` |
| [RC0402FR-07100KL](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-07100KL/part.yaml) | 41 | generated2026-09-08; 1 | `e42aa2b39be7476fef25efbe4656acbbc246d2b9b625d64db6b46e0f5e34d7af` |
| [RC0402FR-07100RL](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-07100RL/part.yaml) | 2 | generated2026-09-08; 1 | `96244ed3114a36954eca20d19815a869caeb52e602a77b094ac9e2ce9ced3962` |
| [RC0402FR-0710KL](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-0710KL/part.yaml) | 11 | generated2026-09-08; 1 | `872eab93bd1231c03c3233a57f6499c8069a0235de29e05634166efd4d7979fa` |
| [RC0402FR-0710RL](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-0710RL/part.yaml) | 16 | generated2026-09-08; 1 | `a5371edd5360291d21799763609d8d126f7e6fb4370ee1c0e3f75d773e190e86` |
| [RC0402FR-0722RL](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-0722RL/part.yaml) | 3 | generated2026-09-08; 1 | `01b28f8a26162220412ef880a1d3285563db5888b1bcea06cc142027434262c2` |
| [RC0402FR-07300RL](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-07300RL/part.yaml) | 17 | generated2026-09-08; 1 | `df728c32fc1a7a87bc63c5e3a9b1609759b09f7579f89a185e4be97a43b0c888` |
| [RC0402FR-0733RL](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-0733RL/part.yaml) | 1 | generated2026-09-08; 1 | `fe52a53bfe0a545ac724c21fbd1f6b68d1a6a79d9fd5f23a89eb80fc8635990b` |
| [RC0402FR-074K7L](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-074K7L/part.yaml) | 2 | generated2026-09-08; 1 | `b894ff1ce27e9567b396a6cb9c16750970e4145c03bf64367db0cc8ca107459f` |
| [SMBJ15A](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/SMBJ15A/part.yaml) | 1 | JC.07/04/25 v4; 6 | `d7df155be4b1f612085401e8c946f065e284d65a0e7de22b9225a7b73946e51b` |

### Fact sections and qualifications

- **12105C106K4Z2A** — p1 exact 1210 10uF +/-10%, 50V X7R FLEXITERM identity, dimensions and specified test conditions; pp1-2 plots are typical, not guaranteed effective capacitance. Updated 12.08.2025. Captured public product data identifies this as historical PN and names KAF32LR71H106KU; no substitution is authorized. Source: [12105C106K4Z2A public authority](https://spicat.kyocera-avx.com/datasheet/12105C106K4Z2A); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/12105C106K4Z2A/Kyocera_AVX_12105C106K4Z2A_20260908.pdf).
- **1812L035/60MR** — p2 exact 1812L035/60 electrical row: 0.35A hold, 0.70A trip, 60V, 10A maximum fault current, Rmin 0.400 ohm and R1max 1.700 ohm; p6 dimensions; p7 exact 1812L035/60MR 1000/reel ordering row. Temperature rerating and average trip curves remain reference data, not application qualification. Explicitly supersedes the previously declared unavailable digest b7c31967db6e941770783e852135ff101b831b49aedcf40f25576d4ce2b3cf1e with the actual locally inspected bytes. Source: [1812L035/60MR public authority](https://www.megastar.com/content/pdfs/1812L-Datasheet-Update.pdf); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/1812L035-60MR/Littelfuse_1812L_GD20240610_Megastar.pdf).
- **2920L260/33DR** — p1 exact 2920L260/33 electrical row: 2.60A hold, 5.00A trip, 33V, 40A fault, 0.020/0.075 ohm; p2 70C/85C hold 1.60/1.27A are reference rerating data; p4 package dimensions; p5 exact ordering number 2920L260/33DR, tape-and-reel quantity 1500. This corrects the unsupported MR ordering suffix without changing family electrical limits, pins or footprint. Typical 3W tripped dissipation and average trip curves do not prove enclosure thermal or TVS coordination performance. Source: [2920L260/33DR public authority](https://cdn.promelec.ru/upload/items/2025/09/04/LF/datasheets/2920L-Datasheet-Update.pdf); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/2920L260-33DR/Littelfuse_2920L_Promelec.pdf).
- **43650-0200** — p1 SD-43650-001 D8 released 2024-11-05: exact Finish A 02-circuit 43650-0200 row, 3.00mm circuit pitch, component-side 2-circuit PCB layout, circuit-1 identification and board-edge placement note 6. Drawing capture closes local-byte availability only; mating hardware, latch/service access, tooling and physical seating remain independent holds. Source: [43650-0200 public authority](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/436/43650/436501000_sd.pdf); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/43650-0200/Molex_436501000_SD_revD8.pdf).
- **43650-0400** — p1 SD-43650-001 D8 released 2024-11-05: exact Finish A 04-circuit 43650-0400 row, 3.00mm pitch, 4-12-circuit component-side PCB layout with locating holes, circuit-1 identification and board-edge note 6. Drawing capture closes local-byte availability only; mating hardware, latch/service access, tooling and physical seating remain independent holds. Source: [43650-0400 public authority](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/436/43650/436501000_sd.pdf); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/43650-0400/Molex_436501000_SD_revD8.pdf).
- **CL05B103KB5NNNC** — p1 exact CL05B103KB5NNNC C-suffix identity, dimensions and packaging: 10nF, 50V, X7R, 0402, 10000/reel, +/-10%; p2 specified test conditions. Manufacturer Reference Sheet, not an order-specific approval or guaranteed effective-capacitance curve. Existing engineering screening allocations remain engineering assumptions. Public POST masterKey=CL05B103KB5NNN&type=specsheet. Source: [CL05B103KB5NNNC public authority](https://product.samsungsem.com/part/download.do); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/CL05B103KB5NNNC/Samsung_CL05B103KB5NNN_specsheet.pdf).
- **CL05B104KO5NNNC** — p1 exact CL05B104KO5NNNC C-suffix identity, dimensions and packaging: 100nF, 16V, X7R, 0402, 10000/reel, +/-10%; p2 specified test conditions. Manufacturer Reference Sheet, not an order-specific approval or guaranteed effective-capacitance curve. Existing engineering screening allocations remain engineering assumptions. Public POST masterKey=CL05B104KO5NNN&type=specsheet. Source: [CL05B104KO5NNNC public authority](https://product.samsungsem.com/part/download.do); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/CL05B104KO5NNNC/Samsung_CL05B104KO5NNN_specsheet.pdf).
- **CL10A475KO8NNNC** — p1 exact CL10A475KO8NNNC C-suffix identity, dimensions and packaging: 4.7uF, 16V, X5R, 0603, 4000/reel, +/-10%; p2 specified test conditions. Manufacturer Reference Sheet, not an order-specific approval or guaranteed effective-capacitance curve. Existing engineering screening allocations remain engineering assumptions. Public POST masterKey=CL10A475KO8NNN&type=specsheet. Captured official product page marks NRND; no KO8NQN substitution or active-life assertion is authorized. Source: [CL10A475KO8NNNC public authority](https://product.samsungsem.com/part/download.do); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/CL10A475KO8NNNC/Samsung_CL10A475KO8NNN_specsheet.pdf).
- **CL10B224KA8NNNC** — p1 exact CL10B224KA8NNNC C-suffix identity, dimensions and packaging: 220nF, 25V, X7R, 0603, 4000/reel, +/-10%; p2 specified test conditions. Manufacturer Reference Sheet, not an order-specific approval or guaranteed effective-capacitance curve. Existing engineering screening allocations remain engineering assumptions. Public POST masterKey=CL10B224KA8NNN&type=specsheet. Source: [CL10B224KA8NNNC public authority](https://product.samsungsem.com/part/download.do); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/CL10B224KA8NNNC/Samsung_CL10B224KA8NNN_specsheet.pdf).
- **CL10B474KA8NFNC** — p1 exact CL10B474KA8NFNC C-suffix identity, dimensions and packaging: 470nF, 25V, X7R, 0603, 4000/reel, +/-10%; p2 specified test conditions. Manufacturer Reference Sheet, not an order-specific approval or guaranteed effective-capacitance curve. Existing engineering screening allocations remain engineering assumptions. Public POST masterKey=CL10B474KA8NFN&type=specsheet. Source: [CL10B474KA8NFNC public authority](https://product.samsungsem.com/part/download.do); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/CL10B474KA8NFNC/Samsung_CL10B474KA8NFN_specsheet.pdf).
- **EEEFK1V4R7R** — FK family document ABA0000C1181, not an EEEFK1A471P-only datasheet. p1 specifications/polarity and p2 dimensions; p4 exact EEEFK1V4R7R 35V, 4.7uF +/-20%, size B diameter4.0 x5.8mm row, 90mArms at100kHz/105C, 1.35ohm impedance at100kHz/20C and 2000/tape packaging. General leakage limit and polarity conditions remain applicable; application ripple/noise and physical assembly are not qualified. Source: [EEEFK1V4R7R public authority](https://industrial.panasonic.com/cdbs/www-data/pdf/RDE0000/ABA0000C1181.pdf); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/EEEFK1V4R7R/Panasonic_FK_ABA0000C1181_20260210.pdf).
- **GCM1555C1H681JA16D** — p2 GCM1555C1H681JA16-01A exact family plus D packaging: 680pF +/-5%, DC50V C0G, 0402/1005, dimensions 1.0x0.5x0.5mm nominal, D paper W8P2 10000/reel. Specifications as of Apr.5,2026. Reference sheet requires approval sheet before ordering; typical characteristics and board-level application performance are not guarantees. Source: [GCM1555C1H681JA16D public authority](https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GCM1555C1H681JA16-01A-EN_PDF_CERAMICCAPACITORSMD?lastModifiedDatetime=20260715162731); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/GCM1555C1H681JA16D/Murata_GCM1555C1H681JA16-01A-EN.pdf).
- **GRM188Z71C475KE21D** — p2 GRM188Z71C475KE21-01A exact family plus D packaging: 4.7uF +/-10%, DC16V, 0603/1608, D paper W8P4 4000/reel. X7R(MURATA) Z7 temperature capacitance range +/-15% is specified with 50% rated voltage applied; retain that special qualification. Specifications as of Jun.19,2026. Reference sheet requires approval sheet before ordering; no guaranteed effective-capacitance or placement-performance claim. Source: [GRM188Z71C475KE21D public authority](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM188Z71C475KE21-01A.pdf); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/GRM188Z71C475KE21D/Murata_GRM188Z71C475KE21-01A.pdf).
- **GRM2195C1H153JA01D** — p2 GRM2195C1H153JA01-01A exact family plus D packaging: 15000pF +/-5%, DC50V C0G, 0805/2012, nominal2.0x1.25x0.85mm, D paper W8P4 4000/reel. Specifications as of Jun.24,2026. Reference sheet requires approval sheet before ordering; typical characteristics are not guaranteed application behavior. Source: [GRM2195C1H153JA01D public authority](https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM2195C1H153JA01-01A-EN_PDF_CERAMICCAPACITORSMD?lastModifiedDatetime=20260730165451); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/GRM2195C1H153JA01D/Murata_GRM2195C1H153JA01-01A-EN.pdf).
- **GRM32ER71A476KE15L** — p2 GRM32ER71A476KE15-04CA exact family plus L packaging: 47uF +/-10%, DC10V X7R, 1210/3225, nominal3.2x2.5x2.5mm, L plastic W8P4 1000/reel. Specifications as of Jun.26,2026. Reference sheet requires approval sheet before ordering; typical characteristics do not guarantee effective capacitance or transient performance. Source: [GRM32ER71A476KE15L public authority](https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM32ER71A476KE15-04CA-EN_PDF_CERAMICCAPACITORSMD?lastModifiedDatetime=20260730173643); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/GRM32ER71A476KE15L/Murata_GRM32ER71A476KE15-04CA-EN.pdf).
- **RC0402FR-070RL** — p1 exact RC0402FR-070RL identity and authored resistance value, +/-1%, 0402/1005 dimensions, nominal0.063W at70C (rounded display; retained1/16W limit is not increased), -55..155C, 50V and 178mm tape-and-reel. Generated09/08/2026. Application-suitability disclaimer remains. Nonfatal malformed optional Suspects metadata was observed; text and raster rendering succeeded and exact PDF bytes are preserved. Exact FR zero-ohm part exists; no JR substitution. Nominal zero is not a guaranteed zero-resistance or unbounded-current specification. Source: [RC0402FR-070RL public authority](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-070RL); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-070RL/Yageo_RC0402FR-070RL_20260908.pdf).
- **RC0402FR-07100KL** — p1 exact RC0402FR-07100KL identity and authored resistance value, +/-1%, 0402/1005 dimensions, nominal0.063W at70C (rounded display; retained1/16W limit is not increased), -55..155C, 50V and 178mm tape-and-reel. Generated09/08/2026. Application-suitability disclaimer remains. Nonfatal malformed optional Suspects metadata was observed; text and raster rendering succeeded and exact PDF bytes are preserved. Source: [RC0402FR-07100KL public authority](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-07100KL); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-07100KL/Yageo_RC0402FR-07100KL_20260908.pdf).
- **RC0402FR-07100RL** — p1 exact RC0402FR-07100RL identity and authored resistance value, +/-1%, 0402/1005 dimensions, nominal0.063W at70C (rounded display; retained1/16W limit is not increased), -55..155C, 50V and 178mm tape-and-reel. Generated09/08/2026. Application-suitability disclaimer remains. Nonfatal malformed optional Suspects metadata was observed; text and raster rendering succeeded and exact PDF bytes are preserved. Source: [RC0402FR-07100RL public authority](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-07100RL); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-07100RL/Yageo_RC0402FR-07100RL_20260908.pdf).
- **RC0402FR-0710KL** — p1 exact RC0402FR-0710KL identity and authored resistance value, +/-1%, 0402/1005 dimensions, nominal0.063W at70C (rounded display; retained1/16W limit is not increased), -55..155C, 50V and 178mm tape-and-reel. Generated09/08/2026. Application-suitability disclaimer remains. Nonfatal malformed optional Suspects metadata was observed; text and raster rendering succeeded and exact PDF bytes are preserved. Source: [RC0402FR-0710KL public authority](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0710KL); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-0710KL/Yageo_RC0402FR-0710KL_20260908.pdf).
- **RC0402FR-0710RL** — p1 exact RC0402FR-0710RL identity and authored resistance value, +/-1%, 0402/1005 dimensions, nominal0.063W at70C (rounded display; retained1/16W limit is not increased), -55..155C, 50V and 178mm tape-and-reel. Generated09/08/2026. Application-suitability disclaimer remains. Nonfatal malformed optional Suspects metadata was observed; text and raster rendering succeeded and exact PDF bytes are preserved. Source: [RC0402FR-0710RL public authority](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0710RL); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-0710RL/Yageo_RC0402FR-0710RL_20260908.pdf).
- **RC0402FR-0722RL** — p1 exact RC0402FR-0722RL identity and authored resistance value, +/-1%, 0402/1005 dimensions, nominal0.063W at70C (rounded display; retained1/16W limit is not increased), -55..155C, 50V and 178mm tape-and-reel. Generated09/08/2026. Application-suitability disclaimer remains. Nonfatal malformed optional Suspects metadata was observed; text and raster rendering succeeded and exact PDF bytes are preserved. Source: [RC0402FR-0722RL public authority](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0722RL); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-0722RL/Yageo_RC0402FR-0722RL_20260908.pdf).
- **RC0402FR-07300RL** — p1 exact RC0402FR-07300RL identity and authored resistance value, +/-1%, 0402/1005 dimensions, nominal0.063W at70C (rounded display; retained1/16W limit is not increased), -55..155C, 50V and 178mm tape-and-reel. Generated09/08/2026. Application-suitability disclaimer remains. Nonfatal malformed optional Suspects metadata was observed; text and raster rendering succeeded and exact PDF bytes are preserved. Source: [RC0402FR-07300RL public authority](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-07300RL); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-07300RL/Yageo_RC0402FR-07300RL_20260908.pdf).
- **RC0402FR-0733RL** — p1 exact RC0402FR-0733RL identity and authored resistance value, +/-1%, 0402/1005 dimensions, nominal0.063W at70C (rounded display; retained1/16W limit is not increased), -55..155C, 50V and 178mm tape-and-reel. Generated09/08/2026. Application-suitability disclaimer remains. Nonfatal malformed optional Suspects metadata was observed; text and raster rendering succeeded and exact PDF bytes are preserved. Source: [RC0402FR-0733RL public authority](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0733RL); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-0733RL/Yageo_RC0402FR-0733RL_20260908.pdf).
- **RC0402FR-074K7L** — p1 exact RC0402FR-074K7L identity and authored resistance value, +/-1%, 0402/1005 dimensions, nominal0.063W at70C (rounded display; retained1/16W limit is not increased), -55..155C, 50V and 178mm tape-and-reel. Generated09/08/2026. Application-suitability disclaimer remains. Nonfatal malformed optional Suspects metadata was observed; text and raster rendering succeeded and exact PDF bytes are preserved. Source: [RC0402FR-074K7L public authority](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-074K7L); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/RC0402FR-074K7L/Yageo_RC0402FR-074K7L_20260908.pdf).
- **SMBJ15A** — p2 exact unidirectional SMBJ15A row: VR15V, VBR16.7-18.5V at1mA, VC24.4V atIPP24.6A; p1 600W rating is a 10/1000us pulse rating, not continuous dissipation; p5 DO-214AA dimensions and cathode-band polarity. JC.07/04/25 v4. No board surge, thermal, or fuse-coordination qualification is claimed. Source: [SMBJ15A public authority](https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_smbj_datasheet.pdf); [local exact PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/SMBJ15A/Littelfuse_SMBJ_v4_2025-07-04.pdf).

Littelfuse 1812L was obtained from the public Megastar mirror and 2920L from
the public Promelec mirror. Their dossier provenance preserves original
manufacturer endpoints and capture access failures; no 403/login/captcha
restriction was bypassed. The 1812L actual local hash explicitly supersedes
the old unavailable digest, rather than asserting equality. The preferred
2920L file is 442,112 bytes, GD02/13/25; p5 positively supports DR/1500-per-reel.
F_IN retains 2.60A/5.00A/33V/40A and 0.020/0.075ohm electrical limits,
reference hot-hold values, physical pins and Fuse:Fuse_2920_7451Metric.

F_IN's live assembly/protection consumers now use DR. Its catalog absence is
not falsely asserted: C22870534 is candidate-only, sourcing.lcsc remains null,
TSX jlc remains empty, generated supplier_part_numbers is exactly
`{"jlcpcb": []}`, and assembly exclusion/on_bom:false and manual/consign
handling remain. `consigned: []` and the 34-ref exclusion set are unchanged.
There is no new turnkey allocation, purchase action, or substituted part.

### Scope of the region correction

Only the broad power pattern's C_LDO* selector was replaced by exact
C_LDO_IN, C_LDO_OUT, C_LDO_NR1..NR5 and C_LDO_EN selectors. The existing
later ADC pattern now owns C_LDO_A/D. The regression imports the real
BoardBuilder.initial_pose/patterns_for methods without constructing a board.
The independent archived/current comparison also proves all other floorplan
semantics equal, not merely a sampled pair or a reimplemented matcher.

| Ref census | Before region/initial pose | After region/initial pose |
| --- | --- | --- |
| C_LDO_A, C_LDO_D | power, (47.5,69.0,0,false) | adc, (94.5,70.0,0,false) |
| Other 297 refs | archived exact source state | unchanged |

This is initial regional intent, not legalized physical placement or owning-pin
proximity acceptance. No pad, model transform, anchor or saved PCB moved.

## Execution, verification and actual stops

The required pcb-design, kicad-pcb and jlcpcb-fab skills/contracts governed
the archive-first source reopening, separate exact-source/placement authority,
bounded runtime and public-only prelayout stop. The original producer and
shared tools were used without editing them. All executable runs below used
the existing pipeline_runtime watchdog with explicit cwd/environment snapshot,
600-second hard bound, 10-second heartbeats and durable complete logs.

| Run | UTC start → finish | Elapsed | Actual result |
| --- | --- | ---: | --- |
| [source_tests](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/source_tests.log) | 2026-09-08T04:01:30.746435Z → 2026-09-08T04:01:31.434123Z | 0.688s | 84 tests PASS; raw runtime PASS, rc0 |
| [full_source_producer](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/full_source_producer.log) | 2026-09-08T04:01:41.034676Z → 2026-09-08T04:02:33.793468Z | 52.759s | rc2 intentional prelayout stop; raw runtime FAIL, rc2 |
| [public_catalog_stock](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/public_catalog_stock.log) | 2026-09-08T04:03:21.909517Z → 2026-09-08T04:04:42.971640Z | 81.062s | 51/51 public stock PASS; no allocation; raw runtime PASS, rc0 |
| [public_prelayout_resume](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/public_prelayout_resume.log) | 2026-09-08T04:05:56.453158Z → 2026-09-08T04:05:59.170585Z | 2.717s | rc1 PR-REVIEW stale witnesses; commissioned stop; raw runtime FAIL, rc1 |
| [regenerated_tests](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/regenerated_tests.log) | 2026-09-08T04:06:51.871401Z → 2026-09-08T04:06:52.567346Z | 0.696s | 84 tests PASS on new artifacts; raw runtime PASS, rc0 |
| [final_verification](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/final_verification.log) | 2026-09-08T04:10:58.042806Z → 2026-09-08T04:10:59.093522Z | 1.051s | read-only checkpoint/integrity verification PASS; raw runtime PASS, rc0 |

The raw runtime FAIL labels for nonzero boundary exits are preserved; they are
not rewritten as producer acceptance. Full-arm electrical closure accepted
9/9 specialist gates; selection readiness accepted2/2; S-COUNT matched all
299 refs across the three source pairs. Public resume accepted prelayout
readiness4/4 and verified the 407-file input census and 11-file prelayout
checkpoint before generated writes. The new schematic checkpoint pins7files.
Public stock is the ADR-0006 negative filter only, with no authentication,
allocation receipt, account interaction or procurement. All 51 code/ref/qty
sets and five-board denominators were revalidated, including returned MPNs.

ERC errors:0. All-severity ERC retains2,076 warnings, identical category
census to the archive:1,587 endpoint_off_grid and489 lib_symbol_issues.
These are the inherited converter geometry/synthesized-library warning
classes; no suppression or independent readability acceptance is asserted.
All reports remain available. The regenerated source has40 supplier-fetch
warning records versus47 previously, plus normal source hash/producer metadata
churn; these are not new electrical connectivity. Original tool output is
retained, including the nonfatal KiCad enum and test ResourceWarnings.

Whole generated comparison proves299 component identities and all2,818
electrical source rows (299components,868ports,165nets,1,244traces,241groups,
1board): only F_IN manufacturer MPN changes MR→DR. The native netlist's only
component value change is the same F_IN order string. All165nets,
828connected pin memberships,40NCs and every component footprint are unchanged.

## Fresh exact review subject

These hashes identify the stopped subject, not approval of it. All old
08_reviews witnesses remain verbatim. PR-REVIEW found topology netlist/parts/
rules stale and render PDF/netlist/parts/rules stale (seven findings).

| Subject | SHA-256 |
| --- | --- |
| [03_tscircuit/build/circuit.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/03_tscircuit/build/circuit.json) | `22db91c1bf52ee3a709e8121b9a85e0102f55064ea1efa141d73d6ef5130f1f2` |
| [03_tscircuit/build/schematic.pdf](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/03_tscircuit/build/schematic.pdf) | `339ecaddadc094d08f3efa6317aa57fa2a738d2417a94d1da3967a1cc18cbab2` |
| [04_kicad/crow_audio_carrier_v1.kicad_sch](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/04_kicad/crow_audio_carrier_v1.kicad_sch) | `544999412cdc87aab91ce4c56a98f8b65ddae5ae9d6c4130468c68757469dec8` |
| [06_build/netlists/crow_audio_carrier_v1.net](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/netlists/crow_audio_carrier_v1.net) | `3b2bba539a61e279c3111a80d01087f6978fc4c498a74f194fbb2512c0aea63f` |
| [06_build/build_provenance.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/build_provenance.json) | `6935866736ec216d93d2c97f6f37dd139d0ea726383d58028f8827e20b0a78b8` |
| [06_build/sourcing/prelayout_request.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/sourcing/prelayout_request.json) | `0062b752250bfba1e95ae3940accdf619dc57d7515729bd93753a51eaaa05ce8` |
| [06_build/checkpoints/prelayout-inputs.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/checkpoints/prelayout-inputs.json) | `029fbdff9e256a473e16f171a477f5b2a2ce41b25cd1a6e545fde314fdb0b4c1` |
| [06_build/checkpoints/prelayout.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/checkpoints/prelayout.json) | `3eaff08ee5c56d33d92201a6e72bbf260703dcc0dd2e6cb8c93a4972e0b9a7fd` |
| [06_build/checkpoints/schematic.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/checkpoints/schematic.json) | `f11c43a958506e7fdaf0c4a59a0da5e155568cff566867508a115e314d8cd445` |
| `netlist_semantic_sha256` | `b6da08f18cecc93d43eb7b5ccd87ccbca01ed3c97c450add1e75ad9d6c88d369` |
| `parts_sha256` | `aca88a2ea82cf15bc5f4e4371a0382b009801ca1d6ef9800547e2f2bd4a99904` |
| `design_rules_sha256` | `e5087b6b49a592e47d04c784df48db6806325dfc9f8be06e40a728055f7736a2` |

Saved artifacts intentionally unchanged:

- `04_kicad/crow_audio_carrier_v1.kicad_pcb`: `72f4b136f2c5477167b06861b2636e48be955a6500a27cac867bd267cb4f0abb`.
- `04_kicad/crow_audio_carrier_v1.kicad_pro`: `d679205c674cc988c910a089d6c2a978221c9734c58b57c734daa2aa1eade0ac`.
- `04_kicad/crow_audio_carrier_v1.kicad_dru`: `bd54be05f191ef1c1d7a3819724b10e75ee90daabfa140e4d3c35b6c3b37f823`.
- `03_tscircuit/kicad/crow_audio_carrier_v1.kicad_sch`: `044c0cea6504fc08b0115a60a30e4076d96ea8ae2c05e83159a40b936755acf6`.

The saved PCB still contains the previous MR value and previous physical
placement; that is explicitly stale generated evidence, not a live-source
identity contradiction to fix by hand. The new native schematic is not
promoted over the old deterministic schematic, because PR-REVIEW has not passed.

## Remaining obligations and handback

DO-NOT-ORDER, TOP77-Q1..Q5/N1, first-power HOLD and thermal/current/noise,
effective-capacitance, connector-service/physical-fit unknowns remain.
Source PDF binding is not independent pin/fact/footprint review or a substitute
for approval sheets. No P-AUTH, physical/model-registration, PCB proximity,
routing, production or release gate is claimed to pass in this batch.

The packet's machine placement-policy PASS4/N-A1 covers its one keep_short
constraint; it does not cover every prose-only manufacturer owning-pin layout
requirement. Root's later read-only saved-PCB sample found supply-pad lower
bounds up to44.39mm for C_OPA4/U_AFE4,28.13mm C_ISO5/U_ISO5,23.17mm
C_LDO_IN/U_LDO and11.84mm C_BUCK_BST/U_BUCK. That separate evidence is
`/tmp/carrier-model-adoption-20260908.ZiLzZp/bypass-diagnostic-observed.txt`;
the later-owner plan is NEXT-PLACEMENT.md in that directory, SHA
`a19bb3755f04398ac6f5c44b8ada3601671cda9ff8951f6b3b41b2355e0a6e38`.
These observations did not expand this source task. Root intends independent
source adoption and a separate pin-owner placement-source correction before
paying for fresh exact schematic reviews. Any further source-census change
must follow the existing checkpoint reopening contract, not a manual rebind.

No next conductor/reviewer action is authorized by this handback itself.
The bounded writer relinquishes the source lease here, before the absolute
04:41:51Z deadline. No replacement worker or delegation was used.

## Evidence index

- [initial-integrity.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/initial-integrity.json)
- [archive-manifest.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/archive-manifest.json)
- [authority-adoption-record.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/authority-adoption-record.json)
- [boundary-retirement.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/boundary-retirement.json)
- [source-delta-proof.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/source-delta-proof.json)
- [generated-delta-proof.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/generated-delta-proof.json)
- [final-integrity.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/final-integrity.json)
- [source_tests.log](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/source_tests.log)
- [source_tests.runtime.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/source_tests.runtime.json)
- [regenerated_tests.log](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/regenerated_tests.log)
- [regenerated_tests.runtime.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/regenerated_tests.runtime.json)
- [full_source_producer.log](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/full_source_producer.log)
- [full_source_producer.runtime.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/full_source_producer.runtime.json)
- [public_catalog_stock.log](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/public_catalog_stock.log)
- [public_catalog_stock.runtime.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/public_catalog_stock.runtime.json)
- [public_prelayout_resume.log](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/public_prelayout_resume.log)
- [public_prelayout_resume.runtime.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/public_prelayout_resume.runtime.json)
- [final_verification.log](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/final_verification.log)
- [final_verification.runtime.json](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/verification/authority-source-20260908/final_verification.runtime.json)

Full scratch inspection/parser/raster evidence and diagnostic scripts remain under `/tmp/carrier-authority-source-20260908.HOlRp3`. Author report and start/change/end STATUS/sourcing/schematic/placement journal records are outside the checkpointed design-authority census.
