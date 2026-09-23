# USB4105 NPTH-to-contact clearance — public-record disposition

**Scope.** Read-only public-record review, 2026-09-23. No board was generated, no source or rule was changed, and no authenticated JLC DFM/BOM action was made.

## Decision

The retained GCT USB4105-GF-A-120 land pattern remains manufacturer-supported, but **public JLC rigid records do not establish that its 0.1944-mm SMD-contact-to-locator-NPTH gap is process-supported**. JLC's rigid capability table publishes NPTH-to-*track* >=0.20 mm, while the current NPTH guide recommends 0.20--0.30 mm copper clearance; neither says that this applies to an SMD pad, nor grants a connector-layout exemption. The nominal gap is 0.0056 mm below 0.20 mm. Keep the four actual DRC findings and exact GCT geometry; do not call them a generic rule exception or alter contact/locator positions.

The preferred public replacement candidate is **GCT USB4215-03-A / LCSC C37616412**: a stocked, horizontal 16-contact USB2 receptacle with SMT contacts and **no locating peg**. Its primary drawing has four plated shell-stake lands but no NPTH locator, so the disputed pad-to-NPTH population is zero. The through-hole-contact USB4085 remains a fallback, but introduces new manual-through-hole assembly scope.

## Actual USB requirement, not the USB4105 headline rating

The circuit is a self-powered USB2 device: the Pi is host, `VBUS_USB` supplies only attachment sensing and must not power `5V_BUCK`, `3V3_ADC`, or the carrier. The connector still needs USB2 D+/D-, both CC pins, VBUS and GND continuity; the present source uses the normal 16-contact USB-C mapping. Thus USB4105's 48 V / 5 A collective VBUS rating is **not a documented system requirement**. It must not be silently downgraded, but it is not a reason to reject a mechanically/process-qualified USB2 receptacle. USB4085 retains the same GCT-published 48 V / 5 A collective VBUS rating anyway.

## Retained geometry and tolerance meaning

USB4105 drawing B4 sheet 1 calls its pattern `Recommended PCB Layout`, tolerance +/-0.05 mm. The retained footprint has two Ø0.65-mm NPTH locators at `(±2.89, -2.605)` and outer 0.60 x 1.15-mm contact lands at `(±3.20, -3.68)`. Native DRC measures the four nearest A1/A12/B1/B12 contact-to-locator edges as **0.1944 mm**. These are intrinsic locator/contact relationships, distinct from its plated shell stakes and from routed tracks.

JLC's blog describes about **+/-0.08 mm finished-hole diameter** tolerance. If used only as an illustrative independent stack, a +0.08-mm diameter increase adds **0.04 mm radial encroachment**, not 0.08 mm. Combining it with two independent +/-0.05-mm relative layout motions would reduce a nominal gap by as much as 0.14 mm. JLC does not publish registration/correlation allocation for this exact feature, so that is a sensitivity illustration, not a factory acceptance calculation.

## Public process authority

| Public record | What it actually says | Disposition |
|---|---|---|
| JLC rigid capabilities | NPTH-to-track >=0.20 mm; min NPTH Ø0.50 mm; non-plated *slot* tolerance +/-0.20 mm. | No SMD-pad-to-round-NPTH clearance or finished round-hole tolerance. Cannot authorize 0.1944 mm. |
| JLC NPTH Design Guide (2026-07-22) | Round NPTH described as finished about +/-0.08 mm; recommends copper clearance about 0.20--0.30 mm. | Relevant conservative guidance, still no specific pad rule. |
| JLC flex capabilities | NPTH-to-copper >=0.20 mm expressly includes pads, tracks and pours. | Do not transfer this explicit flex rule to the rigid board. |

## Alternative screen

| Candidate | Primary package evidence and public stock | Geometry/process outcome |
|---|---|---|
| **GCT USB4215-03-A**, C37616412 | Official GCT drawing A: USB2, horizontal top-mount 16-pin SMT; primary product listing says locating peg without and TH shell stake. `jlcsearch`: stock **1,285**. | **Best package candidate, not adopted.** There are **zero locator NPTHs**, so the USB4105 pad-to-NPTH comparison does not exist. Layout has four plated shell slots, 8.64-mm outside center separation; outer A1/B12 centers are 6.40-mm apart. Thus closest shell-to-outer-contact center separation is `(8.64-6.40)/2 = 1.12 mm`. The drawing's lower-right callouts specify **4x Ø-equivalent 0.60-mm slot width** and **4x 1.00-mm outer copper width**; the outer contact is 0.60-mm wide. Hence contact-copper to shell-copper gap is `1.12 - .30 - .50 = 0.32 mm`, and contact-copper to PTH-slot edge is `1.12 - .30 - .30 = 0.52 mm`. The upper slots are 1.40 mm long in 1.80-mm lands and lower slots 1.80 mm long in 2.20-mm lands, retaining a **0.20-mm minimum land annulus**. These are independent of the nearest A1/B12 and shell pads all being GND. Requires new footprint, exact fit, pin-map and PTH-shell assembly review. |
| **GCT USB4085-GF-A**, C7095263 | GCT product page: active 16-contact USB2 Type-C, horizontal, through-hole PCB mount and shell stake, **locating peg without**, 48 V/5 A. Public `jlcsearch` response: stock **2,167**. | **Concrete replacement candidate.** No NPTH locating pegs, so no USB4105 contact-to-locator check exists. All signal and shell terminations are through-hole: create/review the primary footprint and settle TH population/assembly, mechanical edge location, pin mapping and physical fit before adoption. |
| GCT USB4110-GF-A, C5143397 | Official GCT drawing B4: 16-contact USB2 SMT top mount; recommended layout contains two Ø0.65 holes and gives +/-0.05-mm layout tolerance. `jlcsearch`: stock **3,202**. | **Rejected as a clearance resolution.** It retains locating holes. Its contact array spans 6.40 mm while the locator centers span 5.78 mm, so the outer contact center is only `(6.40 - 5.78)/2 = 0.31 mm` horizontally from the locator center; with a Ø0.65 hole (radius .325 mm), horizontal projection alone overlaps the hole radius before the outer land width is considered. The drawing does not provide sufficient orthogonal pad/locator coordinates to calculate a valid positive edge gap, hence it cannot prove >=0.20/0.25 mm and should not replace USB4105 for this reason. |
| SHOU HAN `TYPE-C 16PIN 2MD(073)`, C2765186 | `jlcsearch`: 16P SMD, stock **1,171,811**. The publicly indexed LCSC-hosted manufacturer PDF identifies 5 V/5 A, but its downloadable data is JS-gated in this environment. | Not a resolution: no reopenable primary land-coordinate extraction/calculation here. Stock and headline rating do not prove contact-to-NPTH clearance or exact pin/physical fit. |
| HCTL `HC-TYPE-C-16P-01A`, C2894897 | `jlcsearch`: 16P right-angle SMD, 20 V/5 A, stock **58,642**. | Not a resolution: no retrieved primary drawing/land geometry. |

