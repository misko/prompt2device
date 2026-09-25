# PESD2USB3UV-T source 3D envelope

This source-only repair attaches a project-authored, conservative SOT23 body
envelope to `crow_usb_analog:Nexperia_PESD2USB3UV_SOT23`. It is not supplier
CAD and does not establish board placement, USB routing, P1, or release.

The retained Nexperia product data sheet
`02_parts/PESD2USB3UV-TR/PESD2USB3UV-T.pdf` (9 September 2020,
SHA-256 `f63451e4af9a93292621f2731a58dc46b3601931e97ae66d636b5e633bd48ab4`)
gives the SOT23 outline in Fig. 13, page 8. Its maximum dimensions are
`D=3.0`, `E=1.4`, `HE=2.5`, `A=1.1`, and lead width `bp=0.48` mm. The model
uses a 3.0 × 1.4 × 1.1 mm rectangular mould envelope and three simplified
0.48 × 0.55 × 0.12 mm leads. Lead tips reach the ±1.25 mm `HE` bound. The
model origin is the footprint centre at the PCB seating plane, with Z spanning
0–1.1 mm. One VRML unit is 2.54 mm and VRML Y is opposite KiCad footprint Y.
Rectangular lead shapes, their 0.55 mm length, and the pin-one mark are
illustrative; only the package bounds and lead width above are datasheet
maxima. Mould draft, lead bends, solder, and actual supplier markings are not
represented. The original authored geometry is covered by the repository MIT
license; no manufacturer model geometry was copied.

The existing footprint has pad 1 at (-0.95,-0.85), pad 2 at (0.95,-0.85), and
pad 3 at (0,+0.85) mm. Model leads 1/2 map to Y=-0.975 after the VRML
inversion, while lead 3 maps to Y=+0.975. All three lead boxes positively
overlap their corresponding native lands. The top mark maps to the negative-X,
negative-Y pin-one quadrant and rotates with the footprint. The model's
3.0 × 2.5 mm outer plan envelope remains inside the 3.3 × 3.0 mm native
courtyard. No pad, silk, fab, courtyard, or component placement field changed.

Verification used a temporary one-footprint native board at 0° outside the
repository. `model_coverage_check.py` passed **1/1**, and `kicad-cli pcb
render` loaded and rendered the model. A numeric check of the five VRML boxes
against the native pad centres passed **3/3** terminal overlaps, pin-one
quadrant, the maximum 3.0 × 2.5 × 1.1 mm envelope, and the Z=0 seating bound.
The source worktree has no current saved `.kicad_pcb` to grade 569/569 fitted
footprints; whole-board model coverage must be rerun on the next generated
board. The temporary fixture was `/tmp/crow-nexperia-model-u5iarv8g/` and is
diagnostic only.

The new model SHA-256 is
`5978f41a1bf669c85770a539acb356c82203271b3cf58c305debdccc97cf9f7f`.
