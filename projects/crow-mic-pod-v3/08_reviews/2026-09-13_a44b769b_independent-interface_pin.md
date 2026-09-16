subject: crow-mic-pod-v3 pre-route a44b769b
date: 2026-09-13
source_commit: abbae71edeab8d1addf9a8912d64c7c23c88ec7e
context-given: zero-context; exact native part-group dossiers and SHA-selected primary PDFs only
source_report_sha256: 4d784dd33ccbe4737f8c1e52fe766182d3d6e54e6fe4d1174a9d78fcc1817e5f
source_evidence_archive: 01_docs/journal/dfceda1b3eb8b705ebf68b43a713f3ed27b91d6ce761b5d0ae5eef766f81e317.tar.gz

review_stage: pre-route
review_kind: pin
reviewer: /root/rj45_pin_pod_interface_approved (actual fresh independent agent)
context: FRESH
design_verdict: INCOMPLETE
order_verdict: DO-NOT-ORDER
board_sha256: a44b769b1a5ad5fa959b476bd30f91a64aeaba9ad64d7868fa4e60ffbb62ee48
parts_sha256: adf3f7221a131e270f963fab153a2e2f56262932f1e272af9cbc0e4814d5c8a6
design_rules_sha256: 02c4ed58432368b92e3019a06bf20c137dbf90765af16c96c458790e88d54a9f
raw_sha256: 9f02bbc839df9e7f0960a76ee25d91a3cff72185c63a2b7c6f537226ee02612e
semantic_sha256: f4e30437d56c280dc68c638cbf44b1625c28fd8149de29e581fbedc4507825e6

Coverage: commissioned J1 and U3 only, one supplied instance each. No whole-board acceptance, routing review, cable assignment validation or assembly approval. Immutable hashes are metadata bindings, not whole-artifact reviewed conclusions.

J1 VERDICT: QUESTION

Primary: Wurth 615008160221 revision 001.003 dated 2025-07-09, PDF page 1 Dimensions and Recommended Hole Pattern. SHA-256 6ed18749211d4e6cbffd99cd0b90461dfe4ec6d70f558ceceeb5901651f0e048. Actual image inspected before dossier.

Measured native count: 10 numbered pads / 10 distinct identities: eight contacts and two separately preserved shield stakes. The dossier also reports two unnumbered paste/mechanical pads; their actual type, geometry and drill sizes are not supplied. Manufacturer drawing shows eight signal tails, two shield stakes, two mechanical pegs, no EP. No fused identity collapse is present in the numbered table. Native 9/10 are software identities for physical shield stakes, not manufacturer contact numbers.

Printed contact rows are 8,6,4,2 upper left-to-right and 7,5,3,1 lower left-to-right; row spacing 4 mm, within-row pitch 2.04 mm and stagger 1.02 mm. With printed pin 1 at the origin, rotating the printed pattern 180 degrees yields all eight native positions exactly at supplied precision. This is a proper rotation, not reflection. The reported CCW scalar is not an applicable perimeter-winding gate for an alternating connector sequence; coordinate-by-identity comparison controls.

J1 pin 1 (CONTACT_1): expected rotated position (0,0); observed (0,0), 12V_POD.
J1 pin 2 (CONTACT_2): expected (1.02,4); observed (1.02,4), GND.
J1 pin 3 (CONTACT_3): expected (2.04,0); observed (2.04,0), 12V_POD.
J1 pin 4 (CONTACT_4): expected (3.06,4); observed (3.06,4), AUDIO_N.
J1 pin 5 (CONTACT_5): expected (4.08,0); observed (4.08,0), AUDIO_P.
J1 pin 6 (CONTACT_6): expected (5.10,4); observed (5.10,4), GND.
J1 pin 7 (CONTACT_7): expected (6.12,0); observed (6.12,0), 12V_POD.
J1 pin 8 (CONTACT_8): expected (7.14,4); observed (7.14,4), GND.
J1 pads 9/10 (SHIELD_S1/S2): expected separate physical stakes 14.8 mm apart; observed (10.97,-2.35) and (-3.83,-2.35), 14.80 mm apart, both POD_SHIELD. No circuit-ground connection is mandated for shield by this primary drawing.

