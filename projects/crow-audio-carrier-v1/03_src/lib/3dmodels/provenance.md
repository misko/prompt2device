# Carrier model-source provenance — 2026-09-08

This library closes source-file availability, not exact-board model registration,
placement approval, connector operation, soldering, thermal analysis or physical
qualification. No supplier part, footprint identity, pad or pin map changes.
All attachments use `${KIPRJMOD}/../03_src/lib/3dmodels/...` from `04_kicad`.
Exact digests of models and retained licensing are in `SHA256SUMS`.

## Unmodified public KiCad asset

`kicad/C_Rect_L7.2mm_W5.0mm_P5.00mm.step` is unmodified, 18,352 bytes,
SHA-256 `35659ae3b9a50ddeb0aa5add4edfaea1770d99f3a8c2db7320eb8fb13be8ee1b`.
Upstream repository: [KiCad packages3D](https://gitlab.com/kicad/libraries/kicad-packages3D).
Immutable upstream commit: `e62ed1fc7862da83f789bd562671b5e4b82afcdf`.
[Original immutable asset URL](https://gitlab.com/kicad/libraries/kicad-packages3D/-/raw/e62ed1fc7862da83f789bd562671b5e4b82afcdf/Capacitor_THT.3dshapes/C_Rect_L7.2mm_W5.0mm_P5.00mm.step).
Downloaded 2026-09-08T02:54:23Z using ordinary public HTTPS.
Copyright2026 KiCAD; CC-BY-SA4.0 with the KiCad electronic-design exception.
Unmodified upstream `kicad/LICENSE.md` is retained (2,101 bytes; SHA-256
`45d2bce75e5a4208f5afb01b8fb2c406e700371c4fe2b5f5cd5c443d46db4d8f`).
[Immutable licence URL](https://gitlab.com/kicad/libraries/kicad-packages3D/-/raw/e62ed1fc7862da83f789bd562671b5e4b82afcdf/LICENSE.md).

Independent package authority is the exact KEMET `R82DC4100DQ60J` specsheet,
local `02_parts/R82DC4100DQ60J/R82DC4100DQ60J_specsheet.pdf`, p1, SHA-256
`2aa26ed87a41bae3038953b2d16a7e00a35ba3ce77baa9e49e5303e469ac90e1`.
[Manufacturer URL](https://search.kemet.com/component-documentation/download/specsheet/R82DC4100DQ60J).
The dimension figure was rendered and inspected: nominal body7.2x5x10mm,
pitch5mm, wire diameter0.5mm. Body tolerances are L+0.3/-0.5,
W+0.1/-0.5,H+0.1/-0.5mm; pitch+/-0.4,wire+/-0.05mm.
The KiCad model has rounded case edges and trimmed below-board leads;
its installed lead length does not represent the18.5mm shipping tape datum.
Its nominal10.0mm case does not cover10.1mm maximum production height.
Do not use a nominal-model render as a worst-case enclosure-clearance proof.

## Independently authored drawing-derived models

Ten files under `derived/` are reproducible with
`/usr/bin/python3 03_src/build_package_models.py`; the Samtec reference is
reproduced with `/usr/bin/python3 03_src/build_samtec_model.py`. The generators retain the
source-owned parameters and their exact dimensional meaning. No downloaded
manufacturer CAD, mesh, logo or drawing artwork is copied into these files;
they are new simplified prisms derived from public dimensional facts. They
are not represented as licensed upstream CAD. No third-party CAD licence is
invented or extended. Source code and generated geometry remain project-owned.

The following PDF figures were independently rendered and visually inspected.
Page numbers are one-based PDF pages and match printed pages where present.
Existing dossier files are unchanged. External-cache files remain recoverable
at their named locations; they are not silently adopted dossier authority.

| Model | Exact dimensional source | SHA-256 / page |
|---|---|---|
| `TI_DSE0006A_nominal.wrl` | `02_parts/TPS389001DSER/TPS3890_SLVSD65A.pdf`; [TI SLVSD65A](https://www.ti.com/lit/ds/symlink/tps3890.pdf); outline4220552/B01/2024 | `ee79599730e7606ba9718d9820b411020e3dcd9ff7d44572f8ee63fead15b9d0`, p24 |
| `TI_DSG0008A_nominal.wrl` | `02_parts/TMUX2821DSGR/TMUX28xx_SCDS488.pdf`; [TI SCDS488](https://www.ti.com/lit/ds/symlink/tmux2821.pdf); outline4218900/E08/2022 | `493e5c0d4eb5ca55dea82dbcce59b1be9c353577e256c161821662c38bb9ac55`, p30 |
| `TI_DSK0010A_nominal.wrl` | `02_parts/TPS7A9201DSKR/TPS7A92_SBVS318B.pdf`; [TI SBVS318B](https://www.ti.com/lit/ds/symlink/tps7a92.pdf); outline4218903/C09/2025 | `e0c0a695e933d9656a7c6fefad654c5129d76a22ac8398d26eacfb844dd4532e`, p31 |
| `Cirrus_CS5308P_QFN48_nominal.wrl` | `02_parts/CS5308P-DN/CS5308P_DS1314F1.pdf`; [Cirrus DS1314F1](https://statics.cirrus.com/pubs/proDatasheet/CS5308P_DS1314F1.pdf), Fig10-1 | `6ca42cc09ac47ebdacacaee435f05e3f9c34b83d5692e52a2d8a26533e810e57`, p93 |
| `Coilcraft_XGL4020_nominal.wrl` | `02_parts/XGL4020-332MEC/XGL4020_Document1529-3.pdf`; [Coilcraft Document1529](https://www.coilcraft.com/getmedia/76c9c081-4945-4c85-9129-9356e1ad6734/xgl4020.pdf), rev02/19/26 | `1e050d7e4f44f7e1f3ae3be38de87b15e4d72b2ef463c7b1f4edc292f83ad2c0`, p3 |
| `Littelfuse_1812L035_60_max-envelope.wrl` | Manufacturer-authored GD06/10/24 PDF from [public Megastar mirror](https://www.megastar.com/content/pdfs/1812L-Datasheet-Update.pdf); local `/tmp/carrier-fuse-authority-20260908.jryPoW/Littelfuse_1812L_GD20240610_Megastar.pdf` | `a18b5ceec6d56cd31b20da55341ed1b35a48184f1f7fff8ca8bc6948cd8fb974`, p6 |
| `Littelfuse_2920L260_33_max-envelope.wrl` | Manufacturer-authored GD06/04/24 PDF from [public Datasheet4u mirror](https://datasheet4u.com/pdf/1487677/2920L260.pdf); local `/tmp/carrier-fuse-authority-20260908.jryPoW/Littelfuse_2920L_GD20240604_Datasheet4u.pdf` | `971e07c88927e6c4730515c390e552e9779366d5a2aefa6bceb64f141ca94896`, p4 |
| Both `Molex_43650-0x00_conservative-envelope.wrl` | Existing repository `projects/crow-mic-pod-v3/02_parts/43650-0400/Molex_436501000_SD_revD8.pdf`; [official sales drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/436/43650/436501000_sd.pdf), SD43650001/D8 released2024-11-05 | `b8942b95bc3fe4c02171de9e714d99b2688055e249ba1524e3c2a8c3cf78eaa3`, p1 |
| `connectors/Samtec_TMM-106-01-L-D_reference.wrl` | `02_parts/TMM-106-01-L-D/TMM-Series_RevAS.pdf`; [Samtec revision-AS print](https://suddendocs.samtec.com/prints/tmm-mkt.pdf), selected style01 | `66d9ffaa15ef8ff9b1614640d81fd2d1c2c6629b522df0cddc64acac3e73efc3`, p1 |
| `Vishay_WSLP1206_50m_nominal.wrl` (added2026-09-09) | `02_parts/WSLP1206R0500FEA/WSLP_30122_20240909.pdf`; [Vishay30122](https://www.vishay.com/docs/30122/wslp.pdf), rev09-Sep-2024, exact0.006..0.050ohm dimension row and package figure | `36e35aeb3d41f110442de6690ef220a8a20c720118a40abb0fa8eedbf7308edb`, p2 |

### Dimensional interpretation and unmodeled detail

| Family | Modeled facts | Deliberate limitations |
|---|---|---|
| DSE | Body1.5x1.5 nominal,0.8maximum height;6 leads,.5pitch,.25width; pin1length.6, other leads.5; noEP | Plan tolerance+/-0.05 not swept; lead width.2..3,length.4..6/pin1.5..7 use midpoints. Body standoff.025 midpoint of0..05. End radii/chamfers omitted; pin1graphic illustrative. |
| DSG | Body2x2 nominal,0.8maximum;8 leads,.5pitch,.25width,.3length; EP.9x1.6 with dimensioned.25pin1corner | Body+/-0.1,EP+/-0.1 not swept; metal sidewall option.2 chosen from two specified options. Lead radii, material layers and true marking omitted. |
| DSK | Body2.5x2.5 nominal,0.8maximum;10 leads,.5pitch,.25width,.4length; EP1.2x2.0 | Body/EP+/-0.1 not swept; optional undimensionedEPcorner not invented; rectangular terminal tips. |
| ADC | Body6x6BSC,.75nominal height;48 leads,.4pitch,.2width,.4length; EP4.6square; standoff.035nominal,metal.203reference | .8maximum height and pad/EP tolerances are not swept. Detailed mold geometry/markings and terminal rounding omitted. |
| XGL | Body4x4nominal,2.1maximum totalheight; terminals.82x3.25, centrepitch2.39=.82+1.57 | Bodymaximum4.3x4.3 is NOT swept. Terminalthickness.05 is an explicit visual estimate because unlisted, not a cited dimension. Optional finishes may add.13height. Start-lead stripe illustrative. Native2.39terminalpitch differs by.02 from2.37PCBlandpitch; never move pads to match a model. |
| 1812L035/60 | Maximum body4.73x3.41x1.8; exact/60 row is1.2..1.8high | Conservative maximum envelope, not nominal4.55x3.24x1.5. End-bandE=.4 midpoint is visual only; castellation, D-range and current markings omitted. Source land-pattern approval is separate. |
| 2920L260/33 | Maximum body7.98x5.44x1.8; exact/33 row is.8..1.8high | E=1.125midpoint visual only; castellation/D-range omitted. This is family mechanical evidence, NOT evidence that existingMRordering suffix is orderable. Root retains that separate sourcing discrepancy. |
| Molex0200/0400 | Width9.65/15.65, depth9.90, body4.37 plus latch1.20 gives maximumheight5.57; frontY=-8.92=-4.32-4.60, backY=.98; .64square board-entry tails, pitch3, taildepth3.18. D8 front/side/isometric views establish separate cavities, lower outside-corner chamfers on the first/last cavities, and the roof latch near the mouth. | Walls/roof.60, cavityhalfwidth1.18, cavityrearY=-2.25, chamferleg.65, latchwidth2.50 and its Y=-8.30..-6.40 station/ramp, horizontalcontacttipY=-7.35 and height2.185 are explicitly undimensioned visual estimates. The NTS drawing is not a scaling authority. Profiles establish depicted orientation/keying identity, not tolerance-qualified mating dimensions or physical fit. Locking pegs, bend radii, markings, undercuts and tolerance extremes are omitted. Not supplier CAD, mating/retention/cable-service proof or human approval. |
| Samtec TMM-106-01-L-D | Body3.94x12x1.50mm REF; twelve .50square pins at2mm pitch; style01 postA3.20, tailB3.50REF, overallL8.20REF, contactC2.54REF | A and C are not labelled MIN. Title-block tolerance applies where applicable; no tolerance sweep. Grooves, tip chamfers, flash, bow and pin tilt omitted. No socket insertion/retention or miniDSP fit claim. |
| WSLP1206R0500FEA | Nominal overall3.20x1.60x.635mm; end-terminal lengthT=.508mm from the exact50mOhm row, not the1.65x1.93mm PCB land. Two nonpolar ends at X-/X+ use the source pad1/2 convention. | All four dimensions have+/-.254mm tolerance. The model does NOT cover maximum3.454x1.854x.889mm. Undimensioned underside relief, coating thickness, internal weld and markings are omitted; the central region fills its nominal enclosing prism toZ0. This deliberately overfills the unquantified relief, not a claimed flat physical underside. No solder volume, thermal material properties or manufacturer CAD are represented. |

Common frame: XY origin remains the source footprint origin; Y is negated
once when emitting native VRML; Z=0 is seating plane and positive is above the
PCB. All model-clause transforms remain zero offset/rotation, unit scale.
No geometry comes from a rendered pixel, and no real footprint was moved.

## Research candidates not adopted

The five other exact requested KiCad paths (two fuses, two Molex, ADC)
returned `HTTP Error 404: Not Found` at the same immutable upstream commit.
All results are retained in
`/tmp/carrier-model-source-20260908.hWZVj5/public-kicad/fetch.json`.
The exact KEMET model endpoint linked inside its PDF returned
`curl: (22) The requested URL returned error: 500`.
The ordinary Molex STEP archive request returned
`curl: (92) HTTP/2 stream 1 was not closed cleanly: INTERNAL_ERROR (err 2)`.
No credentials, account, bypass or repeated unchanged fetch was used.

TI's ordinary public WEBENCH endpoints did return package STEP files:

| Candidate URL | Retained scratch filename | SHA-256 |
|---|---|---|
| `https://webench.ti.com/cad/dlbxl.cgi/newstep/DSE0006A.stp` | `TI_DSE0006A.stp` | `14a47e7abf178da4755a4bbc05c724ca531edd590029a97fa11f6ac0e67ff166` |
| `https://webench.ti.com/cad/dlbxl.cgi/newstep/DSG0008A.stp` | `TI_DSG0008A.stp` | `036e69d19652968e88d5228d04ed57885bb35118ebae21352052a94129402c36` |
| `https://webench.ti.com/cad/dlbxl.cgi/newstep/DSK0010A.stp` | `TI_DSK0010A.stp` | `62e090e3e233dd10586a7d268e2ba53d0fd265afb0bb278f35404da1f0395f4d` |

They are retained only under `/tmp/carrier-model-source-20260908.hWZVj5/`.
An explicit redistribution licence for those CAD files was not established;
they were not copied into source or used as generated geometry. The package
labels alone would also not prove frame/terminal registration. The source
uses independently authored dimensions from the inspected PDF figures instead.
