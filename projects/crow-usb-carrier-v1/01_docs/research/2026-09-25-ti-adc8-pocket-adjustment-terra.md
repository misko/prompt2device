# ADC8 cap/USB pinch: bounded pocket adjustment — research only

This evaluates the full-profile integrated TI research board, candidate SHA-256
`20373950748ac51113b115b2d12d169160c24024a2a000572bb70c67b0f60919`.
It changes no source or board artifact and makes no P1/P2, route, return, or
vendor-process claim.

`C_ADC_AC8N1` is currently at `(198.2,60.25,0°)`.  Its checker physical
envelope is `[195.405,58.505,200.995,61.995]` mm: only 0.005 mm from the
`analog_ch8` x=201 boundary and the `usb_vbus_sense` y=62 boundary.  This is
source-rectangle proximity, not a native foreign-footprint collision: the
closest foreign full envelope is `R_VBUS_B` at 9.5082 mm.

The bounded next source candidate is to change only this movable capacitor's
anchor to `(198.0,60.05,0°)`, a southwest 0.200 mm shift.  It produces
physical envelope `[195.205,58.305,200.795,61.795]` mm: 0.205 mm margin to
each concerned boundary.  It has no full-envelope intersection with any of
the other 568 footprints.  The nearest local support envelopes remain inside
the same functional owner after the shift: `C_A8P` at 0.360 mm, `R_B8P` at
0.480 mm, and `C_FILTER8N1` at 0.780 mm.

The shift preserves, and slightly improves, the two recorded local pad
distances: `C_ADC_AC8N1.1` to `U_ISO8.6` changes 7.846177 to **7.742254 mm**;
`C_ADC_AC8N1.2` to `C_ADC_CM8N.1` changes 13.957539 to **13.870865 mm**.
`J8` and every one of the 27 fixed references remain untouched; all other
568 placements and therefore the 569-reference owner census denominator are
unchanged.  The shifted full envelope and both pads remain inside
`analog_ch8=[179,42,201,84]` and avoid the USB rectangle.

I reproduced a temporary full-profile native screen by copying the candidate,
applying only this pose, then applying the exact TI `.kicad_pro`, `.kicad_dru`
and `generate_tmux4827_pofv.py` producer before `kicad-cli pcb drc`.  It
reports **213 DRC issues and 499 opens**, exactly the established profile
denominators, with no DRC item involving `C_ADC_AC8N1`.  This is evidence for
the one-cap physical adjustment only; it is not a routed board result.

A less complete alternative is an x-only 0.200 mm move to `(198.0,60.25)`.
It clears the analog x edge but retains the 0.005 mm USB-y pinch, so reject it
as a pocket repair.  Likewise, a broad analog/USB region expansion is not a
valid substitute: it would overlap the long-lived `analog_ch8` and
`usb_vbus_sense` rectangles without creating endpoint access or return proof.

Before any source promotion, require a generated-board replay with: exact
569-reference/pad identity and 27-fixed invariance; full-envelope and pad
collision delta; full-profile POFV DRC delta; all owner/foreign-region
incidences; the two locality distances above; and the existing ADC8 endpoint,
return, and 0.005-mm-independent physical-cell obligations.  This candidate
does not settle those outstanding P1/P2 debts.
