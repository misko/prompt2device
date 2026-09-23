# Murata 1210 model-source repair

MEASURED: the current exact native MPN census includes42 instances of
GRM32ER71A476KE15L using `crow_usb_power_aux:Murata_GRM32E_1210` without a
model. Added a zero-offset, unit-scale, zero-rotation binding to an unmodified
public KiCad generic package model, copied from the installed KiCad10 library:
`03_src/lib/3dmodels/kicad/C_1210_3225Metric.step`, SHA256
`f8510481c5044113cf49b0fa6dd54ddab9224508bd6808e1afab8ef0cefdefc9`.
The STEP header carries KiCad StepUp attribution and CC-BY-SA4.0 terms with
KiCad exception; adjacent LICENSE.md is retained. It is not Murata CAD.

The retained Murata exact-family PDF p.2 (SHA256
`fd44194fdabc476650301c34e6e10eeb64d0c7cba90253b20af2371a07fd5ea8`)
states nominal3.2×2.5×2.5mm, tolerances±0.3/±0.2/±0.2mm.
Root parsed all48 STEP VERTEX_POINT references and all3D CARTESIAN_POINT
records: both coordinate bounding sets are X[-1.6,1.6],Y[-1.25,1.25],Z[0,2.5].
This is a nominal package-envelope comparison, not a tolerance sweep or a full
CAD solid validation. Termination shape/solder volume are generic; terminal
polarity is inapplicable to this ceramic capacitor.

The edited native footprint differs only by the added model clause; pad
identity, copper, courtyard and electrical source remain unchanged. The
existing courtyard must continue to enclose maximum package dimensions rather
than rely on the nominal render.

Native KiCad smoke fixture in `06_build/verification/source-model-fixture`
loads one capacitor plus the two new TI models at0/90degrees. Top and front
views visibly place all five bodies above the board. The first capacitor
fixture attempt did not persist its absolute model URI through a SWIG wrapper;
root corrected the scratch fixture with explicit model replacement and checked
the saved native file/render. No product PCB was generated or repaired.
This is neither MODEL-REG nor P1 acceptance; full-board collision, registration,
signed-side quantitative and manufacturing-twin checks remain owed.

Together with the preceding resistor-model restoration and the two correct
TI-model sources, raw file-resolution coverage is projected546/568 if these
sources are regenerated, leaving22 missing instances. That arithmetic is not a
new measured native coverage report and does not certify model identity of
all546. Do not replace the preserved495/568 trial report by this projection.
