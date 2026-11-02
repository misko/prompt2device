# Local r9 multi-angle inspection — 2026-11-01

## Outcome: not all sockets pass

The new reusable [render-board skill](../../../../vnext/skills/render-board/SKILL.md)
was executed on both unchanged r9 native boards. It produces six cardinal views
and eight azimuths at both +45 and -45 degrees elevation. Seven isolated views
per explicitly reviewed connector supplement the whole-board set. All rendering
is local; no JLC model, upload, quote or order was changed.

| Socket | Number across board designs | Local pin/peg registration | Direction relative to required edge |
| --- | ---: | --- | --- |
| Carrier J101–J108, RJHSE-5080 | 8 | PASS, maker drawing rounding <=0.004mm | PASS: native -Y, toward edge |
| Pod J1, RJHSE-5080 | 1 | PASS, same pattern | PASS: native -Y, toward edge |
| Carrier U3 onboard Pico USB | 1 | PASS for module end/pad witnesses | PASS: USB at pin1/pin40 end, native -Y |
| Carrier J1, PJ-102AH power jack | 1 | PASS for numbered nominal terminal coordinates | **FAIL against outward intent: native +Y, into board** |

PASS here is only the stated local coordinate/direction check. It is not a
full model, assembly, clearance, fabrication or release acceptance. Both JLC
placement holds remain, and the power-jack disagreement is an additional hold.

## Images

Use final **carrier-v2** and **pod-v2** outputs. First exploratory `carrier/` and
`pod/` images are retained but superseded; their source-binding hashes predate
the final labeled renderer and must not be treated as current verified output.

- [Carrier gallery, 92 views](carrier-v2/gallery.html), [overview](carrier-v2/overview.png), [45-degree PNG](carrier-v2/upper_045.png).
- [Pod gallery, 29 views](pod-v2/gallery.html), [overview](pod-v2/overview.png), [45-degree PNG](pod-v2/upper_045.png).
- [Power jack front, looking toward the outer edge from inside](carrier-v2/detail-J1-upper_225.png).
- [Power jack top](carrier-v2/detail-J1-top.png), [underside](carrier-v2/detail-J1-bottom.png).
- [Pico USB direction](carrier-v2/detail-U3-upper_045.png).
- [RJ45 mouth](pod-v2/detail-J1-upper_045.png), [peg/contact registration](pod-v2/detail-J1-lower_045.png).

There are123 final PNGs including the two overview sheets. Native STEP outlines,
recesses and holes are used. Connector bodies are **drawing-derived inspection
solids**, not downloaded exact manufacturer CAD. Cavities, latch detail, terminal
profiles and Pico shell dimensions are explicitly illustrative; they make the
source-derived mouth direction visible but do not independently establish it.
All other components are gray native-footprint XY envelopes with illustrative
1mm heights. These pictures do not show copper/silkscreen or realistic complete
component packaging and must not be used for collision/plug-fit acceptance.

## Power jack finding and derivation

The [CUI PJ-102AH RevA drawing](https://cdn-shop.adafruit.com/datasheets/21mmdcjackDatasheet.pdf)
was visually reopened, including the side view and explicitly labeled PCB TOP
VIEW. The source shows front-to-terminal3 distance10.7mm, terminal3-to-terminal1
distance3.0mm, and terminal2 between mouth and terminal3. In the native board:

- Pin1=(188.0,2.2)mm, pin2=(188.0,8.2)mm, pin3=(192.7,5.2)mm.
- The opening is therefore at nominal Y=2.2+3.0+10.7=**15.9mm**, facing +Y.
- Nominal housing centerY=15.9-14.4/2=**8.7mm**, agreeing with the current CPL
  center(188,-8.7) and zero rotation. This is not merely a render-origin mistake.
- The older first-run mating record describes a cable corridor extending toward
  negativeY, while the later THT placement table correctly says mouth +Y. Those
  two claims cannot both describe the same installed connector access direction.

The earlier clearance acceptance must not be transferred as proof that this
socket is outward-facing. Rotating only the model or vendor CPL to hide the
problem would not fix the source's numbered-hole geometry. This task did not
adopt any such correction. Next owner is placement/mating: qualify a bounded
power-jack relocation/reorientation with affected routing, then re-export and
review. Alternatively, an explicitly authorized inward-access requirement
would need a new actual plug/cable clearance review; it is not assumed here.

## RJ45 and USB evidence

RJ45 housing direction follows Amphenol P-RJHSE-X080 RevA, component-side pattern;
the two pegs are2.54mm ahead of pin1's row toward the mouth, with12.7mm spacing.
The reviewed hole pattern and full local dimensions are in the unchanged
[RJ45 diagnosis](../R9-RJ45-ORIENTATION-REVIEW-20261101.md). The new render does
not resolve the inconsistent JLC model observation or authorize JLC rotation.

Pico orientation uses the original SC0915 module pinout/mechanical convention:
USB is at the pin1/pin40 end. Native U3 at(165,27.55), angle0 has the pin1 row
atY3.42 and pin20 row atY51.68. The original Pico manufacturer registration is
retained in the first-run mechanical records. This verifies direction only,
not shell alignment/height, connector relief or the modified Pico's soldering.

## Verification and reproduction

The skill validator and nine regression tests pass, including unique camera
directions, native90-degree transform, wrong-MPN rejection, reversed mouth,
misaligned peg, missing pin, unsupported bottom connector and altered output.
Both final manifests verify; native r9 still passes its113-file check. Native
files, fabrication outputs, BOMs and CPLs are untouched. VTK rendered headlessly
despite a DISPLAY warning; native KiCad emitted existing enum diagnostics.

Run from repository root using an interpreter with the existing mechanical
requirements and Pillow, and a separate Python with KiCad's pcbnew module:

```sh
python3 -B vnext/skills/render-board/scripts/test_render_board.py
python3 vnext/skills/render-board/scripts/render_board.py --verify projects/crow-array/order-readiness/render-review-20261101/carrier-v2
python3 vnext/skills/render-board/scripts/render_board.py --verify projects/crow-array/order-readiness/render-review-20261101/pod-v2
```

For a new render, call the skill helper with `--board` set to the r9 carrier/pod
native PCB, `--inspection` set to the corresponding JSON in this folder and
`--output` set to a NEW directory. The used solid runtime was
`/home/mouse9911/gits/pcb-vnext-replay-zWbkfr/.venv-mechanical/bin/python`, with
`--kicad-python /usr/bin/python3`. The script snapshots sources, exports the bare
board from a disposable copy, renders and records exact hashes/camera vectors.
Verification currently binds absolute source locations; relocated checkouts
must regenerate into a new directory, not edit old manifests.

This is local coordinator inspection, not independent engineering signoff. No
purchases, remote push or change to vendor drafts occurred.
