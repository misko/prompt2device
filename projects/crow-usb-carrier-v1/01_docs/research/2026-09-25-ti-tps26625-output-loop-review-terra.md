# Independent review — TPS26625 channel-8 output-bypass leg

**Disposition: accept as a narrow native-connectivity/geometry witness only; no P2, current, thermal, or EMI acceptance.** This reviews SOL commit `0b1ed6845184dea9c1e07c8e8a7623478a07f624`, packet `2026-09-25-ti-tps26625-output-loop-sol`. I replayed `probe.py` under its archived full profile and restored the UUID-sensitive committed outputs, then independently loaded its filled board with KiCad connectivity.

## Verified native facts

The candidate's receipt pins the current TI source inputs and reports 569 footprints with the 27 fixed refs and pad/pose ledger unchanged. The committed filled board SHA-256 is `28412ec5054d3b322ea03e37516aa969551beb1e2083b2fa0d2662863969dff4`. Independent native inspection finds exactly these `N12V_POD8` additions:

| Layer | Endpoints (mm) | Width |
|---|---|---|
| F.Cu | (191.4, 46.3) to (191.4, 45.8) | 0.50 mm |
| B.Cu | (191.4, 45.8) to (193.65, 45.8) | 0.50 mm |
| F.Cu | (193.65, 45.8) to (193.65, 46.7) | 0.50 mm |

The layer transitions are two through vias, each 0.60 mm outer / 0.30 mm drill. The 0.50-mm copper satisfies the current `POD_POWER` width floor and its 0.20-mm clearance rule; the ordinary 0.30-mm drill family is consistent with the governed assembly posture. This is rule/geometry consistency, not ampacity or via-temperature qualification.

Native connectivity contains `U_SPOKE8.10` and `C_SPOKE_OUT8.1` together. The launch contains the U.10 pad center and the packet measures 0.05684327 mm² land overlap; the capacitor launch contains its pad center with 0.45840504 mm² overlap. The small U.10 overlap is adequate for this geometric witness only: fillet, mask/paste, fabrication tolerance, current crowding, and contact resistance remain unproved. The nearest measured foreign F.Cu copper gaps from the first launch are 0.325011 mm to PowerPAD.11 and 0.330016 mm to U.9.

`C_SPOKE_OUT8.2` remains native-connected to `U_SPOKE8.6` on GND. Its recorded 5.95-mm F.Cu return path lies inside one continuous filled In1 GND outline (outline 8); independent inspection confirms a filled GND In1 zone. `U_SPOKE8.11/.5/.3`, `R_SPOKE_ILIM8.2`, and `C_SPOKE_DVDT8.2` remain a distinct `SPOKE_RTN8` component, with neither U.11 in the U.6 GND component nor U.6 in the RTN component.

The full-profile replay reports 199 violations and 499 unconnected items before and after, with +0/-0 violation identities and no V-PROCESS failures. This means the added leg has no observed native DRC regression; it does not make the remaining opens electrically complete.

## Limits and remaining evidence

The 9.495 mm² number closes pad centers through the internal device/capacitor chords and collapses a B.Cu crossing plus In1 return into a 2-D polygon. It is a reproducible placement surrogate, not loop inductance, return-current distribution, radiated/ conducted EMI, or fault-current evidence. The via antipads and 5.95-mm GND path need a stackup-aware field/return analysis or measurement.

This packet also leaves open the PowerPAD RTN thermal island, ILIM/dVdT/UVLO legs, the actual J8 pod feed, all current/thermal evidence required by the channel-8 accounting review, and the ADC8/J8 physical-cell issue. The next qualifying output-loop evidence must use the realized full route to J8 and measure/extract supply-and-return current paths, via/pad contact resistance, loop inductance or impedance, and 70-C fault/retry temperature. No source-rule relaxation follows.
