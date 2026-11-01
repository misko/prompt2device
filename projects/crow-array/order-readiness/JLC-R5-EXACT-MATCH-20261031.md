# JLC r5 exact-match check — 31 October 2026

## RECOM mismatch found and contained

In the existing carrier draft, JLC auto-matched U10 to `R-78E5.0-0.5`, JLC `C18212367`. The expanded **Part Info** panel identifies its manufacturer as **YLPTEC**, not the specified **RECOM Power**. This is a different-manufacturer component despite matching MPN text. The row had been selected by automatic BOM processing; it was **deselected** in the saved carrier draft. Its quantity is now zero and the row still shows the YLPTEC match: this is an unresolved required part, not an instruction to omit U10. Do not proceed via “Do not place”. The prior report's apparent $7.1126 line is the YLPTEC selection and is not a valid RECOM quotation.

JLC's [C5199916 listing](https://jlcpcb.com/partdetail/RecomPower-R_78E5_0_05/C5199916) identifies `R-78E5.0-0.5` as **Recom Power**, SIP-3. The carrier draft's public-inventory search for C5199916 displayed JLC stock 0, idle stock 0, account inventory 0 and **Inventory shortage**, rather than an available Select action. The exact listing cannot currently be selected from that result. No alternate part was selected. Placement method/handling and vendor acceptance remain open.

JLC Global Sourcing search displayed the exact `R-78E5.0-0.5 RECOM POWER GMBH`, Sager stock 4,692, MOQ 10, 10 units extended price **$48.05**, and **10–16 business days**. This is an unreserved search-screen estimate, not a committed quote, usable-stock date, final purchase quantity or confirmation of assembly acceptance. No part was added to a cart. Some alternate distributor rows show different minima and lead times, not substitutions; packaging/charges must be verified before choosing a route.

## Remaining boundary

In addition to the six previously identified SMT shortages, the correct RECOM makes seven exact sourcing identities to resolve for the current r5 build. No safe full-preview/quote path was established: the prior pod NEXT warning says unselected parts would not be placed; no omission was accepted. Global Sourcing parts are usable only once they reach JLC's warehouse, and the existing account warning says pre-order parts cannot be canceled once quotation is finished. Do not initiate a paid or noncancelable workflow under the user’s no-purchase/no-reservation instruction. This is an observed portal limitation, not proof that JLC cannot give an independent informational estimate.

## Subsequent exact-row and manufacturer check

In the carrier draft, eight previously unchecked available rows were selected after checking their JLC codes against the r5 BOM: five Samsung `CL21B104KBCNNNC` / C1711 rows and three Murata `GRM21BR71A106MA73L` / C710992 rows. In the pod draft, two unchecked Vishay `CRCW06031K00FKEAHP` / C844747 rows (R5 and R10/R9) were selected after the same BOM comparison. The YLPTEC U10 remains unchecked; the five carrier and three pod shortage rows remain unfilled. This selection verifies codes/MPN text against the BOM, not every manufacturer's independent identity or physical orientation. JLC's counters are internally inconsistent after selection (carrier 32 confirmed versus 30 rows; pod 20 confirmed plus three shortage versus 21 rows), so do not treat them as coverage or placement evidence.

JLC's [C599441 page](https://jlcpcb.com/partdetail/AmphenolICC-RJHSE5080/C599441) identifies Amphenol ICC RJHSE-5080, matching the r5 manufacturer and MPN. The [C3096093 LCSC listing](https://www.lcsc.com/product-detail/C3096093.html) identifies CUI PJ-102AH, and the [Same Sky manufacturer datasheet](https://jp.sameskydevices.com/product/resource/pj-102ah.pdf) records the CUI Devices rebrand to Same Sky in 2024. Its 2024 drawing's displayed 14.4 mm length, 10.7/3.0 mm longitudinal and 4.7 mm lateral geometry agrees with the dimensions used in the r5 legacy-drawing center derivation. The manufacturer also records a 2023 reengineering; the actual supplied revision, detailed dimensional tolerance, factory installation method and complete preview still need confirmation. These are identity and dimension checks, not final factory or mechanical acceptance.

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

## Draft support inquiry — UNSENT

> Please provide an informational, non-binding assessment only for our existing PCBA drafts: two assembled carriers and eight assembled pods, including all 478 SMT placements and 28 through-hole placements. Please do not reserve or purchase stock, substitute parts, create a noncancelable procurement quotation, charge us, or start production. If a requested answer requires one of these actions, identify that boundary first.
>
> Our carrier U10 requires **RECOM Power R-78E5.0-0.5**. Your automatic match C18212367 lists manufacturer YLPTEC and has been deselected. Exact RECOM C5199916 shows no available stock in our account. Can you quote the exact RECOM part through Global Sourcing or consignment and confirm packaging, quantity including allowances, fees, usable warehouse date, and compatible through-hole assembly method?
>
> Please also confirm exact sources and per-job required quantities for CB3LV-3I-12M288000, 1206L010/30WR, GRM21BR71A105KA01L, C2012X7R1V225K125AE, C3216X7R1V106K160AC and PCM1864DBT. Are the seven fuses shown in both jobs one shared pool, and can each job use its proposed source without mixing prohibited pools? Please include attrition, inspection/3C fees if applicable, packaging and warehouse arrival estimates.
>
> Is there a way to review complete component placement previews and obtain an itemized, non-binding 2-carrier/8-pod estimate with all required parts before paying for any shortage inventory? Please itemize boards, components, SMT/THT labor, setup/stencil, sourcing/handling, shipping and taxes, and note all unknowns and assumptions. Identify any process controls you cannot support; no preview or production approval is implied.

Draft IDs and the r5 file manifest should be provided privately only if requested and authorized. No supplier message, order, cart addition, reservation, substitution or manufacturing approval was made in this pass.
