# Tentative XU south/west decoupler-fanout backtrack

This is a rejected isolated source-edit candidate. It was applied only to a
temporary floorplan; the generator found pinned courtyard collisions and
produced no candidate board. The canonical `floorplan.yaml` is unchanged, and
proximity, return, and corridor acceptance were not checked.

The isolated board places the obstructing cluster at C_XU_VDD_104 (198.6,96.0), C_XU_VDD_105 (196.5,97.1), C_XU_VDD_106 (198.6,98.2), and C_XU_VDDIO_109 (196.5,99.3), all rotation 0. It blocks the x=176..200.5, y=97.5..98.9 data strip before U_XU.107 (200.838,97.800).

The bounded candidate is to split this ring around the data entry: keep C_XU_VDD_104 at (198.6,94.8,0) and C_XU_VDD_105 at (196.5,95.9,0), move C_XU_VDD_106 to (198.6,101.2,0), and C_XU_VDDIO_109 to (196.5,102.3,0). This leaves the current data-strip band clear of these four bodies, subject to exact courtyard/pad screening. The largest centre move is 3.0 mm; it is therefore not safe to call this a decoupling-preserving move merely from centre distance.

The source integration list identifies these exact capacitors as XU local-ring members, and the XU dossier requires each named VDD/VDDIO capacitor to have a short direct return toward the device ground. Before this candidate can be used, an isolated generator must measure each owning XU supply-pad-to-capacitor non-poured copper gap, the cap ground-to-XU ground return, and collisions with all floaters. It must reject the move if the existing exact-ref P-ADJ ceiling or the XU local-return requirement is exceeded.

This candidate only creates a possible data-entry pocket. It does not free the clock fanout at U_XU.20/.22/.23, does not establish an L-shaped route, and does not solve the unfilled In1 GND reference observed on the isolated board. If the 3.0-mm VDDIO_109 move fails its owning-pin budget, the next backtrack is XU rotation/region geometry rather than displacing its decoupler farther.

## Isolated generation attempt

The four-coordinate edit was applied only in `/tmp/crow-p1-xu-fanout-probe-terra/projects/crow-usb-carrier-v1` and passed to `generate_board_generic.py` with the copied current netlist and full stdout/stderr captured at `/tmp/crow-p1-xu-fanout-generator-terra.log`. This is a real generator rejection, not an output-path mistake: `P-COLLIDE` reports pinned courtyard overlap C_XU_VDDIO_121 ↔ C_XU_VDDIO_109 (bbox 1.910 x 0.210 mm) and C_XU_VDD_113 ↔ C_XU_VDD_106 (bbox 1.910 x 0.210 mm). The generator placed 569 footprints, then refused to save the requested output, so there is no candidate board SHA, P-ADJ result, or corridor comparison. Do not adopt this candidate. A successor must move each relocated capacitor without entering the fixed C_XU_VDDIO_121/C_XU_VDD_113 envelopes, then repeat the isolated collision and owning-pad/return checks.

Alternative A moved only the lower pair farther clear of those fixed capacitors: C_XU_VDD_106=(200.7,101.2,0) and C_XU_VDDIO_109=(194.4,102.3,0), with 104/105 at the proposed north positions. It also failed before board save. The captured log `/tmp/crow-p1-xu-fanout-alt-a.log` reports C_XU_VDD_106 pad overlap with U_XU.115/.116 and a U_XU↔C_XU_VDD_106 pinned courtyard overlap (1.850 x 1.010 mm). This demonstrates that simply pushing 106 east enters the XU body/NC-pad envelope. No second coordinate is justified without first mapping the permitted capacitor envelope around its owning supply pad; broader XU/decoupler-region backtrack is required.
