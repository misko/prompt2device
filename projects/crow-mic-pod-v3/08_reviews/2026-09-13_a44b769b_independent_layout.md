subject: crow-mic-pod-v3 current pre-route layout
date: 2026-09-13
source_commit: abbae71edeab8d1addf9a8912d64c7c23c88ec7e
context-given: zero-context; exact current source/native board/r0/renders
source_report_sha256: 42f35a9c181313854f3eb828f482756bb8a2b6d118d62c08a3148bee28c3fac0
source_evidence_archive: 01_docs/journal/9ee14db60252852bc6a4f52f05a614a436a167e5197504e2cbd26fd9220d48fa.tar.gz

review_stage: pre-route
review_kind: layout
reviewer: /root/rj45_pod_layout_approved
context: FRESH
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: a44b769b1a5ad5fa959b476bd30f91a64aeaba9ad64d7868fa4e60ffbb62ee48
design_rules_sha256: 02c4ed58432368b92e3019a06bf20c137dbf90765af16c96c458790e88d54a9f
prepared_board_sha256: 33b5148e76e630df8aa23a0013c89109579aa49dd0668b6df1f89d38cb7429b9

# Independent current pod placement judgment

The exact frozen native placement is SOUND for the pre-route stage. The source-owned r0 launches meet their authored lengths, layers and widths, and the current footprint arrangement leaves usable clamp, regulator, analog and mounting space. This is not routed-clean acceptance: native DRC has58 expected opens; r0 has33 opens and4 intended dangling launch warnings. The separate ground-return finding below is retained explicitly. FIRST-ARTICLE-ONLY / DO-NOT-ORDER remains in force.

## Authority and measured census

All499 envelope inputs match their sizes and SHA-256 before and after review. The rules digest was independently recomputed from the frozen semantic source projection. The exact envelope subject is `{"raw_sha256": "f443471dd2474c5c30a32a26ad9a31032995750b5dfed653182ae46021771fe3", "semantic_sha256": "4cd278b543ceb7a301ce9b755cb286f59c9bae5d9d90c4848df2124e02f3cceb"}`. No source, board, rule, live file or historical route was adopted or edited; no KRT, rebuild, children or background process was used.

Native and r0 have the same44 footprints,113 pad objects (103 numbered electrical pads,6 unnumbered NPTH objects and4 U2 paste-only apertures), side/rotation/pad nets and model transforms. Sorting duplicate J1 Fab arc graphics removes an object enumeration-order difference; there is no placement change. All40 authored anchors and27 explicit pad/net assertions match. U3's native180° is the expected underside transform of its authored0° placement.

Population is32 fitted bodies:30 top SMT, U3 as the sole bottom SMT, and manual J1. MK1 is a bare two-wire landing; TP1–TP7 are seven bare1.5mm probe pads; H1–H4 are mechanical holes. These12 nonfitted features have intentionally hidden refdes; all32 fitted references are visible on their mounted silkscreen at0.6mm. All32 fitted native model declarations resolve and their files were reopened and hashed. No microphone body is claimed on the PCB.

## Geometry, component bodies and access

The outline is the four native edges at X20..80/Y20..60mm,60×40mm. J1 at(45.5,25.86),0° has its north-going mouth at Y19.50:0.50mm nominal exposure. The manufacturer hole pattern is preserved: eight0.8mm signal drills on2.04mm row pitch with1.02mm stagger and4mm row separation, two3.18mm guides at(42.22,26.56)/(55.92,26.56), and two1×2mm shell slots. Pads9/10 remain POD_SHIELD, separate from signal GND2/6/8.

Native exact shape clearance from either shell land to its adjacent guide is0.268639mm, above the0.25mm hole-to-copper floor by0.018639mm. The derived1.5×2.5mm shell ovals retain0.25mm nominal annulus. Every native pad bounding box is inboard; minimum edge gap is2.260mm at J1 shell pads, comfortably above0.3mm. Four3.2mm mounting drills occupy(24,24),(76,24),(24,56),(76,56). The smallest conservative clearance from a3mm screw radius to a different courtyard is0.725mm at H3/TP4; the other three are2.725,6.5915 and6.2534mm.

No same-side courtyard box intersects another; the tightest conservative box gaps are0.10mm C1/U2 and D2/TP2. D1/J1 is0.55mm. This is positive nominal separation, not a new tolerance allowance. U3 is beneath the jack, in the gap between its tail rows. Its exact pad-to-J1-copper minimum is0.675mm; the conservative Fab-body-to-J1 pad-box minimum is0.50mm. The nearest guide is4.56mm from its Fab box. The bottom view shows its body and pin1 mark in that gap; full-scene sides retain real occlusion by the tails. U3 reflow followed by hand-soldered J1 remains an assembly qualification obligation.

