# Coupled ADC7/8, audio/TDM, and XU-west refloorplan plan

**Research plan only.** This is a reject-first experiment plan for the exact
four-part TI candidate, SHA-256
`046019a13094764baef313d62611b137e0f0af971079734c71ab050dbf46b3a0`.  It does
not alter source or a board, establish a corridor, consume a P1 attempt, or
accept P1/P2.

## What the two negative bounds require

`c9219d88` rejects the isolated nine-part VMID/ADC8 correction: with every
other native pose fixed, `C_ADC_AC8N1` has no owner/foreign-clear pose meeting
the exploratory related-pad locality screen.  Its nearest separated pose is a
12.0-mm move and worsens one related pad distance from 11.811 to 19.170 mm.
Therefore a channel-8 correction must move its local endpoint neighborhood,
not merely the eight `R_B1P`...`R_B8P` resistors plus `C_ADC_AC8N1`.

`3fa0c62c` rejects using silk movement as an ownership remedy.  It changes no
footprint envelope, pad access, region membership, or routing mouth.  All
physical tests below consequently use the checker's `_physical_envelope(fp)`
(body/courtyard, without text) and pads; ref/value-text boxes are only an
assembly-readability follow-up.

## Exact starting ownership and immovable set

The source rectangles are `analog_ch7=[157,42,179,84]`,
`analog_ch8=[179,42,201,84]`, `audio_clock_tdm=[145,72,190,99.84]`, and
`xmos_core=[190,84,217.2,110.5]` mm.  The overlaps at the ADC/audio and
audio/XU boundaries are the defect to resolve; this plan does not license a
larger shared rectangle.  A physical-cell candidate must assign every modular
reference once and must be disjoint from each foreign physical cell.

The following 27 fixed reference poses are invariant in every probe:

```
J1 J2 J3 J4 J5 J6 J7 J8 J_PWR J_USB J_JTAG
C_HOLD1 C_HOLD2 C_HOLD3 C_HOLD4 C_HOLD5 C_HOLD6 C_HOLD7 C_HOLD8
C_HOLD9 C_HOLD10 C_HOLD11 C_HOLD12 C_HOLD13 C_HOLD14 C_HOLD15 C_HOLD16
```

Also invariant until a probe expressly changes it: outline, layer stack,
rotations, footprints/pad numbers/nets/layers, and the candidate's four known
local moves (`Y_AUDIO`, `C_ADC_I2C_A`, `C_ADC_I2C_B`, `C_ADC_CLOCK_OK`).  The
current 0.255-mm ADC7-portal-to-`Y_AUDIO` courtyard separation is a measured
geometry fact, not a clearance, trace, return, or source-ownership credit.

## Minimum coupled movable sets

Each set is a lower bound on a test, not a claim that all members must be
moved in the final board.

1. **Channel-8 endpoint set:** `C_ADC_AC8N1`, `U_ISO8`, and `C_ADC_CM8N`.
   These are the two partners used by the rejected local search.  They must be
   evaluated together before considering a new channel-8 cell boundary.  The
   remaining VMID owners are eight coupled pairs
   `R_BnP`/`C_ADC_ACnP1` for n=1..8; moving a resistor alone is excluded
   because its required west move collides with its own channel capacitor.
2. **ADC7/audio boundary set:** the four already moved local parts
   `Y_AUDIO`, `C_ADC_I2C_A`, `C_ADC_I2C_B`, and `C_ADC_CLOCK_OK`, plus their
   locality partners `C_AUDIO_OSC`, `U_ADC_I2C_XLATE`, and `U_ADC_CLOCK_OK`
   if the probe changes an audio-cell boundary.  A typed ADC7 face at
   `[166,83.9,167.12,85]` cannot coexist with the present audio rectangle:
   any `audio_clock_tdm.y1 >= 85` recut must first enumerate and relocate or
   reassign every real body/courtyard it cuts.  It may not be justified by the
   former text-only collision report.
3. **TDM/XU-west boundary set:** `C_XU_VDD_105` and `C_XU_VDDIO_109`, the two
   native envelopes limiting the previously inspected lower transition.  Do
   not infer route capacity from their nominal spacing.  If either moves, its
   U_XU power-pad access and local return are explicit debts; the source owner
   stays `xmos_core` unless a complete, exclusive replacement cell is proven.

The first candidate should keep these three sets separate in the source:
three typed, nonoverlapping physical cells with explicit member lists and
explicit transition endpoints.  It must not introduce a generic `shared`
region or borrow area from a foreign owner by rectangle overlap.

## Reject-first test order

1. Copy the exact four-part board to an isolated packet and hash it.  Reject
   on any change to the 27 fixed poses, outline, pad identity/net/layer, or
   native full-envelope/pad collision delta.
2. Test the channel-8 endpoint set as a unit.  For every pose, require each
   complete native envelope and every pad to be inside `analog_ch8`'s proposed
   cell and outside all foreign cells; retain the two actual related-pad
   distances to `U_ISO8.6` and `C_ADC_CM8N.1`.  Reject if only a resistor or
   only `C_ADC_AC8N1` is moved, if an endpoint loses pad access, or if the
   unfilled In1.Cu GND zone is used as return credit.
3. Independently screen the ADC7 typed face against physical envelopes and
   pads after applying only the four-part candidate moves.  Reject any source
   boundary recut that intersects a real audio envelope, leaves a modular ref
   unassigned, or creates overlap with `analog_ch7`; silk-only intersections
   are recorded separately.
4. Screen the TDM/XU-west transition with its exact named endpoints, full
   envelopes, and pads.  Reject on an assumed slot count, a straight-cut
   corridor, or a transition with no exclusive owner and no pad-access proof.
5. Only if steps 2--4 each pass, compose their cells and verify all cells are
   mutually disjoint, members occur exactly once, and each required ADC/TDM/XU
   endpoint has a named source owner.  Then measure actual trace entries,
   layer changes, and continuous return geometry; rerun native DRC after
   routing.  The present unfilled GND zone means none of those obligations is
   currently met.

Passing a screen only produces an isolated candidate for review.  P1 remains
`INCOMPLETE` and `p1_accepted: false` until the canonical contract, complete
routes, returns, DRC, and required P2 evidence independently validate it.
