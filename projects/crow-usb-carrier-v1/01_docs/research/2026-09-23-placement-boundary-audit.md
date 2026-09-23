# Crow USB carrier — connector placement/release boundary audit

**Scope and status.** Read-only advisory, 2026-09-23. This is not an admission
review and makes no engineering verdict for a board that does not yet exist.
The current project beacon is `placement / PAUSED`: schematic admission is
PASS 2/2, while the P1 native two-island floorplan trial, physical capacity,
and independent placement review remain owed
(`projects/crow-usb-carrier-v1/01_docs/STATUS.md`). No accepted PCB or release
exists.

## The actual upcoming boundary

The next connector boundary is `rebuild_all.sh` step **[3c]
CONNECTOR-FULL**, after the native candidate PCB and P-PINMAP exist and before
placement approval or routing. It recompiles the base contract and requires
the base receipt to be `PASS` with **zero unknowns**. The conductor explicitly
states that a source-phase receipt is insufficient, and returns INCOMPLETE
until every physical operation/fit/tolerance is qualified on the exact
candidate or a governed coupon:

`projects/crow-usb-carrier-v1/03_src/rebuild_all.sh` lines 404-415.

This is intentionally stronger than the present source boundary:

* Base receipt: `06_build/verification/connector_assembly_contract.json` is
  `INCOMPLETE`, with 19 unknowns and an `UNKNOWN` evidence ceiling.
* Source wrapper: `06_build/verification/connector_assembly_source_gate.json`
  is `PASS`, admitting exactly those same 19 *named physical deferrals* so a
  native candidate may be generated. It does **not** approve placement,
  routing, service, enclosure, release, or ordering.
* The governing statement is
  `skills/pcb-design/references/connector-assembly-contract.md` sections 8–10:
  source PASS permits generation; full requires base PASS/zero unknowns;
  neither receipt is a placement-geometry PASS. The physical/coupon workflow
  itself is separate from product fabrication and release authority.

Therefore, P1 may create and be independently reviewed as a native placement
candidate using current public CAD/source records, but it cannot clear [3c],
enter routing, or contribute a release claim unless the contract is later
closed by governed physical evidence. A good render, correct axes, or
footprint/model parity is not a substitute.

### Is a design-only release currently legitimate?

**No.** ADR 0010 is a *design-admission* exception for public sourcing records,
not a release-mode exception. Its own consequence says that public screening
permits schematic review, block placement, and subsequent design work “subject
to all existing engineering gates,” while retaining DO-NOT-ORDER and
order-time fulfillment checks. Connector FULL is one of those existing gates:
the base contract must be `PASS` and have zero unknowns before placement
approval/routing, and release consumers reopen that same base receipt at their
full bar. There is no evidence of a project policy that permits a sealed
design-only PCB release with 19 connector physical unknowns.

This is not a recommendation to waive or prematurely execute [3c]. It is the
current gate's defined scope. The gate becomes applicable only after P1 has
produced the exact native candidate; it then blocks the next claimed boundary,
not the useful candidate-generation work before it.

## What current public records can prove

The contract binds four operated assemblies, 11 refs, and two simultaneous
service groups (`normal_service`: J1–J8, J_USB, J_PWR; `bench_service`: all
of those plus J_JTAG):

| Assembly / refs | Current public/native support | Still not proven |
|---|---|---|
| `spoke_rj45` / J1–J8 | Exact Wurth receptacle drawing and STEP model; selected cable record; conservative envelope/axis facts. | Exact cross-vendor mate, realized edge/exposure, latch/grip service with populated neighbors, reaction/flex/joints, installed tolerance stack. |
| `usb_device` / J_USB | GCT drawing/spec and selected ASSMANN cable drawing give body/plug conservative envelopes, identity and planned axis. | Exact-pair fit, realized orientation/exposure, populated-neighbor service, shell-stake reaction, cable exit/bend/strain/clearance, installed tolerance stack. |
| `external_power` / J_PWR | Exact Molex 43650/43645 compatible pair, selected 226206-1022 harness identity, planned axis. | Realized latch/service access, reaction, installed cable run/bend/strain, actual registration/tolerance stack. |
| `debug_jtag` / J_JTAG | Exact Samtec FTSH/FFSD keyed compatible pair; conservative selected body/grip and reversible lateral exit candidates. | Actual installed ribbon end/route, physical engagement/access, reaction, full bench-service operation, registration/tolerance stack. |