R0 contains15 actual User.2 rectangles: four3mm H-prefixed mounting exclusions, six drill-plus0.6mm NPTH boxes (including the four mounting drills), four edge bands and the one U2/C6/C5 local-copper reservation. The J1 guide boxes are X40.03..44.41 and53.73..58.11/Y24.37..28.75; they leave0.44mm to the nearest signal-pad bounding boxes and do not swallow the8 contacts or U3. The shell lands overlap the guide box at their inner tips, but their centers and outboard exits remain available; their exact physical drill clearance is separately graded above. The U2 output reservation intentionally contains authored copper and blocks future stochastic intrusion.

## Proximity and actual prepared launches

All6 part-dossier proximity rules pass independently, including each of the four U2 capacitors separately and both J1/U3 channels. All11 already-prepared critical path budgets pass. Distances below are millimetres measured from current pad centers and saved track centerlines; up to1µm attachment handles source endpoint rounding. These measurements do not count empty future routes as completed.

| Path | Pad centers | Prepared path | Limit | Layer |
|---|---:|---:|---:|---|
| D1.1 → D2.1 | 10.2031 | 10.2433 | 12.0 | F.Cu |
| J1.5 → U3.3 | 2.5082 | 3.5368 | 4.2 | B.Cu |
| J1.4 → U3.5 | 2.5082 | 3.5844 | 4.2 | B.Cu |
| U2.8 → C1.1 | 2.5311 | 2.5327 | 3.0 | F.Cu |
| U2.8 → C2.1 | 2.0517 | 2.2250 | 3.0 | F.Cu |
| U2.1 → C5.1 | 2.7483 | 2.8802 | 3.0 | F.Cu |
| U2.1 → C6.1 | 1.5523 | 1.5523 | 3.0 | F.Cu |
| U2.6 → C4.1 | 1.8702 | 1.8702 | 3.0 | F.Cu |
| U2.2 → C3.2 | 2.0896 | 2.1037 | 3.0 | F.Cu |
| U2.1 → C3.1 | 2.0522 | 2.0533 | 3.0 | F.Cu |
| U1.4 → C10.1 | 1.9450 | 1.9450 | 3.0 | F.Cu |

The future R12.2→TP5 and R13.2→TP6 probe connections are not in r0; their3.9300/3.5000mm center distances fit the5mm budget with useful direct-route room. U3.4 has a prepared0.50mm-wide, via-free B.Cu return to J1.6, measured3.6035mm including the0.0005mm pad-center attachment. It does not use POD_SHIELD.

Saved r0 has exactly78 authored segments and8 authored off-pad vias; the independent source-to-saved multiset comparison finds no missing or extra segment and all8 via positions match. D1.1 reaches D2.1 first on F.Cu before the protected tree departs left/down to TP2/C1/C2/U2/R14; there is no pre-D2 same-layer branch. AUDIO_P and AUDIO_N each have only their own three-segment B.Cu connector-to-clamp prefix, without vias or downstream tee. Future routes must depart the clamp pads; a ratline endpoint on a connector-side track does not authorize bypassing that order.

The source floors survive identically in native/r0 project settings:0.127mm fab track/clearance;0.15mm netclass clearance;0.50mm input,0.40mm quiet-power and0.25mm audio/analog width floors;0.6/0.3mm vias;0.15mm annulus;0.25mm hole-to-copper;0.5mm hole-to-hole;0.3mm copper-to-edge. Actual r0 widths are0.26/0.40/0.50mm. U2/U3 adjacent different-net pads reach0.15mm clearance, so their existing direct escapes are appropriate; uncontrolled in-pad layer changes would not be interchangeable with the current launch plan.

The east MK1/C8/R4/R5 bias and input cell is separated from the west power entry. The R8/R9 and R10/R11 feedback satellites are close to their respective U1 inverting pins (roughly4–4.5mm); U1's C10 supply bypass is1.945mm from pin4. MIC_AC still traverses from the east landing cell to the preamp input resistor, so future routing must keep that sensitive run compact and separated from output and supply traces. Shared two-layer GND rather than an arbitrary analog split is the declared return intent; the source owns later ground stitching. No final continuous return, thermal result or noise performance is inferred from placement.

## Native DRC classification

Native command: full severity, refill, schematic parity and exit-on-violations on the isolated byte-identical native PCB/pro/dru. Result:0 violations,58 opens,0 parity findings. R0 initially yielded44 library-resolution warnings plus4 dangling warnings and33 opens because its route directory lacks a library table. Repeating with only a scratch table resolving the frozen libraries yields4 dangling warnings and33 opens; no clearance, short, width, edge, courtyard, drill or thermal violation remains.

