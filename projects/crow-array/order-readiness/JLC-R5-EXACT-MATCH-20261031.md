# JLC r5 exact-match check — 31 October 2026

## Saved fabrication settings and incomplete price

Reopened the saved PCB settings on 2026-10-31: carrier shows 5 fabricated,
2 assembled, Economic and top-side assembly; pod shows 10 fabricated, 8
assembled, Standard and top-side assembly. The carrier screen displayed
$37.40 (including $25 engineering and $12.40 board); the pod displayed
$14.00. Both screens showed dashes for components, SMT, hand-soldering and
manual assembly, so these are incomplete preliminary figures, not PCBA
quotes. Each separately displayed a $26.94 UPS Express Saver (DDP) shipping
estimate; neither combined freight nor applicability to a complete assembly
order is confirmed. The displayed times are not arrival dates. No settings
were changed and no placement preview was obtained.

## RECOM mismatch found and contained

In the existing carrier draft, JLC auto-matched U10 to `R-78E5.0-0.5`, JLC `C18212367`. The expanded **Part Info** panel identifies its manufacturer as **YLPTEC**, not the specified **RECOM Power**. This is a different-manufacturer component despite matching MPN text. The row had been selected by automatic BOM processing; it was **deselected** in the saved carrier draft. Its quantity is now zero and the row still shows the YLPTEC match: this is an unresolved required part, not an instruction to omit U10. Do not proceed via “Do not place”. The prior report's apparent $7.1126 line is the YLPTEC selection and is not a valid RECOM quotation.

JLC's [C5199916 listing](https://jlcpcb.com/partdetail/RecomPower-R_78E5_0_05/C5199916) identifies `R-78E5.0-0.5` as **Recom Power**, SIP-3. The carrier draft's public-inventory search for C5199916 displayed JLC stock 0, idle stock 0, account inventory 0 and **Inventory shortage**, rather than an available Select action. The exact listing cannot currently be selected from that result. No alternate part was selected. Placement method/handling and vendor acceptance remain open.

JLC Global Sourcing search displayed the exact `R-78E5.0-0.5 RECOM POWER GMBH`, Sager stock 4,692, MOQ 10, 10 units extended price **$48.05**, and **10–16 business days**. This is an unreserved search-screen estimate, not a committed quote, usable-stock date, final purchase quantity or confirmation of assembly acceptance. No part was added to a cart. Some alternate distributor rows show different minima and lead times, not substitutions; packaging/charges must be verified before choosing a route.

Further inspection of the same Global Sourcing results found a smaller exact
RECOM offer via **DigiKey 945-1648-5-ND**: displayed supplier MOQ **1**, tube
packaging, 32,691 stock, estimated attrition 0, minimum assembly quantity 0,
and **8–14 business days**. Entering the two installed pieces in the quantity
field displayed **$9.69 extended** (1+ $4.8447/unit). This is $38.36 less in
component line cost than the ten-piece Sager candidate, with eight fewer
surplus pieces. It does **not** prove two are the final required purchase
quantity, confirm assembly/handling acceptance, include any applicable fees,
or establish a warehouse-ready date; the two suppliers' terms and pricing can
change. This exact RECOM DigiKey offer is a candidate to ask JLC about first,
not an order. No Add/cart/checkout action was taken.

## Remaining boundary

In addition to the six previously identified SMT shortages, the correct RECOM makes seven exact sourcing identities to resolve for the current r5 build. No safe full-preview/quote path was established: the prior pod NEXT warning says unselected parts would not be placed; no omission was accepted. Global Sourcing parts are usable only once they reach JLC's warehouse, and the existing account warning says pre-order parts cannot be canceled once quotation is finished. Do not initiate a paid or noncancelable workflow under the user’s no-purchase/no-reservation instruction. This is an observed portal limitation, not proof that JLC cannot give an independent informational estimate.

## Subsequent exact-row and manufacturer check

In the carrier draft, eight previously unchecked available rows were selected after checking their JLC codes against the r5 BOM: five Samsung `CL21B104KBCNNNC` / C1711 rows and three Murata `GRM21BR71A106MA73L` / C710992 rows. In the pod draft, two unchecked Vishay `CRCW06031K00FKEAHP` / C844747 rows (R5 and R10/R9) were selected after the same BOM comparison. The YLPTEC U10 remains unchecked; the five carrier and three pod shortage rows remain unfilled. This selection verifies codes/MPN text against the BOM, not every manufacturer's independent identity or physical orientation. JLC's counters are internally inconsistent after selection (carrier 32 confirmed versus 30 rows; pod 20 confirmed plus three shortage versus 21 rows), so do not treat them as coverage or placement evidence.

