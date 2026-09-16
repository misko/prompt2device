---
id: "0012"
date: 2026-09-08
status: proposed
---
# 0012 — native regulator exits and a reserved quiet-return source cell

## Context

Source adoption a8e8ac31 preserves 299 refs, 868 native pin memberships,
205 nets, 40 NCs and 17 ADC/digital seed banks. Original centre-start 1.20 mm
bulk exits collide at LDO OUT1/2, IN9/10 and BUCK SW5. A centre-start failure
does not establish the largest off-centre copper that can actually contact
the pad. Existing seed emission tests native pad contact and accepts in-pad
off-centre starts; no emitter, shared rule or board generator is changed.

The exact TPS7A92 SBVS318B pin table p3 and layout pp22–23 govern: GND4
returns directly to EP; NR capacitor/lower-divider grounds have their own
quiet component-side return to EP; local power-cap grounds and thermal
egress are separate obligations. Positive feedback retains load-side sense
intent. Merely tracing GND under a solid top GND pour cannot force a return.

Public manufacturer precedent was consulted without importing copper:
[TI TPS7A91EVM-831 guide SBVU036](https://www.ti.com/lit/pdf/sbvu036),
layout p7, is a related 1 A family EVM, not this carrier's current/thermal
qualification. The [TI product page](https://www.ti.com/tool/TPS7A91EVM-831)
and manufacturer-focused search exposed the guide/certificate, but no editable
CAD/Gerber in inspected results. This is a search ceiling, not proof that
files do not exist. The [AP63205WU EVM guide](https://www.diodes.com/assets/Evaluation-Boards/AP63205WU-EVM-User-Guide.pdf)
Rev.2 p4 photo shows close VIN/SW/inductor components and ground-via groups;
its photo and schematic are not editable layout. The
[Diodes product page](https://www.diodes.com/part/view/AP63205) exposed guides
and calculator, not editable copper in inspected public results. No account,
vendor contact, upload or third-party production layout was used. Exact PDF
hashes and rendering evidence are retained; only dossier layout_refs/gotchas
changed. DS41326 Rev.3-2 p15's 2 oz top/bottom thermal recommendation is not
inherited by this carrier's nominal 35 um outer copper.

## Options

- Original centre/bulk exits and original C_LDO_OUT pose: rejected by native
  foreign-pad collisions and needlessly long local output routing.
- Root's unadopted y66 capacitor Case A: not adopted; its reported body
  interference is not reused as a new measured result. Independently screened
  Case B [61,66.5,180] clears all other 298 courtyards, both body/pad directions
  and all 1,732 distinct-footprint pad pairs, including same-net pads.
- Moving R_LDO_TOP as well: no demonstrated cause; preserve its exact pose
  and load-sense topology. Only C_LDO_OUT moves from [62,74.15,270].
- Fresh H1: 36 segments/six vias; west EP diagonal interferes with PG5.
  Retained as a failed candidate. H2 adds a vertical-first west EP escape and
  clears native geometry. H3 widens main OUT1/IN10 from 0.90 to 1.10 mm and
  precisely expands their width areas; the lower branches stay 0.40 mm.
- GND traces beneath the existing full top pour: rejected as uncontrolled
  quiet return. Split GND nets/inner planes or a new power pour: not selected.

## Decision

Propose H3 as bounded source geometry: 15 additional F.Cu banks, 37 straight
primitives and six off-pad 0.50/0.20 mm vias, one capacitor move, five precise
width-only areas and five overlapping top pour/via exclusion rectangles.
No clearance floor is relaxed. Exact coordinate lists in route.yaml and
floorplan.yaml, tested against actual native pads, are authoritative.

OUT1 and IN10 start off-centre inside native copper at 1.10 mm; OUT2/IN9
use explicit 0.40 mm branches. The wider main round ends also touch their
same-footprint parallel pin. That physical contact is permitted, but neither
branch is deleted and no equal sharing/current reduction is assumed. SW5
uses 0.75 mm for 0.90 mm, then 1.20 mm to L_BUCK.1. C_BUCK_BST.2 is not
reached by this seed, so BUCK_SW stays generic, partial ownership. The two
existing complete deterministic nets remain LDO_A_FILT and FSYNC_BUF.

The existing 1.20 mm bulk and 2.5 A transient bound are unchanged. Measured
source subnominal quantities are:

| Copper | Length mm | Straight items |
|---|---:|---:|
| Original west ADC subtotal, preserved exactly | 5.050000000 | 8 |
| Added LDO OUT1/2 | 2.720060973 | 5 |
| Combined 3V3_ADC | 7.770060973 | 13 |
| Added IN9/10 on 5V_LDO_HOLD | 3.075000000 | 4 |
| Added BUCK_SW | 0.900000000 | 1 |

The power wave's existing overall guard becomes 7.770061 mm/13 items, rounded
up from the actual additive source geometry. This is an exact authored
extent allocation, not a newly derived safe ampacity or thermal limit.
Durable tests independently retain the old ADC subtotal and each new net's
exact length/count; the uniform wave guard alone is not that per-net proof.

NR1–5 ground pads and lower-feedback R_LDO_BOT.2 form a component-side tree
to EP11. GND4 connects directly to EP; SS_CTRL6 is separately strapped to EP.
The LDO_QUIET_* rectangles deny only F.Cu pours/vias, including quiet pad
edges and trace margins; tracks/pads are permitted and inner common GND is
unsplit. Two separate 0.35 mm EP exits reach off-pad vias without touching the
quiet tree before EP. A separate 1.20 mm, 8.20 mm component-side power-cap
GND path connects C_LDO_OUT.2 to C_LDO_IN.2, with four distributed drops.
There is no fictitious plane edge in the source contact-graph test.

## Consequences

All five narrowed power branches are screened at the full 2.5 A transient
bound. Conditional DC calculation uses ADR0010's rho85=2.1643958e-8 ohm-m
and nominal 35 um copper, R=rho*L/(w*t), loss=I²R:

| Branch | Width mm | Subnominal length mm | R mOhm | Loss mW at 2.5 A |
|---|---:|---:|---:|---:|
| OUT1 | 1.10 | 1.470061 | 0.826440 | 5.165250 |
| OUT2 | 0.40 | 1.250000 | 1.932496 | 12.078102 |
| IN10 | 1.10 | 1.525000 | 0.857326 | 5.358285 |
| IN9 | 0.40 | 1.550000 | 2.396295 | 14.976846 |
| SW5 | 0.75 | 0.900000 | 0.742079 | 4.637991 |

The complete 1.20 mm local cap-ground path models 4.225725 mOhm/26.410782 mW
at that same full bound. These are resistive estimates, not temperature-rise
or allowable-duration results. Wider main exits reduce impedance while the
short lower-pin/SW necks fit native land constraints; they are not long bulk
trunks. Full-bound losses remain explicit even though pads share copper.
Finished copper thickness, spreading, pad heat flow, plating, fault duration
and steady-state temperature are unqualified. No permissible fault duration
is invented; 2.5 A is not claimed as either regulator's rated DC output.

The six vias have geometric clearance and no via-in-pad/paste requirement.
Two EP drops do not prove achieved thetaJA; four capacitor-ground drops do
not prove a series-bank cutset, equal sharing or a finished-barrel ampacity
allocation. Their count must not become a thermal/current PASS.

Source-native tests include full rounded segments, widened entries, every
foreign pad, all native holes, existing/new seeds, via copper/drills across
physical layers, exact area containment, whole-component placement, quiet
pad/trace/via interference and actual transitive endpoints. Quiet-mask union
coverage uses 5 um centreline sampling with radial margins and native EP
contact at the junction; it is not exact final zone-fill topology proof.
All future generic/stitch copper must be checked for a pre-EP bypass. Filled
GND connectivity, loop impedance, thermal behavior, startup/stability, final
post-import width/extent, native DRC and digital SI remain owed.

Reproduce source arithmetic/geometry with the retained final_source.py and
the project test_regulator_source.py; raw finite-run logs are in
06_build/tmp/regulator-source-20260908. No generated board was opened or
written. This ADR is proposed for independent root source adoption, not
route admission. ADR0007/0009, TOP77, first-power 0.20 A HOLD, all mechanical,
service, sourcing, publication and physical qualification obligations remain.
