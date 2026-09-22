# Supplier identity repair

Root reopened the retained live catalog search rows and checked exact code/MPN joins before adopting the SOL delta. No electrical part or pin/net identity changed. The catalog rows are discovery evidence, not allocated assembly stock.

| Exact MPN | Correct LCSC code |
|---|---|
| BC847B,215 | C57668 |
| RC0402FR-071ML | C138033 |
| TPSM63603V5RDHR | C5219330 |
| TPS26625DRCR | C2862873 |
| XU316-1024-TQ128-C24 | C6362698 |

Removed the unsupported suffixless ADC catalog mapping; CS5308P-DN still requires exact external sourcing. The TPSM exact code is retained even though its observed stock was zero; code identity does not imply availability. Critical flash and LDO supply and full two-source qualification remain open.

Timestamped raw catalog outputs are retained in 06_build/cache/sourcing-20260922 (temporary inventory evidence):

- `false-id-search.md` SHA-256 `9ea5ae6e8828305209bbcd0ed4055109b7b3d4078eede6dfdc4d503384be0515`.
- `jlc-stock-2026-09-22.md` SHA-256 `ca6626871b0e12d0fa2369e93db6c6961ab4b1267c9edfea3bf072d9de94c26c`.