`drc-classification.json` and `drc-classification.md` retain all176 raw records across the three runs, including every exact description, node pair, coordinate and UUID, with a row-specific class/reason/next owner. Native58, initial r081 and resolved r037 are all represented. The four dangling tracks are source-owned VREF U1.2, PRE_OUT U1.7, OUTP_FB R11.2 and MIC_AC R5.1 launches. The32 ordinary r0 signal/power/shield opens await their declared waves. The remaining open is C10.2-to-GND-zone and is explicitly a return/stitch obligation, L1 below. R0 parity was not requested; the separately checked native schematic parity and matched pad/net population provide the applicable pre-route binding.

The native report's five ignored check types are retained verbatim in classification evidence: missing_courtyard, track_not_centered_on_via, tuning_profile_track_geometries, footprint_filters_mismatch and footprint_type_mismatch. Courtyard existence and geometry were measured independently; no ignored type is silently presented as checked.

## Current model and rendered evidence

I reopened aggregate model_registration.md, stage receipt, bundle and index, then both selected group receipts/bundles and all their output pixels. Aggregate and group board inputs bind this exact a44b769b native board. The current two groups are Wurth J1 and TI U2; the old MicroFit group and failed/last_pass material carry no authority here. Supplied group metrics are12/12 J1 drilled centers with0.024067mm image center delta and13/13 U2 pad/aperture centers with0.000mm delta; the U2 count includes four paste apertures and is not13 electrical pins. The U2 lead envelope extends0.903466mm beyond the body Fab box as expected for gull-wing leads, inside its courtyard. Those image-calibration metrics were reopened, not falsely represented as newly regenerated measurements.

I inspected22 exact images, including both approved opaque full-board top/bottom views, all five current full-scene orientation renders, all five J1 crops, and all ten current group images. `inspected-images.json` binds every viewed pixel file by hash and size, and the archive preserves each unchanged. No new render recipe was needed. J1's socket/latch opening faces outboard north; the rear pin structure faces inboard. The two profiles show the shell above the PCB with tails below. There is no visible main-body overlap with top passives or blocked screw hole. The jack's top occludes its pin1 pad, so orientation is supported by bottom pad geometry, the mouth views and current registration, not by an invented visible top pad mark.

D1's cathode stripe faces its west pad1, D2's stripe its north pad1, U1 and U2 pin1 markings agree with their actual pad positions, and U3's bottom-view pin1 mark agrees after underside mirroring. MK1's southern square pad is the positive MIC_RAW landing. The NOT ETHERNET / NOT POE warning, connector pin map, PTC and seven functional testpoint legends are legible in the inspected top pixels. This visual judgment is independent of user P-ORIENT approval. Pixels cannot establish final solder fillets, manufactured tolerance, enclosure access or cord fit.

## Findings and next ownership

- **L1 — P2 routing completion obligation, not a placement blockage.** C10.2 at(52.12,49.00) is isolated from the filled r0 GND plane. Route/stitch owner must restore and verify its short return before routed acceptance. An exact native foreign-copper screen of a hypothetical0.6/0.3mm via at(51.2,49.0),0.92mm away, has minimum0.908847mm clearance; no copper was added and this is not a route certificate.
- **L2 — P3 guidance advisory.** The last ESD elbows at(50.45,28.36) and(47.65,27.36) are square; TI section10.1 recommends rounded exposed corners. The route source owner should consider radiusing them before final copper acceptance while preserving current prefix order and bounds. The current clamp-first placement, length and clearance pass; no physical limit is relaxed.
- **L3 — first-article physical hold.** Qualify nominal shell-guide margin, free spring-finger variation, bottom U3 assembly beside hand-soldered J1 tails, populated latch/mating/unmating, seating, cord strain relief/bend and enclosure stack. Source notes put the free finger only0.001919mm inside the courtyard centerline, so nominal registration cannot become a manufacturing containment claim. The existing owner is mechanical/assembly/first-article qualification.

The source's exact factory Cat6A cord is a custom analog/DC connection, not Ethernet/PoE, and mating is power-off only. Exact carrier fault/transient bounds, sourcing/assembly allocation, rails, noise/gain/clipping, ESD/EMC, capsule acoustics and outdoor enclosure qualification remain held under source authority. They do not require a commissioning measurement to render this honest nominal pre-route placement verdict, and they do not permit ordering.

## Evidence and limits

Raw pcbnew measurements, the exact native DRC files and complete item classification, supported-runtime logs/results, unsuccessful API/environment probes, scripts, current primary PDF extracts, viewed images and relevant frozen inputs are archived. Body/courtyard screens use conservative native boxes where stated; exact copper gaps use native SHAPE.GetClearance. Package source dimensions and registered pixels were inspected; this layout lens did not independently reconstruct the full STEP BREP or a manufactured plug/enclosure tolerance stack. No global routing, source regeneration, procurement, manufacturing or release acceptance was performed.
