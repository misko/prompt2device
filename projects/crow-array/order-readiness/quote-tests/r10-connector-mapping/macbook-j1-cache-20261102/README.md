# C599441: read-only JLC viewer cache extraction

2 November 2026. Diagnostic draft only; **placement remains on HOLD**. Source
of the included catalog footprint: **[JLCEDA/EasyEDA Official Library](https://lceda.cn/)**;
see also [EasyEDA](https://easyeda.com/). Its full attribution and license
notice remain intact in the extracted record.

The existing Chrome tab was already open on the diagnostic placement viewer.
Its on-screen automatic-save timestamp was 05:39 and its `loadMerge` and model
decode console entries preceded this lookup. This is a capture of that loaded
viewer snapshot; it is not an independent reread of later server changes.

## Identity chain

1. The requested `/engine/getComponentPackageInfoByCode` lookup for `C599441`
   returned one entry under the literal key `undefined`, with package UUID
   `4305e070e23841dcbc23b07ddde0edab` and title `RJ45-TH_RJHSE-5080`.
2. The already-loaded footprint cache contained that UUID. In the live console,
   `JSON.stringify` of the lookup entry and of the cached entry compared equal.
   The exact cached entry is [C599441-loaded-footprint.json](C599441-loaded-footprint.json)
   (SHA-256 `c09dbe4e2bc3b4396109e23740f67b03758ca5ac515747f3ad82d108e2d0c8be`).
   It includes eight numbered `PAD` records and two `HOLE` records; no units
   should be assumed without interpreting the source format.
3. The footprint header has `uuid_3d` `6e2a74ad0e854536b0bb5bb1ac297b70`,
   which was **not** a key in the model cache. However, the footprint's
   `SVGNODE` 3D shape references UUID `7d3d1c9e95104606a19576559311bb67`, which
   **was** a key in that cache. The existing viewer log recorded an OBJ decode
   start, end and completion for that same shape UUID before the lookup. The
   matching cache value was a 523,591-character string beginning with OBJ
   vertex records. The asset itself is not included in this handoff.

The two different model UUID fields should not be conflated. The loaded shape
reference and cache key match; the reason the header references a different UUID
has not been established. No geometry acceptance is implied.

## Shape transform fields as returned

The matching footprint's `SVGNODE` attributes were:

```json
{"c_width":"62.039246","c_height":"58.9999","c_rotation":"0,0,0",
 "z":"-11.811","c_origin":"3985.945,2997.5316",
 "uuid":"7d3d1c9e95104606a19576559311bb67",
 "c_etype":"outline3D","id":"g1_outline",
 "title":"RJ45-TH_RJHSE-5080","layerid":"19",
 "transform":"scale(1) translate(0, 0)"}
```

These are raw viewer metadata, not verified physical units or the complete
effective model-to-board transform. No `transformV2` conclusion was drawn.

## Existing draft `comp_info.C599441`

```json
{"ba":"None","is_base":false,"is_temp_code":false,
 "lc_ma":"Amphenol ICC","lc_model":"RJHSE-5080","lc_pkg":"插件",
 "mode":"manualWeld","part_name":"RJHSE-5080","proc":"THT",
 "q":-1,"t":"None","ta":"None","tv":"None"}
```

This record identifies the part but does not itself include a package UUID;
the lookup-to-cache equality and the shape-to-model-cache match are separate
observations. The previously captured J1 effective coordinates and panel set
are in [the previous session report](../macbook-session-20261102/REPORT.md).

No CPL uploads, placement changes, rotations, vendor messages, purchases,
reservations or manufacturing approvals occurred during this extraction.
No account records, credentials, signed URLs or full logs are included.
