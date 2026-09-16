# Pod 3D-model provenance

These models are public-authority inputs used only for placement and render
coverage. They do not replace physical connector, enclosure, or first-article
fit evidence.

| File | Authority | Source | SHA-256 | Boundary |
|---|---|---|---|---|
| `TI_DGN0008G.stp` | Texas Instruments WEBENCH CAD service | `https://webench.ti.com/cad/dlbxl.cgi/newstep/DGN0008G.stp` | `9751a8fa8744b8d50553223b504f942a373396d134eccee1f86c69b545fffc10` | Unmodified public TI package model for the DGN0008 PowerPAD VSSOP family; fetched 2026-09-02. |
| `Molex_43650-0400_drawing-envelope.wrl` | Project-authored from the public Molex 43650 sales drawing and exact project footprint | `https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/436/43650/436500200_sd.pdf` | See `SHA256SUMS` | Simplified housing envelope for placement/render review, not manufacturer CAD and not proof of mate, latch, cable, or enclosure fit. |

The Molex manufacturer STEP archive is publicly linked at
`https://www.molex.com/pdm_docs/stp/43650-0400_stp.zip`, but it was not
retrievable in this non-authenticated build environment. The explicit envelope
keeps that distinction visible rather than relabeling a third-party model as
manufacturer authority.
