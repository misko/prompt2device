# Digital rail inductor adoption

Selected Würth 744373240047 for L_U_1V8, L_U_3V3X and L_U_CORE. TI SLVSEF9I Table 8-5 recommends this exact 0.47-uH part; its retained primary drawing establishes the package and lands that remained unresolved for the prior TDK selection. Wiring and reference identities are unchanged.

The primary rating is 14 mΩ maximum DCR at 20 °C, not the 11.2 mΩ typical value transcribed into TI's maximum column. At 5.05 V input, 2.2 MHz typical switching frequency and 0.329 uH effective inductance, the largest screened peak is 1.79 A. The 10.4 A saturation rating is typical: this calculation is an initial selection screen, not a guaranteed full-PVT or board thermal result. The manufacturer temperature-rise fixture uses 105-um copper 40 mm wide; actual-board thermal evidence remains required.

The larger body is approximately 5.6 times the prior nominal body area. The new outline is unconstrained; price, availability and assembly sourcing remain unqualified. No LCSC identity is asserted.

Root visually checked the primary page-1 drawing. Lands are 1.5 x 2.4 mm at x=±1.85 mm. Review corrected the candidate courtyard to ±2.90 x ±2.45 mm, giving at least 0.27 mm clearance at the stroke edge. The 2.2-mm central restricted stripe extends through maximum body height (4.31 mm); a native all-copper rule area prohibits tracks/vias and permits pads and copper pours. Applying the restriction to every copper layer is a conservative project choice. Native placement/routing must preserve this rule area.

The original SOL delivery receipt remains immutable; its later footprint correction is separately recorded in the trial evidence. No board placement or design-clean status is claimed.

Root validation after adoption: TypeScript passed; full electrical expansion retained 422 components, 85 selected MPNs, 1,391 ports, 1,276 traces and 26 critical endpoint checks with zero source errors. All 85 source-selected native footprints loaded; exact Wurth pads and prohibited-track/via rule area passed explicit checks. Modular plan still covers 422/422 components and 53/53 crossing nets. Project contracts: 335 files, zero violations. These checks do not establish native schematic or routed-board acceptance.
