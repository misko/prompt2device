# Unsent JLC review notes — Crow SMT-only carrier and pods

Request for quotation / production-readiness review only. **Not an order or
authorization to buy/reserve parts, substitute parts, charge payment or start
manufacturing.** No submission has been made with this document.

Our functional target is **one SMT-assembled carrier plus eight SMT-assembled
pods**. Please identify the smallest supported carrier assembly lot; the current
draft has five carrier assemblies, but extras have not been adopted. Compare
the five-carrier/eight-pod case separately. The browser presently shows five
bare carriers and ten bare pods; distinguish fabricated from assembled boards.
If one carrier is unsupported, do not silently convert it to five. Any additional
quantity must be stated and approved before commitment.

The attached per-board BOM/CPL files cover **SMT only**: 127 placements per
carrier and 28 per pod. They are not panel/batch BOMs. All through-hole parts,
Pico modules, microphones and buzzers are supplied/installed at home. Do not
quote factory installation or supply of Amphenol RJHSE-5080, Same Sky PJ-102AH,
RECOM R-78E5.0-0.5, Raspberry Pi SC0915, CMA-4544PF-W or CPE-203. Preserve the
open holes and existing paste exclusions for that later completion.

All six exact shortage identities remain required:

| Exact MPN | Installed target 1+8 | Installed five-carrier case 5+8 |
|---|---:|---:|
| CB3LV-3I-12M288000 | 1 | 5 |
| 1206L010/30WR | 16 | 48 |
| GRM21BR71A105KA01L | 10 | 18 |
| C2012X7R1V225K125AE | 8 | 8 |
| C3216X7R1V106K160AC | 2 | 10 |
| PCM1864DBT | 2 | 10 |

Please show required quantities by job including assembly allowances/minima,
usable shared inventory counted once, additional procurement quantities,
packing and charges. Evaluate regular replenishment for the five non-ADC
identities and exact Global Sourcing for **PCM1864DBT, not DBTR**; do not procure
without separate approval. Installed need is not a purchasing instruction.
Distinguish supplier dispatch, usable JLC inventory date and finished-board
production/delivery. If a complete quote needs prepaid stock first, identify
that boundary and all known costs without omitting unselected components.

Use the provided original Gerber ZIPs and retained placement mapping. Review
exact catalog matches, centroids, orientation, polarity and all placement
previews before any production commitment. Carrier R3 uses the explicitly
documented Panasonic ERJ-3EKF68R0V/ERJ3EKF68R0V spelling reconciliation. CTS X1
needs a compatible SMD assembly route despite its manual catalog label.

Construction: retain the released four-layer 1.6 mm boards, carrier 7628A and
pod 7628 requirements. Confirm actual stack, stencil/paste exclusions, rail/
fiducial/fixture/DFM and mechanical/process limits; do not interpret automated
defaults or these short notes as a waiver. Complete applicable retained release
controls must be included in the production review before approval; these notes
are not a substitute. Flag any unsupported requirement for engineering review.

Please itemize fabrication, setup/stencils/feeders, SMT labor, components and
minimum-order surplus, sourcing/import/handling charges, shipping/tax and
timing separately for each job and shared procurement. No home-install labor,
enclosures or roof hardware in the JLC subtotal. Quote validity and any
non-cancelable prepayment exposure must be explicit. No firmware programming
or functional qualification is implied by assembly.
