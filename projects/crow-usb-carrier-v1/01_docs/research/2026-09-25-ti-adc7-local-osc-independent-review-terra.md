# Independent review: TI ADC7 local oscillator probe

**Research review only.** I reviewed `3a2c1b6f` and `25ce1dd4` against the
exact TI board SHA-256
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
The packet is correctly isolated and preserves the board outline, all 27 fixed
poses, and the complete pad-number/net/layer signature. Its receipt reports
no new checker physical-envelope collision pairs, unchanged 499 unconnected
items, improved listed related-pad centre gaps, and 12 new DRC warnings (seven
`silk_overlap`, five `silk_over_copper`). Those warnings are source-label debt,
not a placement or routing acceptance.

The relevant distinction is valid: `Y_AUDIO` at `(167.5,87.2)` has checker
physical envelope `[164.705,85.105,170.295,89.295]`, yielding 0.105 mm to the
ADC7 portal’s y=85 edge. The closest actual Y copper pads are `.3/.4`, with
top edge y=85.400; their vertical copper-to-portal gap is 0.400 mm. Thus the
0.105-mm number is a courtyard-to-virtual-reservation margin, not a copper
clearance result.

That margin is still too weak for P2 promotion. The packet has no declared
component-placement tolerance, courtyard/reservation clearance rule, actual
ADC7 trace geometry, endpoint fanout, or return proof. The board minimum
0.15-mm copper clearance does not establish a safe 0.105-mm courtyard margin.
Hold the candidate as a useful physical witness, but do not promote its portal
to P2 until either (a) the oscillator is moved upward enough to meet an
explicit, source-governed portal-to-courtyard margin after tolerance, or (b) a
reviewed source rule demonstrates why the 0.105-mm gap is sufficient. An
illustrative 0.25-mm target would require at least 0.145 mm more upward Y
clearance; it is not an admitted requirement.

The candidate is therefore **not rejected as a placement probe**, but it is
rejected for any P2 routing/portal credit at its present margin. Its existing
P1/source ownership and typed-cell failures, full timing denominator, pad
access, filled-return, and silk cleanup remain open.
