# Samtec TCSD-06-D-04.50-01 primary-source fact record

Accessed: 2026-09-01
Authority status: exact selected cable identity; miniDSP-header fit still owed

Primary authorities:

- [Samtec exact product page for TCSD-06-D-04.50-01](https://www.samtec.com/products/tcsd-06-d-04.50-01)
- [Samtec TCSD series print, revision BE](https://suddendocs.samtec.com/prints/tcsd-xx-x-xx.xx-01-x-xxx-xxx-mkt.pdf)

The inspected four-page manufacturer PDF is 339,612 bytes with SHA-256
`fa4643ec2ea321bf7bc186d20bf8c1b31a7fb0b3d335662c2ba8eba9007b108b`.
The exact PDF is vendored as `TCSD-Series_RevBE.pdf`; its bytes match that
digest. This record retains the reviewed facts separately from the immutable
drawing.

The exact order code selects a 2.00 mm-pitch, six-position-per-row (12-circuit),
double-ended female IDC cable assembly with 4.50 inch nominal assembled length
and lead style `-01`. No reverse-wiring, reverse-socket, daisy-chain, breakout,
notch-polarization, or strain-relief suffix is selected. Drawing facts used for
planning are:

- length 114.30 mm with +/-3.175 mm tolerance because it is shorter than
  12.5 inches;
- each base socket body is 16.00 mm reference across the six positions,
  5.08 +/-0.254 mm wide, and 3.18 mm reference along the mating depth;
- the ribbon conductors are 28 AWG, 7/36 tinned copper with PVC insulation;
- assemblies receive 100% short/open testing and 800 V hi-pot testing;
- the colored conductor lies at the first-position-indicator side on the base
  double-ended configuration;
- Samtec lists TMM headers among compatible mating connectors.

The TCSD is therefore the selected exact replacement for anonymous kit cables
on the carrier side. The miniDSP manual identifies only a suitable 2x6,
2.00 mm-pitch cable interface, not its board-header MPN, post section, or
contact length. Consequently module-side fit, actual one-to-one continuity,
socket rotation, retention, bend envelope, and simultaneous J1/J3 service stay
physical first-article holds.
