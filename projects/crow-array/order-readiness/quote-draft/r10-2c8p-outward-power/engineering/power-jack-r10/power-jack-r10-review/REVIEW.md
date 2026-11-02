# Independent affected-engineering review: candidate4

Decision: PASS FOR CONTROLLED PROTOTYPE QUOTE DERIVATIVE ONLY.

Exact native SHA-256: `1fc774524ef57efdd3a644de338328837e42ba648d3a4dd6bb78bad44e8852a1`.
This is not whole-board manufacturing, populated-assembly, vNext stage, release, purchase or production approval. All historical holds survive. Earlier candidates are not accepted.

## Outward pose and clearance

Independent visual reading of both maker drawings resolves the old contradictory model: native mouth is local +Y13.7 from pin1. Final J1 anchor(188,14.7),180 degrees puts the mouth at nativeY1.0, facing outward -Y; pins1/2/3 remain VIN12/GND/NC at (188,14.7)/(188,8.7)/(183.3,11.7). No reflection or pin/net swap is used.

The corrected conservative jack occupied body is local X[-4.7,4.7],Y[-1.3,14.1],Z[0,11.5]. This includes independent drawing tolerances on body depth, front-to-switch and switch-to-pin1. It does not reuse the old too-short/directionally wrong envelope. Conservative rigid-motion bounds include retained radial0.10mm/total1-degree pose restrictions. Nearby actual F1,D1,D3,C1 bodies remain disjoint. The closest D1 separation lower bound is0.536912mm. Candidate3's0.036912mm allocation was rejected for robustness; the explicitly authorized0.5mm outward shift supplies meaningful additional margin. C1 is current Samsung CL31B106KBHNNNE, not the historical TDK; its maker maximum3.4x1.8x1.8 is deliberately covered by the retained3.6x1.9x2.05 box.

For only the straight center-positive PP3-002A, reserve exterior X182.65..193.35,Y-36.5..3.1,Z0.95..12.15mm. The1.10mm finite pose expansion exceeds the independently calculated0.998109mm requirement about the actual deeper jack anchor; it also includes maker axis-height and mouth-location variation and seating elevation once. Finished board top<=0.05 leaves>=0.90mm board gap. The selected barrel alone engages the named standard interface. This is source-supported compatibility and external clearance, not private spring/stop reconstruction or a whole-jack collision waiver. No arbitrary plug, right-angle boot, bend, enclosure, tool or support fit is approved. Retain the below-board finite terminal columns and no-hardware occupancy restriction. Unknown distant/module/enclosure geometry retains its existing limitations; no new full populated-3D acceptance is claimed.

## Native electrical and shared copper

Independent native comparison confirms142 footprints with only J1 pose changed; pad identities/nets/shape/drills and all141 other poses, source schematic and project are preserved. Nineteen track-diff entries comprise eight removed and eleven added VIN/FUSED segments; retained width0.8mm F.Cu, no added via or narrowed path. The only zone-boundary change is the explicit FUSED cooling extension. Board outline and thickness1.6mm are unchanged. Input path remains J1center→F1→D3anode/cathode→12V loads/U10, with the original TVS, input capacitors, U10→5V→D2→Pico and eight protected pod branches unchanged. Source parity and all nets/pads remain intact.

Fresh independent KiCad10.0.4 strict all-severity/all-track/schematic-parity DRC with zone refill/save returns zero violations, opens and parity findings, with no ignored checks. Refilled review-copy bytes equal the frozen native source. Independent routing geometry with the explicit inherited0.15mm annulus allocation reports zero drill/SMD overlaps or annulus findings. The initial review-only check lacking copied libraries produced138 library errors; that diagnostic is preserved and superseded by the complete-library zero result, not waived.

The new J1 sleeve retains continuous shared GND via four thermal spokes into both single inner GND polygons: independently sampled12/12 points per plane before and after; all ground net services are retained, not merely the local jack route. Both inner ground areas and the12V output cooling area are unchanged. Final FUSED copper is one continuous direct D3 island216.184474mm² versus206.407582mm². An independent polygon XOR in the immediate D3 region X186..199/Y16.9..22.5 is zero (71.974517mm² in both), proving exact local copper preservation rather than equal total area alone. A broader lower-region difference is only0.001349mm²; remote upper spreading is redistributed, not claimed thermally equivalent from area alone.

For this bounded prototype quote, retaining the prior D3 sensitivity is reasonable because the immediate anode contact/spreading geometry and output-side cooling are preserved, the input-side island remains continuous and larger, and no current, fuse, ambient or loss assumption is relaxed. This does NOT establish110/130K/W as actual theta. Existing0.51W D3 model at60C air+20C neighbors gives146.3C at130K/W;137.25K/W reaches150C and fails margin. The full eight-pod hot-load, startup/inrush and local D2/D3/LMK temperature gate therefore remains mandatory before deployment; no performed test is claimed.

## Required carry-forward

Transmit the corrected DC orientation, exact numbered pad mapping and finite corridor in the new quote/placement instructions; supersede the conflicting old DC direction/corridor only, not all historical controls. Retain finished jack holes1.60..1.73mm, actual annulus>=0.30mm, maker pattern, pose/seating, manual solder all three terminals including NC, >=75% hidden through-fill qualification, process/lot inspection agreement and representative supported mating/withdrawal qualification up to the retained29.4N force bound. Supplier agreement and actual measurements remain unperformed. Exact quote quantities, vendor preview, stock allocation, thermal/electrical first-article and all release/purchase holds remain separate.

No release-stage receipt was issued or historical receipt refreshed. Use only candidate4's frozen subject for derivative packaging; any subsequent native/model/pose/copper change reopens this review.

The source-bound final-v2 overview and isolated J1 closeup were visually inspected. They show the corrected mouth at the north edge and agree with native pose, but are explicitly diagnostic: other component heights are unqualified and the isolated view hides neighbors. These images supply orientation corroboration only, not the clearance, engagement or copper proof above.
