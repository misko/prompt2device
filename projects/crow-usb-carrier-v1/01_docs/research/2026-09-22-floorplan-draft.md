# Crow USB initial floorplan intent

Adopted a 220 x 120 mm exploratory four-layer canvas from SOL review. This is a draft placement input, not a final outline or accepted board. The 18 modular blocks provide region seeds for 411 nonconnector references. All 11 operated connectors intentionally lack anchors, seeds and region patterns until their exact mating-plane offsets and orientations are reviewed. No mounting-hole coordinates are invented.

Root checked the generator implementation: `require_anchor` only rejects a reference after trying anchors, seeds and matching region patterns. Therefore connectors must be excluded from region patterns; setting the flag alone would not prevent arbitrary connector placement. Region patterns are starting positions, not hard bounds. Overlapping draft regions are permitted only as initial search areas, with legalization and independent placement review still required.

Removed load-cell paths, unrelated anchors and silk captions, and HX711 assertions. Retained existing exact-part model overrides. The board now names crow_carrier and four layers; In1.Cu is the intended continuous GND plane. Native physical stackup, thermal-via geometry, connector service clearance, power copper, analog matching and USB routing still require implementation. The commissioning hold remains in place. route.yaml is still a separate open seed-replacement finding.

Validation: exact modular population is 422 references; 411 are assigned region seeds and 11 connectors deliberately remain unresolved. Project contracts pass with zero violations. No native board was generated or admitted.

## Draft routing replacement

Removed cook-loadcell project paths, keepout rectangles, signal names, stitch coordinates and promoted-copper selection. Current route groups resolve 60 exact source nets plus the remaining control population. USB_DEVICE explicitly routes USB_DP/USB_DN as an F.Cu differential pair at the retained nominal 0.410/0.150-mm width/gap and 1-mm skew ceiling. USB4105 A6/B6 and A7/B7 aliases were checked against parity_padmap.txt; the TPD2EUSB30A shunt pin identities match its dossier. GND and CHASSIS are excluded from stochastic routing; In1.Cu remains the intended reference plane. No via-in-pad rescue is authorized by default.

This remains draft route intent. Analog matching, switch-loop deterministic ownership, actual thermal vias and power copper need placement evidence. The normal decision snapshots and pre-route reviews remain enforced and absent; no source or route admission is claimed.
