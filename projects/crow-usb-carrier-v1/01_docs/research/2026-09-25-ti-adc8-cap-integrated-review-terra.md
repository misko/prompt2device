# Independent review: ADC8 southwest-cap source union

**Disposition: geometry pass; do not promote the cap anchor to canonical source or
P2/P1.**  The source-generated union in SOL commit `9206545a` is a sound,
hash-bound placement experiment, but its one-cap adjustment has no coupled
physical-cell, endpoint, route, or return proof.  It therefore must wait for
that evidence before a source-floorplan promotion.

## Independent replay

Candidate
`01_docs/research/2026-09-25-ti-adc8-cap-integrated-replay-sol/candidate.kicad_pcb`
has SHA-256
`0b9d017706845ad4d77c2b579dd36f2e34c0ecf55a7b699ace4fca97465c5b93`.
The frozen TI board remains
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.

I ran the committed `analyze.py` and `profile_compare.py`.  The latter uses
the hash-pinned full native profile, including the frozen project and DRU,
source-generated Type-VII POFV rule areas, and via-process check.  It reports
213 DRC violations and 499 unconnected items for both the prior union and this
candidate, with an issue-identity delta of `+0/-0` and no `U_ISO8` clearance
finding.  This replaces neither routing nor a clean-board claim.

The ref set remains 569.  All 27 fixed references retain their poses; the
native intrinsic pad identity census remains 1,872 pads with identical
reference, pad number, net, layer set, shape, size, and drill.  There are 46
intentional moves relative to the frozen TI board: the reviewed 45-placement
union plus `Q_PRE`; the only change relative to that union is
`C_ADC_AC8N1 (198.20,60.25,0) -> (198.00,60.05,0)`.

## Physical result

The checker `_physical_envelope` (body/courtyard, excluding movable text) for
the moved cap is `[195.205,58.305,200.795,61.795]` mm.  It has no native
envelope or pad intersection.  Its two relevant source-rectangle gaps are
both 0.205 mm: east to `analog_ch8` x=201 and north to `usb_vbus_sense` y=62.
The closest support envelopes are `C_A8P` at 0.360 mm, `R_B8P` at 0.480 mm,
and `C_FILTER8N1` at 0.780 mm.  Related pad-center distances improve to
7.742254 mm (`C_ADC_AC8N1.1` to `U_ISO8.6`) and 13.870865 mm
(`C_ADC_AC8N1.2` to `C_ADC_CM8N.1`).

The global owner census is unchanged: 454 of 569 footprints fully contained,
115 outside their primary owner rectangles, 139 references with 150 foreign
planning incidences, and zero cross-owner native envelope/body/pad interaction
pairs.  Compared with the frozen TI board, the union also removes the prior
`C_IN3`/`Q_PRE` courtyard-only envelope intersection; it adds no full-envelope
or pad pair.

## Required coupled evidence before source adoption

This move repairs only a rectangle-margin sliver.  It cannot establish that
the ADC8 functional owner has an exclusive physical cell, because the census
still records the existing owner/foreign-region debt.  Current checker branch
semantics use the primary `regions[block]`, rather than a `physical_cell_id`,
so a cap pose cannot by itself authorize an ADC8 pocket or endpoint handoff.

Before adopting the anchor, a source-generated coupled candidate must provide:

1. A typed, nonoverlapping physical-cell/primary-region plan covering the
   affected ADC8 and USB boundary members without hiding foreign footprints.
2. Exact native-pad endpoint access from `C_ADC_AC8N1.2` and a P2 return path,
   with filled In1.Cu reference coverage; this board has an unfilled zone and
   499 opens.
3. Full-profile DRC and complete owner census replay after that region plan,
   with no newly introduced native issue or owner/cell contradiction.

The 0.205 mm geometric gap is useful placement evidence, but it is neither an
assembly allowance nor route/return or P1/P2 credit.

## Commands run

```sh
python3 01_docs/research/2026-09-25-ti-adc8-cap-integrated-replay-sol/analyze.py
python3 01_docs/research/2026-09-25-ti-adc8-cap-integrated-replay-sol/profile_compare.py
```

Both completed successfully.  KiCad printed its known property-enum debug
assertions during load; the committed scripts completed and returned the
results stated above.
