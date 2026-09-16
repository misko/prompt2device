# Reference correction boundary — 2026-09-07 21:23:53 UTC

Status: source progress with power architecture OPEN. This record supersedes
the earlier reference findings in SOURCE-CORRECTION-20260907.md, not its
history. It is neither a SOUND review nor source, layout or release acceptance.

The fresh author started at 20:48:10 UTC and froze all writes at 21:23:53 UTC,
before the declared 21:26:17 UTC deadline. The coordinator acknowledged the
freeze and subsequently checked the exact files. Host runtime/token telemetry
was unavailable; no canonical TaskAttempt or containment claim was fabricated.

## Corrected source

- Two external 10k/10k half-supply dividers now drive the existing VMID
  followers, with 10uF + 1uF bypass per divider. ADC VMID outputs retain
  their separate decoupling only. ADR-0008 records the hardware-mode rule.
- ADC pins 17/44 and all six FILT capacitor negatives now return directly
  to GND. The two former one-ohm negative-return resistors are removed.
- Positive FILT feeds remain one ohm, upgraded to exact pulse-rated Vishay
  CRCW12061R00FKEAHP/C844653, 1206. Both 470uF reservoirs remain.
- Primary Panasonic/Vishay PDFs, hostile regression tests, capacitance
  inventory and reference-settling calculations are retained in source.

The coordinator corrected two remaining descriptive/census errors after the
freeze: the removed R_TDM_OE_PU was still listed for first power, and
ARCHITECTURE.md still described that pull-up and pre-ADR-0007 order timing.
These corrections change neither the frozen TSX nor its generated electrical
subject. The first-power installed set now matches all 212 netlist components
exactly, with no extras, omissions or duplicates. This is a plan census,
not a measured population or permission to apply power.

## MEASURED verification

Coordinator re-runs: 39/39 project unit tests; E-INV 74/74; E-ADR 4/4;
133/133 net labels and 201/201 pin-map assertions; analog topology PASS.
The source-power checker and shared E-TOPO both still fail the old regulator:
283.6875mW versus 238.379mW at the unchanged 150mA/85C allocation.
The native delta was independently parsed against the preserved old netlist:
eight added components, two removed, ten existing-pin net changes and no
existing-component value changes. The positive-feed MPN/package changes are
additional to that electrical pin/value comparison.

The coordinator viewed all six final PDF pages. This is inspection, not a
fresh independent schematic review. The author producer log reports
M-FRESH 9/9, zero embedded errors and 1379 advisory warnings; it stops at
E-TOPO before board regeneration, new ERC/catalog acceptance or review.

Exact generated hashes and command observations are in the companion outcome
JSON. The unchanged placement PCB remains stale relative to this source.
INHERITED: pod release v0.1.0-2026-09-03 was not revalidated or modified.

## Remaining work / fresh handoff

Use research/power-reference-20260907.md as an unadopted proposal, not a
frozen BOM. The surviving TPS7A24 thermal/capacitor/ramp/reverse-current
finding needs a coherent source replacement. Include full/lifecycle charge
inventory, regulator startup/disable behavior, input hold-up and discharge,
and analog-driver/back-power paths during startup and brownout. Public
manufacturer information supports continued engineering; there is no new
user, hardware, uploader, account or vendor-response prerequisite here.

After source closure: regenerate, refresh exact public-catalog evidence,
commission independent reviews, then placement/routing and release gates.
No order, routing, seal, release or push is claimed by this correction.

Preservation/log directory:
`/tmp/carrier-power-reference-preserved-20260907.2Q7Nnh`.
Git history preserves the earlier tracked subject; temporary logs are
diagnostic aids, not the sole authority for these durable observations.
