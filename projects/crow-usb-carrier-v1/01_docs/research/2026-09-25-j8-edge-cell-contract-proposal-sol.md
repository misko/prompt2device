# J8 edge attachment for a typed physical cell: design proposal only

**Disposition:** propose one named, mechanically qualified exception to the *full-envelope containment* test for fixed J8. Keep its physical cell itself entirely inside the native board outline. Do not change the outline, J8 pose, footprint, current checker, or P1 source in this packet. This is a schema design for independent review, not permission to admit the current board to P1/P2.

## Exact problem and scope

On the pinned 569-ref TI integrated research board (SHA-256 `0b9d017706845ad4d77c2b579dd36f2e34c0ecf55a7b699ace4fca97465c5b93`), fixed J8 belongs to the 36-ref `analog_ch8` modular owner. The native outline begins at y=20.000 mm. J8's full checker envelope, body plus both courtyards, is `[198.875,19.955,216.268081,34.495]` mm; body is `[198.891919,19.975,216.268081,34.475]` mm; its 12 pads start at y=23.260 mm. Thus a cell enclosing the full envelope fails `_physical_cells`' in-outline condition by 0.045 mm; clipping the cell at y=20.000 fails full-envelope containment. The reproducible [screen](2026-09-25-ti-adc8-exclusive-cell-unsat-sol/README.md) proves this contradiction. The current `usb_frontend` source region begins at y=35.000, leaving 0.505 mm from J8's envelope; an older y=29 overlap is not current.

The existing checker deliberately enforces source cell outline containment, complete modular-ref assignment, fixed pose, full body/courtyard and pad containment, no other footprint/pad entering a cell, matching source placement patterns, no foreign region overlap, and no capacity from a typed cell. Only one predicate needs a controlled exception: the named member's full envelope may extend by the *qualified* amount beyond the board edge, while its inboard portion and **all pads** remain inside its source cell. No generic out-of-outline region, witness, reservation, route, or via allowance follows.

## Proposed narrow source shape

Extend one occupied `physical_cells` row with an optional `edge_attachment` object; all rows without this object retain today's exact four-key schema and checks. This illustrative row is **not valid current source syntax**:

```yaml
- id: analog_ch8_j8
  owner_block: analog_ch8
  refs: [J8]
  transit: false
  edge_attachment:
    ref: J8
    native_edge: north
    maximum_full_envelope_overhang_mm: 0.045
    mechanical_receipt:
      id: j8-edge-registration-exact-ti-board
      sha256: <independently reviewed receipt digest>
```

The linked floorplan region remains **in-board**, for example a later independently screened J8 cell whose north face is y=20.000. The example intentionally gives no rectangle: the other 35 channel-8 refs and foreign cells require coupled recuts, and the J8 row cannot authorize one by itself. The record must be unique in the source (one named ref/cell/edge), and `ref` must be the row's sole member, in `p1_fixed_refs`, at the source-pinned native pose. No empty transit cell or multi-ref cell can use it. Limit the initially implemented form to the actual straight north edge, not arbitrary polygon cuts, corners, slots, or multiple edges.

## Validation order and independent binding

1. Parse the record with an exact key set. Resolve the receipt from a governed, separately produced mechanical qualification artifact; a path, source assertion, plan, or unchecked prose alone must **not** qualify. The artifact must have an accepted result and bind exact board SHA, native outline geometry/digest, J8 footprint identity/library geometry or native footprint digest, J8 source/native pose, edge segment, mating orientation, part/mate identities, measured or drawing-supported body/courtyard overhang and allowed tolerance, installed setback, and pad accessibility. Its hash must equal the source record. A changed board, footprint, outline, pose, or receipt invalidates the exception. The existing connector qualification plan has unknown mating datum, exposure, setback, and service clearance; it is not itself this accepted evidence.
2. Validate the **cell rectangle** against the complete native outline with unchanged `lane_inside_outline`. Validate every J8 pad bounding box inside both native outline and cell; reject pad copper, drill, or mask features crossing the edge as relevant to the mechanically reviewed connector. Compute J8's full native envelope with unchanged `_physical_envelope`; compare its intersection with the board to the cell and its exterior sliver to the receipt's edge-side and exact projected span. The native overhang must be positive, at most the receipt-qualified maximum (with explicit numeric tolerance), and no part of the envelope may protrude across another edge. Check native body and courtyards independently, so a later footprint edit cannot hide a body overhang behind a courtyard allowance. Never clip the envelope before measuring it.
3. Retain all current owner/ref-denominator, source-pattern, unassigned footprint/pad, foreign-region, and positive-edge-contact checks. Additionally test the exterior sliver against the receipt's connector-only mechanical keepout and other native full envelopes. Do not treat the exterior sliver as an in-board routing area or a corridor face. Keep witnesses, endpoint pockets, reservations, access portals, copper, and returns under their existing strict outline checks.
4. Preserve the 27-fixed-ref pose test and native NPTH explicit-fixed test. In implementation, ensure fixed validation runs before accepting an attachment, rather than letting `_physical_cells` grant an exception before the present later fixed check. It may be sufficient to move the fixed validation earlier; do not duplicate inconsistent pose logic.

The receipt may establish only **this J8 edge attachment**. Connector FULL still needs its own complete mating, simultaneous-use, service, harness, and first-article evidence. Conversely, an eventual connector FULL result should not automatically waive an arbitrary source cell: its exact board/geometry/edge binding and the typed-cell checks still apply.

## Negative controls for a future red regression

| Mutation of an otherwise pinned candidate | Required rejection |
| --- | --- |
| Add `edge_attachment` to movable `C_ADC_AC8N1`, another channel member, or fixed J7 while citing the J8 receipt | Ref/receipt identity or sole-member/fixed binding fails. No blanket connector or courtyard allowance. |
| Move J8 or change its footprint/courtyard/outline after the receipt, without new qualification | Board/pose/native-geometry digest mismatch, even if the observed protrusion stays small. |
| Increase J8 protrusion from 0.045 to e.g. 0.50 mm, or change it to west/east/corner | Qualified bound/edge/span fails; source cannot enlarge the receipt allowance. |
| Let one J8 pad, drill, or required copper area leave the outline or its inboard cell | Pad and mechanical containment fails regardless of envelope exception. |
| Extend the cell rectangle outside the outline or give its exterior strip to a witness/reservation | Existing strict in-outline checks fail. |
| Drop J8 from `analog_ch8` assignment, add an unrelated ref to its cell, overlap a foreign source region, or use an unaccepted/missing receipt | Existing denominator/exclusivity or new evidence gate fails. |

The red suite should also keep a green control: the exact independently qualified J8 footprint and pose may have only its reviewed 0.045-mm north sliver outside the outline, while the inboard cell/pads and all ordinary checks pass. That green control establishes **planning geometry admission only**. It neither supplies ADC8 signal capacity nor proves a filled reference or route; the current analog denominator, 11 foreign-region-hit channel-8 refs, and P2/P3 endpoint/return obligations remain. Until accepted local mechanical evidence exists, the current checker must keep the cell **FAIL**. After local evidence, the checker may classify the typed-cell shape as geometrically valid/`INCOMPLETE`; P1 and P2 decisions still require their separate governed gates and connector FULL remains separately outstanding.
