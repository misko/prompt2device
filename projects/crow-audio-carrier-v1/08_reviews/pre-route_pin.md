review_stage: pre-route
review_kind: pin
reviewer_identity: /root/carrier_topology_refresh
context: FRESH FIX-PASS
completed_at: 2026-09-17T00:11:32Z
source_commit: fd8c88b2accd3df10d8b1443e1e5968e1c4f0c3b
design_verdict: SOUND
order_verdict: BLOCKED-SOURCING
qualification: FIRST-ARTICLE-ONLY
board_sha256: c03db60ae47d6737e0bab2439bc410a127b8f15acfdde82925f77f96d62287df
parts_sha256: 19914c21c35cc6593b6dcc88a26f5b094517c09c3834356f6fc252048ce3b916
design_rules_sha256: 945c7614cbfe8a321faa691286034a9d10fe8f9a14349732a25eb40bdf483792
locator_manifest_sha256: ead3b85efb53b27a1486d5a3d80b53bf778c3afef7c4d373c2801434cdde45bd
bom_sha256: e10bffd5c56171b349af1c282ddaf618f236d4fc66a6d5a14d9f5732fc76d44d
cpl_sha256: b4e43d2ae1e007fa8506b299380fb49b77297cc2b8db9fc352f4d490e1892864
twin_report_sha256: 7450fd61047002827a49f49e41589ee68258e89e83f35dae3277d9e3c5387695
twin_overlay_report_sha256: d3f573dc408fa6ebd4154ba12b6cfe36c04eeb8abd78df76238e0e98f11f451d
orientation_subject_sha256: 155896eb43a7c2b04c684523d4d96309bd4d945670f11a1c7a1d52b01a7a70e8

Fresh independent physical-pin verdict: SOUND for the exact current pre-route
carrier board. I regenerated conclusion-free pin dossiers from this board and
its current BOM, inspected the current part authorities and affected primary
documents, compared every physical identity against the board, and checked the
locator, twin, overlay and connector-orientation evidence. This witness does
not treat internally consistent project artifacts as external pin authority.

P-PINMAP grades 47 multi-pin references and passes 411/411 declared physical
pin identities into both the schematic circuit model and real board pads,
including every explicit fused-land alias. The fresh pin-audit extraction
produces 47 nonempty dossiers with mounted side, component-top coordinate
frame, winding, pad size, function and observed board net. The exact board has
340/340 footprints on F.Cu, 1,058 total pad features and 985 numbered electrical
pads. No component is mounted on the back side.

I compared the current board against the accepted v0.1.5 source board, SHA-256
`0776f364424282a7924266450f899ce69bf28cf95a602ca74d92b86fd91c164d`.
All 340 reference sets match. Footprint library/item identity, value, x/y
position, rotation, mounting side, every numbered and anonymous pad position,
size, shape, attribute, layer set and net are identical for every reference.
Only `exclude_from_pos_files` changed, and only on the intended six references:
U_ADC, F_IN, C_FILT1_470U, C_FILT2_470U, C_HOLD1 and C_HOLD2. This is a
population-file attribute and cannot mirror, renumber, move or reconnect a pad.
Thus the accepted primary-document pin conclusions remain applicable to the
unchanged geometry, while the exact current hashes above bind this review.

The parts-dossier delta is also pin-neutral and was rechecked rather than
assumed. The 2920L260/33DR dossier changes only its sourcing code and still has
two interchangeable passive terminals in the exact 2920 land. The CS5308P-DN
dossier changes only its sourcing code: Cirrus DS1314F1 SHA-256
`6ca42cc09ac47ebdacacaee435f05e3f9c34b83d5692e52a2d8a26533e810e57`
still defines pins 1 through 48 plus exposed paddle 49; the current exact QFN
footprint and board retain all 49 identities, with EP49 on GND_A/GND. The
EEEFK1A471P dossier adds manufacturer-land adjudication without changing its
pin map. Panasonic PDF SHA-256
`b36857d089adaddf3042b33bf11d0f7d83bf70734e983f33b7827152e11854e3`
identifies the standard-P size-F polarized part. Pad 1 remains positive and pad
2 negative on all four instances: C_FILT1_470U.1 is FILT1P,
C_FILT2_470U.1 is FILT2P, C_HOLD1.1 and C_HOLD2.1 are 5V_LDO_HOLD, and all
four pad-2 terminals are GND. The exact native land remains +/-3.55 mm with
4.0 x 2.0 mm pads, matching the manufacturer standard-product table.

The current BOM has 54 lines and the CPL has 306/306 placements, all on the top
side. Each of the six corrected SMD references is present exactly once with its
unchanged value, footprint and rotation: U_ADC 270 degrees, F_IN 0 degrees,
C_FILT1_470U and C_FILT2_470U 180 degrees, C_HOLD1 0 degrees and C_HOLD2
180 degrees. These rotations agree with the unchanged accepted board geometry;
final uploader rotation and polarized-part preview remain mandatory.

Connector evidence is coherent with the pin map. The independently parsed
spoke contract passes 8/8 J1-J8 implementations. Each exact Wurth RJ45 retains
pins 1/3/7 on its channel's protected 12 V rail, pins 2/6/8 on GND, pins 4/5
on AUDIO_N/P respectively, and shell pins 9/10 on CHASSIS. The current
orientation receipt binds this board and passes 9/9 edge connectors: J1-J4 face
north, J5-J8 south, and J9 west, each with model/footprint alignment 1.0. The
user approval binds the same subject SHA-256 and all eleven evidence-image
hashes. J10/J11 remain unchanged top-entry Samtec headers; their pad identities
and nets are byte-for-byte unchanged from the accepted board. The external
MCHStreamer post fit, cable keying and continuity remain explicit first-article
holds because the COTS module-side header identity is not published.

The exact locator structure passes 333/333 references, 1,051 graded pads,
23/23 exception pages and 26 manifest members. The current twin resolves bodies
for 333/333 fitted/manual references, including 306/306 CPL bodies and 27/27
manual bodies. Its same-camera overlay passes calibration and measures 83/83
resolvable bodies; the remaining 250 are explicitly below the image-resolution
floor rather than silently credited. U_ADC, F_IN and all four newly placed
Panasonic cans are among the measured bodies. The twin's retained catalog-CAD
adjudications and D_HOLD's polarity-blind catalog marking preserve their human
uploader checks; they do not contradict a numbered-pad identity on this board.

No pin-count, pin-1, winding, mirror, fused-land, exposed-pad, function-to-net,
pairwise-instance, polarity, mounting-side or connector-direction defect was
found. This review grants placement-stage pin acceptance only. It does not
grant the separate locator/render witness, routing, fabrication, JLC uploader,
first-article or order acceptance. Public evidence remains insufficient to
prove JLC allocation for every exact placed line, so order status remains
BLOCKED-SOURCING.