Authoritative source paths for that limited support are:

* `03_src/rules/connector_assemblies.yaml` — identities, exact/conservative
  evidence, axes, known unknowns, refs and groups.
* `01_docs/research/2026-09-22-connector-selections.md` — candidate identity
  and explicitly stated limits of the catalog facts.
* `01_docs/research/2026-09-22-connector-placement-intent.md` — planned,
  not realized, axes. It says all 11 orientations remain pending native
  placement.
* `06_build/verification/admission-final/connectors.json` — bound source
  inventory with hashes for all 19 evidence files, and the source gate
  `PASS`/base `INCOMPLETE` distinction.

No public drawing or native CAD can establish the exact candidate's mating
plane, board edge, actual seating/rotation, process variation, operator grip,
insertion/withdrawal loads, neighbor disturbance, installed cable bend, or
repeated-service response. The project deliberately records these as unknown,
rather than estimating them.

## Physical evidence that FULL requires

The policy at `03_src/rules/connector_assembly_phases.yaml` maps every one of
the 19 unknowns to only one future class and qualification procedure:

* RJ45: 4 targets — interface, reaction, service, registration — exercised at
  each J1–J8.
* USB: 5 — interface, reaction, service, cable route, registration.
* Power: 5 — interface, reaction, service, cable route, registration.
* JTAG: 5 — interface, reaction, cable route, service, registration.

`01_docs/research/2026-09-22-connector-physical-qualification-plan.md`
requires an exact candidate or coupon with the candidate footprint, thickness,
outline/edge registration and process; exact connector lots/mates/cables;
per-ref operation records with declared groups populated; raw per-sample
registration/process measurements; and visual/motion evidence for reaction,
seating, flex, rotation, joints, latch/polarization and cable route. It also
states that the plan records no realized geometry or physical PASS. The plan
does not invent force, displacement, cycle-count, or tolerance limits; those
need separately cited/approved authority before numeric grading.

Under the present public-records-only and no-purchase instruction, this work
is not merely deferred—it is unavailable: it needs populated physical samples
and the exact mates/cables. It must remain a visible full-gate and release
hold. The current workflow permits P1 native placement work, not physical
closure by proxy.

The unavoidable external dependency is user-authorized access to physical
hardware: an exact-candidate coupon or first article, exact connector lots,
the selected mates and cables, and a way to perform/record the required
operations and measurements. It does **not** require an authenticated JLC
account, a supplier message, a purchase in the current workflow, or any
private inventory data. Public records can prepare the selection and
hash-bound coupon request, but cannot generate its observations.

## Coupon finding

There is **no valid accepted connector-assembly coupon evidence** for Crow.
Specifically, the project has no `03_src/connector_qualification_coupon.yaml`,
no `06_build/connector_qualification_coupon/current/` package, no
`physical-response.yaml`, no grade receipt, and no
`connector_assembly_full_gate.json`. The only in-tree `coupon` is
`02_parts/TMUX4827YBHR/qualification/coupon.kicad_pcb`; its review
`08_reviews/2026-09-23_tmux4827-coupon_sol_source.md` accepts a diagnostic
BGA escape geometry only and expressly excludes PCB-fab/PCBA acceptance. It
does not cover any connector target and cannot be reused as connector evidence.

When physical work becomes authorized, the applicable mechanism is the
governed coupon described in `connector-assembly-contract.md` section 10:
create the required source config only after an exact candidate exists;
prepare the hash-bound connector-only board; then populate exact hardware,
retain lots, record physical responses, and grade them back through the base
contract. `READY_FOR_FABRICATION` for that coupon would authorize only the
named bare coupon, never PCBA, product fabrication, placement, release, or an
order.

## Manual-THT and XMOS sourcing are separate from connector closure

