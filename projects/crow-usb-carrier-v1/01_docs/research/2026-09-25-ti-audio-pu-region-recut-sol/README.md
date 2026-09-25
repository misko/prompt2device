# AUDIO_EN pull-up / input-buck boundary recut (isolated research)

This is one source-region candidate on the reviewed exact 569-ref, 15-part TI board. It derives from the previous **no-credit** sparse AUDIO_EN branch-pocket research packet and changes only the `input_buck` rough planning rectangle from `[25,85,70,110]` to `[27,85,70,110]` mm. The board, all footprint poses, all 27 fixed references, pad identities, modular owners, and all other source regions remain unchanged. Input hashes and generated candidate hashes are in [`receipt.json`](receipt.json).

`R_AUDIO_PU` remains at `(26.2,109.6)` mm. Its native body-plus-courtyard envelope `[25.685,108.625,26.715,110.575]` lies 0.285 mm west of the recut `input_buck` boundary; the AUDIO_EN pad `R_AUDIO_PU.2` is therefore no longer a foreign-region intersection. No `input_buck`-owned native pad or full footprint envelope intersects the removed x25..27, y85..110 strip. The unchanged pull-up envelope intersects no other native envelope; its nearest gaps are 0.250 mm to `R_ADC_BOT`/`R_ADC_TOP` and 0.480 mm to the local `C_AUDIO`. Because the board pose is identical, its existing audio pull-up/supply and timing relationships are preserved. These are geometry checks, not trace-clearance or noise proofs.

The isolated full checker returns `INCOMPLETE`, **zero global errors**, nine unrelated diagnostics, and no AUDIO_EN `physical_blockers` (the predecessor had exactly `R_AUDIO_PU.2` versus `input_buck`). The branch still has all **11** native/source terminals and 11 P2 pad-to-tree duties, a ten-edge P3 connected-tree obligation, and an In1.Cu filled GND-return obligation. Capacity remains null; `routing_realized=false` and `p1_accepted=false`. The checker currently emits a generic unresolved-tree `reason` string that still mentions a “source-region conflict”; the typed blocker list is empty and is the measured result. This isolated recut is not canonical floorplan adoption or P1/P2 credit.

Reproduce from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-audio-pu-region-recut-sol/replay.py
```

The script fails on input-hash drift, any `input_buck` native pad or envelope in the removed strip, a remaining pull-up/full-envelope collision or foreign intersection, loss of the exact 11-terminal/P2/return denominator, or a checker outcome beyond `INCOMPLETE`.
