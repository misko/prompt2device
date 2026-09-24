# Independent review: XU PLL post-anchor source adoption (Terra)

Reviewed commit `76066545` against its parent and the retained isolated
evidence at `/tmp/crow-xu-pll-silk-adopt-sol`. This is a source-placement and
silkscreen review only; it is not PLL power/return or release acceptance.

## Source scope and binding

The commit changes only `03_src/floorplan.yaml` and its evidence note. It adds
these three `placement.post_anchors` poses:

```yaml
C_PLL_100N: [220.0, 102.8, 0]
C_PLL_1U:    [220.0, 105.0, 0]
FB_PLL:      [223.0, 103.9, 180]
```

It adds only the reviewed silk controls: priority for C10/C45/C39, C45's
`[2.2,-0.8]` preferred offset, and `fab_only_refs: [C_XU_VDD_39]`. No
canonical PCB, route source, modular graph, or P1 source is in the commit.

The current floorplan SHA-256 is
`4a457c731c204084a83aa817a29ca8fc8acc07097723adefedc296eb4db37b98`,
matching the adoption note and retained probe; its live netlist SHA-256 is
`f3b4e039a695eeec34843174e9430d4bb5c65c4773ed3fa2a9998a18a0654d0e`.
The retained board SHA-256 is
`bb2f8ff56c5737b84a14b5991db1c06c45055696ee5b238f962caef7f34b048a`.

## Independent regeneration check

I regenerated parent and candidate floorplans in an isolated source root with
the same live netlist. Exactly the three listed footprint poses differ; no
`(ref,pad,net)` identity differs. Candidate P-COLLIDE reports zero pad and
fixed-courtyard overlaps. Its silk report is 260 owned / 264 degraded / 44
automatic unplaced, compared with 259 / 266 / 44 in the parent; it introduces
no additional degraded field.

`C_XU_VDDIO_10` and `C_XU_VDD_45` are visible, owned F.Silk fields at
`(203.5,112.3)` and `(220.2,99.8)` mm. `C_XU_VDD_39` is hidden only as a
reference field, retains one board-level F.Fab text at `(218.0,103.2)` mm,
and appears in the 45-entry `refdes_waiver.json`. The retained waiver SHA-256
is `5173ead8ea2147dead55209ca21b3ea579eb888a3ff22761bdb94f90298f00f8`.

No material source-adoption issue found. The explicit F.Fab-only entry still
needs its separate assembly-drawing/waiver review, and the source placement
does not close the documented PLL feed, filtered-output, or pin-42 return
route acceptance gaps.
