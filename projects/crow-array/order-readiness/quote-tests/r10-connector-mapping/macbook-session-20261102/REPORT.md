# Pod J1 diagnostic: MacBook read-only session

2 November 2026. Base commit `3598a91677c89b76ccbc384caae2ee5814fbf122`.
**Result: inconclusive; diagnostic draft remains on HOLD.** Do not use this
evidence as placement or manufacturing approval.

## Observations

- The existing `POD J1 AB TEST NOT FOR ORDER` draft opened on the MacBook. The
  placement tab worked after proceeding from the BOM; it was not disabled as
  reported by the earlier server-browser attempt. The draft was reloaded and
  the placement viewer reopened without a file upload.
- The BOM/CPL dialog identified the saved placement filename as
  `pod-cpl-J1-000-BASELINE.csv`. JLC's live `loadMerge` J1 record independently
  showed `ec: {x: 10.556, y: -8.373, ang: 0}` and original `oc` x and y strings
  `10.556000mm` and `-8.373000mm`. It showed `des: J1`, `lc_code: C599441`,
  `pick_index: 11`, `is_mount: true`, `sel_mount: true`, `ft_name` and `ft_pins`
  both `插件`. The original rotation field was not separately captured.
- Parent group name was empty and its one set was `{name: 'default',
  x_offset: 0, y_offset: 0, ang: 0}`. JLC displayed RJHSE-5080 / C599441 in
  the BOM and J1 / C599441 in the placement list. The BOM showed 20 grouped
  part lines confirmed; the merge record counted 29 top-side placements. This
  is not an independent audit of every component identity.
- The saved PCB summary showed PCBA quantity 8. Fabrication quantity and the
  two automatic-review settings were not independently rechecked in this
  session; no quantity or review-setting controls were changed.
- [Sanitized baseline preview](baseline-preview.jpg) shows J1 in board context
  on reopening. Its body hides the solder tails and peg-to-hole registration.
  The visible magenta markers are not proof of peg alignment. Pin 1, all eight
  terminal centres, both locator pegs, and the socket opening's physical
  direction could not be verified from this view.

## Scene capture and limits

The loaded viewer versions were engine `3.2.37.6ef6298e` and UI
`1.0.213.a3dc0292`, matching the referenced scene-capture instructions. The
documented read-only footprint and model cache RPCs both returned objects with
`message` fields. The footprint message had 10 entries and the model message
9 entries. The live connector's `comp_info` package UUID, exact matching
footprint and model transform were not isolated; the returned caches therefore
do not yet establish the connector's physical registration. No full console
logs, unrelated caches, headers or account data are included here.

No observable terminal/peg overlay was established, so neither B nor C was
uploaded and no rotation, drag or speculative offset was applied. Baseline A
was already present and was left in place; restoration by re-upload was
unnecessary. Reopening confirmed access to the saved preview; it was not a
persistence test of a changed trial. Carrier connectors and power jack were
not tested.

## File identification

No file was uploaded in this session. These are SHA-256 hashes of the local
files at the base commit, **not** hashes computed from JLC's saved upload:

| File | SHA-256 |
| --- | --- |
| A `pod-cpl-J1-000-BASELINE.csv` | `6d1884eae3369d239da8d7f6214e27d8296df49d61daed141d9a126b4b2df9ae` |
| B `pod-cpl-J1-180-TEST-ONLY.csv` | `2f2324a2689641f1d649655309f95030b3031bfbbfadd5b278e5a2c5fa7813d0` |
| C `pod-ALL-CONNECTORS-RAW-ORIGIN-TEST-ONLY.csv` | `eef7d7cb2029a0f8f75eb1fbc9a9fa1b2d76430c377893c146dd8c14f9199710` |

The r10 213-file package integrity check passed locally. The mapping replay
and tests could not run with the Mac's `/usr/bin/python3` because `pcbnew`
was unavailable; this session does not independently reproduce the backend's
geometric residuals.

No purchases, reservations, substitutions, vendor messages or manufacturing
approvals were made. Original production-intent drafts, native boards and r10
files were not changed. NEXT in the diagnostic workflow caused JLC to update
its automatic-save timestamp, without an intentional placement or file edit.
