# r10 local connector render review

Final carrier: `carrier-final-v2/`, native SHA256
`1fc774524ef57efdd3a644de338328837e42ba648d3a4dd6bb78bad44e8852a1`.
Pod: `pod/`, unchanged r9 native. Earlier `carrier/` and `carrier-final/`
depict superseded engineering candidates; do not use them for upload review.

- [Carrier gallery](carrier-final-v2/gallery.html), [45-degree view](carrier-final-v2/upper_045.png), [overview](carrier-final-v2/overview.png).
- [Power-jack close-up](carrier-final-v2/detail-J1-upper_045.png).
- [Pod gallery](pod/gallery.html), [45-degree view](pod/upper_045.png), [overview](pod/overview.png).

The vNext render-board skill produced six cardinal views, upper/lower45-degree
orbits at eight azimuths, and seven views per reviewed connector. Final sets
contain92 carrier and29 pod views plus two overview sheets:123 PNGs.

Native numbered pad and locator-peg registration checks pass for all reviewed
connectors. Carrier PJ-102AH J1 now points toward board -Y/outward; all eight
RJ jacks, the pod RJ jack and the Pico USB connector retain their outward
direction. The jack's final pin1 anchor is(188,14.7),180deg, body center(188,8.2),
nominal mouthY1.0. These are native coordinates, not a JLC model-angle convention.

Sources, renderer code, native boards, configuration and image hashes are bound
by each set's report/manifest. Verify with the render-board `--verify` command.
The actual independent affected mechanical/electrical decision is separately
recorded in `../power-jack-r10-review/review.json`; rendering never issues it.

Models are drawing-derived diagnostic solids, with illustrative cavities/contact
profiles. Other populated bodies are footprint envelopes with illustrative1mm
height, not manufacturer CAD. They cannot establish jack-to-diode clearance,
plug engagement, terminal/hole fit, thermal cooling, seating or assembly approval.
Those claims require the independent native/manufacturer-envelope review.
In particular, isolated connector close-ups hide neighboring components by design.

JLC placement-registration, stackup and manufacturing holds remain. No vendor
draft, production release, order, reservation or purchase changed.
