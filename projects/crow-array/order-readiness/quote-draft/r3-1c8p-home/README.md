# Revised procurement and JLC submission preparation — 1 carrier / 8 pods

2026-10-31 PDT. **Prepared locally, not submitted or production-approved.**
This revision supersedes r1/r2 only for current batch quantities and manual-work
ownership. It retains the released exact parts, SMT BOM/CPL geometry and Gerbers.
No substitutions, purchases, inventory reservations or manufacturing commitments.

## 1. Choose a batch before buying components

| Scenario | Assembled carriers / pods | Candidate bare boards | JLC SMT placements | Home parts to finish all assemblies | Total installed parts |
|---|---|---|---:|---:|---:|
| A — desired target | 1 / 8 | 5 / 10 if those fabrication choices remain necessary | 351 | 35 | 386 |
| B — observed five-carrier case | 5 / 8 | 5 / 10 | 859 | 79 | 938 |

Bare quantities are candidates from the browser session, not approved purchases.
Two extra bare pods receive no components. Keep fabrication and assembly
quantities separate in the portal. In B, four extra assembled carriers receive
508 additional SMT components; they do not create four additional arrays.

**Five is not a demonstrated minimum.** The retained browser report showed
two/five assembly choices and JLC currently publishes prototype assembly from
two boards. One assembled carrier is therefore a target unsupported by the
observed standard flow, not a submit-ready quantity. Before committing to five,
price the smallest supported carrier quantity (including two if still offered),
or obtain an explicit one-unit exception. Do not adopt extra assemblies merely
because a draft already contains them. This document shows the requested A/B
comparison; neither is purchase approval.
[JLC prototype guidance](https://jlcpcb.com/solutions/pcb-prototype-assembly),
checked 2026-10-31; browser evidence is retained in `../../PCBA-SESSION-20261031.md`.

If B is chosen only to meet a vendor quantity, the four extra carriers can remain
SMT-only spares. Then buy the **35 home parts for one array**, not all 79. The
79-column below describes completing all five carriers, not mandatory purchases.

## 2. Six exact SMT shortages — batch procurement plan

These are installed quantities, not final purchasing quantities. No quantities
from the portal are silently transferred between scenarios.

| Exact MPN | A: 1+8 need | B: 5+8 need | Preferred candidate | Retained Oct 30 regular minimum / observed global offer |
|---|---:|---:|---|---|
| CTS CB3LV-3I-12M288000 | 1 | 5 | JLC replenishment; exact DigiKey global fallback | Regular minimum 4; global 5 at $10.69, displayed 8–14 business days |
| Littelfuse 1206L010/30WR | 16 | 48 | JLC replenishment; exact Mouser global fallback | Regular minimum 14; global minimum 27, displayed 10–20 business days |
| Murata GRM21BR71A105KA01L | 10 | 18 | JLC replenishment | Regular minimum 407; historical 407-line estimate $9.04 |
| TDK C2012X7R1V225K125AE | 8 | 8 | JLC replenishment | Regular minimum 62; historical 62-line estimate $9.14 |
| TDK C3216X7R1V106K160AC | 2 | 10 | JLC replenishment | Regular minimum 14; historical 14-line estimate $9.16 |
| TI PCM1864DBT | 2 | 10 | Exact DigiKey JLC Global Sourcing, tube | Observed 10 at $104.88, displayed 8–14 business days; **10 was an offer query, not a proven global MOQ** |

Source: retained `../../JLC-PRICING-20261030.json`; these are observations,
not current guaranteed prices, private inventory or warehouse-arrival promises.
Regular replenishment arrival dates are unknown. Reconfirm exact selected
offers/quantities once the actual assembly batch is chosen, not through another
35-part catalog sweep. Minimum orders may exceed small-array needs but cheap
passive surplus can cost less than another supplier/shipment.

Request one consolidated JLC procurement proposal for the selected scenario:
gross demand by board job (including actual attrition/assembly minima), usable
allocated stock, whole-order additions, packing, fees and arrival dates. Each
part's purchase quantity is the supplier's allowed order multiple/minimum applied
to **the summed job demand minus only uniquely allocated usable stock**.
For global/consigned versus regular pools, confirm eligibility before any credit.
Do not manufacture allowance numbers from generic percentages.

The Oct 31 session's 5+8 screens reported Murata shortages of 20 carrier and
20 pod, and TDK pod shortage 10 despite only eight installed: retain those
allowances, do not overwrite them with this table. Fuse screens each showed
seven available, with shortfalls 35 and three. If those are the same seven
units and implied gross demands are 42 and ten, total shortfall would be 45,
not 38. This is a double-counting illustration, **not an adopted purchase qty**;
allocation and pool identity must establish the actual value.

Fallback is exact external procurement/consignment only for lines JLC cannot
supply on acceptable terms. `shortage-parts.csv` retains specific external leads.
Compare delivered cost, intake packing/fees, deposits and receipt date before
selecting it; no direct shipment or procurement is authorized. Do not replace
PCM1864DBT with DBTR without separate qualification. RECOM is now externally
purchased for home installation, not part of the JLC Global Sourcing plan.

## 3. Home-install list

| Exact manufacturer / MPN | Per carrier | Per pod | A: finish one carrier + eight pods | B: finish five carriers + eight pods |
|---|---:|---:|---:|---:|
| Amphenol RJHSE-5080 | 8 | 1 | **16** | **48** |
| Same Sky PJ-102AH | 1 | 0 | **1** | **5** |
| RECOM R-78E5.0-0.5 | 1 | 0 | **1** | **5** |
| Raspberry Pi SC0915, original Pico | 1 | 0 | **1** | **5** |
| Same Sky CMA-4544PF-W | 0 | 1 | **8** | **8** |
| Same Sky CPE-203 | 0 | 1 | **8** | **8** |
| **Total** | **11** | **3** | **35** | **79** |

The newly home-owned THT portion is 18 parts for A or 58 for B. The total
includes the earlier Pico/acoustic allocation too. No inventory-on-hand or
spare allowance is assumed; actual purchases subtract confirmed existing stock
and add only approved spares. The machine-readable list has exact refs and
retained DigiKey leads. Those external links are leads, not a fresh stock/price
check for the new quantities. No need to buy JLC's observed ten-unit RECOM
global minimum for a home-installed single module; compare a direct single-unit
exact offer at the procurement decision.

Home-work checklist, under the retained maker/process limits:

1. Before soldering, check incoming exact identities, footprint/pin patterns,
   finished holes and free fit; do not force, ream or substitute. Match RJ jack
   orientation to native refs, not a guessed pin-1 centroid. Inspect SMT joints
   and keep the released exclusions open for home completion.
2. Install RJ/PJ/RECOM with the retained orientation and seating controls; check
   U10 input/GND/output against the actual module drawing before attachment.
   DC pad 1 is center-positive, pad 2 sleeve ground and pad 3 NC. Inspect hidden
   solder fill and shorts as required by the retained assembly instructions.
3. Pico remains original SC0915 with **module D1 only** removed under the retained
   controlled procedure, never carrier D1. Preserve all other module circuitry,
   inspect/record the modification and all castellations. The user-accepted
   prototype fit risk is not a reason to reopen geometry or waive electrical
   checks. No header/Pico H/W/2 substitution.
4. Hand solder microphones/buzzers last using maker thermal limits; no
   reflow/wave/wash of those parts. Microphone pad 2 is case/GND; buzzer marked
   plus is pad 1. Protect acoustic ports; symmetric lead spacing is not polarity
   evidence. Perform unpowered polarity/bridge/short inspection before a
   separately planned current-limited bring-up.

This checklist indexes, not replaces, the retained
[detailed assembly instructions](../../../releases/crow-prototype-v3-first-run-5c10p-public-v1/historical/documentation/carrier/instructions/32-assembly-instructions.md).
Historical batch totals/provider-ownership
statements there are superseded here; per-unit electrical/handling limits remain.
The original release is unprogrammed/unqualified hardware, not a promise of
working eight-channel recording firmware on delivery.

## 4. Submit-ready file organization, with production approval still held

Use **only these six data files** when an authorized JLC quote/review session
asks for files. Both scenarios use the same per-board data; portal quantities
and purchase lists change, not the BOM rows.

| Board | Gerbers | SMT-only BOM | SMT CPL | Per-board JLC placements |
|---|---|---|---|---:|
| Carrier | `carrier-gerbers.zip` | `carrier-bom.csv` | `carrier-cpl.csv` | 127 |
| Pod | `pod-gerbers.zip` | `pod-bom.csv` | `pod-cpl.csv` | 28 |

All six are byte-identical to r1's SMT-only files/ZIPs. No THT, Pico, microphone
or buzzer is in JLC's BOM/CPL. Do not use r1's full BOM, r2's NOT-UPLOAD manual
template or obsolete 60-operation schedule. `JLC-SUBMISSION-NOTES.md` is an
unsent text to accompany review; CSV scope/procurement/home lists and scenarios
are internal planning, not additional vendor BOMs.

The 32 exact SMT identities remain in scope, including every shortage. Global
ADC's public C-code is not usable private inventory; its BOM code remains blank
pending exact global matching. Preserve all 25 original mapped rotation offsets
and validate vendor preview/pin-1/cathode orientation. Native geometry/centers
were checked previously in r1; this revision changes neither and retains its
hash binding. No fresh vendor preview or independent engineering acceptance.

**Production gates still open:** supported/adopted assembly quantity; all exact
parts available to both jobs including allowances; approved matching/placement
previews; exact stack/stencil/paste-exclusion/rails/DFM/mechanical/process
compatibility; complete price/schedule; explicit user spending/manufacturing
approval. No shortage may be dropped to reach a price. If the portal needs
parts purchased before completing its quote, return the exact procurement
commitment for a separate decision; do not pay to discover a final price.

## 5. Cost and practical recommendation

No complete current A or B PCBA total is established. Do not scale the old
$227.71 seven-line 5/10 estimate: it includes now-home-installed RECOM and
different purchase quantities. Compare these buckets separately: JLC exact
SMT components/minima/attrition, bare fabrication, setup/stencil/SMT labor,
sourcing fees, shipping/tax, and direct home parts. Deposits and surplus are
separate, not free. No enclosures, roof hardware, host Pi, PSU or cables here.

1. Preferred: retain one working array as the target; ask for the smallest
   supported carrier PCBA lot and eight pod assemblies, then resolve the six
   exact shortages together. Compare two/five carriers before accepting extras.
   If five is chosen, complete only one at home unless extra finished carriers
   are explicitly wanted. Exact parts/no redesign minimizes engineering changes.
2. Fallback: exact externally sourced consignment for failed lines, or await
   the existing PCBWay 1+8 inquiries as an alternative. PCBWay still includes
   factory THT assembly, so its preliminary $29/$88 assembly-only amounts are
   not directly comparable and are not total board prices. Do not update/contact
   PCBWay without authority or assume its notes were changed.

Next external action would be an authorized consolidated quantity/sourcing/job
review, using the unsent notes—not another full stock search. Preparation here
does not authorize submission, purchase, reservation or manufacturing. Draft
publication is authorized on `codex/crow-jlc-source-review-20261030`, not main.

## MacBook continuation — quantity and six shortages only

Update a clean checkout of that branch with `git fetch origin` and
`git merge --ff-only origin/codex/crow-jlc-source-review-20261030`; preserve
dirty work or use a fresh sibling clone instead of resetting it. Run the
verification command below before using the files. The original session
report is evidence to resume from, not proof of today's account inventory.

Check actual carrier assembly choices and keep eight assembled pods distinct
from ten bare pods. If two carriers are the smallest supported option, report
that choice and compute its installed demand from `procurement-plan.csv`'s
per-board columns; do not label it one or five, or silently adopt it. Compare
the five-carrier case separately. Then inspect exact offers for the six parts
in `shortage-parts.csv`: per-job allowances, shared usable stock, purchase
minima/multiples, packaging, itemized fees and arrival estimates. No new full
catalog pass. Home-installed RECOM stays outside JLC's sourcing requirement.

Use read-only screens or the user's already-authorized non-binding draft actions.
Before any new upload, vendor submission/contact or cart action outside that
scope, ask for specific permission. Stop at payment, reservation or parts-order
requirements; record the exact boundary rather than dropping missing parts.
One pass, at most 30 minutes of active browser work, with one normal retry per
failed screen. Save a new dated result and update STATUS; preserve earlier
observations, privacy and supplier-pool distinctions. Return two ranked paths,
their complete known costs and explicit gaps; no purchase or production approval.

Suggested prompt:

> Follow local vNext and projects/crow-array/order-readiness/quote-draft/r3-1c8p-home/README.md
> on codex/crow-jlc-source-review-20261030. Verify r3, check the smallest supported
> JLC carrier assembly quantity with eight assembled pods, and compare five
> carriers separately. Inspect the six exact SMT shortage offers and prepare one
> consolidated quantity/cost/arrival proposal, avoiding shared-stock double counting.
> All THT/Pico/acoustic installation is at home. Use only authorized non-binding
> draft actions; no purchases, payments, reservations, substitutions or production
> commitments. Save dated evidence and stop at any new authorization boundary.

## Reproduce / verify

```sh
python3 -B projects/crow-array/order-readiness/home_assembly_plan.py verify
python3 -B -m unittest discover -s projects/crow-array/order-readiness -p 'test_*.py'
python3 -B projects/crow-array/publication.py verify
```

`home_assembly_plan.py build --output UNUSED_PATH` reproduces data into a new
directory. Manifest binds the original r1 checks, current browser evidence and
generator. No original release, earlier quote revision or observation is edited.

Validation: 35 order-readiness tests plus 15 publication tests pass (50 total),
including six new scenario/ownership/tamper regressions. All 256 original payloads
are preserved; r1 verification still passes. This is data consistency and source
preservation, not new engineering or vendor production acceptance.
