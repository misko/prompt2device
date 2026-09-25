# `C_XU_VDDIO_35` alternate-pose search — no short-return proof

This is an isolated in-memory search on the same pinned QSPI-gap board used by
the oscillator-handoff study. It changes no source, board, route, or P1 state.

The search keeps the capacitor in the proposed `xmos_core_east`
`[217.2,84,232,105.5]` mm source region, excludes the proposed oscillator
handoff, and checks each 0.05 mm pose at rotations 0/90/180/270. Every native
body and F/B courtyard is buffered by the declared 0.15 mm clearance; the
selected pose is then checked separately against native pad bboxes and all 27
P1-fixed references.

The closest collision-free fallback is `C_XU_VDDIO_35 @ [222.1,102.7]`,
rotation 0°. Its `N1V8` pad is 6.089 mm from `U_XU.35`, compared with 2.037 mm
for the pinned pose: a 4.052 mm increase. It has no native body/courtyard or
pad collision and no P1-fixed reference conflict, but this search cannot call
that connection short or electrically acceptable.

The pinned board contains no local GND via near the selected capacitor (the
nearest existing GND via is recorded in the receipt). A new adjacent GND via,
continuous filled `In1.Cu` return, pad escape, and DRC must therefore be
proven later. The fallback does not preserve a demonstrated direct adjacent
return and is not P2 placement approval.

Reproduce with KiCad 10 `pcbnew` and PyYAML:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/xu_service_variant/c_xu_vddio35_pose_search.py
```

The generated receipt is
[c_xu_vddio35_pose_search.json](c_xu_vddio35_pose_search.json).
