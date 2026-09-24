# XMOS support-block decoupling geometry audit

This read-only audit checked the withdrawn 90-degree XMOS placement from commit
`f5d59d08`, using native candidate board SHA-256
`95d8878f8f6935cb6d0fa5904b8936b2a76afc7fca58a4efc60ab74402aa7afd`.
For each named `C_XU_VDD_*` and `C_XU_VDDIO_*`, it measured capacitor pad 1 to
the matching `U_XU` supply-pin center on the same net.

All 23 distances were 5.351–22.409 mm (median 15.367 mm; mean 14.590 mm), and
17 exceeded 10 mm. `C_XU_VDD_104.1` to `U_XU.104` was 17.2388 mm. These poses
cannot be represented as a local per-pin decoupling block, so all 29 XMOS and
support anchors were removed from current `floorplan.yaml`.

This is a geometry-defect screen, not an electrical limit: the source does not
provide a numeric capacitor-to-pin maximum, and distance does not measure loop
inductance, route length, return vias, plane impedance, or transient response.
The next XMOS block authoring pass must establish those local relationships and
obtain fresh native geometry and electrical review. This audit grants no P1,
P2, routing, release, manufacturing, or order credit.
