# DO-NOT-ORDER / DO-NOT-UPLOAD

Prototype PCB design candidate crow-prototype-v3-first-run-5c10p. No seal or hardware qualification implied.

## Active holds — closure required before ordering

- PURCHASING-AUTHORITY: No vendor contact, upload, purchase or publication is authorized by local design/release acceptance. Closure: Purchaser obtains explicit user authority for the exact accepted/sealed 5-carrier/10-pod packet and actual scope/cost; publication additionally requires repository-delta and redistribution-rights review.

- EXACT-SUPPLY-AND-ALLOCATION: 38 adequate dated supplier offers are not reservations, usable JLC pools or an accepted consignment/global-sourcing route; no attrition extras inferred. Closure: Procurement/assembly owner confirms all exact MPNs, usable pool allocation, lead time, packaging, MOQ and feeder/attrition needs for 1,000 installed parts; retains actual purchased minima separately; substitutes reopen engineering.

- VENDOR-MATCH-AND-ORIENTATION: Local BOM/CPL encoding, identity, centroid and angle checks are not vendor matching, reel convention or placement-preview approval. Closure: Assembly owner checks exact same-MPN matching and every center/side/rotation/pin-1/cathode against current native boards and actual vendor previews before commitment.

- STENCIL-POLICY-RECONCILIATION: JLC internally optimizes production stencil apertures while this accepted process prohibits automatic paste changes; exact agreement is absent. Closure: Fabrication/assembly process owner obtains explicit exact-job production-stencil agreement preserving exclusions, or separately authors/reviews a compatible process revision; no silent edits.

- PROCESS-STACK-RAILS-DFM: Published service capability and nominal CAD do not confirm this exact construction, precision process, finish, rails/fiducials/fixtures or edge-mounted handling/DFM. Closure: Fabrication/assembly owner confirms carrier 7628A and pod 7628, full plots/drills and exclusions, actual stack/finish, panel/rail/fiducial/fixture/DFM scope and preserves all datums/contours; conflicting offers reopen causal engineering.

- FINISHED-MECHANICAL-AGREEMENT: Complete coupled LS43/LS33 incoming/finished hole, pitch, web, annulus, edge, registered top, pose, seat, pool, underside and service limits are design-owned controls, not automatic supplier guarantees. Closure: Fabrication/assembly/metrology owners agree every conjunctive limit, measurement method/uncertainty and traceable records before execution; inspect actual lots/units and quarantine failure rather than force, ream or weaken limits.

- MANUAL-ROUTE-UNSELECTED: The user has selected no manual completion route; header-only factory/all-consigned SMT is a proposal, not turnkey acceptance or an unassembled-kit promise. Closure: Purchaser/assembly owner names JLC or a qualified separate manual assembler and obtains acceptance of each Pico D1-only, RJ/PJ/RECOM and acoustic hand-solder operation, supply route, inspection and responsibility before commitment.

- CONTROLLED-ASSEMBLY-READINESS: Exact original SC0915 Rev3 D1-only preparation, all castellations/pools, PJ fill/retention, protected hand-only acoustics and compatible at-most-two R3 reflows require qualified execution/inspection; none is performed. Closure: Assembly owner agrees compatible profiles, incoming identities, special handling, unpowered inspection, lot/serial/rework and metrology records; executes under complete retained maker/LS43/LS33 instructions after authorization.

- ACTUAL-QUOTE-AND-SCOPE: PCB components plus bare fab/setup $530–1,350 and separate assembly/manual $500–1,400 are unquoted estimates, not a cap or accepted offer. Closure: Purchaser obtains itemized exact 5/10 quote and user approval of actual cost/scope; external host/storage/PSU/adapters/cables/enclosure/roof costs are outside requested comparison, not free or technically waived.

See HANDOFF.md for assembly, firmware, first-article and deployment obligations.

Mechanical scope: Current independently accepted D3-corrected registered assembly on exact 5-carrier/10-pod fabrication: 38 models, 169 mounted references and 54 full-assembly limitation dispositions. Full populated/bare STEP, six views, same-camera bare twins, Pico details, exact contacts, solid/board/access checks and finite LS43/LS33 controls retained. Only accepted D3 cooling copper differs from the prior qualified-P040 assembly; all models and mechanical geometry remain exact. No exact-job supplier/process/manual acceptance or hardware qualification implied.

## Reproduce offline

Requires Linux Landlock ABI >=3, libseccomp, Python3 with pcbnew, KiCad10.0.4,
pdftoppm and the system fonts used by the preserved PDF checks.
The indexed runtime.json also declares any required EGL/GL renderer, GPU driver and
specific character-device capabilities. A different or unavailable profile fails closed;
this Python capsule is not an OS image or a hardware-independent renderer.
Run from this archive: `python3 -B source/tools/release_review.py replay --archive .`.
This checks the archived accepted chain, regenerates schematics/plots/PDF/DRC and assembly
views in disposable scratch. Original workspace and networking are denied.
Receipt verification is not independent electrical judgment or an immutable seal.
