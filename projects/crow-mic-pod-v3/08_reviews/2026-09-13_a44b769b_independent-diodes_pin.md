subject: crow-mic-pod-v3 pre-route a44b769b
date: 2026-09-13
source_commit: abbae71edeab8d1addf9a8912d64c7c23c88ec7e
context-given: zero-context; exact native part-group dossiers and SHA-selected primary PDFs only
source_report_sha256: 8a81f4624dba1dc2a026588233df1116f4bf2df07ffb4652d1c4b06a394c6b1f
source_evidence_archive: 01_docs/journal/e3ea240d2d2d1055b669fa681cd0f73bd2b3765d4c23d8962e17282c610e9d44.tar.gz

review_stage: pre-route
review_kind: pin
reviewer: /root/rj45_pin_pod_diodes_approved (actual fresh independent agent)
context: FRESH
design_verdict: INCOMPLETE
order_verdict: DO-NOT-ORDER
board_sha256: a44b769b1a5ad5fa959b476bd30f91a64aeaba9ad64d7868fa4e60ffbb62ee48
parts_sha256: adf3f7221a131e270f963fab153a2e2f56262932f1e272af9cbc0e4814d5c8a6
design_rules_sha256: 02c4ed58432368b92e3019a06bf20c137dbf90765af16c96c458790e88d54a9f
raw_sha256: 8275e9e92c347cfc2bb2246b041d4e50186918aafe5b3b8a57cb7a5349c97c4d
semantic_sha256: dbb7b87bf88e4cff12b8d677938d1f22a3eb347c68d441aa5c1621dd48455ec2

Coverage is limited to D1 and D2 in the frozen commissioned packet. This is no whole-board acceptance, routing review, assembly inspection, or order authorization. The three immutable file bindings above are supplied metadata, not independently reviewed conclusions. Judgment used only the supplied protocol, native dossiers and exact digest-selected primary PDFs. No live design was opened. Historical verification notes embedded in dossiers were not adopted as evidence.

D1 — VERDICT: QUESTION

Primary: JKSEMI 1N4007(M7)SMA, 2021-10-21 revision c, SHA-256 f893d8385c6fee5af85b9053653bd8e93547c335c031cbab9ecb592c0bb5eddd. Images inspected: PDF page 1 package photo; page 2 all characteristic figures; page 3 PACKAGE OUTLINE, recommended mounting pads and Marking table, including a second render at 240 dpi.

D1 pin 1 (K): expected the physical cathode to connect to the protected output of a series input rectifier; observed west pad 1 at (-2.00,0.00) mm, declared K, on VIN_PROTECTED. The function-to-net assignment is sensible, but the exact supplied PDF does not explicitly label the banded terminal cathode, anode, 1 or 2. The photo has a band; the package drawing contains dimension/projection callout A, which is not an anode label. The native K assignment therefore lacks the explicit primary polarity identification needed for an independent physical-to-electrical pass.
D1 pin 2 (A): expected the series rectifier anode on its incoming positive source; observed east pad 2 at (+2.00,0.00) mm, declared A, on 12V_FUSED. Electrically consistent with the named source/protected rails, subject to the unresolved physical polarity identification above.
D1 package/count: expected two opposite SMA leads and zero exposed pads; observed two native copper pads, two distinct pad IDs, two distinct centers, two distinct function identities, zero EP, and zero collapsed identities. No fused pin alias is needed. Native pads are 2.5 x 1.8 mm at 4.0 mm center separation. The manufacturer's recommended land diagram is a two-land pattern; its nominal 4.2 mm center separation is not a pin-numbering or polarity declaration.
D1 winding/view: two collinear terminals have no defined CW/CCW winding. Native 'n/a (too few perimeter pins)' is correct. The native frame is explicitly footprint-local, rotation undone, +y down and readable as top view. A two-pad line alone cannot prove mirrored polarity. The package photo is a top/side perspective; package outline includes side/end and planar projections without numbered terminals. A mounted copper side is not independently stated in the dossier; only its declared top-view frame is used, with no global-side claim.
D1 unresolved fact (Q-D1-POLARITY): provide authoritative manufacturer identification tying the exact JKSEMI 1N4007(M7)SMA body's banded lead to cathode, and thereby to the native west K/pad 1 convention. A numbered manufacturer pin diagram is not inherently required if the cathode/anode physical marking is explicit. This is an evidence insufficiency, not an established polarity defect.

D2 — VERDICT: PASS

Primary: Littelfuse SMBJ Series, revised JC.07/04/25 v4, SHA-256 d7df155be4b1f612085401e8c946f065e284d65a0e7de22b9225a7b73946e51b. Images inspected: PDF page 1 Functional Diagram; page 5 Physical Specifications and Dimensions DO-214AA (SMB J-Bend); page 6 Part Numbering System, Part Marking System and Tape and Reel Specification.

D2 pin 1 (K): expected banded cathode of the unidirectional TVS on the positive protected rail; observed west pad 1 at (-2.15,0.00) mm, declared K, on VIN_PROTECTED. Page 5 top body figure explicitly places the cathode band at its left terminal; the native west cathode matches that physical orientation.
D2 pin 2 (A): expected opposite, unbanded anode on ground for positive-rail shunt protection; observed east pad 2 at (+2.15,0.00) mm, declared A, on GND. Page 1 unidirectional functional diagram confirms opposite cathode/anode terminals. Page 6 numbering identifies C as bidirectional, so SMBJ15A is the unidirectional member and the polarity requirement applies.
D2 package/count: expected two opposite SMB J-bend terminals and no EP; observed two native copper pads, two distinct IDs, two distinct centers, two distinct function identities, zero EP and zero collapsed identities. No fused aliases are needed. Numeric 1/2 are native artifact labels for K/A, not manufacturer numeric pin identifiers. Native pads are 2.5 x 2.3 mm at 4.3 mm center separation; the observed two-land geometry accommodates the two-terminal package. Exact solder-joint optimization is outside this pin review.
D2 winding/view: two collinear terminals do not define CW/CCW winding; native n/a is correct. Page 5 banded body plan view is top-side identification, with separate side elevation and land pattern beneath it. Page 6 top-marking figure is rotated relative to page 5 and confirms the same banded cathode. Dossier coordinates explicitly undo the board rotation of -90 degrees; local W/E is compared with the top body diagram, without introducing a mirror. A mounted copper side is not independently stated in the dossier; only its declared top-view frame is used, with no global-side claim. Assembly marking/placement artwork was not supplied or reviewed.

Instance comparison: this commission contains one instance of each different part. Both native cathodes share VIN_PROTECTED; D1's anode on 12V_FUSED and D2's anode on GND are the expected difference between a series input rectifier and a shunt TVS. There is no same-part multi-instance symmetry test to perform, and no evidence of an unexplained interchange.

Group disposition: D1 QUESTION, D2 PASS; INCOMPLETE because Q-D1-POLARITY is unresolved. No electrical/package defect is established. Delivery checks may PASS for this complete and honest handback; they do not change the engineering verdict.

Evidence: independent-derivation-before-dossiers.md was recorded before native dossier reading; the archive retains all inspected page images, exact native dossiers, source digest records, extraction/read/render measurement commands, complete combined stdout/stderr logs, runtime receipts, methods and this report. Source PDFs remain at their immutable digest-bound frozen packet paths and are not duplicated. The evidence manifest was built by reopening and hashing every regular archive member, rejecting symlinks, traversal, duplicate names and embedded archives. Post-packaging preflight logs are retained alongside the archive in allocated scratch as delivery receipts.
