# Crow USB initial floorplan intent

Adopted a 220 x 120 mm exploratory four-layer canvas from SOL review. This is a draft placement input, not a final outline or accepted board. The 18 modular blocks provide region seeds for 411 nonconnector references. All 11 operated connectors intentionally lack anchors, seeds and region patterns until their exact mating-plane offsets and orientations are reviewed. No mounting-hole coordinates are invented.

Root checked the generator implementation: `require_anchor` only rejects a reference after trying anchors, seeds and matching region patterns. Therefore connectors must be excluded from region patterns; setting the flag alone would not prevent arbitrary connector placement. Region patterns are starting positions, not hard bounds. Overlapping draft regions are permitted only as initial search areas, with legalization and independent placement review still required.

Removed load-cell paths, unrelated anchors and silk captions, and HX711 assertions. Retained existing exact-part model overrides. The board now names crow_carrier and four layers; In1.Cu is the intended continuous GND plane. Native physical stackup, thermal-via geometry, connector service clearance, power copper, analog matching and USB routing still require implementation. The commissioning hold remains in place. route.yaml is still a separate open seed-replacement finding.

Validation: exact modular population is 422 references; 411 are assigned region seeds and 11 connectors deliberately remain unresolved. Project contracts pass with zero violations. No native board was generated or admitted.
