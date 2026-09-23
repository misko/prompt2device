# Stocked TPS62825 inductor qualification (read-only, 2026-09-23 UTC)

## Disposition

**Defensible source candidate: Coilcraft XFL4015-471MEC, JLCPCB C18221164.** The TI TPS62825 datasheet Table 8-5 expressly recommends `XFL4015-471ME` at 0.47 µH, 6.6 A and 8.36 mΩ. Coilcraft's current primary datasheet lists the fully orderable `XFL4015-471MEC` and states the trailing **C is 7-inch machine-ready reel packaging**, with the same `ME` electrical/termination part. Direct JLCPCB SMT endpoint returned **3,051** pieces at the time of query, above the 3 inductors/board × 5 boards + 150 extra = **165** requirement by 2,886. This is a better-supported candidate than Chilisin C329374 because TI recommends the Coilcraft electrical part and Coilcraft supplies both SRF and typical DC-bias curve.

## Electrical check

* Exact value 0.47 µH ±20%; TI Table 8-3 anticipates -30%/+20% effective L (0.329–0.564 µH). Coilcraft's published *typical* L-versus-DC-current plot is about 0.44 µH at the existing screened maximum 1.79 A, above TI's 0.329 µH screen. The plot is typical, not a guaranteed hot minimum; TI's own recommendation is the stronger source-level basis.
* Coilcraft Isat at 25 °C is 3.5 A for 10% drop, 5.4 A for 20%, **6.6 A for 30%**. The 1.79 A existing screened peak is 27% of the 30%-drop rating; TI asks for approximately 20–30% saturation headroom over calculated Ipeak, and this part exceeds it on listed ratings. (The same existing 1.79 A computation assumes 5.05 V input, 2.2 MHz typical fSW, and 0.329 µH effective L; recalculate if the input maximum or fSW screen changes.)
* DCR 7.60 mΩ typical / **8.36 mΩ maximum at 25 °C** versus current Würth 14 mΩ maximum per its own drawing. Even using 1.79 A as a conservative RMS ceiling gives only 26.8 mW at 25 °C; actual hot copper loss needs the DCR-temperature factor and board thermal context. Coilcraft's 40 °C rise Irms is 11.2 A in its test setup, far above this design screen but not a board-level thermal guarantee.
* Coilcraft reports **89 MHz typical SRF**, around 40× the 2.2 MHz typical switching frequency. TI does **not** specify a numerical SRF acceptance threshold in its TPS62825 selection section; the claim is evidence of margin, not a new invented pass/fail rule. Coilcraft's primary frequency plot places the 0.47 µH curve essentially flat near 2.2 MHz.
* The existing output bank appears to be 2×47 µF nominal (94 µF). TI Table 8-3 checks 0.47 µH with 10, 2×10/22, and 47 µF, but its **100 µF cell is blank** for TPS62825. That pre-existing stability/startup/transient qualification remains open for *either* the retained Würth or this Coilcraft. A source substitution cannot claim that bank TI-proven. Do not alter the cap bank in this task.

## Physical / adoption gate

Coilcraft primary drawing gives body 4.0 ±0.3 × 4.0 ±0.3 mm, 1.60 mm maximum height and **recommended pads 0.98 × 3.4 mm on 2.37 mm pitch** (centres ±1.185 mm). Existing Würth native footprint has 1.5 × 2.4 mm pads on **3.70 mm pitch** (centres ±1.85 mm); it **cannot be reused**. A dedicated Coilcraft native footprint, pad-net escape/routing check, and enclosure/adjacency/thermal check are required before an adopted source commit or PCB fabrication. Coilcraft says the terminal with its start/short-lead marking should connect to high dv/dt SW for lowest EMI; honor this orientation. Its 20 V operating-voltage rating exceeds the 5 V rail in this application.

## Alternatives checked

* **Chilisin MHCI05030-R47M-R8 / C329374:** direct JLC stock 2,619, 0.47 µH ±20%, 8 mΩ max DCR, 14 A typical at -30% L, 10 A typical Irms/40 °C. Manufacturer series PDF has no SRF or hot L(I) model. Electrically plausible, but Coilcraft has explicit TI recommendation and stronger frequency/bias evidence. Its body and recommended lands also require a new footprint.
* **TDK TFM201610ALC-R47MTAA / C2045043:** TI-recommended exact MPN, but direct JLC SMT stock **2**, failing 165 despite stale third-party search inventories showing higher quantities. Do not count it as stocked.
* Exact TI-listed TDK `TFM201610ALM-R47MTAA`/C501954 was observed at 61 via search, also below 165. A near-suffix TDK listing needs manufacturer identity proof before any use.

## Primary evidence and stock method

* [TI TPS62825 datasheet SLVSEF9I](https://www.ti.com/lit/ds/symlink/tps62825.pdf), §§8.2.2.3–8.2.2.4, Tables 8-3/8-5, pages 12–13.
* [Coilcraft XFL4015 manufacturer datasheet, Document 769 rev. 2026-03-10](https://www.coilcraft.com/getmedia/84927b8b-f089-421b-a7f4-a0fa23afe908/xfl4015.pdf), pages 1–2; [exact Coilcraft product configuration](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xfl/xfl4015/xfl4015-471/).
* [Chilisin MHCI05030 manufacturer series PDF](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/MHCI05030_2D00_4R7M_2D00_R8.pdf), exact R47 row; [Würth retained drawing](https://www.we-online.com/components/products/datasheet/744373240047.pdf).
* JLCPCB live endpoint, POST `https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList` with JSON `{ "currentPage":1, "pageSize":10, "keyword":"C18221164" }`; record's `componentLibraryType=expand`, `stockCount=3051`, `erpComponentName="470nH ±20% 6.6A"`, matching [LCSC exact listing](https://www.lcsc.com/product-detail/Power-Inductors_Coilcraft-XFL4015-471MEC_C18221164.html). Stock is time-varying; refresh before order.

No repository files were edited for this qualification.
