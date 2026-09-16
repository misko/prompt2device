# Routing learnings

## Source route contract can fail before route search — 2026-09-08

- MEASURED cause: the existing wave resolver rejects nine absent names:
  eight wildcard-group/reference-name mistakes plus 12V_POD*. Group lists
  require exact names; only exclusions expand globs. FILT1N/FILT2N physical
  pins are grounded, not live named nets. Independent native inventory finds
  164 connected non-ground nets and 62 without an explicit class. A complete
  in-memory partition is a hypothesis, not adopted routing authority.
- MEASURED cause: declared reference/power wave widths undershoot transient
  class floors. Source/helper prediction also finds 0.8 mm below the unchanged
  ampacity model's 1.063 mm for 2.5 A, 1 oz external copper, 10 C rise. This
  predicts a future A-AMP disagreement; no generated A-AMP gate was run.
- MEASURED source geometry: all four configured 0.45/0.20 mm via pairs have
  0.125 mm annulus below the preserved 0.13 mm source minimum. Individual
  tier diameter/drill checks did not establish paired annulus compliance.
- MEASURED limited launch diagnostic: five exact ADC lands permit a sampled
  0.20 mm straight launch at 0.20 mm clearance versus 0.10 mm at 0.25 mm.
  This is package-only, not a full route or universal impossibility proof.
- Prevention: close exact net/class/owner membership, current-tier trunks and
  bounded taps, paired via geometry, stack/SI/return intent and reached local
  constraints before regenerating. Do not globally weaken floors, fabricate
  a poured current path, or let a poured net silently erase adjacency coverage.
- Evidence/method/limits: `06_build/verification/route-source-diagnostics-20260908/`.
  The previously adopted placement source is cfb09588; its geometry/tests do
  not clear these separate routing-source defects. Use a fresh owner and one
  coherent correction batch. Candidate canon: no; project-local application
  of existing route ownership, current rules and source/prep contracts.


## 2026-09-12 — Run package consistency before expensive renewal

- what happened: full routing preflight failed87/87dossiers with one stale escape-tier declaration only after schematic regeneration, physical artifacts and fresh placement review were complete. Original failure is preserved in journal/c60aec968cc6667c05f08bc15ec86ef4c7e63aa8fd3c27b7b7bc39519d2a2c89.tar.gz.
- root cause: the package checker includes historical superseded dossiers, while the earlier canonical conductor invokes native P-LAND but does not invoke this complete package-dossier check. An uninstalled historical part therefore reached the later admission boundary with inconsistent source metadata. The all-part identity also makes its correction invalidate downstream review bindings.
- avoid next time: before a source freeze/canonical renewal, run the existing package checker over exactly pcb_flow.part_files' complete census, alongside the existing source consistency and sourcing-age checks. Keep the full routing preflight afterward. Do not exclude historical records, skip checkers, or restamp reviews to reduce work.
- candidate-canon: no; this is a project-local sequencing recommendation pending a separately reviewed shared-pipeline change. It supplies no acceptance or checkpoint exception.
