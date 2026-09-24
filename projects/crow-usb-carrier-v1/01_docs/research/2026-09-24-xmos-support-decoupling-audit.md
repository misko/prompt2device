# XMOS support-block decoupling geometry audit

This read-only audit checked the withdrawn 90-degree XMOS placement from commit
`f5d59d08`, using native candidate board SHA-256
`95d8878f8f6935cb6d0fa5904b8936b2a76afc7fca58a4efc60ab74402aa7afd`.
For each named `C_XU_VDD_*` and `C_XU_VDDIO_*`, it measured capacitor pad 1 to
the matching `U_XU` supply-pin center on the same net.

All 23 distances were 5.351–22.409 mm (median 15.367 mm; mean 14.590 mm), and
17 exceeded 10 mm. `C_XU_VDD_104.1` to `U_XU.104` was 17.2388 mm. These poses
cannot be represented as a local per-pin decoupling block, so all 29 original
XMOS and support anchors were removed from `floorplan.yaml`.

A separate 24-anchor two-ring reconstruction seed was then generated as native
board SHA-256 `5e74f6e3d4bff5a5fd258eedd6bbc800ac12f42ec626050c8cc751d87ce5d9fb`.
Independent geometry review found all anchors exact, no pad collision, and all
23 per-pin distances improved to 1.767–5.179 mm (median 2.560 mm). The highest
remaining rows are VDDIO121 5.179 mm, VDDIO109 4.868 mm, VDD105 4.819 mm,
VDD18 4.288 mm, and VDDIO56 4.149 mm. The seed is current source placement
intent only; it needs routed supply fanouts and ground-return evidence.

This is a geometry-defect screen, not an electrical limit: the source does not
provide a numeric capacitor-to-pin maximum, and distance does not measure loop
inductance, route length, return vias, plane impedance, or transient response.
The next XMOS block authoring pass must establish those local relationships and
obtain fresh native geometry and electrical review. This audit grants no P1,
P2, routing, release, manufacturing, or order credit.