These passive contact net kinds do not themselves contradict the functions. Cable assignments and contact current budget cannot be established from this packet.

J1-Q1: Actual mounted board side and explicit coordinate reflection normalization are absent. The manufacturer's Recommended Hole Pattern is not expressly labeled top/bottom. The exact printed-pattern rotation match does not independently establish mounted component-side orientation. Resolve with unambiguous primary mounting-view interpretation tied to actual mounted side and native coordinate normalization. Author verification notes are not substituted for missing evidence.

U3 VERDICT: QUESTION

Primary: TI TPD2E2U06 SLLSEG9C, PDF page 3 DRL Package 5-Pin SOT Top View and Pin Functions; PDF pages 17/18 DRL0005A Package Outline and Example Board Layout, drawing 4220753/E 11/2024. SHA-256 a133b86ea3d3c3d34667339b92d3b5e98d541d10e9775d63e7cdfa153794f4ed. All three actual figures inspected before dossier. Alternate DCK package excluded.

Measured native count: five pads / five distinct lead identities, no EP, no fused aliases. Expected DRL has three leads left and two right; pin 1 ID upper left. Native vertical pitch 0.5 mm agrees. Native column spacing 1.42 mm differs from TI example 1.48 mm; lands 0.68 x 0.35 mm differ from TI example 0.67 x 0.30 mm. Manufacturer allows alternate land designs; these differences alone are not a pin identity failure.

U3 orientation: expected component top view 1 upper left, 2 center left, 3 lower left, 4 lower right, 5 upper right, CCW. Observed asserted native top view is 1 lower left, 2 center left, 3 upper left, 4 upper right, 5 lower right, CW; measured +y-down signed area +1.42 mm². This is a definite reflection relative to the dossier's asserted frame. Its board rotation of 180 degrees alone preserves winding and cannot reconcile the assertion. A bottom-side representation may add a reflection, which cannot be adjudicated without actual mounted-side and normalization data.

U3 pin 1 (NC): expected upper left, allowed floating/GND/VCC; observed lower left, unconnected-(U3-NC1-Pad1).
U3 pin 2 (NC): expected center left, allowed floating/GND/VCC; observed center left, unconnected-(U3-NC2-Pad2).
U3 pin 3 (IO1): expected lower left signal channel; observed upper left, AUDIO_P.
U3 pin 4 (GND): expected lower right ground; observed upper right, GND.
U3 pin 5 (IO2): expected upper right signal channel; observed lower right, AUDIO_N.

Logical names/nets by pad number are plausible: NCs have separate unconnected nets, IOs see signal nets, GND sees GND. Audio voltage range is absent; net names do not prove the manufacturer's 0–5.5 V recommended operating range. No waveform or clamping-system approval is made.

U3-C1 conditional consequence: IF native coordinates are already component-side-normalized top view, fitting the three-lead side to the three-land side gives physical pin 1 -> native 3/AUDIO_P; physical 2 -> native 2/NC; physical 3 -> native 1/NC; physical 4 GND -> native 5/AUDIO_N; physical 5 IO2 -> native 4/GND. That case is FAIL and an electrical defect. This is not a proven fabricated-board defect from the supplied packet alone.

U3-Q1: Supply actual mounted board side and whether the dossier removes or retains side reflection when undoing rotation. A confirmed normalized top view yields FAIL; bottom-side mounting needs an explicit transformation and recomparison, not assumed acceptance. Initial unconditional FAIL interpretation was corrected to this bounded conclusion and retained in interpretation-history.md.

Instance symmetry: one instance of each commissioned part; no within-group multi-instance comparison exists. No claim about omitted references.

Method: exact envelope inputs verified before and after; finite direct-argv pdftotext/pdftoppm under shared pipeline_runtime.run_stage, explicit cwd/environment; actual images viewed; derivation saved before native comparison. Evidence retains rendered figures, native dossiers, text, runtime, methods, counts, hashes, and interpretation history. Delivery PASS denotes complete honest handback with engineering questions, not acceptance.
