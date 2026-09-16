---
id: 0018
date: 2026-09-08
status: accepted
---
# 0018 — Reserve the ADC analog pin exits before global routing

## Context

After ADR0017, seven ADC analog pins still lacked a sampled straight 1 mm
exit at the full ANALOG_AUDIO width. Native collision classification located
the conflicts at the adjacent filter-feed widening, filter-negative ground
drops, and reset via. These are source-copper placement conflicts, not missing
JLCPCB data or a demonstrated package impossibility.

The CS5308P-DN footprint/pin identity, external VMID scheme, independent
filter-negative ground returns and existing F.Cu paddle gaps remain authority.
No datasheet, part, analog filter value or current allocation changes.

## Options

- Keep all prior banks: the new regressions reproduce seven blocked exits.
- Reduce analog width, via size or clearance: unnecessary; reject this option.
- Delete the filter-negative returns or connect them directly to ADC49:
  violates the retained ground-return intent; reject.
- Move the filter widening and nearby ground/reset drops outward, then reserve
  the sixteen full-width analog launches: source geometry supports this option.

## Decision

Adopt five changed banks and sixteen added partial input banks in
`03_src/route.yaml prep.seed_stubs.stubs`. The source diff is the geometry
authority. Every other previous bank and all footprint poses remain unchanged.

Each FILT-positive 0.18 mm launch now runs 1.45 mm before widening to 0.35 mm;
both complete positive banks remain three primitives each. The two separate
negative drops move outward within the existing local width/clearance areas.
The reset path gains a full-width dogleg and an outward via. Existing ordinary
0.50/0.20 mm via geometry is unchanged; no via is added.

All sixteen ADC input pins receive a 1 mm straight F.Cu launch at the full
0.20 mm class width. Their complete capsules clear each other, native copper,
old seeds, ordinary/thermal vias, physical holes and both kinds of keepout.
No new rule area, width relaxation, clearance exception or plane cut is needed.
These are partial nets: all sixteen remain owned by the analog route wave,
which still owes their isolation, common-mode capacitor and bias branches.

## Consequences

Source totals become 88 banks / 218 straight primitives / 20 ordinary seed
vias, plus the unchanged nine protected thermal vias. Sixty-seven old banks
remain exact; five change and sixteen are added. The ADC source checker grades
91 existing-cell primitives / 13 cell vias; the new input checker separately
grades the sixteen simultaneous launches. Source tests now total 174.

The longer fine-pitch filter neck has a cost, not free capacity. Using the
existing ADR0015 model (nominal 35 um copper, rho85 = 2.1643958e-8 ohm-m),
each complete FILT-positive bank is 4.500464884544218 mm and 10.371271 mOhm,
versus 9.870535 mOhm previously. Charging the full conditional 2.5 A to each
bank separately gives 64.820444 mW, versus 61.690845 mW previously. This
3.129600 mW modeled increase assumes nominal copper and temperature; it is
not a measured temperature rise, ampacity, fault-duration or startup approval.
The rerunnable model and exact length/count assertions are in
`test_adc_analog_fanout.py`; all other power-path budgets remain unchanged.

Restoring the actual old five banks makes seven of the explicit input launches
fail native clearance again. Removing a launch and crossing neighboring inputs
also fail. The existing tests retain every other historical preservation
assertion while delegating exactly this later source delta to the new suite.

The PCB skills require source-owned fanout and exact geometry checks before
general routing; they do not turn these checks into release acceptance.
No BOARD, route preparation/import, generated schematic, review, checkpoint or
release is produced here. Full analog paired-path matching and trace DCR,
fresh generated admission/reviews, routing, filled-return/SI/thermal checks
and release sealing remain owed. Public-only sourcing, TOP77/0.20 A HOLD,
DO-NOT-ORDER and both-child-seals/fresh P-PUBLISH before main remain intact.
See `../SOURCE-CORRECTION-20260908-adc-analog-fanout.md` for attempt evidence.
