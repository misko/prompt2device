# USB presence-sense Q_VBUS isolated placement probe

**Result: narrow local improvement only; retain as P2 placement research.** No
canonical source, board, route, task record, or P1 attempt was changed.

The current `presence_sense` F.Cu reservation is `[207.7,76,209.2,91.3]`,
vertical, at a 0.45-mm pitch. A fresh baseline generated from the current
floorplan had a 0.000-mm connected width and zero slots. Its blockers were
`Q_VBUS` body plus `C_XU_VDD_85` body/pad 2. The adjacent `presence_xu_entry`
reservation `[204.8,91.3,205.4,106.8]` was independently 0.000 mm / zero
slots because it crosses the U_XU body and pads 88–90.

In `/tmp/crow-presence-B5uZxt/project`, the only source delta was the isolated
post-anchor:

```yaml
placement:
  post_anchors:
    Q_VBUS: [212.0, 74.5, 0]
```

Fresh generation moved exactly **one of 569** footprint poses: `Q_VBUS`
`(207.9,74.5,0)` to `(212.0,74.5,0)`. The other 568 poses, all 1,872
`(ref,pad,net)` identities, and the netlist were identical. The 27 reviewed
fixed refs remained unchanged; `C_XU_VDD_85` remained at `(207.5,90.6,0)`, so
this probe does not loosen or relocate the XMOS decoupling obligation. USB DP/
DN placement and all connector pads are unchanged.

| Reservation | Baseline current width / slots | Q_VBUS variant width / slots | Remaining current obstruction |
| --- | ---: | ---: | --- |
| `presence_sense` | 0.000 mm / 0 | **0.765 mm / 1** | `C_XU_VDD_85` body and pad 2 |
| `presence_xu_entry` | 0.000 mm / 0 | 0.000 mm / 0 | U_XU body, pads 88–90 |

The moved Q clears the local sense reservation's scalar one-slot demand, but
does not create an end-to-end handoff: `presence_xu_entry`, pad access,
continuous GND reference, return, routing, and P2 proximity are still absent.

Both boards received `kicad-cli pcb drc --severity-all --format json`. Each
reported 239 violations (225 clearance and 14 via-dangling), 499 unconnected
items, and schematic parity 0. No candidate DRC item names `Q_VBUS`; the
aggregate native result does not worsen, but these pre-existing errors still
bar any placement acceptance.

| Artifact | SHA-256 |
| --- | --- |
| Baseline floorplan | `4a457c731c204084a83aa817a29ca8fc8acc07097723adefedc296eb4db37b98` |
| Variant floorplan | `187840ff732ccc81e57838a9bdb07e1233919de1b71f01539f762b984429860d` |
| Baseline board | `827560bdafb428d99cb0b17168ef927de421e716e996ee24c56035b491d7bb7d` |
| Variant board | `60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17` |
| Netlist, unchanged | `e7ef7dbd752b9431ade0933ca77ee998963bfe3871c3caf65cddc56442f1371d` |

The candidate is sound only as an isolated placement input for a later owned
P2 redesign. It is not a P1 candidate, a route, a capacity acceptance, or a
reason to alter the 27-fixed-ref authority.