The requested sourcing authorizations are present but do not weaken any
connector gate:

* `08_reviews/2026-09-23_manual-tht_terra_source.md` accepts the exact D9
  manual set: J1–J8 plus C_A1N/C_A1P through C_A8N/C_A8P (24 refs). It
  confirms J_PWR is *not* exempt. This is policy/source review only; it
  explicitly makes no native PCB, CPL, placement, or JLC process claim.
* ADR `01_docs/decisions/0009-xmos-public-stock-reserve-exception.md` limits
  the sole stock exception to U_XU / XU316-1024-TQ128-C24 / JLC C6362698:
  five-board quantity times actual use, with zero extra reserve. JLC stock and
  population still remain mandatory. `08_reviews/2026-09-23_xmos-exception_sol_source.md`
  independently accepts that narrow propagation. It is neither allocation nor
  a purchasing/release/physical qualification authorization.
* ADR `0010-public-records-design-admission.md` permits public records and
  jlcsearch for design admission only. Its stated effect is that placement and
  subsequent design work may continue subject to existing gates; it makes no
  allocation, assembly acceptance, or order-ready claim. The authoritative
  fresh design-screen evidence is `06_build/sourcing/public-stock.json`,
  generated `2026-09-23T15:09:24Z`, `88/88` PASS, together with
  `06_build/verification/manufacturing_readiness_prelayout.json`,
  `ACCEPTED 4/4`. Those receipts remain dated public observations, with
  `predicts_jlc_assembly_allocation=false`, rather than release/order proof.
  `06_build/verification/source-stock-refresh-20260923/report.md` is an
  older historical snapshot (and its then-current low-stock/unresolved rows
  must not be presented as the current public design-screen result).

## Concrete next-work map

1. Finish P1 as a native candidate, bind exact board/outline/footprint/model
   identities, inspect measured native geometry, and obtain the separate
   placement review. This can use current public CAD evidence but should report
   its result as a candidate/placement finding, never connector FULL.
2. Useful design-only work before [3c] is limited to the native candidate and
   its independent placement/geometry review, including connector reference
   census, planned-axis versus saved-board orientation comparison, outline and
   body/model checks, and explicit capture of the exact hardware/coupon
   configuration needed later. Those checks can reject a bad candidate; they
   cannot certify operated service or close a physical target.
3. At [3c], expect `CONNECTOR-FULL INCOMPLETE` with the 19 stable targets;
   preserve that output. Do not edit unknown grades, phase policy, or receipts
   merely to pass it.
4. Do not start routing/release on the basis of the source gate. Physical
   qualification needs a later user-authorized hardware/coupon action and
   complete governed evidence flowing into the base receipt.
5. Keep D9's exact 24-ref manual handling and the D10 XMOS exception narrow in
   the native/BOM consumers: J_PWR remains JLC-coded; all non-XMOS coded parts
   retain five-board plus 150 surplus; public records remain design-only.

## Contradictions / stale-language risks

* No contradiction exists between `connector_assembly_source_gate.json: PASS`
  and the base receipt's `INCOMPLETE`: source admission is expressly an
  additive deferral bar. Treating source PASS as a placement or release PASS
  would contradict both the phase contract and conductor.
* The physical plan says the future subject is produced from
  `03_src/floorplan.yaml`, while the status says P1 is underway. Until a saved
  native board exists, neither has realized geometry. The planned placement
  contract cannot be recast as a measured-orientation receipt.
* The selected JTAG cable has a lateral/reversible exit. The old qualification
  plan's schema-1 warning is now stale: the current contract/compiler supports
  `exit: board_axes` plus signed `exit_axes_board`, and the JTAG contract
  records the two possible ±Y exits. The full-phase compiler then requires
  exactly one installed signed exit axis. This closes representation of the
  candidate exit alternatives; it does **not** close the physical installed
  route, bend, strain relief, clearance, or any other FULL evidence target.
* The D9 manual-THT source review is compatible with J1–J8's physical
  qualification requirement. Manual supply/population does not establish
  mate/service/reaction evidence.
