# JLCPCB PCBA readiness — first run, 5 carriers + 10 pods

Independent read-only review, 2026-10-22, approximately 15:19–15:25 UTC. Target: earlier Astra design and its preserved first-run purchasing derivative, not the separate SOL design. The approved Panasonic R3 qualification/successor is another owner's in-progress work; this report does not accept that replacement or edit the old packet.

## Bottom line

There is a credible path to **unprogrammed prototype PCBA**, but not yet evidence that JLC has accepted this exact build. R3 qualification and a new local release alone will not establish that. The smallest remaining external step is one exact-job JLC engineering/quotation review covering the finished mechanical requirements, stencil/handling workflow, selected parts and responsibility for manual completion. No new whole-design rebuild is justified merely by an unanswered vendor question.

Current purchasing scope is 915 top-side SMT placements across 32 exact manufacturer/MPN identities, plus 85 manual parts across six identities, totaling 1,000 installed components/38 identities. Original factory BOMs are header-only; the offered per-board files describe consigned SMT, not turnkey completion. For the approved R3 successor, regenerate through its owner; do not upload old Vishay R3 bytes while ordering Panasonic.

The existing 33-file draft was rehashed unchanged in this pass. ZIP SHA256 remains `47a597c4e3c0aed3b369d2d33d2632bf18ece9e871f473993504af5ee54b4d9e`; manifest SHA256 remains `4a40b72d3f10ea6e64c61f162262efad223c1e640d714152894aec7f40747583`. Earlier independent payload/DRC/quantity checks remain scoped evidence, not fresh whole-engineering or supplier acceptance.

## Which controls are essential, and which are design-owned proof limits?

The distinction matters for choosing a practical supplier discussion. It does **not** authorize deleting an accepted requirement.

| Class | Actual examples | Consequence |
| --- | --- | --- |
| Functional/manufacturer/interface essentials | Exact qualified part identity and pad polarity; correct circuit/pattern; no shorts, forced insertion or mechanical interference; retained stack assumptions; Pico D1-only power modification; acoustic handling restrictions; usable USB/DC/RJ service access | Keep. An incompatible process or part must be corrected, not relabeled as a later test. |
| Astra design-owned numerical acceptance/proof limits | RJ hole ±0.05 reject ranges; four incoming package boxes including flash; universal radial 0.10-mm/total 1-degree pose cap; registered connector-zone top ≤+0.05 mm; explicit seat/gap/underbody limits; PJ ≥75% through-thickness fill; finite module solder-pool envelope/registration limits | These are not published universal maker tolerances or automatic JLC guarantees. They condition the accepted collision/fit proof, so they remain mandatory until a separate source-owned engineering review replaces that proof or geometry. |
| Physical qualification after fabrication/assembly | Actual solder integrity and jack-load retention; rail/power-transition/thermal behavior; microphone/acoustic response; eight-channel USB firmware and timing; harness and rooftop protection | Agree an executable plan and ownership before commitment where required; actual results are not prerequisites to ordering every experimental prototype. Do not claim a working array until qualified. |

Normative local evidence: packet `instructions/integrated-mechanical-controls.md`, `module-controls.md`, `assembly-plan-original.md`, `assembly-instructions-original.md`, `process-original.md`, and full sealed LS43/LS33/LS46 evidence. The controls themselves explicitly identify designer reject limits, rather than claiming maker or ordinary-fabricator tolerances. A source-supported larger tolerance margin could be a legitimate future simplification; calling an existing limit conservative is not its engineering closure. No such relaxation was performed here.

## Ranked job-specific gaps

### 1. Obtain the exact finished-mechanical/process acceptance