JLC's [C599441 page](https://jlcpcb.com/partdetail/AmphenolICC-RJHSE5080/C599441) identifies Amphenol ICC RJHSE-5080, matching the r5 manufacturer and MPN. The [C3096093 LCSC listing](https://www.lcsc.com/product-detail/C3096093.html) identifies CUI PJ-102AH, and the [Same Sky manufacturer datasheet](https://jp.sameskydevices.com/product/resource/pj-102ah.pdf) records the CUI Devices rebrand to Same Sky in 2024. Its 2024 drawing's displayed 14.4 mm length, 10.7/3.0 mm longitudinal and 4.7 mm lateral geometry agrees with the dimensions used in the r5 legacy-drawing center derivation. The manufacturer also records a 2023 reengineering; the actual supplied revision, detailed dimensional tolerance, factory installation method and complete preview still need confirmation. These are identity and dimension checks, not final factory or mechanical acceptance.

The [manufacturer's PCN index](https://jp.sameskydevices.com/quality/pcn-notifications) associates `PCN-0450722R-01` with PJ-102AH, but its linked PDF returned HTTP 403 in this review. A separately indexed PDF that contains the same PCN number names **PJ-090BH**, not PJ-102AH; do not treat that different-product notice as evidence for the jack's 2023 change. The 2024 PJ-102AH datasheet and the selected lot's details remain the appropriate evidence pending the correct PCN or manufacturer clarification. No mechanical hold is closed by this observation.

The carrier draft's expanded Part Info was also checked directly for its two
unavailable IC/oscillator matches. C2863172 explicitly identifies **Texas
Instruments PCM1864DBT**, package labeled `TFSOP-30-175mil`, and SMT assembly;
this establishes the portal's manufacturer/MPN text, not stock or placement.
Although its linked TI datasheet URL ends in `pcm1865`, the [TI document](https://www.ti.com/lit/ds/symlink/pcm1865.pdf)
explicitly covers the PCM1864 family member as well. C17275161 identifies
**CTS Electronic Components CB3LV-3I-12M288000**, package SMD7050-4P; the portal
still labels its assembly type Wave Soldering. These observations do not settle
TI packing and package-label reconciliation, oscillator handling, actual stock,
or factory acceptance. Both remain shortage rows; no selections or purchases
were made in this check.

### Manufacturer evidence for oscillator and ADC package

The [CTS CB3/CB3LV datasheet, revision K](https://www.ctscorp.com/Files/DataSheets/Passives/FCP/Clock-Oscillators/clock-ocillators-CB3_CB3LV-datasheet.pdf),
page 4, identifies a surface-mount package and specifies reflow per J-STD-020,
with a maximum of 260°C for 20 seconds; it lists MSL 1. Page 6 includes the
12.288 MHz frequency. This supports reflow as a manufacturer-documented
process for the specified series, despite JLC's Wave Soldering label; it does
not establish why JLC uses that label or that JLC will apply an acceptable
profile. Obtain JLC's confirmation and retain all other process controls.

JLC's own [assembly FAQ](https://jlcpcb.com/help/article/pcb-assembly-faqs)
says parts marked “wave soldering” in its library are assembled manually,
and describes a manual-soldering charge and added assembly day. This makes the
CTS label a substantive process and cost question, not evidence that its SMD
oscillator will be reflowed. Ask JLC whether its general description applies
to C17275161, whether it can use the CTS-specified reflow process, and what
temperature/time controls, price and schedule it would apply if manual. No
manual process or added charge has been accepted or verified for this job.

The [TI PCM1864 datasheet](https://www.ti.com/lit/ds/symlink/pcm1864.pdf)
identifies PCM1864DBT as a 30-pin DBT TSSOP in tubes. Its DBT0030A drawing
specifies a 4.3–4.5 mm body width, 7.75–7.85 mm length and 0.5 mm lead
pitch, consistent with the r5 BOM's `TSSOP-30_4.4x7.8mm_P0.5mm` footprint
description and the 175-mil (4.445 mm) width in JLC's package label. This is
a nominal-dimension reconciliation, not verification of land pattern, pin-1
orientation, lot packaging or assembly preview. The exact `PCM1864DBT` suffix
remains required; JLC's source and handling must still be confirmed.

#### ADC land-pattern comparison

Read-only inspection of the released carrier's native U1 and U2 footprints
found 30 pads each, arranged as 15 per side at 0.5 mm pitch, with pad numbers
1/15/16/30 at the same four corners as TI's DBT0030A example when viewed in
footprint-local coordinates. Both use 1.475 × 0.300 mm copper pads and
5.725 mm between pad-column centers; TI's example shows 1.500 × 0.300 mm and
5.800 mm. Thus pad length is 0.025 mm shorter and column spacing 0.075 mm
narrower than TI's example. TI calls its pattern an example and notes that
alternate designs exist; these differences are not by themselves a failure
or an engineering acceptance. No stencil, solder-mask, tolerance-stack or
assembled-board inspection is implied. Native U1 and U2 are rotated 180°
relative to each other; r5 CPL lists 0° and 180° respectively. JLC library
rotation convention is not established, so verify each pin-1 position in the
actual factory preview and do not change rotations on this evidence alone.

### Inventory pooling and preview constraints

JLC's [own-parts instructions](https://jlcpcb.com/help/article/how-to-use-my-own-parts-for-pcb-assembly-order)
say public plus pre-order stock may be combined for the same component, and
Global Sourcing plus consigned stock may be combined; other combinations for
the same component are unsupported. For global/consigned stock below a job's
needs, the page says the system uses sufficient public stock instead, not a
mixed pool. Therefore do not add the fuse's seven public units to a global
shortage quantity unless JLC confirms an exception, and do not count that
seven independently for both jobs. This is per-order guidance: allocation
between the two jobs and actual attrition remain to be confirmed.

JLC's [component matching guidance](https://jlcpcb.com/help/article/component-matching-guidelines-for-pcba-orders)
says private sourced or consigned components must be received, stored and
selected to proceed, and unselected parts are treated as unplaced. This
supports the observed portal blocker; it does not rule out an informational
estimate or preview provided outside the self-service flow. No inventory was
ordered or reserved.

## Draft support inquiry — UNSENT

> Please provide an informational, non-binding assessment only for our existing PCBA drafts: two assembled carriers and eight assembled pods, including all 478 SMT placements and 28 through-hole placements. Please do not reserve or purchase stock, substitute parts, create a noncancelable procurement quotation, charge us, or start production. If a requested answer requires one of these actions, identify that boundary first.
>
> Our carrier U10 requires **RECOM Power R-78E5.0-0.5**. Your automatic match C18212367 lists manufacturer YLPTEC and has been deselected. Exact RECOM C5199916 shows no available stock in our account. Your Global Sourcing screen showed a DigiKey 945-1648-5-ND tube offer with MOQ one and an illustrative two-piece line of $9.69. Can you confirm whether this exact offer is eligible, the required quantity including allowances, packaging and handling fees, usable warehouse date, and compatible through-hole assembly method? Please compare consignment if it cannot be used.
>
> Please also confirm exact sources and per-job required quantities for CB3LV-3I-12M288000, 1206L010/30WR, GRM21BR71A105KA01L, C2012X7R1V225K125AE, C3216X7R1V106K160AC and PCM1864DBT. Are the seven fuses shown in both jobs one shared pool, and can each job use its proposed source without mixing prohibited pools? Please include attrition, inspection/3C fees if applicable, packaging and warehouse arrival estimates.

> Your FAQ says library parts marked wave soldering are assembled manually, whereas CTS specifies reflow for CB3LV. Does that FAQ apply to C17275161, and can you reflow it within the CTS datasheet limits? If manual assembly is proposed instead, please state its process, thermal controls, charge and timing for review before any commitment.
>
> Is there a way to review complete component placement previews and obtain an itemized, non-binding 2-carrier/8-pod estimate with all required parts before paying for any shortage inventory? Please itemize boards, components, SMT/THT labor, setup/stencil, sourcing/handling, shipping and taxes, and note all unknowns and assumptions. Identify any process controls you cannot support; no preview or production approval is implied.

Draft IDs and the r5 file manifest should be provided privately only if requested and authorized. No supplier message, order, cart addition, reservation, substitution or manufacturing approval was made in this pass.
