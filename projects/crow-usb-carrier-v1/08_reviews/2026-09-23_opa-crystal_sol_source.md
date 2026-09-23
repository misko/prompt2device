subject: crow-usb-carrier-v1 OPA/crystal candidate 15beff8e + 3e9cabeb
date: 2026-09-23
reviewer: independent SOL agent /root/modular_review, source/electrical/physical mapping
context-given: full-tree
source_commit: 3e9cabeb8c343b4706b77f4034ddfc64abe665af
board_sha256: not-generated (source-only review)
design_verdict: SOUND (bounded OPA/crystal source delta only)
order_verdict: BLOCKED-SOURCING

# Independent review — OPA/crystal source candidate

Date: 2026-09-23
Candidate stack: `15beff8e0c46b8dc631545ec7add32a44f11422c` + `3e9cabeb8c343b4706b77f4034ddfc64abe665af`
Verdict: **ACCEPT as a bounded source candidate**. Broader D5 sourcing, ADC architecture, native placement, oscillator measurement, uploader matching and release holds remain open.

## Re-review disposition

The original review correctly found the native KiCad footprint wrong, but incorrectly treated the TSX coordinates as having the same Y convention. Independent coordinate reconstruction confirms:

- YXC page 1 top view: upper row `4,3`; lower row `1,2`; pins 1/3 crystal and pins 2/4 case ground.
- TSX uses Y-up. Its positive-Y upper row is `4,3` and negative-Y lower row is `1,2`, so the original TSX land was already correct.
- KiCad uses Y-down. Repair `3e9cabeb` now places negative-Y upper `4,3` and positive-Y lower `1,2`, making its physical top view agree with the manufacturer and the TSX land.
- The native footprint now adds the 3.2 x 2.5 mm fabrication body, a 4.8 x 3.7 mm courtyard, and pin-1 marks. `test_yxc_crystal_land.py` passes and checks both coordinate sets, pad size/pitch, physical pin roles, source nets, body and courtyard. An independent coordinate probe also produced upper `4,3`, lower `1,2` for both conventions.

## Accepted evidence and boundaries

- TI SBOS513F SHA-256 `1d13d91bc220d3f37e814e29599ce23e086bd661227618104dcae5482c8144fc` confirms OPA2320AID and OPA2320AIDR are the same active-production SOIC(D)-8 device/pinout; AID is a 75-piece tube and AIDR a 2500-piece reel. The eight source edits change only exact MPN/code (`OPA2320AIDR`, `C2863402`) and retain pin/net connections.
- Raw JLC `C2863402.json` SHA-256 `56dfa41b06a7e10bfb439155f545bd3e1a56f8e735a59cb4d46546e0d49242d1` identifies exact TI OPA2320AIDR and stock 582 at 2026-09-23T02:51:00Z.
- Raw JLC `C70590.json` SHA-256 `ca878f238dd9cc2ea15d74eae4a55f895bfc9e50900a181c2e481aa2f1fc8f46` identifies exact YXC X322524MOB4SI, 24 MHz/12 pF/±10 ppm/±20 ppm/-40..85 C and stock 66,719 at 2026-09-23T02:50:59Z. YXC primary PDF SHA-256 `8448fb1ea37694ca77ad3d9579b5d10921746ccd8b3ff79349ef61322453340c` supports the body, lands, 50-ohm maximum ESR at 24 MHz, and terminal roles.
- The retained 22 pF + 22 pF network gives 11 pF ideal differential load plus stray; matching a 12 pF crystal is a bounded assumption consistent with the retained XMOS example. The candidate correctly leaves parasitic extraction and oscillator start/frequency/drive for later proof.
- Candidate output has 493 source components, 1,627 source ports and 1,498 source traces. The source diff changes nine identities and the Y_XU land, with existing connection expressions unchanged.

This acceptance establishes these two source selections and corrected land geometry only. Catalog stock is not allocation or PCBA eligibility, and the project release remains held by the explicitly retained obligations.
