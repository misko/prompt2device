# Read-only JLC geometry capture before another CPL trial

2 November 2026. This supplements the inconclusive A/B session at `a8e2cf84`
and takes priority over the B/C upload sequence in the original handoff.
**Leave the diagnostic draft at restored A. Do not upload C yet.**

### Server-browser attempt: capability unavailable

A [bounded read-only TinyFish run](https://agent.tinyfish.ai/runs/4173370e-bfa5-4a4c-8656-19b49a2e6122)
completed after 190 seconds / 14 steps. Its [returned report](scene-capture-attempt.json)
contains BOM observations, but no scene data or screenshot artifacts. It reports
that JavaScript runtime/console and network-response inspection are unavailable
to that browser tool. Do not repeat this capture through TinyFish.

It also reports the placement tab disabled with an upload prompt. This is not
proof the saved MacBook placement was lost: the earlier MacBook A/B evidence
shows that preview working, and no response/scene evidence explains the
discrepancy. Check the exact diagnostic draft on the MacBook before any upload;
if it too is disabled, preserve a screenshot and stop without recreating it.
The run reports no writes. Its expansions of `oc`/`ec` as “orientation code” /
“element code” are unsupported; the inspected UI code uses those objects for
original/effective coordinates. No numerical pose or pin alignment was verified.

## Finding and limits

The publicly served JLC viewer has a model-transform path that recenters a
3D asset's bounding box, then scales, rotates and offsets it. A separate
`transformV2` path can override that transform. Consequently, the retained
catalog footprint's origin alone does not establish where the actual draft's
3D solder tails appear. The 1.017 mm correction in test C remains conditional,
not a verified correction and not evidence that the native footprint is wrong.

The UI also distinguishes original coordinates (`oc`) from effective coordinates
(`ec`) and applies each panel set's rotation and translation. We need these
actual data plus the loaded footprint/model identity before interpreting the
preview numerically. Neither a successful model rotation nor a model-only fit
proves the production placement.

## MacBook agent: one bounded read-only capture

1. Open only [POD J1 AB TEST NOT FOR ORDER](https://cart.jlcpcb.com/smt-order/?pcbFileNo=1f8dfa850b474dc9b4ac3860b26bbd59).
   Record that A is restored, J1 is RJHSE-5080 / C599441, and the draft remains
   on HOLD. Do not edit matching, position, rotation, stackup or review settings.
2. Open browser developer tools before loading the placement preview. Record
   the actual loaded engine/UI script versions. The inspected versions below
   are a reference, not a guarantee that the live page uses the same ones.
3. In the console, find the existing `loadMerge() bom_merge data:` log. If it is
   absent, reload this diagnostic preview once with the console open. Inspect
   the logged object; **do not call any save, merge, patch or auto-align method**.
   Retain a local copy of only:
   - the J1 entry in `designator_info[*].top`, including `des`, `lc_code`,
     `pick_index`, `oc`, `ec`, `is_mount`, `ft_name` and `ft_pins` if present;
   - its parent group's `name` and `set` records, including each set's `name`,
     `ang`, `x_offset`, `y_offset`;
   - the matching `comp_info` entry for its actual `lc_code`.
   Preserve missing fields as missing. Record units verbatim, not guessed mm.
   Omit `file_info`, account/order identifiers, cookies, tokens and signed URLs.
4. If the loaded engine matches the inspected version, the following calls
   retrieve catalog footprint/model caches. They do not save placement. They
   can fetch missing catalog assets; they are not guaranteed to be offline.
   Run in the page's console context, **not** in the address bar:

   ```js
   const crowBus = window._MSG_BUS_;
   if (!crowBus || typeof crowBus.rpcCall !== "function") {
     throw new Error("Viewer bus unavailable: stop, do not guess another API");
   }
   const crowFootprints = await crowBus.rpcCall("/engine/cache/footprint/all");
   console.log("Crow diagnostic footprint cache", crowFootprints.message);
   const crowModels = await crowBus.rpcCall("/engine/cache/obj/all");
   console.log("Crow diagnostic model cache", crowModels.message);
   ```

   These are source-reviewed instructions, **not yet live-browser tested**.
   If the version differs, a response lacks `message`, or a call fails, stop
   and report the exact limitation. Do not try guessed endpoints or setters.
   Keep raw returned assets local initially. Identify the C599441 package UUID
   from the actual package data; retain that footprint, its referenced model
   UUID/asset, and its model-transform metadata (`x/y/z`, `rx/ry/rz`, dimensions,
   scale and `transformV2` where present). Do not select an asset by appearance
   alone or publish unrelated caches. Screenshots of the relevant expanded
   fields are acceptable if an export cannot be isolated safely.
5. Return the sanitized J1 records, relevant catalog geometry/metadata, versions
   and a board-context image. Do not publish full console logs, a HAR or raw
   network headers. If the existing log is unavailable, report that; the next
   alternative is targeted inspection of the already-loaded scene responses,
   not a blind request to a private API. End with A unchanged and HOLD intact.

## Backend interpretation and next controlled test

Reconstruct effective J1 pose, panel transform, catalog pad coordinates and
3D-model transform separately. Map axes/units using the native notch and pad
pattern. Compare all eight numbered terminals and both locator pegs to the
manufacturer/native references; determine the mouth direction independently.
Inspect whether the 3D asset actually includes physical tails and pegs. A
missing or inaccurate feature cannot be converted into positive evidence.

If the data demonstrate that B aligns the physical pattern, discard C's origin
hypothesis. If they demonstrate the predicted 1.017 mm offset, run the existing
controlled B/C procedure with observable features, reopen, then restore A.
If model geometry disagrees with pad geometry, retain the placement hold and
report a model/placement discrepancy; do not move native pads to fit a model.
No production approval follows automatically from either result.

Only after resolving the pod mapping should the same method be applied to
carrier J101–J108 individually. Carrier power J1 requires its own C3096093
geometry and transform. No carrier correction is authorized by this pod trial.
No purchases, reservations, substitutions, vendor messages or manufacturing
approvals. Native boards and original r10 stay unchanged.

## Public implementation evidence

Retrieved read-only on 2 November 2026; no signed-in draft data was accessed.

| Public source | SHA-256 | Relevant behavior |
| --- | --- | --- |
| [Engine 3.2.37.6ef6298e](https://modules.lceda.cn/smt-gl-engine/3.2.37.6ef6298e/smt-gl-engine.js) | `e291df6d440e67289a430eda8244ad48138841d6fa74b5faafe2e73ecfc246e7` | `N$` model recenter/transform path; read-only cache RPC handlers |
| [UI 1.0.213.a3dc0292](https://modules.lceda.cn/smt-ui/1.0.213.a3dc0292/smt-foreign-trade.js) | `5226c650bdcfc213fa6b8bd216778719c0fa2162723e6f7d2e09b755ae3b461e` | `loadMerge`, `loadComponent`: logged scene data, effective pose and panel transform |
| [Order-page bundle](https://cart.jlcpcb.com/smt-static/js/2e2a2a1ed89d00198537.js) | `0cb8a0c14abab4536bae7050ab3237bd1db52ceee1d7e606f4554c10dbc4c006` | Loads/merges two scene ZIP responses before `/smt-ui/load/zip` |

These are implementation observations, not a documented or stable JLC API.
The live draft may load different assets or a different transform path.
