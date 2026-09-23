# Independent SOURCE-only ADC bypass and placement review

review_verdict: SOUND

source_adoption: ELIGIBLE_AFTER_REPAIRS

native_admission: NOT_REVIEWED

## Scope and packet integrity

This is a fresh, READ_ONLY judgment of the proposed source change only.  The
schema-2 envelope is valid: its SHA-256 is
`e9e8af9e295b5435f7ae17b30ec8b8cb0fa6dcaada32f9106b17b459869f21df`; its
106 declared inputs were checked for both SHA-256 and byte size, with **0
mismatches**.  The detached manifest SHA-256 is
`652c7004c5e4d0c03d789bc5b4c1d1d2588729cc100ccfd3c206f3b5df9f0abb`.

All **90/90** raw selected `part.yaml` dossiers were independently checked
against `inputs/selected_dossier_manifest.json`
(`f97a0ff6e4c68db3f126d5aa6f898595610325eb2cff03d2eb09fbc30049fc4a`):
zero hash or size mismatches.  The exact selected supervisor dossier is
`TPS389001DSER`, SHA-256
`ce8a63c2839cc285f1e7bf9f9e7dcbf2269458de3a63e089bfb9dfb2c440a3ec`, and
it records the adjustable 1.15-V threshold, pins 2=GND and 4=VDD.  Both
authored ADC supervisors specify `TPS389001DSER` / `C1509297`; the patch makes
no TPS389018 substitution.  Per the final corrigendum, the earlier TPS389018
claims in the retained disposition are superseded and were not used as the
part-identity judgment.

Exact principal input hashes: `complete65_source.patch`
`bc11a51c570e72f03ac63fdeced8aaaedb69fd0d3a6b2fe81ef4451f029ffee9`;
geometry JSON `70677edc20c6363d68f6bfeef44c407d6adf1765ba1bd83ebd4a7d65f83a6519`;
geometry stderr `ecfdabc9a488fbdbeb42728b58080ecf903a12f0cabcb48d0622d8aa9f2d1a1e`;
corrected disposition `9eefc6bfc0d5747bf629d376d072341d016b0e3db0ca1e73b7cd5f020a408435`.

The submitted current README is `README.md`, SHA-256
`d8dd45c772386934251c138c6f1aec5333ae80d364cd2818b98b83142c76d0c6`, and
correctly cites geometry SHA `70677...`.  The SHA named in the prompt,
`c82f55fb60542e1ec8104a04ff4daf9ee81879c4ab8aa432abe235024927ae90`, belongs
to the retained `README.original.md`; it contains the superseded `5177ce...`
geometry SHA.  The supplied README-derived diff is a one-line repair from that
historical copy.  Therefore the stale prose does **not** block this source
review or undermine the current geometry claim; it is a repaired README-only
record and must not replace the current README during adoption.

## Six-file source review

All six patch targets and ten hunks were inspected against the copied baseline:

1. `crow_retained_analog.tsx` adds exactly
   `C_ADC_3V3X_OK_VDD`: 100 nF, 0402 `CL05B104KO5NNNC` / `C1525`, authored
   `3V3_ADC` to GND.  This is the authored spelling of derived `N3V3_ADC`.
   It supplies the second TPS389001 locally; the existing
   `C_ADC_DIGITAL_OK` remains the first supervisor's bypass.
2. The schematic-presentation source moves the existing capacitor and adds a
   presentation pose for the new one, so the schematic source remains complete.
3. The manifest increments the source census from 568 to **569** and adds the
   reference once.
4. `modular_plan.json` changes the ADC-reference scope from **64 to 65** and
   assigns both capacitor pads to the relevant GND and `N3V3_ADC` integration
   endpoints.  This establishes modular scope and pad ownership.
5. The floorplan supplies the composed full 65-reference pose set: 63
   overridden/added ADC-reference anchors plus the retained baseline anchors
   cover every 65-reference scope member; the new pose is
   `[118.1, 107.0, 270]`.  No scope ref is missing after composition.
6. `integration.yaml` adds the new reference to the integration census,
   consistently with the manifest and modular plan.

## Electrical and geometry assessment

The source electrical interpretation is correct: VDD is supervisor pin 4,
GND is pin 2, and pin 3 is MR_N tied to the same rail, not the VDD pin.  The
geometry JSON identifies, for **each** local capacitor, 2.905237 mm from pad 1
to functional VDD.4 and 1.300154 mm from pad 2 to GND.2.  Its 1.969873-mm
MR_N.3 value is correctly diagnostic only.

Proposal-evidence coverage is: scope **65**; whole-board census **569**;
17/17 exact poses; inherited numeric prediction **16/16**; zero reported
courtyard, foreign pad/body, and pad-separation findings; and zero VREF
corridor hits across 1,396 tested foreign pads for each of four VREF
reservations.  This supports source planning only.  It does not establish
actual pad shapes, copper return impedance, routes, DRC/ERC, or saved-board
geometry.

## Findings and required boundary

- **P0: none.**
- **P1: retained verifier stderr is nonempty.** It contains three KiCad
  `PROPERTY_ENUM()` assertions.  The JSON records an in-memory PASS, but the
  packet does not provide a clean native execution record or native artifact.
  This does not invalidate the source-only geometric proposal; it prevents any
  promotion of that result to native placement acceptance.
- **P2: historical identity/README material is retained.** The current README
  repair and final TPS389001 corrigendum resolve it for this review.  Preserve
  those corrections when admitting source; do not revive the old README or
  TPS389018 evidence.

Missing proof before native P2: apply/admit the exact source change, perform a
fresh full schematic rebuild and independent schematic review, then generate
and inspect the native board with clean tool results, electrical connectivity,
VDD/GND copper-return/impedance, pad geometry, DRC/ERC, and placement checks.

The exact next boundary is source admission followed by the full source
conductor and its required fresh schematic rebuild/review checkpoint.  The TSX
change invalidates the prior 568-component/64-scope derived schematic, board,
placement, routing, fabrication/BOM/sourcing, and release evidence as stated
in the current README.  Isolated P2 and FULL19 remain blocked pending that
checkpoint; this review authorizes neither P3, routing, nor release.
