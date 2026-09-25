# D15 pair-clearance and public-calculator review

**Review only — 2026-09-25.** This record neither accepts D15 nor creates a Crow board, route, fabrication candidate, or stage credit.

## D15 authority and scope

The revised proposed D15 correctly identifies that generating the private USB pair-rule contract may be *route preparation* under D11. Its narrow, one-copy override is therefore needed: it permits a stack/rule preview only, while retaining D11's bars on route import and all tracks, vias, arcs and teardrops. An accepted project-owned D15 and independent preflight are a sufficient decision mechanism under the continuing release-design instruction; D14 does not impose a separate user-specific approval.

Two text corrections are needed before accepting the draft:

1. It both requires a tight named rule area for the pair scope and says that no other `rule or geometry` change is permitted. Add that one named, F.Cu-only permissive rule area (its exact name, layers and bounding-box evidence) to the private delta allowlist. Do not permit a broad or multi-layer area.
2. The preflight refers to a copied-source diff “against the table above”, but the draft contains no such table. Replace this with an explicit allowlist of copied files and fields, including the rule-area addition.

These corrections do not enlarge the authority. The final receipt must still set every routing, fabrication, qualification and release-credit field false.

## Disposable KiCad precedence control

I created and DRC-checked a synthetic board only in `/tmp` with KiCad 10.0.4; no Crow source or board was read or changed by the test. Its `.kicad_dru` contained, in this order:

```scheme
(rule "generic_copper_clearance" (constraint clearance (min 0.150mm)))
(rule "scoped_clr_usb_pair_envelope"
  (condition "A.insideArea('usb_pair_envelope') && B.insideArea('usb_pair_envelope') && (((A.NetName == 'USB_DP') && (B.NetName == 'USB_DN')) || ((A.NetName == 'USB_DN') && (B.NetName == 'USB_DP')))" )
  (constraint clearance (min 0.100mm)))
```

Three F.Cu tracks were 0.180 mm wide: `USB_DP`/`USB_DN` had an exact 0.100-mm copper-edge gap inside a tight, F.Cu-only `usb_pair_envelope`; `FOREIGN`/`USB_DN` had a 0.140-mm edge gap, with the foreign track outside the area. `kicad-cli pcb drc` reported no DP/DN clearance violation and did report:

```
Clearance violation (rule 'generic_copper_clearance' clearance 0.1500 mm; actual 0.1400 mm)
```

The other findings were expected missing-outline, 0.200-mm default track-width, and dangling-track findings from the deliberately minimal board. This verifies that the generated exact-pair rule overrides the generic rule for the pair and retains 0.150 mm for a foreign net. It does **not** qualify an actual Crow escape. KiCad's `insideArea` predicate is overlap-based, so the eventual F.Cu rule area must be tightly bounded around only the intended pair envelope; a track that merely overlaps it can satisfy the predicate.

## Public calculator replay

`replay_frontend_binding.py` reran successfully on 2026-09-25 and returned `PUBLIC_RESEARCH_ONLY`, `89.9172598796` ohms both at HZ0 108 and the HZ0=90 control, with frontend SHA-256 `dd57ca32426d511d6fe392ae66c205c872601a9837a56763b78c6d334ad7aec5`. It supports a public, template-derived numeric cross-section hypothesis: 3313A's two prepregs total 0.2064 mm at Er 4.1, and the UI generates an `accessId` for the calculator-list item rather than binding the calculation to a vendor production stack selection. It is not an authenticated quote, production impedance commitment, source adoption, or physical qualification.

Before commit, correct the first summary paragraph of `2026-09-25-jlc-3313-uniform-usb-solve-sol/README.md`: it says HZ0 semantics were not verified while the later frontend section documents the controlled HZ0=90 replay. State consistently that HZ0's *physical meaning* remains unknown, but the tested forward result was insensitive to the documented 108-to-90 control.
