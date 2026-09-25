# Independent review: TI four-part ADC7 candidate

**Research review only.** Commit `d7a47c93` binds candidate board SHA-256
`046019a13094764baef313d62611b137e0f0af971079734c71ab050dbf46b3a0` to the
three-part source candidate SHA-256
`c9b758d69867b274f0592bd2eceb9a26d64a80dd2daafa8ab9516d23d5925502`.
Its receipt records unchanged outline, all 27 fixed poses, and all
pad-number/net/layer identities. Physical-envelope and pad overlap counts
remain 3→3, with no new pairs; both ADC portals are physically clear.

This is a better **P2 research candidate** than the three-part placement: the
ADC7 portal-to-Y courtyard margin increases from 0.105 to **0.255 mm**, while
Y-to-TDM and Y-to-bypass gaps improve to 15.643 and 5.982 mm. Moving
`C_ADC_I2C_B` improves its VCCB-to-translator pad-centre gap from 7.920 to
1.671 mm. The 0.255-mm result exceeds the earlier illustrative 0.25-mm
screen, which remains not a source requirement.

It is not ready for P2 promotion. `C_ADC_I2C_B` has only **0.150 mm** to the
`U_ADC_I2C_XLATE` courtyard and **0.195 mm** to the `U_TDM_XLATE` courtyard.
Those are geometry gaps, not demonstrated copper/pad escape, assembly
tolerance, or return margins. DRC rises from 12 to 15 warnings, all silk;
the three additions are moved-cap reference-field overlaps. Unconnected items
stay 499 and no new non-silk DRC type is reported, but this is not routed DRC
acceptance.

Before any P2 use, source must persist the four placements and readable label
locations, clear all 15 silk warnings, prove cap pad access and return-via
geometry, route ADC7 with effective clearance, prove filled In1.Cu return,
and resolve channel-8 ownership plus complete timing-bundle endpoints. No P1
or P2 acceptance follows from this review.
