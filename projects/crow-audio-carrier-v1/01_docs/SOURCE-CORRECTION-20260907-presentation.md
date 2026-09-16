# Root schematic source correction — 2026-09-07

Source owner: root, sole writer after both bdf reviews completed.
Attempt deadline: 2026-09-07T23:52:59Z.
Order state: DO-NOT-ORDER. No placement, copper, physical qualification,
carrier release, tag, push or publication acceptance is asserted.

## Implemented

- DMP6023LFG-13 dossier now records all eight manufacturer identities.
  Drain positions6–8 explicitly fuse into source-symbol/physical composite
  pad5. DS37204 Rev.2-2 p.1/p.5 and the exact KiCad land support the mapping.
  Primary PDF bytes are unchanged; this repairs extraction, not a revision.
- Two TPS7A92 capacitor descriptions corrected to47uF10VX7R. E-CAP numeric
  assumptions unchanged; the additional lifecycle loss in the separate
  power-state model is now explicitly distinguished.
- Imported source-only schematic_presentation.tsx assigns299refs to19sheets,
  with complete per-channel circuits, split power/control functions, explicit
  main paths, local ground/bypass rail labels and flow-oriented pin placement.
  Board-source named nets remain authoritative; scratch PCB poses and governed
  floorplan/copper are unchanged. Missing/duplicate ownership fails closed.
- Shared human renderer canonicalizes exact source-net names on real
  trace-bound text as well as net-label records; custom notes remain verbatim.
- Shared native converter removes pinless wire islands retained solely by
  provisional producer junction/label anchors. No component-bearing island
  is intentionally removed. Strict native ERC and native parity remain gates.

## Evidence and limits

- Carrier62tests PASS, including5fused-identity tests and6presentation tests.
  Presentation paths are checked against generated named-pin membership;
  this test is not an independent topology review.
- Shared renderer13tests PASS; converter45tests PASS,16known-bad fixtures.
  The added pinless-island fixture checks native strict ERC and all4original
  pin entries/3named nets.
- Full r2:299components, electrical closure9/9, manufacturing selection2/2,
  freshness9/9. Native205nets and868pin entries exactly match bdf66acd,
  including intentional NCs. Root viewed19/19 actual r2 PDF pages.
- Human-PDF regression floor:7native points for references/values/net names,
  6for pins, measured with integer-rounded Poppler XML. This is a minimum
  regression guard, not human readability or physical print approval.
- Public catalog refreshed against51exact codes for5boards:51/51cover the
  quantity. r2 probe CSV is byte-identical to the refreshed probe. No PCBA
  allocation/availability guarantee is inferred from the separate catalog pool.
- r2 public resume: manufacturing4/4 and connectorSOURCE PASS; ERC found one
  detached two-segment island near Q_RST1. The full r3 rebuild incorporates
  the converter correction. Final result is recorded in STATUS/journal.

The original requests/checkpoints/artifacts remain recoverable under
/tmp/crow-carrier-prelayout-before-presentation.KM9Qbc,
/tmp/crow-carrier-presentation-r1.Iiuoeq and
/tmp/crow-carrier-presentation-r2.aJO95a, as well as committed history.
The only deliberate r2 checkpoint refresh changed the source-folder contract
to document its imported presentation helper and executable font floor;
verification identified that sole changed input before refresh368/368.

Final r3 at23:52:11Z: electrical closure9/9, native205nets/868pin entries
unchanged, M-FRESH9/9 plus audit1/1, manufacturing4/4, ERC0errors/2101warnings
(1612off-grid,489library), schematic checkpoint7/7. Source correction frozen
before deadline; no further source changes during the next independent review.
Circuit JSON SHA256:a0a4818bdd30634dc727637be30465c239f467e5d3f4f7dd644580031845ee38.
PDF SHA256:9bd63701177f611b0822e30d6b8438e2c515522539007fa2502708e682ad7e89.

Next: commission fresh
independent topology/readability witnesses. Existing bdf witnesses remain
DEFECTIVE and are not relabeled. Physical power qualification and first-power
current-limit procedure remain owed. Pod sealed release is unchanged.
