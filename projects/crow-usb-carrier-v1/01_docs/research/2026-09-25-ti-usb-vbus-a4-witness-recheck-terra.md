# TI USB VBUS `J_USB.2` native-witness recheck

**Status: source-bound obstruction; no P1/P2 acceptance claim.** This is a
read-only rerun on the frozen TI source packet and its native board. It does
not change the canonical board, source, or checker.

## Exact authorities

| Authority | SHA-256 |
| --- | --- |
| `04_kicad/crow_carrier.kicad_pcb` | `8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10` |
| `03_src/rules/p1_corridor_requirements.yaml` | `191e5580a6ddf56bc9670aff3593c9e9a02d91e75c0c79998b500955050e82a3` |
| `03_src/modular_plan.json` | `75c3a517cea50dd6b5745fae96b051d334debd48aac143becaca3d5fe3fc35dc` |
| `02_parts/USB4215-03-A/part.yaml` | `a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e` |
| `03_src/floorplan.yaml` | `0032b1202f5742b6575198d27ea50629826d49cf81cf12a31fead8a2929d9868` |

The exact board identifies `J_USB` as `USB4215-03-A`. Its native F.Cu VBUS
pads are:

| Pad | Native pad bbox, mm | Center, mm |
| --- | --- | --- |
| `A4` | `[232.1, 26.1, 232.7, 27.25]` | `[232.4, 26.675]` |
| `B4` | `[227.3, 26.1, 227.9, 27.25]` | `[227.6, 26.675]` |

The authoritative alias dossier maps schematic `2` to footprint `A4` and
schematic `10` to footprint `B4`. Thus `J_USB.2 -> J_USB.B4` is not a legal
native correction, even though both pads are on `VBUS_USB`.

## Fail-closed checks

The stale witness used `J_USB.2/A4`, owner `usb_edge_connector`, and
`[232.0, 25.9, 232.8, 28.0]`. Its 2.10 mm height exceeded one quarter of the
stale 8.00 mm region span, producing the reported nonlocal-bridge failure.

Against the frozen source packet, `J_USB.2` is instead owned by
`usb_frontend`. Rebinding only that owner and proposing `B4` with its exact
native bbox produces this independent diagnostic:

```
J_USB.2: witness source/native alias mismatch
```

This was obtained with the checker at SHA-256
`7da1571999ccb4de0050178153396250d43f7b6c5dd21bdb88cbd9d98af2f906`.
The B4 candidate contract SHA-256 was
`4b6f65df879231f73e6d6258f002e26e31991fbf1464111e71213ca64897e549`.

An isolated A4 control used the exact `A4` bbox above, owner `usb_frontend`,
F.Cu/north face, and moved the synthetic `vbus_entry` reservation start from
`y=28.00` to `y=27.25` so the pad's south edge contacts it. Its contract SHA
was `afb7d91448a9a51c7e0e20c6c96c4381dc54f9c27a694f895792688a18dc7c76`.
The `--diagnose-all` result contained no `J_USB.2` diagnostic. This proves the
alias, pad, layer, bbox, and reservation-edge predicates only.

## Why this is not an admissible packet correction

The frozen source floorplan assigns `usb_frontend` to
`[200, 35, 238.5, 40]`. The only legal native pad for `J_USB.2`, `A4`, is at
`[232.1, 26.1, 232.7, 27.25]`: it is fully outside that source-owned region by
7.75 mm in Y. The frozen packet also places the old `vbus_entry` at
`[231.1, 28, 239, 37]`, leaving a 0.75 mm gap from A4's south edge.

Therefore the B4 suggestion is fail-closed by the alias authority, and the
A4 bbox reduction alone cannot be a source-owned corridor witness. A valid
future source change would need to declare an edge-connector owner/region (or
an explicit connector-to-frontend transition) that contains A4 and a
reservation beginning at its physical edge. That source-model revision is
outside this research note and was not made here.

The isolated A4 control still exits `FAIL`: unrelated packet-level integration
and reset denominators remain, and `usb_device_pair` first fails at an
unmodified USB-DP ownership witness. It is evidence for neither P1 nor P2.

## Reproduction

Run the current checker with the board and four packet inputs listed above,
the A4 control contract SHA, and `--diagnose-all`. The essential control
changes are exactly:

```json
{"source":"J_USB.2","native":"J_USB.A4","block":"usb_frontend",
 "face":"north","layer":"F.Cu",
 "boundary_bbox":[232.1,26.1,232.7,27.25],"reservation_id":"vbus_entry"}
```

and `vbus_entry.bbox[1] = 27.25`. Replacing `A4` with `B4` fails at the alias
check before any native-pad geometry can qualify it.
