# Assembly mapping checkpoint — draft, not upload-ready

Current worksheet: `procurement-map-20261026-v3.csv`; v1/v2 are retained history.
V2 corrected TDK/Panasonic fallback locators using OR3 evidence; v3 records the
user-selected assembly split only, without refreshing inventory observations.
Generated from the immutable 38-identity demand and per-reference population,
31 catalog leads and exact supplier observations. Total: 1,000 installed parts
for five carriers and ten pods. No quantities for attrition are invented.

## SMT routing candidates

| Disposition | Exact identities |
|---|---:|
| Exact JLC catalog identity with positive supplier availability | 11 |
| Exact LCSC identity with sufficient displayed availability; JLC eligibility unconfirmed | 14 |
| External/global-sourcing/consignment candidate | 7 |
| Total SMT identities | 32 |

These are sourcing-route candidates, not qualified factory BOM rows. Package,
usable PCBA pool, packaging/attrition and vendor orientation still need review.
LCSC stock is not automatically JLC assembly stock. Manufacturer spelling
equivalences are explicit in `catalog_mapping.py`; no MPN suffix is removed.
The CUI PJ-102AH lead remains an identity-review item, not an automatically
accepted Same Sky alias. Wrong-maker RECOM-name and Littelfuse-name search hits
were rejected, as was TLV9062IDR-MS. No substitute adopted.

`catalog-observations-20261026.json` retains exact supplier offers and JLCSearch
responses, URLs, retrieval times and hashes; six OR3 records retain their original
timestamps. Insufficient published counts override InStock badges (the Littelfuse
PTC offer has 13 versus 50 installed need). JLCSearch counts are never substituted
for usable supplier inventory. External offers already recorded remain fallback
leads, with their OR2/OR3 freshness limitations; no new shortage claim is made.

## The 80 remaining manual components

“Manual” describes the released assembly process, not who must perform it.
User selected JLC for the 60 connectors/regulators and user installation of the
20 acoustic parts, in addition to the five Picos. JLC's scope is requested,
not yet submitted or accepted.

| Part | Per carrier | Per pod | Batch total | JLC consideration |
|---|---:|---:|---:|---|
| Amphenol RJHSE-5080 jacks | 8 | 1 | 50 | Normal THT assembly category; exact part/process and existing fit/seating controls need matching. No blanket JLC limitation identified. |
| Same Sky PJ-102AH power jack | 1 | 0 | 5 | Normal THT category; current round-hole/pitch requirements and manual solder-fill inspection remain specific open issues. |
| RECOM R-78E5.0-0.5 module | 1 | 0 | 5 | Normal three-pin THT category; exact RECOM LCSC offer currently zero. Existing external-source route remains possible; do not use same-name other makers. |
| Same Sky CMA-4544PF-W microphone | 0 | 1 | 10 | User installation after JLC processing; protected hand soldering, no reflow/wave/wash. |
| Same Sky CPE-203 buzzer | 0 | 1 | 10 | User installation after JLC processing; hand-only/no-wave/no-wash handling and polarity checks. |
| Total excluding Pico | 10 | 3 | 80 | JLC requested: 60; user accepted: 20. |

Five Picos are separately user-installed; neither they nor the other manual
parts enter machine CPL files. Do not confuse blank factory BOMs with absence of
an SMT population: the released 915 SMT placements remain in consigned files.

Official JLC [PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
support mixed SMT/THT, while the [assembly FAQ](https://jlcpcb.com/help/article/pcb-assembly-faqs)
describes manual assembly. General service support does not confirm the exact
hand-only acoustic process or package-specific temperature/cleaning limits.

Selected route: JLC fabrication, 915 SMT placements and 60 connector/regulator
installations; user installs 20 acoustic parts and five Picos. User-installed
positions remain outside JLC placement/paste scope, with through-holes open for
later installation. Retain existing D1-only Pico preparation and all inspection
instructions. Arrange user-part procurement separately; do not assume JLC will
ship loose parts. Exact JLC sourcing/process acceptance and pricing remain open.
This decision does not authorize vendor contact, uploads or purchasing. If JLC
declines any of the 60 operations, return the exception for a new route decision;
do not silently transfer that work to the user.

## Reproduction and checks

Run from repository root:

```sh
python3 projects/crow-array/order-readiness/catalog_mapping.py build --observations projects/crow-array/order-readiness/catalog-observations-20261026.json --output /absolute/new-worksheet.csv
python3 -m unittest discover -s projects/crow-array/order-readiness -p 'test_*.py'
python3 projects/crow-array/publication.py verify
```

Fourteen tests pass, including wrong-maker/suffix rejection, inventory-pool
separation, insufficient-count precedence, demand coverage, manual exclusion
from factory candidates and overwrite refusal. Publication preservation passes
for 256 payload files. No engineering receipt, process waiver, purchase, upload
or supplier contact occurred. Pico relief research remains stopped per the user.
