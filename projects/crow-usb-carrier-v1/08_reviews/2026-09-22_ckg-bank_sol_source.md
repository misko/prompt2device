# Independent final source review — CKG57K capacitor bank

- Review date: 2026-09-22 (America/Los_Angeles)
- Integrated subject: `051246af9d973aef102de72001bd85a54415b242`
- Source candidate compared: `3451f6e3e17e91614cc57187a9d94b748b939684`
- Scope: exact TDK capacitor-bank source, its native footprint, source identity/provenance, and the LT3045/TPS62825 conditional electrical claims only
- Verdict: **ACCEPT — source acceptance only**

## Verbatim verdict

> ACCEPT — The integrated source preserves the independently reviewed 13-part `CKG57KX7R1E476M335JH` population and exact two-pad J-lead land. The tracked native footprint matches the TSX geometry: pads 1 and 2 at X = -2.925 mm and +2.925 mm, each 1.75 mm by 4.75 mm, on F.Cu/F.Mask/F.Paste; its F.Fab maximum-body envelope is 6.5 mm by 5.5 mm and its F.CrtYd envelope is 8.1 mm by 6.0 mm. The selected midpoint geometry corresponds to TDK PA = 4.10 mm, PB = 1.75 mm, and PC = 4.75 mm. This acceptance does not establish placement, stencil/process acceptance, routed interconnect inductance, startup/load-step stability, thermal performance, PCBA allocation, or orderability.

## Evidence checked

`pcbnew.FootprintLoad` reopened `TDK_CKG57K_JLead.kicad_mod` from the integrated commit and returned exactly two pads. Independent numeric assertions passed for pad number, center, size, copper/mask/paste layers, F.Fab bounds `(-3.25,-2.75)..(3.25,2.75)`, and F.CrtYd bounds `(-4.05,-3.00)..(4.05,3.00)`.

The integrated source has thirteen exact references in `exact-parts.csv`; the same references exist in `integration.yaml`. Twelve references participate in device-minimum effective-capacitance banks. `C_OPA_BULK` remains the thirteenth physical part and is correctly described only as an advisory downstream reservoir with no invented regulator-stability minimum. All five TSX construction sites carry exact MPN `CKG57KX7R1E476M335JH`, exact source identity `C2171626`, and the selected native footprint; their loops expand to thirteen parts. The order-facing CSV intentionally leaves the LCSC allocation field blank because observed JLC stock was zero, while the dossier and TSX retain catalog identity. No JLC allocation is claimed.

Independent arithmetic gives:

- TPSM output: `3 * 47 * 0.80 * 0.40 * 0.85 * 0.875 = 33.558 uF`.
- Doubled TPS62825 and LT3045 output banks: `2 * 47 * 0.80 * 0.35 * 0.85 * 0.875 = 19.5755 uF`.
- Single LT3045 input and advisory OPA reservoir estimate: `47 * 0.80 * 0.35 * 0.85 * 0.875 = 9.78775 uF`.

The integrated prose now matches those results. The capacitance gate independently passed all fifteen current E-CAP rows; the CKG-backed rows reported 33.558/25 uF, 19.575/10 uF for each TPS62825 output, 9.788/4.7 uF for LT3045 input, and 19.575/10 uF for LT3045 output.

The TPS62825 claim remains conditional: TI's 0.47-uH table contains nominal 47-uF and 100-uF cases, while this design installs 94 uF nominal. Proximity to the 100-uF column is not stability proof; startup, ramp, and load-step validation remain required.

The exact TDK primary product page was reviewed on 2026-09-22 for production status, 47 uF ±20%, 25 V, X7R, body dimensions, and PA/PB/PC ranges. The exact TDK equivalent-circuit-library row dated 2026-02-27 reports `L1 = 2.000 nH` and `R1 = 0.0041 ohm`. Direct ECM byte retention returned HTTP 403, and the source correctly claims no retained ECM PDF or hash. Two ideal equal capacitors give 1.000 nH and 2.05 mΩ before PCB interconnect. The LT3045 requirement is strictly below 2 nH for the complete COUT network, so shared connection and layout inductance must be strictly below 1.000 nH and the assembled network must be extracted or measured before physical acceptance.

## Proof limits

This review is not a native board, placement, routing, DRC, stencil, assembly-process, thermal, transient, impedance, sourcing-allocation, or order approval. It does not convert typical/cross-part capacitance proxies into guaranteed TDK production limits. It accepts the source representation and its explicit validation obligations only. The main worktree was read without modification, and no full native build was run for this review.