Published JLC values checked today: ordinary through-hole diameter +0.13/−0.08 mm; position ±0.075 mm; circular press-fit ±0.05 mm only for 0.55–2.0-mm finished holes on multilayer ENIG; routed edge precision ±0.10 versus regular ±0.20 mm; ≥1-mm board thickness ±10%. These are distinct options, not one blanket precision guarantee. [Official rigid capabilities](https://jlcpcb.com/capabilities/pcb-capabilities).

For this design, request the complete LS43/LS33 limits and an identified inspection owner. Priority questions:

- Can the precision-hole option be applied to the soldered RJ contact holes at 0.89 ±0.05 mm? It cannot be assumed to cover 3.25 ±0.05-mm NPTH pegs.
- Can JLC guarantee carrier PJ finished openings 1.60–1.73 mm and the complete maker ±0.05-mm pitch pattern? Ordinary nominal 1.60 permits a 1.52-mm opening and therefore does not suffice.
- Can JLC guarantee the carrier relief-hole finished ranges, A/B absolute radial position ≤0.05, combined webs/copper distances, and all actual recess clear rectangles/inside radii? Independent diameter/position maxima cannot replace combined web limits.
- Who establishes the registered finished-top, annulus and subsequent installed seating/pose conditions, by what method/uncertainty and lot records? Overall thickness tolerance is not a local surface-height or seating guarantee.

The chosen precision-profile service is a plausible ordinary option; the coupled mount/registration/top conditions still need exact agreement. A capability-page mismatch proves that defaults are insufficient, **not** that JLC cannot meet a separately assessed requirement. Preserve current source; if a specific constraint is refused, return only that causal issue to engineering. PJ maker plated slots are an already-documented possible redesign direction, not an authorized change here.

### 2. Reconcile real JLC production workflow with the accepted packet

This pass identified a concrete workflow issue not closed by the earlier payload checks: JLC states it prepares optimized stencil apertures from its internal engineering data, rather than directly manufacturing the uploaded paste Gerbers. Only selected SMT parts normally receive apertures, and special requests can be reviewed. [Official stencil workflow](https://jlcpcb.com/help/article/smt-stencil-data-prepared-for-smt-orders).

The accepted process requires exported mask/paste exclusions and prohibits automatic edits. Therefore obtain explicit agreement on the proposed stencil/production data and all manual exclusions, or have the owner separately review a compatible process-policy revision. A good native paste layer does not establish that JLC will use it unchanged. Do not respond by silently permitting arbitrary stencil edits. The current sources have no manual-part paste apertures, which is consistent with the intended separation.

JLC's assembly terms also specify medium/low-density footprint/spacing practice and a generic 2.5-mm body-to-edge rule, require production-placement review, and allow default tooling/rail additions if the supplied setup is incompatible. They do not include routine functional testing. [Official assembly terms](https://jlcpcb.com/help/article/terms-and-conditions-of-jlcpcb-assembly-service).

Edge-mounted jacks/Pico in any JLC final-completion scope consequently need an explicit handling/DFM disposition; do not interpret their intended overhang as a newly proven circuit collision or assume automatic acceptance. Rails/fixtures must preserve the shaped contours, reliefs, access and datum; no unreviewed copper/profile changes. The Standard route supports all stack-ups and requires rails/fiducials, while Economic permits standard stack-ups only. Both current board sizes/quantities fit the published Standard envelope. Exact carrier 7628A eligibility and chosen reflow/handling remain job-specific; consignment alone does not prove Standard is mandatory. [Official assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities).

### 3. Assign all manual work explicitly; JLC support is possible, not established

The 85 manual components are 50 RJ jacks, five PJ jacks, five RECOM modules, five original Picos, ten microphones and ten buzzers. JLC publicly supports THT/manual soldering and lists custom jig/edge-clamping, pin-bending and manual insertion services subject to evaluation. This is evidence of a general service path, not proof that a particular job is excluded or accepted. [Assembly FAQ](https://jlcpcb.com/help/article/pcb-assembly-faqs), [personalized services](https://jlcpcb.com/help/article/jlcpcb-supported-personalized-services).

Ask JLC to accept or decline each operation and its inspection requirements before treating it as turnkey:

- Original SC0915 matching Rev3 power topology; remove only MODULE D1 off-board; preserve divider and other components; before/after records and unpowered checks; controlled relief/pool registration and all 40 castellated joints per carrier. No public source reviewed promises this specific modification.
- PJ/RECOM/RJ mounting, free insertion and applicable lead preparation, full seating/pose and solder inspection. PJ includes all three joints, hidden-fill method and later supported-board retention qualification.
- MIC/BZ polarity, hand-only soldering, acoustic-port protection, no reflow/wave/wash, supported free-lead preparation and inspection. A catalog label such as wave soldering is not authority to apply that process to these parts.

Most practical fallback if JLC declines special work: **JLC SMT PCBA plus a named qualified manual assembler**, agreed before commitment. This still uses JLC PCBA and is not a design change. Buy the external assembler's six manual identities through an appropriate separate parts route; do not assume JLC will deliver an unassembled parts kit with the boards. Global-sourcing and consignment terms restrict shipment of unassembled material with PCBs. [Global sourcing terms](https://jlcpcb.com/help/article/global-sourcing-parts-order-terms-conditions), [consignment terms](https://jlcpcb.com/help/article/consignment-part-terms-conditions).

### 4. Match usable inventory and obtain one real batch quote

Prior dated supplier observations establish leads, not usable JLC warehouse allocation. Exact same-MPN JLC library, pre-order/global-sourcing or customer consignment routes may be considered; the existing all-consigned policy is the staged proposal, not evidence that all 915 positions technically require externally mailed parts. Any chosen route must appear consistently in a reviewed purchasing/population derivative and actual matching; do not silently replace manufacturer/MPN or patch BOM/CPL angles.

JLC requires own-parts selection during matching and separates combinable inventory pools for the same component. The public+pre-order pool and global-sourcing+consignment pool cannot simply be summed together. [Own-parts instructions](https://jlcpcb.com/help/article/how-to-use-my-own-parts-for-pcb-assembly-order).

Global sourcing requires assembly review and arrival in JLC's warehouse; successful lines generally cannot be canceled simply because another requested line fails. Minimum assembly/attrition quantities are additional to installed demand. [Global sourcing guide](https://jlcpcb.com/help/article/how-to-use-jlcpcb-global-sourcing-parts-service), [terms](https://jlcpcb.com/help/article/global-sourcing-parts-order-terms-conditions). Consignment likewise needs extra quantities and suitable handling; it does not include component functional qualification. [Consignment terms](https://jlcpcb.com/help/article/consignment-part-terms-conditions).

For the successor, first close its approved Panasonic R3 qualification and exact identity, then request allocation/packaging/MOQ/attrition for all selected lines. Keep five-carrier/ten-pod installed quantities distinct from purchase extras. Quote this uneven batch item-by-item, including setup, PCB, SMT, manual work/fixtures, sourcing/handling and shipping/tax. Do not assume five complete arrays or infer a $3,000 budget. No new stock sweep was performed in this bounded service-readiness review.

## Firmware is not a hidden fabrication prerequisite

The actual adopted release says firmware still must initialize PCM1864s, configure common 12.288-MHz/manual 24-ksps TDM/channel ownership and fault recovery, transport eight synchronized 24-bit channels (576 kB/s nominal sample payload), and control default-off buzzers. Physical power/rail/clock/thermal/acoustic results remain outstanding. These are explicit first-article/system obligations, not a claimed completed recorder or a concealed manufacturing step. Sources: sealed `03_src/release/ls47/handoff.md` §§ Electrical/firmware/deployment, `01_docs/BRIEF.md`, and assembly plan.

JLC describes firmware programming as an optional Standard-PCBA service requiring customer files/interface/instructions, after assembly, with support assessment. [Official programming service](https://jlcpcb.com/help/article/pcba-programming-service). Therefore a truthful order can request **unprogrammed, not-functionally-qualified prototype hardware**. If the user instead requires a demonstrated working array or JLC functional acceptance, firmware and a safe executable fixture/test procedure become deliverables before that service. No flashing, power test or firmware execution occurred here.

## Smallest truthful user handoff

After the source owner finishes the qualified R3 successor and exact packet:

1. Obtain one JLC written capability/scope response for those exact board/package hashes: full LS43/LS33 constraints, production stencil/rails/DFM handling, and whether JLC will perform the named special/manual operations. Retain explicit exceptions/refusals; do not buy against unresolved constraints.
2. Obtain actual exact-part matching/allocation, placement previews and an itemized 5/10 quote; name the manual assembler if not JLC. Check approved successor bytes rather than the old R3 packet, then ask the user to approve the real cost/scope before payment.

Until those responses exist the accurate statement is: **“The design files can be prepared for a 5-carrier/10-pod JLC PCBA prototype order. We still need JLC to accept its unusual finished-mechanical/process controls and confirm parts/manual scope. Firmware is separate; these will not yet be working-qualified arrays.”** Neither another local PASS nor finishing the Panasonic substitution can substitute for that supplier decision.

## Evidence and boundary

Read applicable vNext pcb-design fabrication/assembly contracts, earlier FABRICATION/SOURCING reports, first-run PREPARE/REVIEW, actual packet texts, original controls, and current sealed handoff/assembly/brief obligations. Public sources were consulted 2026-10-22 15:19–15:24 UTC; most Help Center articles label their revision September 9, 2026. Nine raw HTML snapshots plus source/digest index are in `jlc-readiness-evidence/`; two global-sourcing raw requests were rate-limited, while their official browser-rendered pages were successfully read. That is a retrieval distinction, not evidence of service unavailability.

No live CAD/seal/old packet edit, new receipt, vendor contact/upload/purchase, physical inspection, power test, flash or full engineering replay. This report may inform the independently owned successor; it does not admit it.
