# PCB-SOURCING — local admission contract

Input role: accepted `architecture_locked`. Output role: `parts_locked`.
Use the local independently reviewed admission verifier below. A prerequisite
certificate is required. Never execute a legacy gate.

Use the [skill's design-stage sourcing policy](../../procedures/part-recheck.md).
For the exploration route, this is the final exact-BOM check after schematic
development stabilizes: batch-select generic common resistor/capacitor positions
now, preserving their specified electrical properties. Their earlier omission
of exact MPNs is intentional, not a reason to interrupt schematic development.
All exact identities still close before this stage's acceptance.
The [part recheck](../../procedures/part-recheck.md) also applies before this
stage and on later repairs: `parts_locked` is not a perpetual stock check.
Record every selected exact MPN, package, quantity per assembly and assembly
route in the candidate parts table. Bind critical pin functions, recommended
limits, footprints and reference circuits to retained, hashed manufacturer
documents in part dossiers. Proposed substitutes are not silently equivalent.

Prefer JLCPCB supply/assembly; where unavailable, screen Western alternatives
briefly and ask the user if no in-stock option is readily found. An explicit
stock statement is sufficient for design availability, not actual allocation,
quantity guarantee or electrical fit. Keep volatile observations dated and
separate from build-consumed part facts. Include every required board type and
instance quantity, plus cables, enclosures and other deployment hardware when
in scope, in the cost assessment; exclude existing equipment only when authorized.

Independent review uses [admission](../../procedures/commission/admission.md)
to check exact identity, pin facts, availability, assembly and cost. Prototype
availability does not approve a purchase or certify repeat-production supply.
If a selected part changes, reopen its architecture interfaces and dependent
schematic evidence. Preserve failed candidates and the sourcing rationale.
