# Source selection and digital verification — 2026-09-22

The source selection census covers 485 unique references and 85 exact MPNs. All 85 selected native footprint identifiers load in KiCad, and their pad sets cover every external source pin after explicit dossier aliases. Root repaired the omitted two-terminal map in the 5.1 kΩ USB CC resistor dossier and reran the complete census with no findings. This is source pin/footprint coverage, not native board or sourcing acceptance.

The new `01_docs/sourcing/exact-parts.csv` is a candidate identity/quantity input. Root tested it through the actual shopping-list BOM reader: 85 exact dossier joins, 485 unique references, zero unmatched rows. It uses the owning reader's case-sensitive MPN/Designator/LCSC headers. Distributor stock and two-source qualification remain separate; this file contains no stock or price claims.

C_ADC_START_DELAY carried an inconsistent supplier code, C473840, while the two existing same-MPN capacitors and dossier used C318640. Root reopened the [exact LCSC catalog record](https://www.lcsc.com/product-detail/C318640.html), which identifies Samsung CL10B474KA8NFNC, and normalized the new source reference to C318640. No electrical value, footprint or manufacturer identity changed. No availability claim follows from this identity correction.

Independent merged-source review rendered 37 schematic pages with all 485 references exactly once, including all eight spoke-protection sheets. Every page reported zero source/render errors. These are source presentation pages, not a complete native KiCad schematic or independent full topology/readability acceptance. Retained coverage: `06_build/verification/schematic-pages-485.json`; SVGs: `06_build/tmp/schematic_pages_complete/`.

Seventy digital pin/net/value/MPN assertions pass on the latest source expansion. The reviewed engineering reset bounds are 9.102 ms initial high versus 2 ms required and 19.602 ms second low versus 1 ms required. Added held-rail static load is screened below 0.56 mA, within the prior 5.729 mA allocation remainder. Startup/hold-up and dropout trajectories remain under calculation; static load and nominal capacitance do not prove quiet shutdown.

Retained current evidence hashes:

- `01_docs/sourcing/exact-parts.csv`: `255b4abe351cbbd05128133d55cd5b69031514f12e3c0984befb73da0ba6f241`
- `06_build/tmp/full-source/circuit.json`: `784af4958a04515b8485f199e2bcbce1c02013c46b5e0c2001fb8b7340852ec2`
- `06_build/verification/source-admission-485/audit.json`: `ce1e9b956cb5f9a502432747c5aec9790c569db54b54963f73875f7074ca77cf`
- `06_build/verification/digital-power-state-485.json`: `9cda103f3bb6c1525b82a6f968c92726245c3a9e50c96332a669a80c775ee8e7`
- `06_build/verification/schematic-pages-485.json`: `9983e1976dd245f19f0b020140ca2bdf2deb4d38d68b2c299e04be33fdba1c51`
