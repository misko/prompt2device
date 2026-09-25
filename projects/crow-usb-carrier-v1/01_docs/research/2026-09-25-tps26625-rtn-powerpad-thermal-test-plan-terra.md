# TPS26625 channel-8 RTN/PowerPAD thermal-island test plan

This is a source-and-primary-record test plan for `U_SPOKE8` only. It changes no source or board and grants no P1/P2 credit. Primary authority is TI TPS2662 SLVSDT4F revision F, retained at `02_parts/TPS26625DRCR/TI_TPS2662_SLVSDT4F.pdf` (SHA-256 `ff038eaa557fb618f93c0b6276a5ae08d0d3d9fbff1dddf0c45974a89120aefa`), plus the current part and power-tree records.

## Governing net and thermal contract

The current exact pins are U.3 OVP, U.5 RTN, U.6 system GND, and U.11 PowerPAD. Crow source assigns U.3/U.5/U.11, `R_SPOKE_ILIM8.2`, and `C_SPOKE_DVDT8.2` to isolated `SPOKE_RTN8`; U.6 and both bypass-capacitor returns are GND. `02_parts/TPS26625DRCR/part.yaml` and `ic_reference_research.yaml` require the ILIM/dVdT components to return to RTN, never GND; EP11 must join RTN copper for heat spreading; and pin 5 needs an independent RTN-copper connection. The current project also declares 70 C as the thermal-analysis ambient and leaves RTN/thermal copper and vias unqualified.

TI says not to connect RTN to GND, to connect the PowerPAD to the RTN plane for thermal performance, and to size the result for the application. It does **not** provide a Crow-specific minimum island area, via count, copper length, layout temperature rise, or acceptance temperature. The existing 2.5-mm IN/ILIM proximity ceilings are project engineering controls, not thermal limits from TI.

## Unfabricated-board evidence

Before any hardware claim, produce a saved native board and record:

1. Exact net/component graph proving U.3/U.5/U.11, R(ILIM).2, and C(dVdT).2 are one RTN component; U.6, C(IN).2, and C(OUT).2 are GND; and no copper, zone, via, or schematic alias bridges the two.
2. Native EP11 land, RTN island, plane/zone outlines, vias, layer transitions, copper weights, and stackup. Run board DRC, net connectivity, and the mandatory via-process check. Any via centered in an SMT land needs the governed filled/capped process and evidence; ordinary vias must remain off-pad.
3. A reproducible electrical/thermal model on those exact geometries. Sweep normal 0.100-A loading and the conditional 0.145/0.152/0.159-A overload table row only at its TI test condition (24 V and 1-V drop). Separately bound fault/startup/retry waveforms rather than treating 0.159 A as all-state DC. Include pass-FET loss from the applicable RON condition, PowerPAD/RTN conduction, copper/via resistance, input/output capacitor current, external source/cable impedance, and the actual four-layer stack.
4. Model outputs: segment current density and IR loss, via/pad/trace temperature rise, RTN-island temperature field, package junction-to-board path assumptions, and cooling between retries. State every material, convection, solder, and boundary assumption; model output is a screening result, not qualification.

## First-article closure

On a fabricated board, inspect EP solder attachment and the implemented via/plane geometry, then electrically verify RTN/GND isolation and all named returns. At the project 70-C ambient, capture synchronized VIN, VOUT, IIN/IOUT, FLT, retry timing, and board temperatures across normal load, startup/output-capacitor charge, regulated overload, fast-short behavior, and repeated retry/cooldown episodes. Measure voltage drop and resistance on the input, output, RTN, and PowerPAD paths with the realized solder joints and vias.

Measure board/EP-adjacent temperature with a documented calibrated method and correlate it to the model; any junction-temperature inference must state its thermal model and uncertainty. Confirm that observed retry behavior, thermal recovery, and source/cable contribution remain inside the separately governed whole-episode source envelope. Do not use TI's typical 1.6-A fast-trip, 220-ns delay, 512-ms retry, or 155-C shutdown figures as guaranteed Crow acceptance limits.

This plan leaves P1/P2 closure contingent on the complete board routes, source-cell authority, ADC8/J8 resolution, and evidence above; a clean local DRC or plane connectivity result alone is insufficient.
