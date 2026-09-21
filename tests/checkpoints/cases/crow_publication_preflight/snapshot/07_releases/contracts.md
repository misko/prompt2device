# Synthetic reduced release contract

This contract belongs only to the checkpoint coupon. It names the complete
required pre-review artifact set and the four legitimate future review outputs.

```
07_releases/
└── <version>/
    ├── MANIFEST.txt                         REQUIRED
    ├── fab/                                REQUIRED
    │   ├── board.gbr
    │   └── board-PTH.drl
    ├── source/                             REQUIRED
    │   └── board.kicad_pcb
    └── verification/                       REQUIRED
        ├── pre_review_gate.json
        ├── evidence.zip
        ├── pin_review.md
        ├── redteam_layout.md
        ├── redteam_topology.md
        └── render_review.md
```
