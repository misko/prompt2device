# Three-cell board-integration shared-zone variant

This is an isolated, **rejected** source-floorplan study. It leaves the canonical `03_src/floorplan.yaml`, modular endpoint ownership, 59-net P1 denominator, PCB, task state, and P1 attempt count unchanged. The exact source record is [the variant YAML](2026-09-24-p1-audio-xmos-clock-shared-zone-variant-terra.yaml); the native measurement is [the audit JSON](2026-09-24-p1-audio-xmos-clock-shared-zone-audit-terra.json).

The proposal replaces the three overlapping logical rectangles with one `board_integration` territory represented by this rectilinear union:

```text
audio_clock_tdm:   [140,72,190,112]
xmos_core:         [185,72,232,128]
clock_flash_debug: [185,112,232,136]
union owner:       board_integration/audio_xmos_clock_service
```

The union preserves the actual territory exactly, so a point in either former overlap has one spatial owner. It needs a union-of-rectangles or polygon source-zone type; a single bounding rectangle would take unrelated ADC, analog, digital-power, and USB-sense space. The source record keeps the 27 fixed refs byte-for-byte equal to current authority and retains rejection of the y=112 and x=145 straight cuts.

The isolated native board is `06_build/modular/repaired-trial/crow_carrier.kicad_pcb`, SHA-256 `37b455203fcdae0c20880a94b17a4bcfb61103fa2b8b9df9ecf095c9c97aa519`. Using KiCad full footprint bounds (`GetBoundingBox(True, True)`), it measures 155 union-intersecting footprints: all 76 member refs—39 audio/timing, 29 XMOS, and eight clock/flash—and 79 foreign refs. The latter belong to ADC reference (9), analog channels 6–8 (15/12/15), digital power (24), and USB VBUS sense (4). No fixed ref intersects the proposed zone, but fixed-reference preservation does not clear the 79 movable foreign bodies.

The outer perimeter has 12 rectilinear segments. Five have full-footprint crossings: x=140 has 14 refs, the y=72 segments have 21, 7, and 7 refs, and y=112 from x=140..185 has 10 refs. The complete per-segment lists are in the audit. This candidate has no sound virtual face, reservation edge, or P1 handoff.

Current schema-2 accepts rectangular reservations and direct endpoint-owner virtual witnesses only. A future source model needs explicit `board_integration` shared-zone authority for a union/polygon, delegated member ownership, all foreign full-footprint intersections, and P2 pad-access/local-return/coexistence obligations. This probe does not claim capacity, GND return, DRC, routing, or P1 acceptance.
