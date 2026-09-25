# AUDIO_EN local owner pockets on the 15-part TI board — 2026-09-25 UTC

**Research-only geometry and source-model screen; no canonical edit, P1/P2
credit, or placement promotion.** Measurements use the exact [15-part native
board](2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb), SHA-256
`d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`,
the [unified floorplan](2026-09-25-ti-unified-p1-diagnostic-sol/floorplan.yaml)
SHA-256 `7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0`,
and [modular owners](2026-09-25-ti-unified-p1-diagnostic-sol/modular_plan.json)
SHA-256 `02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8`.
The checker was SHA-256
`b4ece816b23bcc1f213a6e66253d4aa2dfe1a1358a5a74aaaea40fd8a36bab95`.
KiCad `_physical_envelope` means native body plus courtyards without movable
reference/value text; every native pad was checked separately.

| Current owner/ref | Native physical envelope (mm) | Small enclosing pocket (mm) | Nearest other envelope, gap |
| --- | --- | --- | --- |
| `quiet_power` / `R_AUDIO_PD` | `[22.185,104.125,23.215,106.075]` | `[22.0,104.0,24.5,106.2]` | `C_AUDIO_CT1`, 0.125 mm |
| `quiet_power` / `U_AUDIO` | `[21.455,108.35,23.945,110.645]` | `[21.3,108.2,24.1,110.8]` | `C_AUDIO`, 0.095 mm |
| `analog_ch1` / `U_ISO1` | `[21.455,65.755,25.145,69.445]` | `[21.3,65.5,25.3,69.7]` | `R_ADC_PD1P`, 0.325 mm |

Each proposed pocket contains all pads of its named footprint and intersects
no other native physical envelope or pad. The three source rectangles remain
close to their current electrically related parts and do not move any pose.
They do **not** prove required clearance, route access, decoupling, CT
behavior, signal integrity, or filled return. The `U_ISO1` pocket overlaps
the current *same-owner* `analog_ch1` planning region in x=25..25.3; none
overlaps a foreign planning region. The two `quiet_power` pockets stay west
of x=25 and do not enter `input_buck`.

The present checker cannot admit these as three sparse `physical_cells`.
`_physical_cells` requires a complete partition of **all** refs of each
opted-in owner, a primary cell named exactly for the owner, and no overlap
with *any* other region. The current `quiet_power` primary rectangle already
overlaps `input_buck` (x25..70, y105..110) and `hold_bank_left` (x24..74,
y113..134), while the `U_ISO1` pocket overlaps its own primary region.
Recutting `analog_ch1`'s west edge to x25.3 to make that pocket disjoint would
strand nearby owner footprints including `R_IN1P` (physical x24.025..25.975)
and `U_ESD1` (x24.755..27.245); it is not a three-ref repair.

Separately, `_unresolved_branches` checks every `AUDIO_EN` pad against
`regions[block]`, ignoring `physical_cells` even if a cell were valid. A
**pad-only** isolated recut of `quiet_power` west x25→21 and `analog_ch1` west
x25→21 contains the three missing `AUDIO_EN` pads without moving them; it
introduces no newly intersecting foreign-owner pad at those west strips.
However, `R_AUDIO_PD`'s physical envelope starts y104.125, north of the
unchanged `quiet_power` y105 edge. Moving that whole planning rectangle north
to y104 would newly include the two `C_IN3` pads owned by `input_buck`.
Furthermore `R_AUDIO_PU.2` still intersects `input_buck` within the existing
overlap, so its blocker must remain exact. The west-edge recuts alone can
repair the branch's three pad-containment failures, **not** exclusive
physical ownership or the remaining foreign-region debt.

The minimal model extension for a footprint-level repair is an opt-in,
geometry-free **branch owner pocket**: source-declare `{id, owner_block,
exact_refs, bbox}` for each local pocket; verify complete native
body/courtyard and pad containment, no foreign-owner native envelope/pad or
foreign planning-region intersection, and unique ref assignment. Permit
overlap only with that same owner's rough planning region, require each
affected branch endpoint and P2 obligation to name the pocket, and evaluate
the branch pad against that validated pocket instead of `regions[block]`.
Do not give the pocket copper area, capacity, route, or P1 credit. This avoids
pretending the current all-owner `physical_cells` partition is satisfied.
Before any source adoption, the branch's exact 11 native `AUDIO_EN` pads and
`R_AUDIO_PU.2` foreign blocker inventory must be regenerated and independently
checked; the four separate two-terminal audio/TDM gaps and power-window
failures remain.
