# ADC thermal-via source milestone — 2026-09-08

ADR0016 adds nine source-owned ADC49 thermal vias and a fabrication-visible
filled/capped process. This is source progress, not a completed PCB or release.
ROOT is author/operator, not an independent reviewer. Primary dirty checkout,
sealed pod and all generated/review/checkpoint bytes are preserved.

Baseline bfe61d4ee04ba57984947b790d9f9195ec66c72a was clean. The before
inventory binds 1,312 tracked carrier subjects / 103,476,554 bytes; Git keeps
the recoverable baseline. Ignored transients are not claimed censused.

## Measured observations

- 11:40:19Z: 299 footprints / 868 copper pads / 20 seed vias; no existing
  via-in-pad, no ADC49 thermal drops. LDO's two drops are external, not in-pad.
- 11:50:30Z: H1 geometry passes. Nine 0.60/0.30 mm vias fit completely inside
  ADC49 on a 1 mm grid. Source tests independently grade native copper and
  holes on F.Cu/In1.Cu/In2.Cu/B.Cu, including all 36 thermal-hole pairs.
- 11:51:25Z: actual unchanged baseline fails missing-drop coverage and absent
  process/guard requirements. Probe rc0 means the expected negative occurred,
  not that the old source passed.
- 11:53:41Z: existing source consumers pass: ADC 127,156, regulator 49,659,
  digital 21,831 comparisons; 19/19 other clock entries; 8/8 source classes,
  367/367 net references; exact-input shadow 205 owners / 159 generic nets.
  These older geometry helpers count route-seed vias only. The new thermal
  checker separately covers every new field against all those existing items.
- Generated order-note text names both drill families and requires uploader
  confirmation. No board census is fabricated in that source-only text.
- 11:54:20Z: final full suite 162/162 PASS, zero errors/failures/skips and
  every tested input hash unchanged across execution. New thermal source
  screen: 39,850 checks, zero findings, nine intentional ADC49 sites and
  zero ordinary in-pad sites. Its 107 component-drill entries are all
  distinct from the protected 0.30 mm selector.
- 11:59:54Z: scoped structure comparison reports no new findings. The owning
  checker returns the same 18 carrier naming/contract findings on baseline
  and current paths, with all 38 governing contracts baseline-exact. The
  broad repository audit remains FAIL: 2,893 findings and an exceeded debt
  ceiling. No ceiling or contract was weakened. This inherited governance
  debt still needs disposition before claiming a green release battery.

Raw attempts, full source-suite logs and before/terminal identities are in
`06_build/tmp/thermal-vias-20260908`, with a last-written hash inventory.
The initial H1 run hit a Path-to-JSON serialization error after calculation;
the retry changes serialization only. The first 162-test run has one ERROR:
the new test used a nonexistent PAD getter. Corrected it to KiCad's actual
`GetLocalZoneConnection` accessor, with no design change or suppressed test.
The first structure-delta wrapper also exited before saving captured output;
its replacement catches the owning CLI's SystemExit and retains both real
negative verdicts. It does not relabel the broad audit PASS.
The final run and exact input hashes are the source-test acceptance evidence:
`check_live_final.log` SHA256
`9afe45ad80223758c70b02e46fd1aef98634a67de7956fb8a5a1fb4e1732e3b0`.

## What stays unchanged / what remains owed

All 72 seed banks, 201 straight primitives, 20 ordinary seed vias, 299 part
poses, circuit identities, library footprint/paste, stack, netclasses, width/
clearance scopes and current limits stay exact. Source total is now 29 vias:
20 route-seed ordinary plus nine floorplan thermal protected. This is not the
future router's final via census.

The PCB/JLCPCB skills require process intent to be explicit and later graded
against actual board and order bytes. Public capability lets source design
proceed; it does not certify uploader selection, final cost, assembly or heat
removal. The nine paste windows and separate GND_A/GND_D returns remain intact.
No circuit can be energized under the 0.20 A HOLD.

Next: remaining analog endpoint/source checks, then fresh generation/admission
and independent schematic/placement reviews, actual routing and release gates.
Carrier is still stale/unrouted/unreleased; parent remains boardless and pod
sourcing-held. No upload, account, purchase, release tag or main push occurred.