## Next repair

1. Preserve the four USB4105 DRC failures and their exact 0.1944-mm measured geometry while the retained package remains selected.
2. If a public-only solution is required before supplier-specific feedback, review **USB4215** first: reproduce the official mixed SMT/PTH-shell footprint, prove the exact 16-contact map and board-edge/keep-out fit, and resolve shell-stake assembly. It removes the disputed NPTH relationship without changing the signal contacts to through-hole. Keep USB4085 as the fallback that also removes it, but needs a new manual-through-hole decision for all contacts.
3. If USB4105 is retained, obtain a feature-specific supplier disposition for SMD pad to round locator-NPTH clearance; public rigid records alone do not close it.

## Evidence and reopenable local captures

* Retained GCT USB4105 B4 drawing: `02_parts/USB4105-GF-A-120/GCT_USB4105_drawing.pdf`, SHA-256 `fb331fbabee8392ed2937ed757c1610cb0f174b84625147c0b580a18eea8c0e5`; [drawing](https://gct.co/files/drawings/usb4105.pdf), [product page](https://gct.co/connector/usb4105).
* [JLC rigid capabilities](https://jlcpcb.com/capabilities/Capab); [JLC NPTH Design Guide](https://jlcpcb.com/blog/npth-design-guide); [JLC flex capabilities](https://jlcpcb.com/capabilities/flex-pcb-capabilities), only to distinguish its non-transferable explicit pad wording.
* GCT USB4085 primary page and drawing: [product page](https://gct.co/connector/usb4085), [drawing](https://gct.co/files/drawings/usb4085.pdf); local `/tmp/gct-usb4085-primary.pdf`, SHA-256 `39afb82c5104579e8c2db4f4e758825c48cab1c4b06d4c61c62056470ff09e9e`.
* GCT USB4110 primary drawing: [drawing](https://gct.co/files/drawings/usb4110.pdf); local `/tmp/gct-usb4110-primary.pdf`, SHA-256 `b083cd7825c1d58d590e9b0ec6e8533ec43711b385d448d7b7a0fd25bd7f4d71`.
* GCT USB4215 primary drawing: [drawing](https://gct.co/files/drawings/usb4215.pdf); local `/tmp/gct-usb4215-primary.pdf`, SHA-256 `1659ba00769b9b774a033fac72cb2f3bfc481a3272c53f34e87520f33635a9e1`; [product page](https://gct.co/connector/usb4215). Raw stock response `/tmp/jlc-gct-usb4215.json`, SHA-256 `d4694044864b9b9f64567008ab9cabe6f32085e5f0e86ac4eade50bb7ae9e993`.
* Raw public catalog responses: `/tmp/jlc-gct-usb4085.json` SHA-256 `5132e94f6f226c493f615e869ac98440a544d4f3b694e77b3e2594cd923503c1`; `/tmp/jlc-gct-usb4110.json` SHA-256 `fbb87c545bbff4a75ac19430cf1e6b7cea3318b550605ae609ea3aed1a76ee95`; `/tmp/jlc-hctl-hc-type-c-16p-01a.json` SHA-256 `6e0369219b8b6ea8a71ab057fdb0721eddf9c9e50f55a7f16a9b1c85f000ac90`; `/tmp/jlc-shouhan-type-c-16pin-2md-073.json` SHA-256 `40201f01fdfd74ef0cffa49fcdf6f4022199921cb51c9cedb7a74df1e91a74c3`.
* Shou Han public primary PDF URL (web-indexed but not locally downloadable because LCSC returns a JS gate): [LCSC C2765186 datasheet](https://datasheet.lcsc.com/lcsc/2111231930_SHOU-HAN-TYPE-C-16PIN-2MD-073_C2765186.pdf).
